#!/usr/bin/env python3
"""
LAUTECH Database Backup Script

Backs up the database to S3 with compression and encryption.
Can be run manually or via Lambda/EventBridge for automation.

Usage:
    python3 backup_database.py
    python3 backup_database.py --local  # Backup to local file only
"""

import boto3
import sqlite3
import psycopg2
import os
import gzip
import json
import argparse
from datetime import datetime
from pathlib import Path

# Configuration
DB_TYPE = os.getenv('DB_TYPE', 'sqlite')  # sqlite or postgres
SQLITE_PATH = 'lautech_data.db'
S3_BUCKET = os.getenv('BACKUP_BUCKET', 'lautech-backups-prod')
BACKUP_DIR = Path('backups')
BACKUP_DIR.mkdir(exist_ok=True)


def get_db_credentials():
    """Get PostgreSQL credentials from Secrets Manager"""
    if DB_TYPE != 'postgres':
        return None

    client = boto3.client('secretsmanager')
    try:
        secret = client.get_secret_value(SecretId='lautech/db/credentials')
        return json.loads(secret['SecretString'])
    except Exception as e:
        print(f"❌ Error getting credentials: {e}")
        return None


def backup_sqlite(backup_file):
    """Backup SQLite database"""
    print(f"📦 Backing up SQLite database...")

    if not Path(SQLITE_PATH).exists():
        print(f"❌ Database not found: {SQLITE_PATH}")
        return False

    # Create backup using SQLite backup API
    source = sqlite3.connect(SQLITE_PATH)
    dest = sqlite3.connect(backup_file)

    with dest:
        source.backup(dest)

    source.close()
    dest.close()

    print(f"✅ SQLite backup created: {backup_file}")
    return True


def backup_postgres(backup_file):
    """Backup PostgreSQL database"""
    print(f"📦 Backing up PostgreSQL database...")

    creds = get_db_credentials()
    if not creds:
        return False

    # Use pg_dump
    dump_cmd = f"""
    PGPASSWORD='{creds['password']}' pg_dump \
      -h {creds['host']} \
      -U {creds['username']} \
      -d {creds['dbname']} \
      -F p \
      -f {backup_file}
    """

    result = os.system(dump_cmd)

    if result == 0:
        print(f"✅ PostgreSQL backup created: {backup_file}")
        return True
    else:
        print(f"❌ pg_dump failed with code {result}")
        return False


def compress_backup(backup_file):
    """Compress backup file with gzip"""
    print(f"🗜️  Compressing backup...")

    compressed_file = f"{backup_file}.gz"

    with open(backup_file, 'rb') as f_in:
        with gzip.open(compressed_file, 'wb') as f_out:
            f_out.writelines(f_in)

    # Remove uncompressed file
    os.remove(backup_file)

    # Get file sizes
    compressed_size = Path(compressed_file).stat().st_size / 1024 / 1024  # MB

    print(f"✅ Backup compressed: {compressed_file} ({compressed_size:.2f} MB)")
    return compressed_file


def upload_to_s3(local_file):
    """Upload backup to S3"""
    print(f"☁️  Uploading to S3...")

    timestamp = datetime.now().strftime('%Y/%m/%d')
    filename = Path(local_file).name
    s3_key = f"database/{timestamp}/{filename}"

    try:
        s3 = boto3.client('s3')

        # Upload with server-side encryption
        s3.upload_file(
            local_file,
            S3_BUCKET,
            s3_key,
            ExtraArgs={
                'ServerSideEncryption': 'AES256',
                'StorageClass': 'STANDARD_IA',
                'Metadata': {
                    'backup-date': datetime.now().isoformat(),
                    'database-type': DB_TYPE
                }
            }
        )

        s3_url = f"s3://{S3_BUCKET}/{s3_key}"
        print(f"✅ Backup uploaded: {s3_url}")

        # Set lifecycle policy if not exists
        try:
            s3.put_bucket_lifecycle_configuration(
                Bucket=S3_BUCKET,
                LifecycleConfiguration={
                    'Rules': [
                        {
                            'Id': 'DeleteOldBackups',
                            'Status': 'Enabled',
                            'Prefix': 'database/',
                            'Expiration': {'Days': 90},
                            'Transitions': [
                                {
                                    'Days': 30,
                                    'StorageClass': 'GLACIER'
                                }
                            ]
                        }
                    ]
                }
            )
            print("✅ Lifecycle policy configured (30 days → Glacier, 90 days → Delete)")
        except:
            pass  # Policy might already exist

        return s3_url

    except Exception as e:
        print(f"❌ S3 upload failed: {e}")
        return None


def send_notification(success, backup_info):
    """Send SNS notification about backup status"""
    try:
        sns = boto3.client('sns')
        topic_arn = os.getenv('BACKUP_SNS_TOPIC')

        if not topic_arn:
            return

        subject = "✅ LAUTECH Backup Success" if success else "❌ LAUTECH Backup Failed"
        message = json.dumps(backup_info, indent=2)

        sns.publish(
            TopicArn=topic_arn,
            Subject=subject,
            Message=message
        )

        print("✅ Notification sent")

    except Exception as e:
        print(f"⚠️  Could not send notification: {e}")


def main():
    parser = argparse.ArgumentParser(description='Backup LAUTECH database')
    parser.add_argument('--local', action='store_true', help='Local backup only (no S3 upload)')
    args = parser.parse_args()

    print("=" * 60)
    print("LAUTECH Database Backup")
    print("=" * 60)
    print()

    # Generate backup filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = BACKUP_DIR / f"lautech_{DB_TYPE}_{timestamp}.{'db' if DB_TYPE == 'sqlite' else 'sql'}"

    start_time = datetime.now()
    success = False
    s3_url = None

    try:
        # Create backup
        if DB_TYPE == 'sqlite':
            success = backup_sqlite(str(backup_file))
        else:
            success = backup_postgres(str(backup_file))

        if not success:
            raise Exception("Backup creation failed")

        # Compress
        compressed_file = compress_backup(str(backup_file))

        # Upload to S3 (unless --local flag)
        if not args.local:
            s3_url = upload_to_s3(compressed_file)
            if not s3_url:
                raise Exception("S3 upload failed")
        else:
            print(f"📁 Local backup: {compressed_file}")

        duration = (datetime.now() - start_time).total_seconds()

        print()
        print("=" * 60)
        print("✅ BACKUP COMPLETED")
        print("=" * 60)
        print(f"Duration: {duration:.2f} seconds")
        if s3_url:
            print(f"Location: {s3_url}")
        else:
            print(f"Location: {compressed_file}")
        print()

        # Send notification
        send_notification(True, {
            'status': 'success',
            'database_type': DB_TYPE,
            'duration_seconds': duration,
            'backup_location': s3_url or str(compressed_file),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        print()
        print("=" * 60)
        print("❌ BACKUP FAILED")
        print("=" * 60)
        print(f"Error: {str(e)}")
        print()

        # Send failure notification
        send_notification(False, {
            'status': 'failed',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

        return 1

    return 0


if __name__ == '__main__':
    exit(main())

#!/usr/bin/env python3
"""
LAUTECH SQLite → PostgreSQL RDS Migration Script

Migrates data from local SQLite database to AWS RDS PostgreSQL.

Prerequisites:
- RDS PostgreSQL instance created
- Credentials stored in AWS Secrets Manager (secret: lautech/db/credentials)
- psycopg2 installed: pip install psycopg2-binary

Usage:
    python3 migrate_to_rds.py
    python3 migrate_to_rds.py --verify  # Verify migration only
    python3 migrate_to_rds.py --dry-run # Show what would be migrated
"""

import sqlite3
import psycopg2
from psycopg2.extras import execute_batch
import boto3
import json
import argparse
from datetime import datetime

SQLITE_DB = 'lautech_data.db'


def get_rds_credentials():
    """Get RDS credentials from Secrets Manager"""
    print("🔐 Fetching RDS credentials from Secrets Manager...")

    try:
        client = boto3.client('secretsmanager')
        secret = client.get_secret_value(SecretId='lautech/db/credentials')
        creds = json.loads(secret['SecretString'])
        print(f"✅ Credentials retrieved for host: {creds['host']}")
        return creds
    except Exception as e:
        print(f"❌ Error getting credentials: {e}")
        print("\n💡 Make sure the secret 'lautech/db/credentials' exists:")
        print("""
aws secretsmanager create-secret \\
  --name lautech/db/credentials \\
  --secret-string '{
    "username": "lautechadmin",
    "password": "YOUR_PASSWORD",
    "host": "lautech-db.xxxxxxxxx.us-east-1.rds.amazonaws.com",
    "port": 5432,
    "dbname": "lautech_db"
  }'
        """)
        return None


def create_postgres_tables(pg_cursor):
    """Create tables in PostgreSQL with indexes"""
    print("📋 Creating PostgreSQL tables...")

    # Courses table
    pg_cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            code VARCHAR(20) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            credits INTEGER,
            prerequisites TEXT,
            description TEXT,
            semester VARCHAR(50),
            lecturer VARCHAR(255),
            department VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Fees table
    pg_cursor.execute("""
        CREATE TABLE IF NOT EXISTS fees (
            id SERIAL PRIMARY KEY,
            level VARCHAR(50) NOT NULL,
            amount INTEGER NOT NULL,
            fee_type VARCHAR(50),
            session VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Academic calendar table
    pg_cursor.execute("""
        CREATE TABLE IF NOT EXISTS academic_calendar (
            id SERIAL PRIMARY KEY,
            event_type VARCHAR(100) NOT NULL,
            event_date DATE NOT NULL,
            semester VARCHAR(50),
            session VARCHAR(20),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Hostels table
    pg_cursor.execute("""
        CREATE TABLE IF NOT EXISTS hostels (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            gender VARCHAR(20),
            capacity INTEGER,
            status VARCHAR(50),
            facilities TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    print("✅ Tables created")

    # Create indexes
    print("📑 Creating indexes...")

    pg_cursor.execute("CREATE INDEX IF NOT EXISTS idx_courses_department ON courses(department)")
    pg_cursor.execute("CREATE INDEX IF NOT EXISTS idx_courses_semester ON courses(semester)")
    pg_cursor.execute("CREATE INDEX IF NOT EXISTS idx_fees_level ON fees(level)")
    pg_cursor.execute("CREATE INDEX IF NOT EXISTS idx_fees_session ON fees(session)")
    pg_cursor.execute("CREATE INDEX IF NOT EXISTS idx_calendar_date ON academic_calendar(event_date)")
    pg_cursor.execute("CREATE INDEX IF NOT EXISTS idx_calendar_semester ON academic_calendar(semester)")
    pg_cursor.execute("CREATE INDEX IF NOT EXISTS idx_hostels_status ON hostels(status)")
    pg_cursor.execute("CREATE INDEX IF NOT EXISTS idx_hostels_gender ON hostels(gender)")

    print("✅ Indexes created")


def migrate_table(sqlite_cursor, pg_cursor, table_name, columns, dry_run=False):
    """Migrate a table from SQLite to PostgreSQL"""
    print(f"\n📊 Migrating table: {table_name}")

    # Get data from SQLite
    sqlite_cursor.execute(f"SELECT {','.join(columns)} FROM {table_name}")
    rows = sqlite_cursor.fetchall()

    print(f"   Found {len(rows)} rows in SQLite")

    if dry_run:
        print(f"   [DRY RUN] Would migrate {len(rows)} rows")
        return len(rows)

    if len(rows) == 0:
        print("   ⚠️  No data to migrate")
        return 0

    # Prepare INSERT statement
    placeholders = ','.join(['%s'] * len(columns))
    insert_sql = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"

    # Batch insert for better performance
    execute_batch(pg_cursor, insert_sql, rows, page_size=100)

    print(f"   ✅ Migrated {len(rows)} rows")
    return len(rows)


def verify_migration(sqlite_cursor, pg_cursor, table_name):
    """Verify data was migrated correctly"""
    sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    sqlite_count = sqlite_cursor.fetchone()[0]

    pg_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    pg_count = pg_cursor.fetchone()[0]

    match = "✅" if sqlite_count == pg_count else "❌"
    print(f"   {match} {table_name}: SQLite={sqlite_count}, PostgreSQL={pg_count}")

    return sqlite_count == pg_count


def main():
    parser = argparse.ArgumentParser(description='Migrate LAUTECH database to RDS')
    parser.add_argument('--verify', action='store_true', help='Verify migration only')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be migrated')
    args = parser.parse_args()

    print("=" * 70)
    print("LAUTECH Database Migration: SQLite → PostgreSQL RDS")
    print("=" * 70)
    print()

    # Get RDS credentials
    creds = get_rds_credentials()
    if not creds:
        return 1

    # Connect to SQLite
    print(f"\n📂 Connecting to SQLite: {SQLITE_DB}")
    try:
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        sqlite_cursor = sqlite_conn.cursor()
        print("✅ SQLite connected")
    except Exception as e:
        print(f"❌ SQLite connection failed: {e}")
        return 1

    # Connect to PostgreSQL
    print(f"\n🐘 Connecting to PostgreSQL: {creds['host']}/{creds['dbname']}")
    try:
        pg_conn = psycopg2.connect(
            dbname=creds['dbname'],
            host=creds['host'],
            user=creds['username'],
            password=creds['password'],
            port=creds.get('port', 5432)
        )
        pg_cursor = pg_conn.cursor()
        print("✅ PostgreSQL connected")
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check RDS instance is running")
        print("   2. Verify security group allows your IP")
        print("   3. Check credentials are correct")
        return 1

    if args.verify:
        # Verification mode
        print("\n" + "=" * 70)
        print("VERIFICATION MODE")
        print("=" * 70)

        all_match = True
        all_match &= verify_migration(sqlite_cursor, pg_cursor, 'courses')
        all_match &= verify_migration(sqlite_cursor, pg_cursor, 'fees')
        all_match &= verify_migration(sqlite_cursor, pg_cursor, 'academic_calendar')
        all_match &= verify_migration(sqlite_cursor, pg_cursor, 'hostels')

        if all_match:
            print("\n✅ All tables verified successfully!")
        else:
            print("\n❌ Verification failed - row counts don't match")

        sqlite_conn.close()
        pg_conn.close()
        return 0 if all_match else 1

    # Migration mode
    try:
        # Create tables
        create_postgres_tables(pg_cursor)
        pg_conn.commit()

        # Migrate data
        total_rows = 0

        total_rows += migrate_table(
            sqlite_cursor, pg_cursor, 'courses',
            ['code', 'name', 'credits', 'prerequisites', 'description', 'semester', 'lecturer', 'department'],
            dry_run=args.dry_run
        )

        total_rows += migrate_table(
            sqlite_cursor, pg_cursor, 'fees',
            ['level', 'amount', 'fee_type', 'session'],
            dry_run=args.dry_run
        )

        total_rows += migrate_table(
            sqlite_cursor, pg_cursor, 'academic_calendar',
            ['event_type', 'event_date', 'semester', 'session', 'description'],
            dry_run=args.dry_run
        )

        total_rows += migrate_table(
            sqlite_cursor, pg_cursor, 'hostels',
            ['name', 'gender', 'capacity', 'status', 'facilities'],
            dry_run=args.dry_run
        )

        if not args.dry_run:
            # Commit transaction
            pg_conn.commit()

            print("\n" + "=" * 70)
            print("✅ MIGRATION COMPLETED SUCCESSFULLY")
            print("=" * 70)
            print(f"Total rows migrated: {total_rows}")
            print()

            # Verify
            print("\n🔍 Verifying migration...")
            all_match = True
            all_match &= verify_migration(sqlite_cursor, pg_cursor, 'courses')
            all_match &= verify_migration(sqlite_cursor, pg_cursor, 'fees')
            all_match &= verify_migration(sqlite_cursor, pg_cursor, 'academic_calendar')
            all_match &= verify_migration(sqlite_cursor, pg_cursor, 'hostels')

            if all_match:
                print("\n✅ All data verified!")
            else:
                print("\n⚠️  Warning: Row counts don't match")

            print("\n📝 Next steps:")
            print("   1. Update application to use PostgreSQL connection")
            print("   2. Test thoroughly in staging environment")
            print("   3. Update AgentCore configuration")
            print("   4. Deploy updated application")
            print("   5. Monitor for any issues")
            print()
        else:
            print(f"\n[DRY RUN] Would migrate {total_rows} total rows")
            print("Run without --dry-run to perform actual migration")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        pg_conn.rollback()
        return 1

    finally:
        sqlite_conn.close()
        pg_conn.close()

    return 0


if __name__ == '__main__':
    exit(main())

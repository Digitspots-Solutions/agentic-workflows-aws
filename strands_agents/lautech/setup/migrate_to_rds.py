"""
Migrate data from SQLite to RDS PostgreSQL
Transfers all data from the local SQLite database to the production RDS instance
"""

import sqlite3
import boto3
import json
import psycopg2
import psycopg2.extras
from pathlib import Path

# Configuration
SQLITE_PATH = Path("lautech_data.db")
SECRET_NAME = "lautech/rds/credentials"
REGION = "us-east-1"


def get_rds_credentials():
    """Get RDS credentials from AWS Secrets Manager"""
    client = boto3.client('secretsmanager', region_name=REGION)
    response = client.get_secret_value(SecretId=SECRET_NAME)
    return json.loads(response['SecretString'])


def get_sqlite_data():
    """Read all data from SQLite database"""
    print(f"📖 Reading data from SQLite: {SQLITE_PATH.absolute()}")

    if not SQLITE_PATH.exists():
        raise FileNotFoundError(f"SQLite database not found: {SQLITE_PATH}")

    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    data = {}

    # Get courses
    cursor.execute("SELECT * FROM courses")
    data['courses'] = [dict(row) for row in cursor.fetchall()]
    print(f"   ✓ Found {len(data['courses'])} courses")

    # Get fees
    cursor.execute("SELECT * FROM fees")
    data['fees'] = [dict(row) for row in cursor.fetchall()]
    print(f"   ✓ Found {len(data['fees'])} fees")

    # Get calendar
    cursor.execute("SELECT * FROM academic_calendar")
    data['calendar'] = [dict(row) for row in cursor.fetchall()]
    print(f"   ✓ Found {len(data['calendar'])} calendar events")

    # Get hostels
    cursor.execute("SELECT * FROM hostels")
    data['hostels'] = [dict(row) for row in cursor.fetchall()]
    print(f"   ✓ Found {len(data['hostels'])} hostels")

    conn.close()
    return data


def create_postgres_schema(pg_conn):
    """Create PostgreSQL schema"""
    print("\n🏗️  Creating PostgreSQL schema...")

    cursor = pg_conn.cursor()

    # Create courses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            credits INTEGER,
            prerequisites TEXT,
            description TEXT,
            semester TEXT,
            lecturer TEXT,
            department TEXT
        )
    """)
    print("   ✓ Created courses table")

    # Create fees table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fees (
            id SERIAL PRIMARY KEY,
            level TEXT NOT NULL,
            amount INTEGER NOT NULL,
            fee_type TEXT,
            session TEXT
        )
    """)
    print("   ✓ Created fees table")

    # Create calendar table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS academic_calendar (
            id SERIAL PRIMARY KEY,
            event_type TEXT NOT NULL,
            event_date TEXT NOT NULL,
            semester TEXT,
            session TEXT,
            description TEXT
        )
    """)
    print("   ✓ Created academic_calendar table")

    # Create hostels table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hostels (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            gender TEXT,
            capacity INTEGER,
            status TEXT,
            facilities TEXT
        )
    """)
    print("   ✓ Created hostels table")

    pg_conn.commit()
    cursor.close()


def clear_postgres_data(pg_conn):
    """Clear existing data from PostgreSQL tables"""
    print("\n🧹 Clearing existing data...")

    cursor = pg_conn.cursor()

    cursor.execute("DELETE FROM courses")
    cursor.execute("DELETE FROM fees")
    cursor.execute("DELETE FROM academic_calendar")
    cursor.execute("DELETE FROM hostels")

    pg_conn.commit()
    cursor.close()

    print("   ✓ Cleared all tables")


def migrate_data(data, pg_conn):
    """Migrate data from SQLite to PostgreSQL"""
    print("\n📦 Migrating data to PostgreSQL...")

    cursor = pg_conn.cursor()

    # Migrate courses
    print(f"\n   Migrating {len(data['courses'])} courses...")
    for course in data['courses']:
        cursor.execute("""
            INSERT INTO courses (code, name, credits, prerequisites, description, semester, lecturer, department)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (code) DO UPDATE SET
                name = EXCLUDED.name,
                credits = EXCLUDED.credits,
                prerequisites = EXCLUDED.prerequisites,
                description = EXCLUDED.description,
                semester = EXCLUDED.semester,
                lecturer = EXCLUDED.lecturer,
                department = EXCLUDED.department
        """, (
            course['code'], course['name'], course['credits'],
            course['prerequisites'], course['description'],
            course['semester'], course['lecturer'], course['department']
        ))
    print(f"      ✓ Migrated {len(data['courses'])} courses")

    # Migrate fees
    print(f"\n   Migrating {len(data['fees'])} fees...")
    for fee in data['fees']:
        # Skip the 'id' field for auto-increment
        cursor.execute("""
            INSERT INTO fees (level, amount, fee_type, session)
            VALUES (%s, %s, %s, %s)
        """, (
            fee['level'], fee['amount'], fee['fee_type'], fee['session']
        ))
    print(f"      ✓ Migrated {len(data['fees'])} fees (including dance fee)")

    # Migrate calendar
    print(f"\n   Migrating {len(data['calendar'])} calendar events...")
    for event in data['calendar']:
        cursor.execute("""
            INSERT INTO academic_calendar (event_type, event_date, semester, session, description)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            event['event_type'], event['event_date'],
            event['semester'], event['session'], event['description']
        ))
    print(f"      ✓ Migrated {len(data['calendar'])} calendar events")

    # Migrate hostels
    print(f"\n   Migrating {len(data['hostels'])} hostels...")
    for hostel in data['hostels']:
        cursor.execute("""
            INSERT INTO hostels (name, gender, capacity, status, facilities)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            hostel['name'], hostel['gender'], hostel['capacity'],
            hostel['status'], hostel['facilities']
        ))
    print(f"      ✓ Migrated {len(data['hostels'])} hostels")

    pg_conn.commit()
    cursor.close()


def verify_migration(pg_conn):
    """Verify data was migrated correctly"""
    print("\n🔍 Verifying migration...")

    cursor = pg_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Count records
    cursor.execute("SELECT COUNT(*) as count FROM courses")
    courses_count = cursor.fetchone()['count']
    print(f"   ✓ Courses: {courses_count}")

    cursor.execute("SELECT COUNT(*) as count FROM fees")
    fees_count = cursor.fetchone()['count']
    print(f"   ✓ Fees: {fees_count}")

    # Check for dance fee specifically
    cursor.execute("SELECT * FROM fees WHERE level = 'Dance' OR fee_type = 'Other'")
    dance_fee = cursor.fetchone()
    if dance_fee:
        print(f"   ✓ Dance fee found: ₦{dance_fee['amount']:,} ({dance_fee['level']})")
    else:
        print("   ⚠️  Dance fee not found!")

    cursor.execute("SELECT COUNT(*) as count FROM academic_calendar")
    calendar_count = cursor.fetchone()['count']
    print(f"   ✓ Calendar events: {calendar_count}")

    cursor.execute("SELECT COUNT(*) as count FROM hostels")
    hostels_count = cursor.fetchone()['count']
    print(f"   ✓ Hostels: {hostels_count}")

    cursor.close()

    return courses_count > 0 and fees_count > 0


def main():
    """Main migration function"""
    print("=" * 60)
    print("LAUTECH Database Migration: SQLite → RDS PostgreSQL")
    print("=" * 60)
    print()

    try:
        # Get SQLite data
        data = get_sqlite_data()

        # Get RDS credentials
        print("\n🔐 Retrieving RDS credentials from Secrets Manager...")
        creds = get_rds_credentials()
        print(f"   ✓ Connected to: {creds['host']}")

        # Connect to PostgreSQL
        print("\n🔌 Connecting to PostgreSQL...")
        pg_conn = psycopg2.connect(
            host=creds['host'],
            port=creds['port'],
            database=creds['dbname'],
            user=creds['username'],
            password=creds['password'],
            connect_timeout=10
        )
        print("   ✓ Connected successfully")

        # Create schema
        create_postgres_schema(pg_conn)

        # Clear existing data
        clear_postgres_data(pg_conn)

        # Migrate data
        migrate_data(data, pg_conn)

        # Verify migration
        if verify_migration(pg_conn):
            print("\n" + "=" * 60)
            print("✅ Migration completed successfully!")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Update Lambda environment variable: USE_POSTGRES=true")
            print("2. Update Lambda environment variable: DB_SECRET_NAME=lautech/rds/credentials")
            print("3. Add IAM permissions for Lambda to access RDS and Secrets Manager")
            print("4. Test the agent with the new database")
            print("=" * 60)
        else:
            print("\n⚠️  Migration completed but verification failed")

        pg_conn.close()

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("Make sure you're running this script from the lautech directory")
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()

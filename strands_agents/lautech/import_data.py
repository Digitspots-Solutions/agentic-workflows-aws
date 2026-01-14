#!/usr/bin/env python3
"""
LAUTECH Data Import Script

Import CSV data into the SQLite database for the AgentCore agent.

Usage:
    python3 import_data.py --all           # Import all CSV files
    python3 import_data.py --courses       # Import only courses
    python3 import_data.py --fees          # Import only fees
    python3 import_data.py --calendar      # Import only calendar
    python3 import_data.py --hostels       # Import only hostels
"""

import csv
import sqlite3
import argparse
from pathlib import Path

DB_PATH = Path("lautech_data.db")
DATA_DIR = Path("data")


def create_tables(conn):
    """Create all tables if they don't exist"""
    cursor = conn.cursor()

    # Courses table
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

    # Fees table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT NOT NULL,
            amount INTEGER NOT NULL,
            fee_type TEXT,
            session TEXT
        )
    """)

    # Calendar table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS academic_calendar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            event_date TEXT NOT NULL,
            semester TEXT,
            session TEXT,
            description TEXT
        )
    """)

    # Hostels table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hostels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            gender TEXT,
            capacity INTEGER,
            status TEXT,
            facilities TEXT
        )
    """)

    conn.commit()
    print("✅ Tables created/verified")


def clear_table(conn, table_name):
    """Clear all data from a table"""
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table_name}")
    conn.commit()
    print(f"🗑️  Cleared {table_name} table")


def import_courses(conn, clear=False):
    """Import courses from CSV"""
    if clear:
        clear_table(conn, 'courses')

    csv_file = DATA_DIR / "courses.csv"
    if not csv_file.exists():
        print(f"❌ File not found: {csv_file}")
        return

    cursor = conn.cursor()
    count = 0

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO courses
                    (code, name, credits, prerequisites, description, semester, lecturer, department)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row['code'],
                    row['name'],
                    int(row['credits']),
                    row['prerequisites'],
                    row['description'],
                    row['semester'],
                    row['lecturer'],
                    row['department']
                ))
                count += 1
            except Exception as e:
                print(f"❌ Error importing course {row.get('code', 'unknown')}: {e}")

    conn.commit()
    print(f"✅ Imported {count} courses")


def import_fees(conn, clear=False):
    """Import fees from CSV"""
    if clear:
        clear_table(conn, 'fees')

    csv_file = DATA_DIR / "fees.csv"
    if not csv_file.exists():
        print(f"❌ File not found: {csv_file}")
        return

    cursor = conn.cursor()
    count = 0

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                cursor.execute("""
                    INSERT INTO fees (level, amount, fee_type, session)
                    VALUES (?, ?, ?, ?)
                """, (
                    row['level'],
                    int(row['amount']),
                    row['fee_type'],
                    row['session']
                ))
                count += 1
            except Exception as e:
                print(f"❌ Error importing fee {row.get('level', 'unknown')}: {e}")

    conn.commit()
    print(f"✅ Imported {count} fees")


def import_calendar(conn, clear=False):
    """Import calendar events from CSV"""
    if clear:
        clear_table(conn, 'academic_calendar')

    csv_file = DATA_DIR / "calendar.csv"
    if not csv_file.exists():
        print(f"❌ File not found: {csv_file}")
        return

    cursor = conn.cursor()
    count = 0

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                cursor.execute("""
                    INSERT INTO academic_calendar
                    (event_type, event_date, semester, session, description)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    row['event_type'],
                    row['event_date'],
                    row['semester'],
                    row['session'],
                    row['description']
                ))
                count += 1
            except Exception as e:
                print(f"❌ Error importing event {row.get('event_type', 'unknown')}: {e}")

    conn.commit()
    print(f"✅ Imported {count} calendar events")


def import_hostels(conn, clear=False):
    """Import hostels from CSV"""
    if clear:
        clear_table(conn, 'hostels')

    csv_file = DATA_DIR / "hostels.csv"
    if not csv_file.exists():
        print(f"❌ File not found: {csv_file}")
        return

    cursor = conn.cursor()
    count = 0

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                cursor.execute("""
                    INSERT INTO hostels (name, gender, capacity, status, facilities)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    row['name'],
                    row['gender'],
                    int(row['capacity']),
                    row['status'],
                    row['facilities']
                ))
                count += 1
            except Exception as e:
                print(f"❌ Error importing hostel {row.get('name', 'unknown')}: {e}")

    conn.commit()
    print(f"✅ Imported {count} hostels")


def show_statistics(conn):
    """Show database statistics"""
    cursor = conn.cursor()

    print("\n" + "=" * 60)
    print("DATABASE STATISTICS")
    print("=" * 60)

    cursor.execute("SELECT COUNT(*) FROM courses")
    print(f"📚 Courses: {cursor.fetchone()[0]}")

    cursor.execute("SELECT COUNT(*) FROM fees")
    print(f"💰 Fees: {cursor.fetchone()[0]}")

    cursor.execute("SELECT COUNT(*) FROM academic_calendar")
    print(f"📅 Calendar Events: {cursor.fetchone()[0]}")

    cursor.execute("SELECT COUNT(*) FROM hostels")
    print(f"🏠 Hostels: {cursor.fetchone()[0]}")

    print("=" * 60)

    # Show sample data
    print("\n📚 Sample Courses:")
    cursor.execute("SELECT code, name, semester FROM courses LIMIT 5")
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} ({row[2]})")

    print("\n💰 Sample Fees:")
    cursor.execute("SELECT level, amount, fee_type FROM fees LIMIT 5")
    for row in cursor.fetchall():
        print(f"   {row[0]}: ₦{row[1]:,} ({row[2]})")

    print("\n📅 Upcoming Events:")
    cursor.execute("""
        SELECT event_type, event_date, description
        FROM academic_calendar
        WHERE event_date >= date('now')
        ORDER BY event_date
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"   {row[1]}: {row[0]} - {row[2]}")

    print()


def main():
    parser = argparse.ArgumentParser(description='Import LAUTECH data into database')
    parser.add_argument('--all', action='store_true', help='Import all data')
    parser.add_argument('--courses', action='store_true', help='Import courses')
    parser.add_argument('--fees', action='store_true', help='Import fees')
    parser.add_argument('--calendar', action='store_true', help='Import calendar')
    parser.add_argument('--hostels', action='store_true', help='Import hostels')
    parser.add_argument('--clear', action='store_true', help='Clear existing data before import')
    parser.add_argument('--stats', action='store_true', help='Show database statistics only')

    args = parser.parse_args()

    # If no arguments, show help
    if not (args.all or args.courses or args.fees or args.calendar or args.hostels or args.stats):
        parser.print_help()
        return

    print("=" * 60)
    print("LAUTECH Data Import Tool")
    print("=" * 60)
    print()

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    create_tables(conn)

    if args.stats:
        show_statistics(conn)
        conn.close()
        return

    # Import data
    if args.all or args.courses:
        import_courses(conn, clear=args.clear)

    if args.all or args.fees:
        import_fees(conn, clear=args.clear)

    if args.all or args.calendar:
        import_calendar(conn, clear=args.clear)

    if args.all or args.hostels:
        import_hostels(conn, clear=args.clear)

    # Show statistics
    show_statistics(conn)

    conn.close()

    print("\n✅ Import complete!")
    print("\n📝 Next steps:")
    print("   1. Verify data: sqlite3 lautech_data.db 'SELECT * FROM courses LIMIT 5;'")
    print("   2. Test locally: agentcore launch -l")
    print("   3. Deploy: agentcore launch")
    print()


if __name__ == "__main__":
    main()

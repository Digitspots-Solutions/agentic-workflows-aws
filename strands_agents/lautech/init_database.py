#!/usr/bin/env python3
"""
Initialize LAUTECH database with initial data
Run this BEFORE deploying to AWS to create the database file
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("lautech_data.db")

def init_database():
    """Initialize SQLite database with LAUTECH data"""

    # Remove existing database if any
    if DB_PATH.exists():
        print(f"⚠️  Removing existing database: {DB_PATH}")
        DB_PATH.unlink()

    print(f"📦 Creating new database: {DB_PATH.absolute()}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

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

    # Create fees table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT NOT NULL,
            amount INTEGER NOT NULL,
            fee_type TEXT,
            session TEXT
        )
    """)

    # Create calendar table
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

    # Create hostels table
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

    # Insert sample data
    print("📝 Inserting sample data...")

    courses = [
        ("CSC201", "Computer Programming II", 3, "CSC101",
         "Advanced programming concepts, data structures, and algorithms",
         "Second Semester", "Dr. Adeyemi O.", "Computer Science"),
        ("CSC301", "Database Management Systems", 3, "CSC201",
         "Database design, SQL, normalization, and transaction management",
         "First Semester", "Prof. Ibrahim S.", "Computer Science"),
        ("CSC302", "Operating Systems", 3, "CSC201",
         "Process management, memory management, file systems, and concurrency",
         "Second Semester", "Dr. Ogunleye T.", "Computer Science"),
        ("CSC303", "Web Programming", 3, "CSC201",
         "HTML, CSS, JavaScript, backend development, and web frameworks",
         "First Semester", "Mr. Adeleke M.", "Computer Science"),
    ]
    cursor.executemany("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?, ?, ?)", courses)
    print(f"   ✅ Inserted {len(courses)} courses")

    fees = [
        ("100 Level", 100000, "Tuition + Acceptance", "2024/2025"),
        ("200-400 Level", 75000, "Tuition", "2024/2025"),
        ("500 Level", 85000, "Tuition", "2024/2025"),
    ]
    cursor.executemany("INSERT INTO fees (level, amount, fee_type, session) VALUES (?, ?, ?, ?)", fees)
    print(f"   ✅ Inserted {len(fees)} fees")

    events = [
        ("Registration Start", "2024-09-01", "First Semester", "2024/2025", "Registration opens"),
        ("Registration End", "2024-09-15", "First Semester", "2024/2025", "Registration closes"),
        ("Semester Start", "2024-09-16", "First Semester", "2024/2025", "Classes begin"),
    ]
    cursor.executemany("INSERT INTO academic_calendar (event_type, event_date, semester, session, description) VALUES (?, ?, ?, ?, ?)", events)
    print(f"   ✅ Inserted {len(events)} calendar events")

    hostels = [
        ("Ajose Hall", "Male", 400, "Available", "24/7 electricity, Water, Security"),
        ("Adeoye Hall", "Female", 380, "Available", "24/7 electricity, Water, Security"),
    ]
    cursor.executemany("INSERT INTO hostels (name, gender, capacity, status, facilities) VALUES (?, ?, ?, ?, ?)", hostels)
    print(f"   ✅ Inserted {len(hostels)} hostels")

    conn.commit()
    conn.close()

    print(f"\n✅ Database initialized successfully!")
    print(f"📁 Location: {DB_PATH.absolute()}")
    print(f"📊 Size: {DB_PATH.stat().st_size / 1024:.2f} KB")
    print(f"\n🎯 Next steps:")
    print(f"   1. Run admin panel to add/edit data: ./run_admin.sh")
    print(f"   2. Deploy to AWS: agentcore launch")

if __name__ == "__main__":
    init_database()

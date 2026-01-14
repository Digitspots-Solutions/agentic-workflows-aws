"""
Database utilities for LAUTECH Agent
Supports both SQLite (local/development) and PostgreSQL (production/RDS)
"""

import os
import json
import logging
from typing import Optional, List, Dict
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Database configuration
USE_POSTGRES = os.getenv('USE_POSTGRES', 'false').lower() == 'true'
SECRET_NAME = os.getenv('DB_SECRET_NAME', 'lautech/rds/credentials')
SQLITE_PATH = os.getenv('SQLITE_PATH', '/tmp/lautech_data.db')

# Import database libraries
if USE_POSTGRES:
    try:
        import psycopg2
        import psycopg2.extras
        import boto3
        HAS_POSTGRES = True
    except ImportError:
        logger.warning("psycopg2 not installed. Install with: pip install psycopg2-binary")
        HAS_POSTGRES = False
else:
    import sqlite3
    HAS_POSTGRES = False


def get_db_credentials():
    """Get database credentials from AWS Secrets Manager"""
    if not USE_POSTGRES:
        return None

    try:
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )

        response = client.get_secret_value(SecretId=SECRET_NAME)
        secret = json.loads(response['SecretString'])

        logger.info(f"✅ Retrieved database credentials from {SECRET_NAME}")
        return secret

    except Exception as e:
        logger.error(f"Failed to retrieve database credentials: {e}")
        raise


@contextmanager
def get_db_connection():
    """Get database connection (SQLite or PostgreSQL)"""
    if USE_POSTGRES and HAS_POSTGRES:
        # PostgreSQL connection
        creds = get_db_credentials()
        conn = psycopg2.connect(
            host=creds['host'],
            port=creds['port'],
            database=creds['dbname'],
            user=creds['username'],
            password=creds['password'],
            connect_timeout=10
        )
        try:
            yield conn
        finally:
            conn.close()
    else:
        # SQLite connection
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()


def execute_query(query: str, params: tuple = None, fetch: str = 'all') -> Optional[List[Dict]]:
    """
    Execute a database query

    Args:
        query: SQL query to execute
        params: Query parameters
        fetch: 'all', 'one', or None (for INSERT/UPDATE/DELETE)

    Returns:
        List of dictionaries (for SELECT queries) or None
    """
    with get_db_connection() as conn:
        if USE_POSTGRES and HAS_POSTGRES:
            # PostgreSQL
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(query, params or ())

            if fetch == 'all':
                result = [dict(row) for row in cursor.fetchall()]
            elif fetch == 'one':
                row = cursor.fetchone()
                result = dict(row) if row else None
            else:
                result = None

            conn.commit()
            cursor.close()
            return result
        else:
            # SQLite
            cursor = conn.cursor()
            cursor.execute(query, params or ())

            if fetch == 'all':
                result = [dict(row) for row in cursor.fetchall()]
            elif fetch == 'one':
                row = cursor.fetchone()
                result = dict(row) if row else None
            else:
                result = None

            conn.commit()
            cursor.close()
            return result


def init_database():
    """Initialize database schema"""
    logger.info(f"Initializing database (USE_POSTGRES={USE_POSTGRES})...")

    # Define schema
    # PostgreSQL uses SERIAL for auto-increment, SQLite uses AUTOINCREMENT
    if USE_POSTGRES and HAS_POSTGRES:
        courses_table = """
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
        """

        fees_table = """
            CREATE TABLE IF NOT EXISTS fees (
                id SERIAL PRIMARY KEY,
                level TEXT NOT NULL,
                amount INTEGER NOT NULL,
                fee_type TEXT,
                session TEXT
            )
        """

        calendar_table = """
            CREATE TABLE IF NOT EXISTS academic_calendar (
                id SERIAL PRIMARY KEY,
                event_type TEXT NOT NULL,
                event_date TEXT NOT NULL,
                semester TEXT,
                session TEXT,
                description TEXT
            )
        """

        hostels_table = """
            CREATE TABLE IF NOT EXISTS hostels (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                gender TEXT,
                capacity INTEGER,
                status TEXT,
                facilities TEXT
            )
        """
    else:
        courses_table = """
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
        """

        fees_table = """
            CREATE TABLE IF NOT EXISTS fees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                amount INTEGER NOT NULL,
                fee_type TEXT,
                session TEXT
            )
        """

        calendar_table = """
            CREATE TABLE IF NOT EXISTS academic_calendar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                event_date TEXT NOT NULL,
                semester TEXT,
                session TEXT,
                description TEXT
            )
        """

        hostels_table = """
            CREATE TABLE IF NOT EXISTS hostels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                gender TEXT,
                capacity INTEGER,
                status TEXT,
                facilities TEXT
            )
        """

    # Create tables
    execute_query(courses_table, fetch=None)
    execute_query(fees_table, fetch=None)
    execute_query(calendar_table, fetch=None)
    execute_query(hostels_table, fetch=None)

    logger.info("✅ Database schema initialized")


# Query functions for each table - with optional limits for performance
MAX_RESULTS = int(os.getenv('DB_MAX_RESULTS', '50'))  # Increased limit to ensure all records are returned

def get_courses(limit: int = MAX_RESULTS, search: str = None) -> List[Dict]:
    """Get courses with optional limit and search filter"""
    if search:
        if USE_POSTGRES and HAS_POSTGRES:
            query = "SELECT code, name, credits, department FROM courses WHERE LOWER(name) LIKE %s OR LOWER(code) LIKE %s LIMIT %s"
            params = (f'%{search.lower()}%', f'%{search.lower()}%', limit)
        else:
            query = "SELECT code, name, credits, department FROM courses WHERE LOWER(name) LIKE ? OR LOWER(code) LIKE ? LIMIT ?"
            params = (f'%{search.lower()}%', f'%{search.lower()}%', limit)
        return execute_query(query, params, fetch='all') or []
    else:
        return execute_query(f"SELECT code, name, credits, department FROM courses LIMIT {limit}", fetch='all') or []


def get_fees(limit: int = MAX_RESULTS, level: str = None) -> List[Dict]:
    """Get fees with optional limit and level filter"""
    if level:
        if USE_POSTGRES and HAS_POSTGRES:
            return execute_query("SELECT level, amount, fee_type FROM fees WHERE LOWER(level) LIKE %s LIMIT %s", 
                               (f'%{level.lower()}%', limit), fetch='all') or []
        else:
            return execute_query("SELECT level, amount, fee_type FROM fees WHERE LOWER(level) LIKE ? LIMIT ?", 
                               (f'%{level.lower()}%', limit), fetch='all') or []
    return execute_query(f"SELECT level, amount, fee_type FROM fees LIMIT {limit}", fetch='all') or []


def get_calendar(limit: int = MAX_RESULTS, upcoming_only: bool = True) -> List[Dict]:
    """Get calendar events with optional limit"""
    return execute_query(f"SELECT event_type, event_date, description FROM academic_calendar ORDER BY event_date LIMIT {limit}", fetch='all') or []


def get_hostels(limit: int = MAX_RESULTS, gender: str = None) -> List[Dict]:
    """Get hostels with optional limit and gender filter"""
    if gender:
        if USE_POSTGRES and HAS_POSTGRES:
            return execute_query("SELECT name, gender, capacity, status FROM hostels WHERE LOWER(gender) LIKE %s OR LOWER(gender) = 'mixed' LIMIT %s",
                               (f'%{gender.lower()}%', limit), fetch='all') or []
        else:
            return execute_query("SELECT name, gender, capacity, status FROM hostels WHERE LOWER(gender) LIKE ? OR LOWER(gender) = 'mixed' LIMIT ?",
                               (f'%{gender.lower()}%', limit), fetch='all') or []
    return execute_query(f"SELECT name, gender, capacity, status, facilities FROM hostels ORDER BY name LIMIT {limit}", fetch='all') or []


def get_course_by_code(code: str) -> Optional[Dict]:
    """Get a specific course by code"""
    if USE_POSTGRES and HAS_POSTGRES:
        return execute_query("SELECT * FROM courses WHERE code = %s", (code,), fetch='one')
    else:
        return execute_query("SELECT * FROM courses WHERE code = ?", (code,), fetch='one')


def get_fees_by_level(level: str) -> List[Dict]:
    """Get fees for a specific level"""
    if USE_POSTGRES and HAS_POSTGRES:
        return execute_query("SELECT * FROM fees WHERE level = %s", (level,), fetch='all') or []
    else:
        return execute_query("SELECT * FROM fees WHERE level = ?", (level,), fetch='all') or []

"""
LAUTECH Admin Panel - Staff Management Dashboard

Full CRUD interface for managing university data:
- Courses, Fees, Calendar, Hostels
- CSV Import/Export
- Database Statistics
- User Management (future)

Admin access only - requires authentication.
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
from pathlib import Path

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="LAUTECH Admin Panel",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS - ADMIN THEME
# ============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Inter:wght@400;500;600&display=swap');

    :root {
        --admin-primary: #1E40AF;
        --admin-secondary: #7C3AED;
        --admin-success: #10B981;
        --admin-warning: #F59E0B;
        --admin-danger: #EF4444;
        --admin-dark: #1F2937;
    }

    * {
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif;
    }

    .block-container {
        padding-top: 2rem;
        max-width: 1400px;
    }

    /* Header */
    .admin-header {
        background: linear-gradient(135deg, var(--admin-primary) 0%, var(--admin-secondary) 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .admin-title {
        font-size: 2rem;
        font-weight: 700;
        color: white;
        margin: 0;
    }

    .admin-subtitle {
        color: rgba(255,255,255,0.9);
        margin-top: 0.5rem;
    }

    /* Cards */
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid var(--admin-primary);
    }

    /* Tables */
    .dataframe {
        font-size: 0.875rem;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.3s;
    }

    /* Success/Error messages */
    .stSuccess {
        background-color: #D1FAE5;
        border-left: 4px solid var(--admin-success);
    }

    .stError {
        background-color: #FEE2E2;
        border-left: 4px solid var(--admin-danger);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--admin-dark);
    }

    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background: rgba(255,255,255,0.05);
        padding: 1rem;
        border-radius: 8px;
    }

    [data-testid="stMetricValue"] {
        color: var(--admin-primary);
        font-size: 2rem;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATABASE CONNECTION
# ============================================================================

DB_PATH = Path("lautech_data.db")

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

def get_table_data(table_name):
    """Get all data from a table"""
    conn = get_db_connection()
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_table_stats():
    """Get statistics for all tables"""
    conn = get_db_connection()
    cursor = conn.cursor()

    stats = {}
    tables = ['courses', 'fees', 'academic_calendar', 'hostels']

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        stats[table] = cursor.fetchone()[0]

    conn.close()
    return stats

# ============================================================================
# AUTHENTICATION (Simple - Improve for production)
# ============================================================================

def check_authentication():
    """Simple authentication check"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("""
        <div class="admin-header">
            <h1 class="admin-title">🔐 LAUTECH Admin Panel</h1>
            <p class="admin-subtitle">Staff Authentication Required</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown("### Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            if st.button("Login", use_container_width=True):
                # TODO: Replace with real authentication
                if username == "admin" and password == "lautech2024":
                    st.session_state.authenticated = True
                    st.session_state.admin_user = username
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")

            st.info("**Demo credentials:** admin / lautech2024")
            st.warning("⚠️ Production: Integrate with university SSO/LDAP")

        return False

    return True

# ============================================================================
# CRUD OPERATIONS
# ============================================================================

def add_course(code, name, credits, prerequisites, description, semester, lecturer, department):
    """Add a new course"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO courses (code, name, credits, prerequisites, description, semester, lecturer, department)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (code, name, credits, prerequisites, description, semester, lecturer, department))
        conn.commit()
        conn.close()
        return True, "Course added successfully!"
    except Exception as e:
        return False, f"Error: {str(e)}"

def update_course(code, name, credits, prerequisites, description, semester, lecturer, department):
    """Update existing course"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE courses
            SET name=?, credits=?, prerequisites=?, description=?, semester=?, lecturer=?, department=?
            WHERE code=?
        """, (name, credits, prerequisites, description, semester, lecturer, department, code))
        conn.commit()
        conn.close()
        return True, "Course updated successfully!"
    except Exception as e:
        return False, f"Error: {str(e)}"

def delete_course(code):
    """Delete a course"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM courses WHERE code=?", (code,))
        conn.commit()
        conn.close()
        return True, "Course deleted successfully!"
    except Exception as e:
        return False, f"Error: {str(e)}"

def add_fee(level, amount, fee_type, session):
    """Add a new fee"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO fees (level, amount, fee_type, session)
            VALUES (?, ?, ?, ?)
        """, (level, amount, fee_type, session))
        conn.commit()
        conn.close()
        return True, "Fee added successfully!"
    except Exception as e:
        return False, f"Error: {str(e)}"

def delete_fee(fee_id):
    """Delete a fee"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM fees WHERE id=?", (fee_id,))
        conn.commit()
        conn.close()
        return True, "Fee deleted successfully!"
    except Exception as e:
        return False, f"Error: {str(e)}"

def add_calendar_event(event_type, event_date, semester, session, description):
    """Add a calendar event"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO academic_calendar (event_type, event_date, semester, session, description)
            VALUES (?, ?, ?, ?, ?)
        """, (event_type, event_date, semester, session, description))
        conn.commit()
        conn.close()
        return True, "Event added successfully!"
    except Exception as e:
        return False, f"Error: {str(e)}"

def delete_event(event_id):
    """Delete a calendar event"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM academic_calendar WHERE id=?", (event_id,))
        conn.commit()
        conn.close()
        return True, "Event deleted successfully!"
    except Exception as e:
        return False, f"Error: {str(e)}"

def add_hostel(name, gender, capacity, status, facilities):
    """Add a hostel"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO hostels (name, gender, capacity, status, facilities)
            VALUES (?, ?, ?, ?, ?)
        """, (name, gender, capacity, status, facilities))
        conn.commit()
        conn.close()
        return True, "Hostel added successfully!"
    except Exception as e:
        return False, f"Error: {str(e)}"

def delete_hostel(hostel_id):
    """Delete a hostel"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM hostels WHERE id=?", (hostel_id,))
        conn.commit()
        conn.close()
        return True, "Hostel deleted successfully!"
    except Exception as e:
        return False, f"Error: {str(e)}"

# ============================================================================
# MAIN APPLICATION
# ============================================================================

# Check authentication
if not check_authentication():
    st.stop()

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ ADMIN PANEL")
    st.markdown(f"**User:** {st.session_state.admin_user}")
    st.markdown("---")

    # Navigation
    page = st.radio(
        "Navigation",
        ["📊 Dashboard", "📚 Courses", "💰 Fees", "📅 Calendar", "🏠 Hostels", "📥 Import/Export", "⚙️ Settings"]
    )

    st.markdown("---")

    # Quick Stats
    st.markdown("#### 📈 Quick Stats")
    stats = get_table_stats()
    st.metric("Courses", stats['courses'])
    st.metric("Fees", stats['fees'])
    st.metric("Events", stats['academic_calendar'])
    st.metric("Hostels", stats['hostels'])

    st.markdown("---")

    # Logout
    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.rerun()

# Header
st.markdown("""
<div class="admin-header">
    <h1 class="admin-title">LAUTECH Admin Panel</h1>
    <p class="admin-subtitle">Manage university data and system settings</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# DASHBOARD PAGE
# ============================================================================

if page == "📊 Dashboard":
    st.markdown("## 📊 System Overview")

    # Stats Cards
    col1, col2, col3, col4 = st.columns(4)
    stats = get_table_stats()

    with col1:
        st.metric("📚 Total Courses", stats['courses'])
    with col2:
        st.metric("💰 Fee Records", stats['fees'])
    with col3:
        st.metric("📅 Calendar Events", stats['academic_calendar'])
    with col4:
        st.metric("🏠 Hostels", stats['hostels'])

    st.markdown("---")

    # Recent Activity (placeholder)
    st.markdown("### 📋 Recent Activity")
    st.info("Activity logging coming soon in Part E (Production Hardening)")

    # Database Health
    st.markdown("### 💚 Database Health")
    col1, col2 = st.columns(2)

    with col1:
        st.success("✅ Database connected")
        st.info(f"📁 Location: {DB_PATH.absolute()}")

    with col2:
        db_size = DB_PATH.stat().st_size / 1024  # KB
        st.metric("Database Size", f"{db_size:.2f} KB")

# ============================================================================
# COURSES PAGE
# ============================================================================

elif page == "📚 Courses":
    st.markdown("## 📚 Course Management")

    tab1, tab2, tab3 = st.tabs(["📋 View All", "➕ Add New", "✏️ Edit/Delete"])

    with tab1:
        st.markdown("### All Courses")
        courses_df = get_table_data('courses')
        st.dataframe(courses_df, use_container_width=True, height=400)

        # Export
        csv = courses_df.to_csv(index=False)
        st.download_button(
            "📥 Download CSV",
            csv,
            "courses.csv",
            "text/csv"
        )

    with tab2:
        st.markdown("### Add New Course")

        with st.form("add_course_form"):
            col1, col2 = st.columns(2)

            with col1:
                code = st.text_input("Course Code*", placeholder="CSC401")
                name = st.text_input("Course Name*", placeholder="Software Engineering")
                credits = st.number_input("Credits*", min_value=1, max_value=6, value=3)
                prerequisites = st.text_input("Prerequisites", placeholder="CSC301, CSC302")

            with col2:
                semester = st.selectbox("Semester*", ["First Semester", "Second Semester", "Both"])
                lecturer = st.text_input("Lecturer*", placeholder="Prof. Ibrahim")
                department = st.text_input("Department*", placeholder="Computer Science")
                description = st.text_area("Description*", placeholder="Course description...")

            submit = st.form_submit_button("➕ Add Course", use_container_width=True)

            if submit:
                if code and name and description and lecturer and department:
                    success, message = add_course(code, name, credits, prerequisites, description, semester, lecturer, department)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("❌ Please fill all required fields (*)")

    with tab3:
        st.markdown("### Edit or Delete Course")

        courses_df = get_table_data('courses')

        if len(courses_df) > 0:
            course_codes = courses_df['code'].tolist()
            selected_code = st.selectbox("Select Course", course_codes)

            if selected_code:
                course = courses_df[courses_df['code'] == selected_code].iloc[0]

                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown("#### Edit Course")

                    with st.form("edit_course_form"):
                        new_name = st.text_input("Course Name", value=course['name'])
                        new_credits = st.number_input("Credits", min_value=1, max_value=6, value=int(course['credits']))
                        new_prerequisites = st.text_input("Prerequisites", value=course['prerequisites'])
                        new_description = st.text_area("Description", value=course['description'])
                        new_semester = st.selectbox("Semester", ["First Semester", "Second Semester", "Both"],
                                                   index=["First Semester", "Second Semester", "Both"].index(course['semester']))
                        new_lecturer = st.text_input("Lecturer", value=course['lecturer'])
                        new_department = st.text_input("Department", value=course['department'])

                        update_btn = st.form_submit_button("💾 Update Course", use_container_width=True)

                        if update_btn:
                            success, message = update_course(
                                selected_code, new_name, new_credits, new_prerequisites,
                                new_description, new_semester, new_lecturer, new_department
                            )
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)

                with col2:
                    st.markdown("#### Delete")
                    st.warning(f"Delete **{selected_code}**?")
                    if st.button("🗑️ Delete Course", use_container_width=True):
                        success, message = delete_course(selected_code)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
        else:
            st.info("No courses available")

# ============================================================================
# FEES PAGE
# ============================================================================

elif page == "💰 Fees":
    st.markdown("## 💰 Fee Management")

    tab1, tab2, tab3 = st.tabs(["📋 View All", "➕ Add New", "🗑️ Delete"])

    with tab1:
        st.markdown("### All Fees")
        fees_df = get_table_data('fees')
        st.dataframe(fees_df, use_container_width=True, height=400)

        # Export
        csv = fees_df.to_csv(index=False)
        st.download_button("📥 Download CSV", csv, "fees.csv", "text/csv")

    with tab2:
        st.markdown("### Add New Fee")

        with st.form("add_fee_form"):
            col1, col2 = st.columns(2)

            with col1:
                level = st.text_input("Level*", placeholder="200 Level")
                amount = st.number_input("Amount (₦)*", min_value=0, value=50000)

            with col2:
                fee_type = st.selectbox("Fee Type*", [
                    "Tuition", "Administrative", "Laboratory", "Library",
                    "Sports", "Medical", "Development", "Examination", "Other"
                ])
                session = st.text_input("Session*", value="2024/2025")

            submit = st.form_submit_button("➕ Add Fee", use_container_width=True)

            if submit:
                if level and fee_type and session:
                    success, message = add_fee(level, amount, fee_type, session)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("❌ Please fill all required fields")

    with tab3:
        st.markdown("### Delete Fee")

        fees_df = get_table_data('fees')

        if len(fees_df) > 0:
            # Display with delete buttons
            for idx, row in fees_df.iterrows():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**{row['level']}** - ₦{row['amount']:,} ({row['fee_type']}) - {row['session']}")
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_fee_{row['id']}"):
                        success, message = delete_fee(row['id'])
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
        else:
            st.info("No fees available")

# ============================================================================
# CALENDAR PAGE
# ============================================================================

elif page == "📅 Calendar":
    st.markdown("## 📅 Academic Calendar Management")

    tab1, tab2, tab3 = st.tabs(["📋 View All", "➕ Add New", "🗑️ Delete"])

    with tab1:
        st.markdown("### Academic Calendar")
        calendar_df = get_table_data('academic_calendar')
        st.dataframe(calendar_df, use_container_width=True, height=400)

        # Export
        csv = calendar_df.to_csv(index=False)
        st.download_button("📥 Download CSV", csv, "calendar.csv", "text/csv")

    with tab2:
        st.markdown("### Add Calendar Event")

        with st.form("add_event_form"):
            col1, col2 = st.columns(2)

            with col1:
                event_type = st.text_input("Event Type*", placeholder="Registration Start")
                event_date = st.date_input("Event Date*")
                semester = st.selectbox("Semester*", ["First Semester", "Second Semester", "Both"])

            with col2:
                session = st.text_input("Session*", value="2024/2025")
                description = st.text_area("Description*", placeholder="Event details...")

            submit = st.form_submit_button("➕ Add Event", use_container_width=True)

            if submit:
                if event_type and event_date and semester and session and description:
                    success, message = add_calendar_event(
                        event_type,
                        event_date.strftime("%Y-%m-%d"),
                        semester,
                        session,
                        description
                    )
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("❌ Please fill all required fields")

    with tab3:
        st.markdown("### Delete Event")

        calendar_df = get_table_data('academic_calendar')

        if len(calendar_df) > 0:
            for idx, row in calendar_df.iterrows():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**{row['event_date']}** - {row['event_type']} ({row['semester']})")
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_event_{row['id']}"):
                        success, message = delete_event(row['id'])
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
        else:
            st.info("No events available")

# ============================================================================
# HOSTELS PAGE
# ============================================================================

elif page == "🏠 Hostels":
    st.markdown("## 🏠 Hostel Management")

    tab1, tab2, tab3 = st.tabs(["📋 View All", "➕ Add New", "🗑️ Delete"])

    with tab1:
        st.markdown("### All Hostels")
        hostels_df = get_table_data('hostels')
        st.dataframe(hostels_df, use_container_width=True, height=400)

        # Export
        csv = hostels_df.to_csv(index=False)
        st.download_button("📥 Download CSV", csv, "hostels.csv", "text/csv")

    with tab2:
        st.markdown("### Add New Hostel")

        with st.form("add_hostel_form"):
            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input("Hostel Name*", placeholder="Ajose Hall")
                gender = st.selectbox("Gender*", ["Male", "Female", "Mixed"])
                capacity = st.number_input("Capacity*", min_value=1, value=100)

            with col2:
                status = st.selectbox("Status*", ["Available", "Full", "Under Renovation", "Closed"])
                facilities = st.text_area("Facilities*", placeholder="Power | Water | WiFi | Security")

            submit = st.form_submit_button("➕ Add Hostel", use_container_width=True)

            if submit:
                if name and gender and status and facilities:
                    success, message = add_hostel(name, gender, capacity, status, facilities)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("❌ Please fill all required fields")

    with tab3:
        st.markdown("### Delete Hostel")

        hostels_df = get_table_data('hostels')

        if len(hostels_df) > 0:
            for idx, row in hostels_df.iterrows():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**{row['name']}** - {row['gender']} ({row['capacity']} capacity) - {row['status']}")
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_hostel_{row['id']}"):
                        success, message = delete_hostel(row['id'])
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
        else:
            st.info("No hostels available")

# ============================================================================
# IMPORT/EXPORT PAGE
# ============================================================================

elif page == "📥 Import/Export":
    st.markdown("## 📥 Import/Export Data")

    tab1, tab2 = st.tabs(["📥 Import CSV", "📤 Export Database"])

    with tab1:
        st.markdown("### Import CSV Files")

        st.info("💡 **Tip:** Use the import_data.py script for bulk imports:\n```bash\npython3 import_data.py --all\n```")

        table = st.selectbox("Select Table", ["courses", "fees", "academic_calendar", "hostels"])

        uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])

        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                st.markdown("#### Preview:")
                st.dataframe(df.head(), use_container_width=True)

                st.markdown(f"**Rows:** {len(df)}")

                if st.button("✅ Import Data"):
                    # This would need proper implementation based on table schema
                    st.warning("CSV import via web UI coming soon. Use import_data.py script for now.")
            except Exception as e:
                st.error(f"Error reading CSV: {str(e)}")

    with tab2:
        st.markdown("### Export All Data")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            courses_df = get_table_data('courses')
            csv = courses_df.to_csv(index=False)
            st.download_button("📥 Courses", csv, "courses.csv", "text/csv", use_container_width=True)

        with col2:
            fees_df = get_table_data('fees')
            csv = fees_df.to_csv(index=False)
            st.download_button("📥 Fees", csv, "fees.csv", "text/csv", use_container_width=True)

        with col3:
            calendar_df = get_table_data('academic_calendar')
            csv = calendar_df.to_csv(index=False)
            st.download_button("📥 Calendar", csv, "calendar.csv", "text/csv", use_container_width=True)

        with col4:
            hostels_df = get_table_data('hostels')
            csv = hostels_df.to_csv(index=False)
            st.download_button("📥 Hostels", csv, "hostels.csv", "text/csv", use_container_width=True)

# ============================================================================
# SETTINGS PAGE
# ============================================================================

elif page == "⚙️ Settings":
    st.markdown("## ⚙️ System Settings")

    tab1, tab2, tab3 = st.tabs(["🔐 Authentication", "🗄️ Database", "📊 System Info"])

    with tab1:
        st.markdown("### Authentication Settings")
        st.warning("⚠️ Production: Integrate with university SSO/LDAP")
        st.info("Current: Simple demo authentication (admin/lautech2024)")

        st.markdown("#### TODO (Part E):")
        st.markdown("""
        - [ ] Integrate with university SSO
        - [ ] Add role-based access control
        - [ ] Add user management
        - [ ] Add audit logging
        - [ ] Add session management
        """)

    with tab2:
        st.markdown("### Database Settings")

        st.info(f"**Current Database:** SQLite at `{DB_PATH.absolute()}`")

        st.markdown("#### Migration to RDS (Part E):")
        st.code("""
# PostgreSQL connection for production
import psycopg2

conn = psycopg2.connect(
    dbname=os.environ['RDS_DB_NAME'],
    host=os.environ['RDS_HOST'],
    user=os.environ['RDS_USER'],
    password=os.environ['RDS_PASSWORD'],
    port=5432
)
        """, language="python")

        st.markdown("#### Database Backup")
        if st.button("📦 Create Backup"):
            import shutil
            backup_path = f"lautech_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy(DB_PATH, backup_path)
            st.success(f"✅ Backup created: {backup_path}")

    with tab3:
        st.markdown("### System Information")

        import sys
        import platform

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Python Environment")
            st.code(f"""
Python: {sys.version}
Platform: {platform.platform()}
Streamlit: {st.__version__}
            """)

        with col2:
            st.markdown("#### Database Info")
            db_size = DB_PATH.stat().st_size / 1024
            stats = get_table_stats()
            st.code(f"""
Database Size: {db_size:.2f} KB
Total Courses: {stats['courses']}
Total Fees: {stats['fees']}
Total Events: {stats['academic_calendar']}
Total Hostels: {stats['hostels']}
            """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    ⚙️ LAUTECH Admin Panel v1.0 | For authorized staff only<br>
    <small>Report issues to IT Support</small>
</div>
""", unsafe_allow_html=True)

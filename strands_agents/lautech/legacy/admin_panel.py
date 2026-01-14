import streamlit as st
import os
import pandas as pd
import sys
from contextlib import contextmanager

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Explicitly import all required names
    from db_utils import get_db_connection, execute_query, USE_POSTGRES, HAS_POSTGRES
except ImportError:
    st.error("Could not import db_utils. Please check the file structure.")
    # Define fallbacks to avoid crashes
    USE_POSTGRES = False
    HAS_POSTGRES = False
    
    @contextmanager
    def get_db_connection():
        yield None
        
    def execute_query(q, p=None, fetch=None):
        return []

# Styles
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Force all text to be visible */
    .stApp, .stApp p, .stApp span, .stApp label, .stApp div {
        color: #1a1a1a !important;
    }
    
    /* Headings */
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #1a1a1a !important; 
    }
    
    /* Input labels */
    .stTextInput label, .stSelectbox label, .stTextArea label {
        color: #1a1a1a !important;
    }
    
    /* Button text */
    .stButton > button {
        color: #ffffff !important;
        background-color: #4f46e5 !important;
    }
    
    .stButton > button:hover {
        background-color: #4338ca !important;
    }
    
    /* Login Card */
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
    }
    
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
    }
    
    /* Sidebar text */
    [data-testid="stSidebar"], [data-testid="stSidebar"] * {
        color: #1a1a1a !important;
    }
    
    /* Tab text */
    .stTabs [data-baseweb="tab"] {
        color: #1a1a1a !important;
    }
    
    /* Radio button text */
    .stRadio label {
        color: #1a1a1a !important;
    }
</style>
""", unsafe_allow_html=True)

# Page Config (Moved to top via replacements if needed, but assuming separate set_page_config is fine if first st call)

# Authentication Logic
def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        if st.session_state["password"] == os.getenv("ADMIN_PASSWORD", "admin123"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Show Login Form
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            st.markdown("## 🔐 Admin Login")
            st.text_input("Password", type="password", on_change=password_entered, key="password")
            st.markdown("*Restricted Access Area*")
        return False
        
    elif not st.session_state["password_correct"]:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            st.markdown("## 🔐 Admin Login")
            st.text_input("Password", type="password", on_change=password_entered, key="password")
            st.error("😕 Password incorrect")
        return False
    else:
        return True

if check_password():
    # Sidebar
    with st.sidebar:
        st.title("🎓 LAUTECH Admin")
        st.markdown("---")
        menu = st.radio("Navigation", ["Dashboard", "Database", "Settings"])
        st.markdown("---")
        if st.button("Log out"):
            del st.session_state["password_correct"]
            st.rerun()

    # Main Content
    if menu == "Dashboard":
        st.title("Admin Dashboard")
        st.markdown("Overview of system performance and data.")
        
        # Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric(label="Active Sessions", value="12", delta="2")
        with m2:
            st.metric(label="Total Queries", value="1,284", delta="145")
        with m3:
            st.metric(label="DB Status", value="Healthy", delta_color="normal")
        with m4:
            st.metric(label="Avg Latency", value="580ms", delta="-12%")
            
        st.markdown("---")
        st.subheader("System Health")
        st.info("Additional charts and logs would appear here.")

    elif menu == "Database":
        st.title("🗄️ Database Management")
        
        tab1, tab2, tab3 = st.tabs(["📊 Table Viewer", "➕ Add Record", "⚡ SQL Editor"])
        
        # --- TAB 1: VIEW DATA ---
        with tab1:
            table_name = st.selectbox("Select Table", ["courses", "fees", "academic_calendar", "hostels"])
            
            if st.button(f"Load {table_name}", key="load_btn"):
                try:
                    with get_db_connection() as conn:
                        query = f"SELECT * FROM {table_name}"
                        if USE_POSTGRES and HAS_POSTGRES:
                            df = pd.read_sql(query, conn)
                        else:
                            df = pd.read_sql(query, conn)
                        st.dataframe(df, use_container_width=True)
                        st.session_state['last_df'] = df
                except Exception as e:
                    st.error(f"Error loading table: {e}")

        # --- TAB 2: ADD DATA ---
        with tab2:
            st.subheader(f"Add New Record")
            target_table = st.selectbox("Target Table", ["courses", "fees", "academic_calendar", "hostels"], key="add_table_select")
            
            with st.form("add_record_form"):
                if target_table == "courses":
                    c_code = st.text_input("Code (e.g. CSC 101)")
                    c_name = st.text_input("Name")
                    c_units = st.number_input("Credits (Units)", min_value=1, max_value=6)
                    c_dept = st.text_input("Department")
                    submitted = st.form_submit_button("Add Course")
                    if submitted:
                        query = "INSERT INTO courses (code, name, credits, department) VALUES (%s, %s, %s, %s)" if USE_POSTGRES else "INSERT INTO courses (code, name, credits, department) VALUES (?, ?, ?, ?)"
                        params = (c_code, c_name, c_units, c_dept)
                
                elif target_table == "fees":
                    f_level = st.text_input("Level (e.g. 100)")
                    f_amount = st.number_input("Amount", min_value=0)
                    f_type = st.text_input("Type (e.g. Tuition)")
                    submitted = st.form_submit_button("Add Fee")
                    if submitted:
                       query = "INSERT INTO fees (level, amount, fee_type) VALUES (%s, %s, %s)" if USE_POSTGRES else "INSERT INTO fees (level, amount, fee_type) VALUES (?, ?, ?)"
                       params = (f_level, f_amount, f_type)

                elif target_table == "academic_calendar":
                    e_type = st.text_input("Event Type")
                    e_date = st.text_input("Date (YYYY-MM-DD)")
                    e_desc = st.text_input("Description")
                    submitted = st.form_submit_button("Add Event")
                    if submitted:
                        query = "INSERT INTO academic_calendar (event_type, event_date, description) VALUES (%s, %s, %s)" if USE_POSTGRES else "INSERT INTO academic_calendar (event_type, event_date, description) VALUES (?, ?, ?)"
                        params = (e_type, e_date, e_desc)

                elif target_table == "hostels":
                    h_name = st.text_input("Name")
                    h_gender = st.selectbox("Gender", ["Male", "Female", "Mixed"])
                    h_cap = st.number_input("Capacity", min_value=1)
                    submitted = st.form_submit_button("Add Hostel")
                    if submitted:
                        query = "INSERT INTO hostels (name, gender, capacity) VALUES (%s, %s, %s)" if USE_POSTGRES else "INSERT INTO hostels (name, gender, capacity) VALUES (?, ?, ?)"
                        params = (h_name, h_gender, h_cap)

                # Execution Logic
                if submitted:
                    try:
                        execute_query(query, params, fetch=None)
                        st.success(f"Successfully added record to {target_table}")
                    except Exception as e:
                        st.error(f"Failed to add record: {e}")

        # --- TAB 3: SQL EDITOR ---
        with tab3:
            st.subheader("Run Raw SQL")
            st.warning("⚠️ Proceed with caution. You can modify/delete data here.")
            sql_query = st.text_area("SQL Query", height=150, placeholder="SELECT * FROM courses WHERE credits > 3")
            
            if st.button("Execute Query"):
                try:
                    # Determine if it's a SELECT or Action
                    lower_q = sql_query.strip().lower()
                    fetch_mode = 'all' if lower_q.startswith('select') or list_tables_cmd(lower_q) else None
                    
                    results = execute_query(sql_query, params=None, fetch=fetch_mode)
                    
                    if fetch_mode:
                        st.dataframe(pd.DataFrame(results) if results else [])
                        st.success(f"Query executed. {len(results) if results else 0} rows returned.")
                    else:
                        st.success("Command executed successfully.")
                        
                except Exception as e:
                    st.error(f"Execution Error: {e}")

    elif menu == "Settings":
        st.title("Settings")
        st.text("System Configuration")
        st.json(os.environ)

def list_tables_cmd(q):
    return 'pragma' in q or 'information_schema' in q

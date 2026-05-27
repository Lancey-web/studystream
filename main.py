import streamlit as st
import mysql.connector
from admin_dashboard import show_admin_dashboard
from student_dashboard import show_student_dashboard
from style import apply_custom_css
from database import get_db_connection, close_db_connection, log_activity
from supabase import create_client, Client
from credentials import SUPABASE_URL, SUPABASE_KEY

# Cloud Authentication Setup
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- GLOBAL PAGE CONFIGURATION ---
st.set_page_config(
    page_title="StudyStream: RTU LMS", 
    layout="wide",
    initial_sidebar_state="expanded"
)
apply_custom_css()

# --- SESSION STATE INITIALIZATION ---
if "authenticated" not in st.session_state:
    st.session_state.update({
        "authenticated": False, 
        "role": None, 
        "user_data": None, 
        "quiz_active": False, 
        "current_exam_file": None,
        "current_page": "Dashboard Home" # Tracks active sidebar page routing
    })

# --- AUTHENTICATION FLOW ---
if not st.session_state.authenticated:
    st.markdown('<div class="rtu-header"><h1> StudyStream: RTU Portal</h1><p>Integrated Learning Management System | BSIT Specialist Edition</p></div>', unsafe_allow_html=True)
    _, col_center, _ = st.columns([1, 2, 1])
    
    with col_center:
        tab_login, tab_signup = st.tabs(["Secure Login", "New Registration"])
        
        with tab_login:
            with st.form("main_login_form"):
                role_selection = st.selectbox("Login as:", ["Student", "Administrator / Teacher"])
                email_input = st.text_input("Institutional Email (@rtu.edu.ph)")
                pass_input = st.text_input("Password", type="password")
                
                if st.form_submit_button("Login to Portal", use_container_width=True):
                    conn = get_db_connection()
                    user = None
                    
                    if conn:
                        cursor = conn.cursor(dictionary=True)
                        try:
                            query = "SELECT * FROM mdl_user WHERE email = %s AND password = %s"
                            cursor.execute(query, (email_input, pass_input))
                            user = cursor.fetchone()
                        except mysql.connector.Error as err:
                            st.error(f"Database Query Error: {err}")
                        finally:
                            close_db_connection(conn, cursor)
                    
                    if user:
                        st.session_state.authenticated = True
                        log_activity(email_input, f"Login Successful: {role_selection}")
                        
                        # Route based on selected dropdown role option
                        if role_selection == "Administrator / Teacher":
                            st.session_state.role = "Admin"
                        else:
                            st.session_state.role = "Student"
                            
                        st.session_state.user_data = user
                        st.rerun()
                    else:
                        st.error("Access Denied: Invalid email or password configuration.")

        with tab_signup:
            with st.form("main_signup_form"):
                st.info("Registration is restricted to authorized RTU students.")
                col1, col2 = st.columns(2)
                with col1: first_name = st.text_input("First Name")
                with col2: last_name = st.text_input("Last Name")
                new_email = st.text_input("RTU Email (@rtu.edu.ph)")
                new_pass = st.text_input("Create Password", type="password")

                if st.form_submit_button("Create Account", use_container_width=True):
                    if not (first_name and last_name and new_email and new_pass):
                        st.error("❌ Please fill in all required fields.")
                    elif not new_email.endswith("@rtu.edu.ph"):
                        st.error("❌ Registration error: Must use an authorized @rtu.edu.ph domain.")
                    else:
                        conn = get_db_connection()
                        if conn:
                            db_success = False
                            try:
                                cursor = conn.cursor()
                                sql = "INSERT INTO mdl_user (firstname, lastname, email, password) VALUES (%s, %s, %s, %s)"
                                cursor.execute(sql, (first_name, last_name, new_email, new_pass))
                                conn.commit()
                                db_success = True
                            except mysql.connector.Error as db_err:
                                st.error(f"❌ Database Error: {db_err}")
                            finally:
                                close_db_connection(conn, cursor)
                            
                            if db_success:
                                try:
                                    supabase.auth.sign_up({"email": new_email, "password": new_pass})
                                    st.success("✅ Account compiled successfully! Swap over to Login tab.")
                                    log_activity(new_email, "Registered Account")
                                except Exception as e:
                                    st.warning(f"⚠️ Cloud sync state exception: {e}")

# --- DASHBOARD CONTROL LAYER ---
else:
    with st.sidebar:
        st.markdown(f"### {st.session_state.user_data.get('firstname', 'User')}")
        st.caption(f"Access Level: {st.session_state.role}")
        st.divider()
        
        if not st.session_state.quiz_active:
            st.write("**Course Navigation**")
            if st.button("Dashboard Home", use_container_width=True):
                st.session_state.current_page = "Dashboard Home"
                st.rerun()
            if st.button("Notifications", use_container_width=True):
                st.session_state.current_page = "Notifications"
                st.rerun()
        
        st.divider()
        if st.button("Logout", type="secondary", use_container_width=True):
            log_activity(st.session_state.user_data.get('email', 'Unknown'), "Logged Out")
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    if st.session_state.role == "Admin":
        show_admin_dashboard(st.session_state.user_data)
    else:
        show_student_dashboard(st.session_state.user_data)
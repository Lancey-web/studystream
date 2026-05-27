import streamlit as st
import mysql.connector
from admin_dashboard import show_admin_dashboard
from student_dashboard import show_student_dashboard
from style import apply_custom_css
from database import get_db_connection, close_db_connection, log_activity, verify_tables
from supabase import create_client, Client
from credentials import SUPABASE_URL, SUPABASE_KEY

# Cloud Authentication Setup
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 1. GLOBAL PAGE CONFIGURATION ---
st.set_page_config(
    page_title="StudyStream: RTU LMS", 
    layout="wide",
    initial_sidebar_state="expanded"
)
apply_custom_css()

# Optional: Runs table verification checks on startup to assist development
# verify_tables()

# --- 2. SESSION STATE INITIALIZATION ---
if "authenticated" not in st.session_state:
    st.session_state.update({
        "authenticated": False, 
        "role": None, 
        "user_data": None, 
        "quiz_active": False, 
        "current_exam_file": None
    })

# --- 3. AUTHENTICATION & LANDING PAGE ---
if not st.session_state.authenticated:
    # RTU Branding Header
    st.markdown('<div class="rtu-header"><h1> StudyStream: RTU Portal</h1><p>Integrated Learning Management System | BSIT Specialist Edition</p></div>', unsafe_allow_html=True)
    
    # Centered Login/Signup Container
    _, col_center, _ = st.columns([1, 2, 1])
    
    with col_center:
        tab_login, tab_signup = st.tabs(["Secure Login", "New Registration"])
        
        # --- LOGIN FEATURE ---
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
                        
                        # Validate status via Supabase cloud if local verification checks out
                        if user:
                            try:
                                auth_user = supabase.auth.sign_in_with_password({
                                    "email": email_input, 
                                    "password": pass_input
                                })
                            except Exception as e:
                                st.error("Login blocked: Please verify your email via the link sent to your inbox.")
                                user = None 

                    # MASTER-ACCESS BACKDOOR LOGIC FOR TESTING
                    is_antonio = email_input == "2024-200364@rtu.edu.ph" or "antonio" in email_input.lower()
                    
                    if user or is_antonio:
                        st.session_state.authenticated = True
                        log_activity(email_input, f"Login Successful: {role_selection}")
                        
                        if is_antonio:
                            st.session_state.role = "Admin"
                            st.session_state.user_data = user if user else {"firstname": "Antonio", "email": email_input}
                        else:
                            st.session_state.role = "Admin" if role_selection == "Administrator / Teacher" else "Student"
                            st.session_state.user_data = user
                        
                        st.success(f"Welcome back, {st.session_state.user_data.get('firstname', 'User')}!")
                        st.rerun()
                    else:
                        st.error("Access Denied: Invalid institutional email or password configuration.")

        # --- SIGN-UP FEATURE (CREATE) ---
        with tab_signup:
            with st.form("main_signup_form"):
                st.info("Registration is restricted to authorized RTU students.")
                
                col1, col2 = st.columns(2)
                with col1:
                    first_name = st.text_input("First Name")
                with col2:
                    last_name = st.text_input("Last Name")
                    
                new_email = st.text_input("RTU Email (@rtu.edu.ph)")
                new_pass = st.text_input("Create Password", type="password")

                if st.form_submit_button("Create Account", use_container_width=True):
                    if not (first_name and last_name and new_email and new_pass):
                        st.error("❌ Please fill in all required form fields.")
                    elif not new_email.endswith("@rtu.edu.ph"):
                        st.error("❌ Registration error: Must use an authorized @rtu.edu.ph domain assignment.")
                    else:
                        conn = get_db_connection()
                        if conn:
                            db_success = False
                            try:
                                cursor = conn.cursor()
                                sql = "INSERT INTO mdl_user (firstname, lastname, email, password) VALUES (%s, %s, %s, %s)"
                                cursor.execute(sql, (first_name, last_name, new_email, new_pass))
                                conn.commit()
                                st.success("✅ Registration written successfully to local registry database!")
                                db_success = True
                                    
                            except mysql.connector.Error as db_err:
                                if db_err.errno == 1062:
                                    st.error("❌ Conflict Error: This institutional email has already been claimed.")
                                else:
                                    st.error(f"❌ SQL Execution Error: {db_err}")
                            finally:
                                close_db_connection(conn, cursor)
                            
                            # Fire cloud registration sequence only if local writes succeed without hanging
                            if db_success:
                                try:
                                    with st.spinner("Broadcasting validation token securely to cloud systems..."):
                                        supabase.auth.sign_up({
                                            "email": new_email, 
                                            "password": new_pass
                                        })
                                    st.info("📨 Verification link deployed successfully! Please check your RTU inbox.")
                                    st.success("Account setup finished. Swap over to the Secure Login panel to continue.")
                                    log_activity(new_email, "Account Registered Successfully")
                                except Exception as auth_error:
                                    st.warning(f"⚠️ Local database updated, but cloud synchronization met an unexpected state: {auth_error}")
                        else:
                            st.error("❌ Connection failed: Unable to fetch connection from the application pool. Verify XAMPP status.")

# --- 4. DASHBOARD ROUTING ---
else:
    with st.sidebar:
        st.markdown(f"### {st.session_state.user_data.get('firstname', 'User')}")
        st.caption(f"Access Level: {st.session_state.role}")
        st.divider()
        
        if not st.session_state.quiz_active:
            st.write("**Course Navigation**")
            st.button("Dashboard Home", use_container_width=True)
            st.button("Notifications", use_container_width=True)
        
        if st.button("Logout", type="secondary", use_container_width=True):
            log_activity(st.session_state.user_data.get('email', 'Unknown'), "Logged Out")
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    if st.session_state.role == "Admin":
        show_admin_dashboard(st.session_state.user_data)
    else:
        show_student_dashboard(st.session_state.user_data)
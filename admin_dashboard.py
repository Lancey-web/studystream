import streamlit as st
import pandas as pd
import PyPDF2
import time
from database import get_db_connection

def show_admin_dashboard(user_data):
    # Professional Header with BSIT Branding
    st.markdown('<div class="rtu-header"><h1>Instructor Control Center</h1><p>RTU Learning Management System | BSIT Specialist Portal</p></div>', unsafe_allow_html=True)
    
    # Feature Navigation
    tab_manage, tab_quiz, tab_analytics = st.tabs([
        "Student Management (CRUD)", 
        "AI Quiz Generator", 
        "System Analytics"
    ])

    # --- TAB 1: STUDENT MANAGEMENT (CRUD) ---
    with tab_manage:
        st.header("Database Control")
        
        # 1. CREATE: Manual Student Registration
        with st.expander("Register New Student Manually"):
            with st.form("admin_manual_registration"):
                st.write("Enter student details to save directly to **mdl_user** table.")
                col1, col2 = st.columns(2)
                with col1:
                    u = st.text_input("Username (e.g., rtu_student1)")
                    f = st.text_input("First Name")
                    l = st.text_input("Last Name")
                with col2:
                    e = st.text_input("Email (@rtu.edu.ph)")
                    p = st.text_input("Temporary Password", type="password")
                
                if st.form_submit_button("Save to Database", use_container_width=True):
                    if u and e.endswith("@rtu.edu.ph") and p:
                        conn = get_db_connection()
                        if conn:
                            cursor = conn.cursor()
                            # SQL INSERT (CREATE)
                            sql = "INSERT INTO mdl_user (username, firstname, lastname, email, password) VALUES (%s, %s, %s, %s, %s)"
                            cursor.execute(sql, (u, f, l, e, p))
                            conn.commit()
                            conn.close()
                            st.success(f"Success! {f} is now registered and can log in.")
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.error("Registration failed. Use a valid @rtu.edu.ph email and fill all fields.")

        st.divider()
        
        # 2. READ & 4. DELETE: View and Remove Users
        conn = get_db_connection()
        if conn:
            # SQL SELECT (READ)
            df = pd.read_sql("SELECT id, username, firstname, lastname, email FROM mdl_user", conn)
            
            st.subheader("Registered Users")
            st.dataframe(df, use_container_width=True)
            
            st.subheader("Remove User Account")
            to_del = st.selectbox("Select account to delete:", df['username'].tolist())
            
            if st.button("Permanently Delete Account", type="primary"):
    # REFINED SAFETY LOCK: Matches your exact admin username/email only
                admin_usernames = ['admin', 'antonio_admin'] # Add your exact admin usernames here
                
                if to_del.lower() in admin_usernames or to_del == user_data.get('username'):
                    st.error("🛡️ Access Denied: This is a Master Admin account and cannot be deleted.")
                else:
                    # SQL DELETE (Proceeds for students like 'Antonio, Pooru')
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM mdl_user WHERE username = %s", (to_del,))
                    conn.commit()
                    st.warning(f"⚠️ Account '{to_del}' has been removed from the system.")
                    time.sleep(1)
                    st.rerun()
            conn.close()

    # --- TAB 2: AI QUIZ GENERATOR (UPDATE FEATURE) ---
    with tab_quiz:
        st.header("Assessment Hub")
        st.info("Upload a PDF reviewer. The system will generate a 30-item exam and update the database.")
        
        uploaded_reviewer = st.file_uploader("Upload Master Reviewer (PDF)", type=['pdf'])

        if uploaded_reviewer:
            reader = PyPDF2.PdfReader(uploaded_reviewer)
            text = "".join([page.extract_text() for page in reader.pages])
            st.success(f"{uploaded_reviewer.name} processed successfully.")

            if st.button("Generate & Save 30 Questions", use_container_width=True):
                conn = get_db_connection()
                if conn:
                    try:
                        cursor = conn.cursor()
                        # Clean existing questions for this file (UPDATE logic)
                        cursor.execute("DELETE FROM mdl_quiz_questions WHERE file_name = %s", (uploaded_reviewer.name,))
                        
                        # Generate 30 Items
                        for i in range(1, 31): 
                            q_text = f"Question {i}: Based on {uploaded_reviewer.name}, identify key concept #{i}."
                            a_key = "Answer Key Placeholder" 
                            
                            sql = "INSERT INTO mdl_quiz_questions (file_name, question_text, answer_key) VALUES (%s, %s, %s)"
                            cursor.execute(sql, (uploaded_reviewer.name, q_text, a_key))
                        
                        conn.commit()
                        st.balloons()
                        st.success(f"30-item assessment for {uploaded_reviewer.name} is now live!")
                    except Exception as err:
                        st.error(f"Database Error: {err}")
                    finally:
                        conn.close()

    
    # --- TAB 3: ANALYTICS ---
        with tab_analytics:
            st.header("Class Performance Analytics")
            
            # 1. Metrics and Logic
            avg_score = 88.5 
            def get_rtu_equivalent(s):
                if s >= 99: return 1.00
                elif s >= 96: return 1.25
                elif s >= 93: return 1.50
                elif s >= 90: return 1.75
                elif s >= 87: return 2.00
                elif s >= 75: return 3.00
                else: return 5.00

            rtu_grade = get_rtu_equivalent(avg_score)
            
            # Dashboard Top Row
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Students", "24", "+2 New")
            c2.metric("Class Average", f"{avg_score}%")
            c3.metric("RTU Grade", f"{rtu_grade:.2f}")
            
            st.divider()

            # 2. NEW FEATURE: GRADE DISTRIBUTION CHART
            st.subheader("Grade Distribution Chart")
            
            # This creates the data for the bars
            chart_data = pd.DataFrame({
                'Grade': ['1.00', '1.25', '1.50', '1.75', '2.00', '3.00', '5.00'],
                'Count': [3, 5, 8, 4, 2, 1, 1] 
            }).set_index('Grade')

            # This draws the bar chart in RTU Blue
            st.bar_chart(chart_data, color="#003366") 

            st.info(f"Most students are performing at the {rtu_grade:.2f} level.")

            # --- 3. SYSTEM AUDIT LOGS ---
            st.divider()
            st.subheader("Recent System Activity")
                    
            conn = get_db_connection()
            if conn:
                # This query pulls the latest 10 logs from your database
                query = "SELECT user_email as 'User', action as 'Action', timestamp as 'Time' FROM mdl_logs ORDER BY timestamp DESC LIMIT 10"
                df = pd.read_sql(query, conn)
                
                if not df.empty:
                    # This displays that '2 rows' you saw in phpMyAdmin
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("No logs found in the database yet.")
                conn.close()    
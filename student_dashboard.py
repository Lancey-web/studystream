import streamlit as st
import pandas as pd
from database import get_db_connection, close_db_connection

def show_student_dashboard(user_data):
    # Dynamic Sidebar Page Routing Check
    current_view = st.session_state.get("current_page", "Dashboard Home")

    if current_view == "Notifications":
        st.subheader("🔔 System Notifications")
        st.divider()
        st.info("💬 Your workspace links have updated and synced flawlessly with your MariaDB connection pool.")
    else:
        # Render main dashboard layout contents
        st.markdown(f"## Student Portal Workspace")
        st.caption("Integrated Learning Management System | Specialist Track")
        st.write("---")

        tab_materials, tab_exams = st.tabs(["Learning Materials Hub", "AI Mock Exams"])

        # TAB 1: LEARNING MATERIALS WORKSPACE
        with tab_materials:
            st.subheader("Academic Resources")
            st.caption("Access your lecture notes and official course documents below.")

            col_docs, col_videos = st.columns(2)
            with col_docs:
                st.markdown("### 📄 Document Library")
                st.download_button(
                    label="📄 IT 401: SYSTEMS INTEGRATION SYLLABUS.PDF",
                    data=b"Syllabus Content",
                    file_name="IT401_Syllabus.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                st.download_button(
                    label="📄 DATABASE MANAGEMENT REVIEWER.PDF",
                    data=b"Reviewer Content",
                    file_name="DBMS_Reviewer.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            with col_videos:
                st.markdown("### 🎥 Video Lectures")
                with st.expander("▶️ WATCH: SQL FUNDAMENTALS & JOINS"):
                    st.video("https://www.youtube.com/watch?v=HXV3zeQKqGY")
                with st.expander("▶️ WATCH: PYTHON STREAMLIT FOR BSIT"):
                    st.video("https://www.youtube.com/watch?v=B0g0mP8Mst0")

        # TAB 2: INTERACTIVE TESTING MODULES
        with tab_exams:
            st.subheader("AI Mock Exams Panel")
            
            exam_options = []
            conn = get_db_connection()
            if conn:
                try:
                    df = pd.read_sql("SELECT DISTINCT file_name FROM mdl_quiz_questions", conn)
                    exam_options = df['file_name'].tolist()
                except Exception as e:
                    print(f"Error checking schemas: {e}")
                finally:
                    conn.close()
            
            if not exam_options:
                exam_options = ["IT_Specialist_Exam_1.csv", "Database_Systems_Final.csv"]

            selected_blueprint = st.selectbox("Choose an evaluation set to execute:", exam_options)
            
            if st.button("🚀 Launch Interactive Testing Session", use_container_width=True):
                st.session_state.quiz_active = True
                st.session_state.current_exam_file = selected_blueprint
                st.success(f"Assessment pipeline established for {selected_blueprint}! Fetching components...")
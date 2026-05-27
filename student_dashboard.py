# ==========================================
# FILE: student_dashboard.py
# ==========================================
import streamlit as st
import pandas as pd
from database import get_db_connection, close_db_connection

def show_student_dashboard(user_data):
    # If a testing session is active, detour directly to our clean exam wrapper interface
    if st.session_state.get("quiz_active", False):
        render_active_examination_engine()
        return

    # Dynamic Sidebar Page Routing Check for non-quiz screens
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
                    st.video("https://www.youtube.com/watch?v=D0D4Pa22iG0")

        # TAB 2: INTERACTIVE TESTING MODULES (AI MOCK EXAMS)
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
            
            # Append our dedicated cloud exam to the selection matrix options
            if "Cloud_and_DevOps_Specialist_Exam.csv" not in exam_options:
                exam_options.append("Cloud_and_DevOps_Specialist_Exam.csv")
            if "IT_Specialist_Exam_1.csv" not in exam_options:
                exam_options.append("IT_Specialist_Exam_1.csv")

            selected_blueprint = st.selectbox("Choose an evaluation set to execute:", exam_options)
            
            if st.button("🚀 Launch Interactive Testing Session", use_container_width=True):
                st.session_state.quiz_active = True
                st.session_state.current_exam_file = selected_blueprint
                st.session_state.current_question_index = 0
                st.session_state.student_answers = {}
                st.session_state.quiz_completed = False
                st.rerun()


def render_active_examination_engine():
    """Renders an isolated, distraction-free testing terminal for the student."""
    exam_target = st.session_state.get("current_exam_file", "Exam")
    st.markdown(f"## 📝 Examination: {exam_target}")
    st.warning("⚠️ Examination Environment Active: Sidebar navigation loops are locked until submission.")
    st.write("---")

    questions = []

    # Try fetching data directly from your local MariaDB database first
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM mdl_quiz_questions WHERE file_name = %s", (exam_target,))
            questions = cursor.fetchall()
        except Exception as e:
            print(f"Fallback to dynamic internal script array context: {e}")
        finally:
            close_db_connection(conn, cursor)

    # Hardcoded 10-Item Fixed Matrix for AWS, Azure, GCP, API-First, Docker, & CI/CD
    if not questions and exam_target == "Cloud_and_DevOps_Specialist_Exam.csv":
        questions = [
            {
                "question_text": "A team is designing an application using an API-first stack approach. What is the primary operational advantage of implementing this design paradigm before writing core backend code?",
                "option_a": "It allows frontend and backend development teams to work in parallel by using the finalized API contract as a mock dependency.",
                "option_b": "It completely removes the requirement for a functional database layer or persistent object store.",
                "option_c": "It automatically generates edge-routing scripts for container platforms like Docker without developer intervention.",
                "option_d": "It forces all data communication to use asynchronous message brokers instead of standard synchronous protocols.",
                "correct_answer": "A"
            },
            {
                "question_text": "In a Docker multi-stage build, what is the primary benefit of using multiple 'FROM' instructions within a single Dockerfile?",
                "option_a": "It forces the execution of container processes to run strictly under a root administrative user context.",
                "option_b": "It enables the container to run on both Linux and Windows kernel environments simultaneously at runtime.",
                "option_c": "It speeds up container networking by caching API requests made to cloud services like AWS or GCP.",
                "option_d": "It allows the final production image to remain extremely small by excluding heavy build tools, compilers, and development dependencies.",
                "correct_answer": "D"
            },
            {
                "question_text": "An engineer needs to establish a fully automated CI/CD pipeline. What is the fundamental difference between Continuous Delivery and Continuous Deployment?",
                "option_a": "Continuous Delivery requires a manual approval step before deploying to production, whereas Continuous Deployment automates the release directly to production without manual intervention.",
                "option_b": "Continuous Delivery only operates within local git repositories, while Continuous Deployment requires an active public cloud connection.",
                "option_c": "Continuous Delivery strictly deploys monolithic applications, while Continuous Deployment is used exclusively for containerized Docker microservices.",
                "option_d": "Continuous Deployment performs security scanning, while Continuous Delivery only compiles source binaries.",
                "correct_answer": "A"
            },
            {
                "question_text": "Which of the following compute services represents the correct cross-cloud mapping for serverless container execution where developers deploy containers without managing virtual machine infrastructure?",
                "option_a": "AWS EC2 | Azure Virtual Machines | GCP Compute Engine",
                "option_b": "AWS Fargate | Azure Container Apps | GCP Cloud Run",
                "option_c": "AWS S3 | Azure Blob Storage | GCP Cloud Storage",
                "option_d": "AWS Lambda | Azure Functions | GCP Cloud Functions",
                "correct_answer": "B"
            },
            {
                "question_text": "When building a Dockerfile, why is it highly recommended to place instructions like 'COPY package.json .' and 'RUN npm install' BEFORE copying the rest of the application source code?",
                "option_a": "Because Docker completely fails to compile if code files are present in the working directory before package configurations.",
                "option_b": "To leverage Docker's layer caching mechanism, preventing slow dependency downloads if the project's packages haven't changed.",
                "option_c": "To encrypt the dependencies before the application source layer is compiled.",
                "option_d": "To force the container to run strictly inside isolated private VPC subnets within cloud setups.",
                "correct_answer": "B"
            },
            {
                "question_text": "In an API-first stack configuration, what is the role of an API Gateway within a cloud infrastructure deployment?",
                "option_a": "It compiles source code commits into Docker images whenever developers push revisions to GitHub repositories.",
                "option_b": "It serves as the main primary relational database engine to store user credentials securely.",
                "option_c": "It acts as a single reverse-proxy entry point to route client traffic, handle authentication, manage rate limiting, and collect telemetry across backend microservices.",
                "option_d": "It provides cross-platform file storage sharing between AWS, Azure, and GCP data buckets.",
                "correct_answer": "C"
            },
            {
                "question_text": "A company wants to implement a multi-cloud disaster recovery architecture. They need to host identical containerized workloads across AWS, Azure, and GCP. Which technology abstraction provides the most consistent infrastructure management layer to achieve this?",
                "option_a": "Kubernetes",
                "option_b": "AWS CloudFormation",
                "option_c": "Azure Active Directory",
                "option_d": "Google Cloud BigQuery",
                "correct_answer": "A"
            },
            {
                "question_text": "During a CI/CD build run, a security scanner flags a critical vulnerability inside an open-source library used by your Docker container. At which step of the workflow should the pipeline fail to maintain a secure deployment posture?",
                "option_a": "After the container is deployed to production and actively serving customer traffic.",
                "option_b": "During the Continuous Integration (CI) test phase, stopping the runner before the unsafe image is built or pushed to a container registry.",
                "option_c": "Only when the cloud database throws a connection pooling handshake exception.",
                "option_d": "During the manual DNS routing configuration update phase.",
                "correct_answer": "B"
            },
            {
                "question_text": "Which AWS service provides fully managed private Git repositories that can integrate into an automated CI/CD pipeline, and what is its direct counterpart in Google Cloud Platform (GCP)?",
                "option_a": "AWS CodePipeline | GCP Cloud Build",
                "option_b": "AWS ECR | GCP Artifact Registry",
                "option_c": "AWS CodeCommit | GCP Source Repositories",
                "option_d": "AWS IAM | GCP Cloud Identity",
                "correct_answer": "C"
            },
            {
                "question_text": "When designing an API-first stack that uses microservices, what does the term 'Idempotency' mean regarding API endpoint safety?",
                "option_a": "The API endpoint changes its endpoint URL routing automatically on every request call.",
                "option_b": "The API can only accept connection requests originating from inside a Docker container environment.",
                "option_c": "The API requires all incoming data payloads to be formatted as raw uncompressed CSV matrices.",
                "option_d": "Making multiple identical requests to the API endpoint will produce the exact same system state as making a single request.",
                "correct_answer": "D"
            }
        ]

    # Default fallback dataset if anything else is selected while database is blank
    if not questions:
        questions = [{
            "question_text": "What does IT stand for?",
            "option_a": "Information Technology", "option_b": "Internet Telephony",
            "option_c": "Integrated Tools", "option_d": "International Transmission",
            "correct_answer": "A"
        }]

    total_q = len(questions)
    current_idx = st.session_state.get("current_question_index", 0)

    if not st.session_state.get("quiz_completed", False):
        st.write(f"**Question {current_idx + 1} of {total_q}**")
        st.progress((current_idx + 1) / total_q)
        
        q_data = questions[current_idx]
        st.markdown(f"### {q_data['question_text']}")
        
        options = {
            "A": f"A) {q_data['option_a']}",
            "B": f"B) {q_data['option_b']}",
            "C": f"C) {q_data['option_c']}",
            "D": f"D) {q_data['option_d']}"
        }
        
        existing_choice = st.session_state.student_answers.get(current_idx, None)
        index_default = list(options.keys()).index(existing_choice) if existing_choice in options else 0

        chosen_letter = st.radio(
            "Select your answer:", 
            options=list(options.keys()), 
            format_func=lambda x: options[x],
            index=index_default
        )
        
        st.session_state.student_answers[current_idx] = chosen_letter
        
        st.write("")
        col_prev, col_spacer, col_next = st.columns([1, 2, 1])
        
        with col_prev:
            if current_idx > 0:
                if st.button("⬅️ Previous Question", use_container_width=True):
                    st.session_state.current_question_index -= 1
                    st.rerun()
                    
        with col_next:
            if current_idx < total_q - 1:
                if st.button("Next Question ➡️", use_container_width=True):
                    st.session_state.current_question_index += 1
                    st.rerun()
            else:
                if st.button("🏁 Submit Examination", type="primary", use_container_width=True):
                    st.session_state.quiz_completed = True
                    st.rerun()
    else:
        st.balloons()
        st.success("🎉 Evaluation submitted successfully to local registry arrays!")
        
        score = 0
        for idx, q in enumerate(questions):
            student_ans = st.session_state.student_answers.get(idx, None)
            if student_ans == q['correct_answer']:
                score += 1
                
        pct = (score / total_q) * 100
        
        st.markdown(f"### Performance Metrics Summary")
        st.metric(label="Final Earned Score", value=f"{score} / {total_q}", delta=f"{int(pct)}% Pass Rating")
        
        with st.expander("👁️ Review Detailed Question Diagnostics"):
            for idx, q in enumerate(questions):
                ans = st.session_state.student_answers.get(idx, 'N/A')
                is_correct = ans == q['correct_answer']
                status_icon = "✅" if is_correct else "❌"
                st.markdown(f"**Q{idx+1}: {q['question_text']}**")
                st.write(f"Your selection: `{ans}` | Structural Target Key: `{q['correct_answer']}` ({status_icon})")
                st.divider()

        if st.button("↩️ Return to Student Dashboard Home", use_container_width=True):
            st.session_state.quiz_active = False
            st.session_state.current_exam_file = None
            st.session_state.quiz_completed = False
            st.rerun()
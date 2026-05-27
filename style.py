import streamlit as st

def apply_custom_css():
    """
    Applies the visual framework for StudyStream RTU LMS.
    Focuses on branding, form elevation, and distraction-free assessment UI.
    """
    st.markdown("""
        <style>
        /* Global Background and Typography */
        .stApp {
            background-color: #f4f7f9;
            font-family: 'Inter', -apple-system, sans-serif;
        }
        
        /* RTU Branding Header */
        .rtu-header {
            padding: 2rem;
            background: linear-gradient(135deg, #003366 0%, #004080 100%);
            color: #ffffff;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(0, 51, 102, 0.2);
            border-bottom: 4px solid #ffcc00; /* RTU Gold Accent */
        }
        
        .rtu-header h1 {
            font-weight: 800;
            letter-spacing: -1px;
            margin-bottom: 0.5rem;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e0e6ed;
        }
        
        /* Elevated CRUD and Login Forms */
        [data-testid="stForm"] {
            border: 1px solid #e0e6ed;
            border-radius: 12px;
            background-color: #ffffff;
            padding: 2.5rem;
            box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        }

        /* Input Field Focus */
        .stTextInput input, .stSelectbox select {
            border-radius: 8px !important;
        }

        /* Standardized Buttons */
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            transition: all 0.2s ease-in-out;
        }
        
        /* Primary Action (Login/Submit) */
        button[kind="primary"] {
            background-color: #003366 !important;
            border: none !important;
        }
        
        button[kind="primary"]:hover {
            background-color: #004080 !important;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }

        /* Tab Navigation Polish */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: transparent;
        }

        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #ffffff;
            border-radius: 8px 8px 0 0;
            border: 1px solid #e0e6ed;
            padding: 10px 20px;
            color: #475569;
        }

        .stTabs [aria-selected="true"] {
            background-color: #003366 !important;
            color: #ffffff !important;
            border-bottom: 2px solid #ffcc00 !important;
        }

        /* Fullscreen Assessment Styling */
        .quiz-container {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 12px;
            border-left: 5px solid #003366;
            margin-bottom: 1rem;
        }

        /* Hide specific elements during exams if necessary */
        .quiz-active .stActionButton {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)
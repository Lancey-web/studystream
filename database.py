import mysql.connector
from mysql.connector import pooling
import streamlit as st

# --- 1. LOCAL DATABASE CONFIGURATION ---
# Centralizing parameters. For XAMPP defaults: user is 'root', password is empty string.
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",               # Keep this completely blank for default XAMPP!
    "database": "studystream_db" # <-- CHANGE THIS to your exact phpMyAdmin DB name!
}

# --- 2. CONNECTION POOLING INITIALIZATION ---
# Manages multiple simultaneous user interactions cleanly.
try:
    connection_pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="studystream_pool",
        pool_size=10,             # Increased size slightly for cleaner request handling
        pool_reset_session=True,
        **DB_CONFIG
    )
except mysql.connector.Error as err:
    # Captures the error cleanly if XAMPP MySQL isn't booted up yet
    st.error(f"⚠️ Critical Database Error: {err}")
    st.info("💡 Troubleshooting: Ensure your XAMPP Control Panel has 'MySQL' started and running green.")
    connection_pool = None

# --- 3. HELPER FUNCTIONS ---

def get_db_connection():
    """
    Fetches a reliable connection directly from our connection pool.
    """
    if connection_pool:
        try:
            return connection_pool.get_connection()
        except mysql.connector.Error as err:
            print(f"❌ Error fetching connection from pool: {err}")
            return None
    else:
        # Failsafe fallback attempt to create a direct link if the pool failed initialization
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            return conn
        except mysql.connector.Error:
            return None

def close_db_connection(conn, cursor=None):
    """
    Properly closes the active cursor and returns the connection asset back to the pool.
    """
    try:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close() # In pooling setups, .close() returns it to the pool instead of destroying it
    except Exception as e:
        print(f"Note: Error during connection cleanup: {e}")

def verify_tables():
    """
    Checks if your required tables exist in your phpMyAdmin system during startup.
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Verify mdl_user table structure
            cursor.execute("SHOW TABLES LIKE 'mdl_user'")
            if not cursor.fetchone():
                st.warning("⚠️ Table 'mdl_user' missing in your database schema!")
            
            # Verify mdl_quiz_questions table structure
            cursor.execute("SHOW TABLES LIKE 'mdl_quiz_questions'")
            if not cursor.fetchone():
                st.warning("⚠️ Table 'mdl_quiz_questions' missing in your database schema!")
        except mysql.connector.Error as err:
            print(f"Schema verification error: {err}")
        finally:
            close_db_connection(conn, cursor)

def log_activity(email, action):
    """
    Inserts a user activity log event record into your audit database tables.
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Matches your main.py query setup expectations
            cursor.execute("INSERT INTO mdl_logs (user_email, action) VALUES (%s, %s)", (email, action))
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Activity logging failed: {err}")
        finally:
            close_db_connection(conn, cursor)
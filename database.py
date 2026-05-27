import mysql.connector
from mysql.connector import pooling
import streamlit as st

# --- LOCAL DATABASE CONFIGURATION ---
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",               # Blank for default XAMPP configuration
    "database": "studystream_db"  # Your verified database name
}

# --- CONNECTION POOLING INITIALIZATION ---
try:
    connection_pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="studystream_pool",
        pool_size=10,
        pool_reset_session=True,
        **DB_CONFIG
    )
except mysql.connector.Error as err:
    st.error(f"⚠️ Critical Database Error: {err}")
    st.info("💡 Troubleshooting: Ensure your XAMPP Control Panel has 'MySQL' started and running green.")
    connection_pool = None

def get_db_connection():
    if connection_pool:
        try:
            return connection_pool.get_connection()
        except mysql.connector.Error:
            return None
    else:
        try:
            return mysql.connector.connect(**DB_CONFIG)
        except mysql.connector.Error:
            return None

def close_db_connection(conn, cursor=None):
    try:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
    except Exception as e:
        print(f"Note: Error during connection cleanup: {e}")

def log_activity(email, action):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO mdl_logs (user_email, action) VALUES (%s, %s)", (email, action))
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Activity logging failed: {err}")
        finally:
            close_db_connection(conn, cursor)
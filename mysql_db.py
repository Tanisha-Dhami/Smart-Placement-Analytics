import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def get_setting(name, default=None):
    # First, read from local .env
    value = os.getenv(name)

    if value:
        return value

    # If not found, read from Streamlit Cloud Secrets
    try:
        import streamlit as st
        return st.secrets.get(name, default)
    except Exception:
        return default


def get_connection():
    ssl_ca = get_setting("MYSQL_SSL_CA")

    # Resolve relative CA certificate path
    if ssl_ca and not os.path.isabs(ssl_ca):
        ssl_ca = os.path.join(os.path.dirname(__file__), ssl_ca)

    return mysql.connector.connect(
        host=get_setting("MYSQL_HOST"),
        port=int(get_setting("MYSQL_PORT", "4000")),
        user=get_setting("MYSQL_USER"),
        password=get_setting("MYSQL_PASSWORD"),
        database=get_setting("MYSQL_DATABASE", "smart_placement_db"),

        ssl_ca=ssl_ca,
        ssl_verify_cert=True,
        ssl_verify_identity=True
    )


def query_all(sql, params=()):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        return cur.fetchall()
    finally:
        conn.close()


def execute(sql, params=()):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        return cur.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def execute_transaction(sql_statements):
    """Run a list of SQL operations in one transaction."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        for sql, params in sql_statements:
            cur.execute(sql, params)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
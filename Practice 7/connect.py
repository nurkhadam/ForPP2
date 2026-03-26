import psycopg2
from config import host, user, password, db_name, port

def get_connection():
    try:
        conn = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
            port=port
        )
        return conn
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
        return None
# connect.py — single place for DB connections
# Centralising the connection here means if we ever change DB settings,
# we only need to update config.py — nothing else in the project changes.

import psycopg2          # PostgreSQL adapter for Python; lets us send SQL from Python
from config import DB_CONFIG  # import the credentials dictionary from config.py


def get_connection():
    # DB_CONFIG-ті қолданбай, мәліметтерді тікелей жазамыз
    return psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="1111",
        port="5432"
    )
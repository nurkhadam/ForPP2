import psycopg2
import csv
from connect import get_connection

def create_table():
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS phonebook (
                contact_id SERIAL PRIMARY KEY,
                user_name VARCHAR(100) NOT NULL,
                phone_number VARCHAR(20) NOT NULL UNIQUE
            );
        """)
    conn.commit()
    conn.close()

def insert_from_csv(file_path):
    conn = get_connection()
    with conn.cursor() as cursor:
        with open(file_path, mode='r') as f:
            reader = csv.reader(f)
            for row in reader:
                cursor.execute("INSERT INTO phonebook (user_name, phone_number) VALUES (%s, %s) ON CONFLICT DO NOTHING", (row[0], row[1]))
    conn.commit()
    conn.close()
    print("CSV-ден мәліметтер жүктелді.")

def insert_from_console():
    name = input("Аты: ")
    phone = input("Телефон: ")
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO phonebook (user_name, phone_number) VALUES (%s, %s)", (name, phone))
    conn.commit()
    conn.close()

def update_contact(old_name, new_phone):
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("UPDATE phonebook SET phone_number = %s WHERE user_name = %s", (new_phone, old_name))
    conn.commit()
    conn.close()

def query_contacts(filter_val):
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM phonebook WHERE user_name ILIKE %s OR phone_number LIKE %s", (f"%{filter_val}%", f"%{filter_val}%"))
        for row in cursor.fetchall():
            print(row)
    conn.close()

def delete_contact(val):
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM phonebook WHERE user_name = %s OR phone_number = %s", (val, val))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_table()
    # Осы жерде функцияларды шақырып тексерсең болады
    # insert_from_csv('contacts.csv')
    print("PhoneBook дайын!")
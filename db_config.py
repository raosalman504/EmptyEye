import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',  # Set your MySQL root password if any
        database='empty_eye_db'
    )

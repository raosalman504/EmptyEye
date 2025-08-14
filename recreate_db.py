import mysql.connector

def recreate_database():
    # Connect to MySQL server without specifying a database
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password=''  # Update this if your XAMPP MySQL has a password
    )
    cursor = conn.cursor()
    
    # Create database if it doesn't exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS empty_eye_db")
    print("Database 'empty_eye_db' created or already exists")
    
    # Connect to the newly created database
    conn.close()
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',  # Update this if your XAMPP MySQL has a password
        database='empty_eye_db'
    )
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        password VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL
    )
    """)
    print("Table 'users' created or already exists")
    
    # Create notifications table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INT AUTO_INCREMENT PRIMARY KEY,
        recipient VARCHAR(100) NOT NULL,
        message TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        type VARCHAR(50) DEFAULT 'alert'
    )
    """)
    print("Table 'notifications' created or already exists")
    
    # Close connection
    cursor.close()
    conn.close()
    print("Database setup complete")

if __name__ == "__main__":
    recreate_database()

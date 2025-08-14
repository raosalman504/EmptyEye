from db_config import get_db_connection
import mysql.connector
from datetime import datetime

def test_database_connection():
    """Test if we can connect to the database"""
    try:
        conn = get_db_connection()
        print("✅ Database connection successful!")
        
        # Test if notifications table exists
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES LIKE 'notifications'")
        result = cursor.fetchone()
        
        if result:
            print("✅ Notifications table exists")
            # Test if we can insert and retrieve
            test_message = f"Test notification at {datetime.now()}"
            cursor.execute("INSERT INTO notifications (message, timestamp) VALUES (%s, %s)",
                          (test_message, datetime.now()))
            conn.commit()
            print("✅ Inserted test notification")
            
            cursor.execute("SELECT * FROM notifications ORDER BY timestamp DESC LIMIT 5")
            notifications = cursor.fetchall()
            print(f"✅ Retrieved {len(notifications)} notifications:")
            for notification in notifications:
                print(f"  - {notification}")
        else:
            print("❌ Notifications table does not exist!")
            print("Creating notifications table...")
            try:
                cursor.execute("""
                CREATE TABLE notifications (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    message VARCHAR(255) NOT NULL,
                    timestamp DATETIME NOT NULL
                )
                """)
                conn.commit()
                print("✅ Created notifications table")
            except Exception as e:
                print(f"❌ Failed to create table: {e}")
        
        cursor.close()
        conn.close()
    except mysql.connector.Error as e:
        print(f"❌ Database connection failed: {e}")
        
        if e.errno == 1049:  # Unknown database
            print("\nThe database 'empty_eye_db' does not exist. Creating it...")
            try:
                conn = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password=''
                )
                cursor = conn.cursor()
                cursor.execute("CREATE DATABASE empty_eye_db")
                print("✅ Created database 'empty_eye_db'")
                
                conn.database = 'empty_eye_db'
                cursor.execute("""
                CREATE TABLE notifications (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    message VARCHAR(255) NOT NULL,
                    timestamp DATETIME NOT NULL
                )
                """)
                conn.commit()
                print("✅ Created notifications table")
                
                cursor.execute("""
                CREATE TABLE users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL
                )
                """)
                conn.commit()
                print("✅ Created users table")
                
                cursor.close()
                conn.close()
            except Exception as create_error:
                print(f"❌ Failed to create database: {create_error}")

if __name__ == "__main__":
    test_database_connection()

import mysql.connector
import os
import bcrypt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'port': int(os.getenv('DB_PORT', 3306))
}

def init_database():
    # Connect without database
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Create database if not exists
        db_name = os.getenv('DB_NAME', 'gneralgames')
        cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
        cursor.execute(f"CREATE DATABASE {db_name}")
        cursor.execute(f"USE {db_name}")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        """)
        
        # Create files table
        cursor.execute("""
            CREATE TABLE files (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                path VARCHAR(1024),
                size BIGINT,
                type VARCHAR(50),
                user_id INT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP NULL,
                in_trash BOOLEAN DEFAULT FALSE,
                deleted_at TIMESTAMP NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create file_favorites table
        cursor.execute("""
            CREATE TABLE file_favorites (
                file_id INT,
                user_id INT,
                PRIMARY KEY (file_id, user_id),
                FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create todos table
        cursor.execute("""
            CREATE TABLE todos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                priority VARCHAR(20) NOT NULL DEFAULT 'medium',
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                deadline TIMESTAMP NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INT,
                FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        
        # Create todo_assignees table
        cursor.execute("""
            CREATE TABLE todo_assignees (
                todo_id INT,
                user_id INT,
                PRIMARY KEY (todo_id, user_id),
                FOREIGN KEY (todo_id) REFERENCES todos(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create chat_messages table
        cursor.execute("""
            CREATE TABLE chat_messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                recipient_id INT,
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
                FOREIGN KEY (recipient_id) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        
        # Create chat_reactions table
        cursor.execute("""
            CREATE TABLE chat_reactions (
                message_id INT,
                user_id INT,
                reaction_emoji VARCHAR(32),
                PRIMARY KEY (message_id, user_id),
                FOREIGN KEY (message_id) REFERENCES chat_messages(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create time_records table
        cursor.execute("""
            CREATE TABLE time_records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                check_in DATETIME NOT NULL,
                check_out DATETIME,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create calendar_events table
        cursor.execute("""
            CREATE TABLE calendar_events (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                type VARCHAR(50),
                date TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create admin user
        admin_password = "Orpund2552"
        hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("""
            INSERT INTO users (username, password, role) 
            VALUES (%s, %s, %s)
        """, ("Jerry", hashed_password.decode('utf-8'), "admin"))
        
        conn.commit()
        print(f"Database '{db_name}' and all tables created successfully!")
        print("Admin user 'Jerry' created successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    init_database()

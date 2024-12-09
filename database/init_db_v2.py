import os
from dotenv import load_dotenv
import mysql.connector

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'port': int(os.getenv('DB_PORT', 3306))
}

def init_database():
    # First connect without database to create it
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()
    
    try:
        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS generalgames")
        cursor.execute("USE generalgames")
        
        # Read and execute schema
        with open('database/schema_v2.sql', 'r') as f:
            schema = f.read()
            
        # Split into individual statements
        statements = schema.split(';')
        
        # Execute each statement
        for statement in statements:
            if statement.strip():
                cursor.execute(statement)
        
        # Create default admin user if it doesn't exist
        cursor.execute("""
            INSERT IGNORE INTO users (username, password, role)
            VALUES ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYmR0ctDl.', 'admin')
        """)
                
        connection.commit()
        print("Database 'generalgames' and all tables created successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    init_database()

import mysql.connector
from datetime import datetime
import bcrypt
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Database configuration
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'port': int(os.getenv('DB_PORT', 3306))
}

class DatabaseManager:
    def __init__(self):
        """Initialize database connection."""
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.connection.cursor(dictionary=True)
            print("Successfully connected to MariaDB")
            self._init_tables()
        except Exception as e:
            print(f"Database connection error: {e}")
            raise Exception(f"Failed to connect to MariaDB: {e}")

    def _init_tables(self):
        """Initialize database tables if they don't exist"""
        try:
            # Check if we need to add new columns to users table
            needed_columns = {
                'email': 'VARCHAR(255)',
                'position': 'VARCHAR(255)',
                'department': 'VARCHAR(255)',
                'location': 'VARCHAR(255)',
                'is_active': 'BOOLEAN DEFAULT TRUE'
            }
            
            # Get existing columns
            self.cursor.execute("""
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'users'
            """)
            existing_columns = {row['COLUMN_NAME'] for row in self.cursor.fetchall()}
            
            # Add missing columns
            for column, data_type in needed_columns.items():
                if column not in existing_columns:
                    print(f"Adding {column} column to users table...")
                    self.cursor.execute(f"""
                        ALTER TABLE users
                        ADD COLUMN {column} {data_type}
                    """)
                    self.connection.commit()
                    print(f"{column} column successfully added")

            # Create users table if it doesn't exist
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    email VARCHAR(255),
                    position VARCHAR(255),
                    department VARCHAR(255),
                    location VARCHAR(255),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Files table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    path VARCHAR(1024),
                    size BIGINT,
                    type VARCHAR(50),
                    user_id INT,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    in_trash BOOLEAN DEFAULT FALSE,
                    deleted_at TIMESTAMP NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # File favorites table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_favorites (
                    file_id INT,
                    user_id INT,
                    PRIMARY KEY (file_id, user_id),
                    FOREIGN KEY (file_id) REFERENCES files(id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # Todos table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS todos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    priority VARCHAR(50) NOT NULL,
                    deadline DATE,
                    status VARCHAR(50) NOT NULL,
                    completed BOOLEAN DEFAULT FALSE,
                    created_by INT,
                    project_id INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users(id),
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                )
            """)

            # Todo assignees table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS todo_assignees (
                    todo_id INT,
                    user_id INT,
                    PRIMARY KEY (todo_id, user_id),
                    FOREIGN KEY (todo_id) REFERENCES todos(id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # Projects table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    created_by INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users(id)
                )
            """)

            # Chat messages table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    recipient_id INT,
                    message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (recipient_id) REFERENCES users(id)
                )
            """)

            # Chat reactions table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_reactions (
                    message_id INT,
                    user_id INT,
                    reaction_emoji VARCHAR(10),
                    PRIMARY KEY (message_id, user_id),
                    FOREIGN KEY (message_id) REFERENCES chat_messages(id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # Time records table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS time_records (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    check_in DATETIME NOT NULL,
                    check_out DATETIME,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # Calendar events table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS calendar_events (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    type VARCHAR(50) NOT NULL,
                    date DATETIME NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            self.connection.commit()
        except Exception as e:
            print(f"Error initializing tables: {e}")
            raise

    def _ensure_connection(self):
        """Ensure database connection is active, reconnect if needed"""
        try:
            self.connection.ping(reconnect=True, attempts=3, delay=5)
        except Exception as e:
            print(f"Error reconnecting to database: {e}")
            raise

    def add_file(self, file_info):
        """Add a new file."""
        self._ensure_connection()
        try:
            self.cursor.execute("""
                INSERT INTO files (name, path, size, type, user_id, uploaded_at)
                VALUES (%(name)s, %(path)s, %(size)s, %(type)s, %(user_id)s, %(uploaded_at)s)
            """, file_info)
            self.connection.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print("Database error:", e)
            return None

    def get_files(self, user_id=None):
        """Get files, optionally filtered by user_id."""
        self._ensure_connection()
        try:
            query = """
                SELECT f.*, 
                       GROUP_CONCAT(ff.user_id) as favorite_users
                FROM files f
                LEFT JOIN file_favorites ff ON f.id = ff.file_id
            """
            params = {}
            
            if user_id:
                query += " WHERE f.user_id = %(user_id)s"
                params['user_id'] = user_id
            
            query += " GROUP BY f.id"
            
            self.cursor.execute(query, params)
            files = self.cursor.fetchall()
            
            # Convert favorite_users string to list
            for file in files:
                if file['favorite_users']:
                    file['favorites'] = [int(uid) for uid in file['favorite_users'].split(',')]
                else:
                    file['favorites'] = []
                del file['favorite_users']
            
            return files
        except Exception as e:
            print("Database error:", e)
            return []

    def add_to_favorites(self, file_id, user_id):
        """Add a file to user's favorites."""
        self._ensure_connection()
        try:
            self.cursor.execute("""
                INSERT IGNORE INTO file_favorites (file_id, user_id)
                VALUES (%s, %s)
            """, (file_id, user_id))
            self.connection.commit()
            return True
        except Exception as e:
            print("Database error:", e)
            return False

    def remove_from_favorites(self, file_id, user_id):
        """Remove a file from user's favorites."""
        self._ensure_connection()
        try:
            self.cursor.execute("""
                DELETE FROM file_favorites
                WHERE file_id = %s AND user_id = %s
            """, (file_id, user_id))
            self.connection.commit()
            return True
        except Exception as e:
            print("Database error:", e)
            return False

    def move_to_trash(self, file_id, user_id):
        """Move a file to trash."""
        self._ensure_connection()
        try:
            self.cursor.execute("""
                UPDATE files
                SET in_trash = TRUE, deleted_at = CURRENT_TIMESTAMP
                WHERE id = %s AND user_id = %s
            """, (file_id, user_id))
            self.connection.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print("Database error:", e)
            return False

    def restore_from_trash(self, file_id, user_id):
        """Restore a file from trash."""
        self._ensure_connection()
        try:
            self.cursor.execute("""
                UPDATE files
                SET in_trash = FALSE, deleted_at = NULL
                WHERE id = %s AND user_id = %s
            """, (file_id, user_id))
            self.connection.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print("Database error:", e)
            return False

    def get_trash(self, user_id):
        """Get files in user's trash."""
        self._ensure_connection()
        try:
            self.cursor.execute("""
                SELECT f.*, 
                       GROUP_CONCAT(ff.user_id) as favorite_users
                FROM files f
                LEFT JOIN file_favorites ff ON f.id = ff.file_id
                WHERE f.user_id = %s AND f.in_trash = TRUE
                GROUP BY f.id
            """, (user_id,))
            files = self.cursor.fetchall()
            
            # Convert favorite_users string to list
            for file in files:
                if file['favorite_users']:
                    file['favorites'] = [int(uid) for uid in file['favorite_users'].split(',')]
                else:
                    file['favorites'] = []
                del file['favorite_users']
            
            return files
        except Exception as e:
            print("Database error:", e)
            return []

    def delete_file(self, file_id):
        """Delete a file permanently."""
        self._ensure_connection()
        try:
            # First delete from favorites
            self.cursor.execute("DELETE FROM file_favorites WHERE file_id = %s", (file_id,))
            # Then delete the file
            self.cursor.execute("DELETE FROM files WHERE id = %s", (file_id,))
            self.connection.commit()
            return True
        except Exception as e:
            print("Database error:", e)
            return False

    def search_files(self, user_id, query):
        """Search files by name."""
        self._ensure_connection()
        try:
            self.cursor.execute("""
                SELECT f.*, 
                       GROUP_CONCAT(ff.user_id) as favorite_users
                FROM files f
                LEFT JOIN file_favorites ff ON f.id = ff.file_id
                WHERE f.user_id = %s 
                AND f.in_trash = FALSE
                AND f.name LIKE %s
                GROUP BY f.id
            """, (user_id, f"%{query}%"))
            
            files = self.cursor.fetchall()
            
            # Convert favorite_users string to list
            for file in files:
                if file['favorite_users']:
                    file['favorites'] = [int(uid) for uid in file['favorite_users'].split(',')]
                else:
                    file['favorites'] = []
                del file['favorite_users']
            
            return files
        except Exception as e:
            print("Database error:", e)
            return []

    def get_upload_path(self):
        """Get the path for file uploads."""
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
        os.makedirs(path, exist_ok=True)
        return path

    def get_todos(self, user_id=None, project_id=None):
        """Get todos, optionally filtered by user_id and/or project_id."""
        self._ensure_connection()
        try:
            query = """
                SELECT t.*, 
                       GROUP_CONCAT(ta.user_id) as assignee_ids,
                       p.name as project_name
                FROM todos t
                LEFT JOIN todo_assignees ta ON t.id = ta.todo_id
                LEFT JOIN projects p ON t.project_id = p.id
            """
            params = []
            where_clauses = []

            if user_id:
                where_clauses.append("(t.created_by = %s OR ta.user_id = %s)")
                params.extend([user_id, user_id])

            if project_id:
                where_clauses.append("t.project_id = %s")
                params.append(project_id)

            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

            query += " GROUP BY t.id"

            self.cursor.execute(query, tuple(params))
            todos = self.cursor.fetchall()

            # Convert assignee_ids string to list
            for todo in todos:
                if todo['assignee_ids']:
                    todo['assignees'] = [int(uid) for uid in todo['assignee_ids'].split(',')]
                else:
                    todo['assignees'] = []
                del todo['assignee_ids']

            return todos
        except Exception as e:
            print("Database error:", e)
            return []

    def create_todo(self, title, description, priority, deadline, created_by, project_id=None, assignees=None):
        """Create a new todo with optional assignees."""
        self._ensure_connection()
        try:
            self.cursor.execute("""
                INSERT INTO todos (title, description, priority, deadline, created_by, project_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (title, description, priority, deadline, created_by, project_id))
            todo_id = self.cursor.lastrowid

            if assignees:
                for assignee in assignees:
                    self.cursor.execute("""
                        INSERT INTO todo_assignees (todo_id, user_id)
                        VALUES (%s, %s)
                    """, (todo_id, assignee))

            self.connection.commit()
            return todo_id
        except Exception as e:
            print("Database error:", e)
            return None

    def update_todo(self, todo):
        """Update a todo's status and other fields."""
        self._ensure_connection()
        try:
            # Update todo
            self.cursor.execute("""
                UPDATE todos
                SET status = %s,
                    title = %s,
                    description = %s,
                    priority = %s,
                    deadline = %s,
                    completed = %s
                WHERE id = %s
            """, (todo['status'], todo['title'], todo['description'],
                  todo['priority'], todo['deadline'], todo['completed'], todo['id']))
            
            # Update assignees
            self.cursor.execute("DELETE FROM todo_assignees WHERE todo_id = %s", (todo['id'],))
            if todo.get('assignees'):
                for assignee in todo['assignees']:
                    self.cursor.execute("""
                        INSERT INTO todo_assignees (todo_id, user_id)
                        VALUES (%s, %s)
                    """, (todo['id'], assignee))
            
            self.connection.commit()
            return True
        except Exception as e:
            print("Database error:", e)
            return False

    def get_chat_users(self, user_id):
        """Get list of users the current user has chatted with"""
        self._ensure_connection()
        try:
            self.cursor.execute("""
                SELECT DISTINCT u.id, u.username, u.role
                FROM users u
                INNER JOIN (
                    SELECT user_id as uid FROM chat_messages 
                    WHERE recipient_id = %s
                    UNION
                    SELECT recipient_id as uid FROM chat_messages 
                    WHERE user_id = %s
                ) chat_users ON u.id = chat_users.uid
                WHERE u.id != %s
            """, (user_id, user_id, user_id))
            return self.cursor.fetchall()
        except Exception as e:
            print("Database error:", e)
            return []

    def save_chat_message(self, user_id, recipient_id, message):
        """Save a new chat message"""
        self._ensure_connection()
        try:
            self.cursor.execute("""
                INSERT INTO chat_messages (user_id, recipient_id, message)
                VALUES (%s, %s, %s)
            """, (user_id, recipient_id, message))
            self.connection.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print("Database error:", e)
            return None

    def get_chat_messages(self, sender_id, receiver_id, since_id=0, limit=50):
        """
        Get chat messages between two users, optionally only messages newer than since_id
        """
        try:
            self._ensure_connection()
            query = """
                SELECT m.id, m.sender_id, m.receiver_id, m.message, m.timestamp,
                       s.username as sender_name, r.username as receiver_name
                FROM chat_messages m
                JOIN users s ON m.sender_id = s.id
                JOIN users r ON m.receiver_id = r.id
                WHERE ((m.sender_id = %s AND m.receiver_id = %s)
                OR (m.sender_id = %s AND m.receiver_id = %s))
                AND m.id > %s
                ORDER BY m.timestamp ASC
                LIMIT %s
            """
            
            self.cursor.execute(query, (sender_id, receiver_id, receiver_id, sender_id, since_id, limit))
            messages = self.cursor.fetchall()
            return messages
                    
        except Exception as e:
            print(f"Fehler beim Abrufen der Chat-Nachrichten: {e}")
            return []

    def add_message_reaction(self, message_id, user_id, reaction_emoji):
        """Add a reaction to a chat message"""
        self._ensure_connection()
        try:
            self.cursor.execute("""
                INSERT INTO chat_reactions (message_id, user_id, reaction_emoji)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE reaction_emoji = VALUES(reaction_emoji)
            """, (message_id, user_id, reaction_emoji))
            self.connection.commit()
            return True
        except Exception as e:
            print("Database error:", e)
            return False

    def remove_message_reaction(self, message_id, user_id):
        """Remove a reaction from a chat message"""
        self._ensure_connection()
        try:
            self.cursor.execute("""
                DELETE FROM chat_reactions
                WHERE message_id = %s AND user_id = %s
            """, (message_id, user_id))
            self.connection.commit()
            return True
        except Exception as e:
            print("Database error:", e)
            return False

    def get_users(self):
        """Get all users from the database."""
        self._ensure_connection()
        try:
            print("Versuche Benutzer aus der Datenbank zu laden...")
            # Einfachere Abfrage ohne is_active Filter, da die Spalte möglicherweise nicht existiert
            self.cursor.execute("""
                SELECT id, username, role, created_at
                FROM users
                ORDER BY username
            """)
            users = self.cursor.fetchall()
            print(f"Gefundene Benutzer: {len(users)}")
            for user in users:
                print(f"- {user['username']} (ID: {user['id']}, Role: {user['role']})")
            return users
        except Exception as e:
            print(f"Datenbankfehler beim Laden der Benutzer: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_users_by_ids(self, user_ids):
        """Get specific users by their IDs."""
        if not user_ids:
            return []
        
        self._ensure_connection()
        try:
            placeholders = ', '.join(['%s'] * len(user_ids))
            self.cursor.execute(f"""
                SELECT id, username, role, created_at
                FROM users
                WHERE id IN ({placeholders})
            """, tuple(user_ids))
            return self.cursor.fetchall()
        except Exception as e:
            print("Database error:", e)
            return []

    def create_user(self, username, password, role="user"):
        """Create a new user in the database."""
        self._ensure_connection()
        try:
            # Hash the password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            self.cursor.execute("""
                INSERT INTO users (username, password, role)
                VALUES (%s, %s, %s)
            """, (username, hashed_password, role))
            self.connection.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    def get_time_records(self, user_id, start_date=None, end_date=None):
        """Get time records for a specific user with optional date range."""
        self._ensure_connection()
        try:
            query = """
                SELECT tr.*, u.username
                FROM time_records tr
                JOIN users u ON tr.user_id = u.id
                WHERE tr.user_id = %s
            """
            params = [user_id]

            if start_date:
                query += " AND tr.check_in >= %s"
                params.append(start_date)
            if end_date:
                query += " AND tr.check_in <= %s"
                params.append(end_date)

            query += " ORDER BY tr.check_in DESC"
            
            self.cursor.execute(query, tuple(params))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error fetching time records: {e}")
            return []

    def add_time_record(self, user_id, check_in, check_out=None):
        """Add a new time record."""
        self._ensure_connection()
        try:
            self.cursor.execute("""
                INSERT INTO time_records 
                (user_id, check_in, check_out)
                VALUES (%s, %s, %s)
            """, (user_id, check_in, check_out))
            self.connection.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Error adding time record: {e}")
            return None

    def update_time_record(self, record_id, check_out):
        """Update an existing time record with check out time."""
        self._ensure_connection()
        try:
            self.cursor.execute("""
                UPDATE time_records 
                SET check_out = %s
                WHERE id = %s
            """, (check_out, record_id))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error updating time record: {e}")
            return False

    def get_last_time_record(self, user_id):
        """Get the last time record for a user"""
        self._ensure_connection()
        try:
            self.cursor.execute("""
                SELECT *
                FROM time_records
                WHERE user_id = %s
                ORDER BY check_in DESC
                LIMIT 1
            """, (user_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print("Database error:", e)
            return None

    def get_calendar_events(self, user_id, date=None):
        """Get calendar events for a user, optionally filtered by date"""
        self._ensure_connection()
        try:
            if date:
                self.cursor.execute("""
                    SELECT e.*, u.username as creator_name
                    FROM calendar_events e
                    LEFT JOIN users u ON e.user_id = u.id
                    WHERE e.user_id = %s
                    AND DATE(e.date) = DATE(%s)
                    ORDER BY e.date ASC
                """, (user_id, date))
            else:
                self.cursor.execute("""
                    SELECT e.*, u.username as creator_name
                    FROM calendar_events e
                    LEFT JOIN users u ON e.user_id = u.id
                    WHERE e.user_id = %s
                    ORDER BY e.date ASC
                """, (user_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print("Database error:", e)
            return []

    def create_calendar_event(self, user_id, title, description, type, date):
        """Create a new calendar event"""
        self._ensure_connection()
        try:
            self.cursor.execute("""
                INSERT INTO calendar_events (user_id, title, description, type, date)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, title, description, type, date))
            self.connection.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print("Database error:", e)
            return None

    def update_calendar_event(self, event_id, title, description, type, date):
        """Update an existing calendar event"""
        self._ensure_connection()
        try:
            self.cursor.execute("""
                UPDATE calendar_events
                SET title = %s,
                    description = %s,
                    type = %s,
                    date = %s
                WHERE id = %s
            """, (title, description, type, date, event_id))
            self.connection.commit()
            return True
        except Exception as e:
            print("Database error:", e)
            return False

    def delete_calendar_event(self, event_id):
        """Delete a calendar event"""
        self._ensure_connection()
        try:
            self.cursor.execute("DELETE FROM calendar_events WHERE id = %s", (event_id,))
            self.connection.commit()
            return True
        except Exception as e:
            print("Database error:", e)
            return False

    def get_calendar_event(self, event_id):
        """Get a specific calendar event"""
        self._ensure_connection()
        try:
            self.cursor.execute("""
                SELECT e.*, u.username as creator_name
                FROM calendar_events e
                LEFT JOIN users u ON e.user_id = u.id
                WHERE e.id = %s
            """, (event_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print("Database error:", e)
            return None

    def check_users(self):
        """Check all users in the database for debugging."""
        self._ensure_connection()
        try:
            self.cursor.execute("SELECT COUNT(*) as count FROM users")
            result = self.cursor.fetchone()
            print(f"Total users found: {result['count']}")
        except Exception as e:
            print(f"Error checking users: {e}")

    def authenticate_user(self, username, password):
        """Authenticate a user with username and password."""
        self._ensure_connection()
        try:
            # Get user from database
            self.cursor.execute("""
                SELECT id, username, password, role 
                FROM users 
                WHERE username = %s AND is_active = TRUE
            """, (username,))
            
            user = self.cursor.fetchone()
            if not user:
                return None
            
            # Verify password
            if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                # Return user data without password
                return {
                    'id': user['id'],
                    'username': user['username'],
                    'role': user['role']
                }
            return None
        except Exception as e:
            print(f"Authentication error: {e}")
            return None

    def get_all_users(self):
        """Get all users from the database"""
        try:
            self.cursor.execute("""
                SELECT id, username, role, is_active,
                       created_at, email, position, department, location
                FROM users
                ORDER BY username
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting users: {e}")
            return []

    def create_user(self, user_data):
        """Create a new user"""
        try:
            # Hash the password
            password = user_data['password'].encode('utf-8')
            hashed = bcrypt.hashpw(password, bcrypt.gensalt())
            
            self.cursor.execute("""
                INSERT INTO users (username, password, role, email, 
                                 position, department, location)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                user_data['username'],
                hashed.decode('utf-8'),
                user_data['role'],
                user_data.get('email', ''),
                user_data.get('position', ''),
                user_data.get('department', ''),
                user_data.get('location', '')
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False

    def update_user(self, username, user_data):
        """Update an existing user"""
        try:
            update_fields = []
            values = []
            
            # Handle all fields except password
            field_mapping = {
                'email': 'email',
                'role': 'role',
                'position': 'position',
                'department': 'department',
                'location': 'location'
            }
            
            for field, db_field in field_mapping.items():
                if field in user_data and user_data[field]:
                    update_fields.append(f"{db_field} = %s")
                    values.append(user_data[field])
            
            # Handle password separately
            if 'password' in user_data and user_data['password']:
                password = user_data['password'].encode('utf-8')
                hashed = bcrypt.hashpw(password, bcrypt.gensalt())
                update_fields.append("password = %s")
                values.append(hashed.decode('utf-8'))
            
            # Add username to values
            values.append(username)
            
            # Construct and execute query
            if update_fields:
                query = f"""
                    UPDATE users 
                    SET {', '.join(update_fields)}
                    WHERE username = %s
                """
                self.cursor.execute(query, values)
                self.connection.commit()
                return True
            return False
        except Exception as e:
            print(f"Error updating user: {e}")
            return False

    def delete_user(self, username):
        """Delete a user"""
        try:
            self.cursor.execute("DELETE FROM users WHERE username = %s", (username,))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False

    def get_projects(self, user_id=None):
        """Get all projects, optionally filtered by user_id."""
        self._ensure_connection()
        try:
            if user_id:
                self.cursor.execute("""
                    SELECT p.*, COUNT(t.id) as todo_count
                    FROM projects p
                    LEFT JOIN todos t ON p.id = t.project_id
                    WHERE p.created_by = %s
                    GROUP BY p.id
                """, (user_id,))
            else:
                self.cursor.execute("""
                    SELECT p.*, COUNT(t.id) as todo_count
                    FROM projects p
                    LEFT JOIN todos t ON p.id = t.project_id
                    GROUP BY p.id
                """)
            return self.cursor.fetchall()
        except Exception as e:
            print("Database error:", e)
            return []

    def get_project(self, project_id):
        """Get a specific project by ID."""
        self._ensure_connection()
        try:
            self.cursor.execute("""
                SELECT p.*, COUNT(t.id) as todo_count
                FROM projects p
                LEFT JOIN todos t ON p.id = t.project_id
                WHERE p.id = %s
                GROUP BY p.id
            """, (project_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print("Database error:", e)
            return None

    def create_project(self, name, description, created_by):
        """Create a new project."""
        self._ensure_connection()
        try:
            self.cursor.execute("""
                INSERT INTO projects (name, description, created_by)
                VALUES (%s, %s, %s)
            """, (name, description, created_by))
            self.connection.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print("Database error:", e)
            return None

    def update_project(self, project_id, name, description):
        """Update a project's details."""
        self._ensure_connection()
        try:
            self.cursor.execute("""
                UPDATE projects
                SET name = %s, description = %s
                WHERE id = %s
            """, (name, description, project_id))
            self.connection.commit()
            return True
        except Exception as e:
            print("Database error:", e)
            return False

    def delete_project(self, project_id):
        """Delete a project and all its todos."""
        self._ensure_connection()
        try:
            # The todos will be automatically deleted due to ON DELETE CASCADE
            self.cursor.execute("DELETE FROM projects WHERE id = %s", (project_id,))
            self.connection.commit()
            return True
        except Exception as e:
            print("Database error:", e)
            return False

    def __del__(self):
        """Cleanup database connection"""
        try:
            if hasattr(self, 'cursor'):
                self.cursor.close()
            if hasattr(self, 'connection'):
                self.connection.close()
        except Exception as e:
            print(f"Error closing database connection: {e}")

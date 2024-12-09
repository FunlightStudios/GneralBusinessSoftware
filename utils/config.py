import os

# Debug mode flag - set to True by default for development
DEBUG_MODE = True

# Database configuration
DB_CONNECTION_STRING = os.getenv('DB_CONNECTION_STRING', 'mongodb://localhost:27017')
DB_NAME = os.getenv('DB_NAME', 'gaming_business_db')

# Collections
USERS_COLLECTION = 'users'
TODOS_COLLECTION = 'todos'
CHAT_COLLECTION = 'chat_messages'
TIME_RECORDS_COLLECTION = 'time_records'
FILES_COLLECTION = 'files'
CALENDAR_EVENTS_COLLECTION = 'calendar_events'

# File upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'zip', 'rar'}

from database.db_manager import DatabaseManager

def add_initial_users():
    db = DatabaseManager()
    
    # Add Jerry as admin
    db.create_user(
        username="jerry",
        password="jerry123",  # Bitte nach dem ersten Login ändern
        role="admin"
    )
    
    # Add Mischa as admin
    db.create_user(
        username="mischa",
        password="mischa123",  # Bitte nach dem ersten Login ändern
        role="admin"
    )
    
    print("Initial users added successfully!")

if __name__ == "__main__":
    add_initial_users()

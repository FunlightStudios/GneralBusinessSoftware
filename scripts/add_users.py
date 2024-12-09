from database.db_manager import DatabaseManager

def main():
    db = DatabaseManager()
    
    # Add users
    users_to_add = [
        {
            "username": "Jerry",
            "password": "Orpund2552",
            "role": "admin",
            "email": "jerry@example.com",
            "position": "Developer",
            "department": "Engineering",
            "location": "Switzerland"
        },
        {
            "username": "Mischa",
            "password": "Orpund2552",
            "role": "admin",
            "email": "mischa@example.com",
            "position": "Developer",
            "department": "Engineering",
            "location": "Switzerland"
        }
    ]
    
    for user_data in users_to_add:
        success = db.create_user(user_data)
        if success:
            print(f"Successfully created user {user_data['username']}")
        else:
            print(f"Failed to create user {user_data['username']}")
    
    print("\nCurrent users in database:")
    db.check_users()

if __name__ == "__main__":
    main()

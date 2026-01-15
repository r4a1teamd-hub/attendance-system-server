from app import create_app, db
from app.models import User

app = create_app()

def recreate_db():
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        
        # Create Admin User
        student_id = "00001111"
        password = "admin"
        
        print(f"Creating admin user {student_id}...")
        user = User(
            student_id=student_id,
            username="Admin Teacher",
            email="admin@school.edu",
            role=1,
            is_password_changed=True  # Admin is considered changed or pre-set
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        print("Database recreated and admin user configured.")

if __name__ == "__main__":
    confirm = input("This will DELETE ALL DATA. Are you sure? (yes/no): ")
    if confirm.lower() == 'yes':
        recreate_db()
    else:
        print("Cancelled.")

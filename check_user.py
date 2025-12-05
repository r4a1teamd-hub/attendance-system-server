from app import create_app, db
from app.models import User

app = create_app()

def check_user():
    with app.app_context():
        student_id = "00001111"
        user = User.query.filter_by(student_id=student_id).first()
        
        if user:
            print(f"User found: ID={user.id}, StudentID={user.student_id}, Username={user.username}, Role={user.role}")
            print(f"Password Hash: {user.password_hash[:20]}...")
            
            # Verify password manually
            if user.check_password("admin"):
                print("Password verification: SUCCESS")
            else:
                print("Password verification: FAILED")
        else:
            print(f"User {student_id} NOT found.")

if __name__ == "__main__":
    check_user()

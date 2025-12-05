from app import create_app, db
from app.models import User

app = create_app()

def setup_test_user():
    with app.app_context():
        student_id = "TEST_STUDENT_01"
        email = "r4a1.teamd@gmail.com"
        username = "Test Student 01"
        
        user = User.query.filter_by(student_id=student_id).first()
        
        if user:
            print(f"User {student_id} exists. Updating email to {email}...")
            user.email = email
            user.role = 0
        else:
            print(f"Creating new user {student_id} with email {email}...")
            user = User(
                student_id=student_id,
                username=username,
                email=email,
                role=0
            )
            user.set_password("password")
            db.session.add(user)
        
        db.session.commit()
        print(f"Test user {student_id} configured successfully.")

if __name__ == "__main__":
    setup_test_user()

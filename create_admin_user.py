from app import create_app, db
from app.models import User

app = create_app()

def create_admin():
    with app.app_context():
        student_id = "00001111"
        password = "admin"
        
        user = User.query.filter_by(student_id=student_id).first()
        
        if user:
            print(f"User {student_id} exists. Updating...")
            user.set_password(password)
            user.role = 1 # Teacher
        else:
            print(f"Creating new user {student_id}...")
            user = User(
                student_id=student_id,
                username="Admin Teacher",
                email="admin@school.edu",
                role=1
            )
            user.set_password(password)
            db.session.add(user)
        
        db.session.commit()
        print(f"Admin user {student_id} configured successfully.")

if __name__ == "__main__":
    create_admin()

from app import create_app, db
from app.models import User, Attendance
from datetime import datetime, timedelta
import random

app = create_app()

def update_student_data():
    with app.app_context():
        student_id = "20240002"
        email = "yecunxiuya@gmail.com"
        
        user = User.query.filter_by(student_id=student_id).first()
        
        if not user:
            print(f"User {student_id} not found. Creating...")
            user = User(student_id=student_id, username="Student 20240002", email=email, role=0)
            user.set_password("password")
            db.session.add(user)
        else:
            print(f"Updating email for {student_id} to {email}...")
            user.email = email
        
        # Add 83 absent records
        print(f"Adding 83 absent records for {student_id}...")
        base_date = datetime.now()
        for i in range(83):
            timestamp = base_date - timedelta(days=i)
            timestamp = timestamp.replace(hour=9, minute=random.randint(0, 30))
            
            attendance = Attendance(
                user_id=user.id,
                status='absent',
                recorded_by='admin_script',
                timestamp=timestamp
            )
            db.session.add(attendance)
            
        db.session.commit()
        print("Update complete.")

if __name__ == "__main__":
    update_student_data()

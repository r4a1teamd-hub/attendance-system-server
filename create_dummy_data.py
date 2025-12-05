from app import create_app, db
from app.models import User, Attendance
from datetime import datetime
import random

app = create_app()

def create_dummy_data():
    with app.app_context():
        # Create 10 dummy students
        for i in range(1, 11):
            student_id = f"2024{i:04d}"
            username = f"Student {i}"
            email = f"student{i}@school.edu"
            
            user = User.query.filter_by(student_id=student_id).first()
            if not user:
                print(f"Creating user {username}...")
                user = User(
                    student_id=student_id,
                    username=username,
                    email=email,
                    role=0
                )
                user.set_password("password")
                db.session.add(user)
            else:
                print(f"User {username} already exists.")
            
            # Create attendance record for today (randomly)
            # 70% present, 10% late, 10% absent (record exists but status absent), 10% unrecorded (no record)
            rand = random.random()
            
            # Check if attendance already exists for today
            # Simplified check: just check if any attendance exists for this user today
            # For this script, we'll just add if not exists to avoid duplicates on re-run
            existing_attendance = Attendance.query.filter_by(user_id=user.id).filter(Attendance.timestamp >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).first()
            
            if not existing_attendance:
                status = None
                if rand < 0.7:
                    status = 'present'
                elif rand < 0.8:
                    status = 'late'
                elif rand < 0.9:
                    status = 'absent'
                # else: unrecorded (no record created)
                
                if status:
                    print(f"  Creating attendance for {username}: {status}")
                    attendance = Attendance(
                        user_id=user.id if user.id else 0, # user.id might be None before commit if new? No, session.add should handle it but let's commit users first
                        timestamp=datetime.now(),
                        status=status,
                        recorded_by='script'
                    )
                    # We need user.id, so let's commit users first
        
        db.session.commit()
        
        # Now add attendance
        for i in range(1, 11):
            student_id = f"2024{i:04d}"
            user = User.query.filter_by(student_id=student_id).first()
            
            existing_attendance = Attendance.query.filter_by(user_id=user.id).filter(Attendance.timestamp >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).first()
            
            if not existing_attendance:
                rand = random.random()
                status = None
                if rand < 0.7:
                    status = 'present'
                elif rand < 0.8:
                    status = 'late'
                elif rand < 0.9:
                    status = 'absent'
                
                if status:
                    attendance = Attendance(
                        user_id=user.id,
                        timestamp=datetime.now(),
                        status=status,
                        recorded_by='script'
                    )
                    db.session.add(attendance)
        
        db.session.commit()
        print("Dummy data created successfully.")

if __name__ == "__main__":
    create_dummy_data()

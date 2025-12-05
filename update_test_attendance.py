from app import create_app, db
from app.models import User, Attendance
from datetime import datetime, timedelta
import random

app = create_app()

def update_test_attendance():
    with app.app_context():
        student_id = "TEST_STUDENT_01"
        user = User.query.filter_by(student_id=student_id).first()
        
        if not user:
            print(f"User {student_id} not found. Please run setup_test_user.py first.")
            return

        print(f"Adding 25 absent records for {user.username} ({user.student_id})...")
        
        # 過去30日間の日付を使って25件の欠席データを生成
        base_date = datetime.now()
        for i in range(25):
            # 日付を少しずつずらす
            timestamp = base_date - timedelta(days=i+1)
            # 時間をランダムに設定 (9:00 - 10:30)
            timestamp = timestamp.replace(hour=9, minute=random.randint(0, 30))
            
            attendance = Attendance(
                user_id=user.id,
                status='absent',
                recorded_by='admin_script',
                timestamp=timestamp
            )
            db.session.add(attendance)
        
        db.session.commit()
        print(f"Successfully added 25 absent records for {student_id}.")

if __name__ == "__main__":
    update_test_attendance()

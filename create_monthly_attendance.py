from app import create_app, db
from app.models import User, Attendance
from datetime import datetime, timedelta
import random

app = create_app()

def create_monthly_data():
    with app.app_context():
        print("Generating monthly attendance data...")
        
        # 今月の日付範囲を取得
        now = datetime.now()
        year = now.year
        month = now.month
        
        # 月の初日
        start_date = datetime(year, month, 1)
        # 今日まで（未来のデータは作らない）
        end_date = now
        
        students = User.query.filter_by(role=0).all()
        
        for student in students:
            print(f"Processing {student.username}...")
            
            current_day = start_date
            while current_day <= end_date:
                # 土日はスキップ (0:月, 6:日)
                if current_day.weekday() >= 5:
                    current_day += timedelta(days=1)
                    continue
                
                # 既存のデータがあるか確認
                existing = Attendance.query.filter(
                    Attendance.user_id == student.id,
                    db.func.date(Attendance.timestamp) == current_day.date()
                ).first()
                
                if not existing:
                    # ランダムにステータスを決定
                    rand = random.random()
                    status = 'present'
                    if rand < 0.1: # 10% 欠席
                        status = 'absent'
                    elif rand < 0.2: # 10% 遅刻
                        status = 'late'
                    
                    # 時間設定
                    hour = 9
                    minute = random.randint(0, 59)
                    if status == 'late':
                        minute = random.randint(15, 59) # 遅刻っぽい時間
                    
                    timestamp = current_day.replace(hour=hour, minute=minute)
                    
                    attendance = Attendance(
                        user_id=student.id,
                        status=status,
                        recorded_by='script',
                        timestamp=timestamp
                    )
                    db.session.add(attendance)
                
                current_day += timedelta(days=1)
        
        db.session.commit()
        print("Monthly data generation complete.")

if __name__ == "__main__":
    create_monthly_data()

from app import create_app, db
from app.models import User, Attendance

app = create_app()

def cleanup_users():
    with app.app_context():
        # Keep admin and TEST_STUDENT_01 (optional, user asked to remove others)
        # User asked: "TEST_STUDENT_01以外を削除しよう" -> So keep TEST_STUDENT_01 and Admin
        # Wait, usually admin is 00001111. TEST_STUDENT_01 is 20240001.
        
        # Get all users
        users = User.query.all()
        
        deleted_count = 0
        
        for user in users:
            # Skip Admin (role=1) and TEST_STUDENT_01
            if user.role == 1:
                print(f"Skipping Admin user: {user.username} ({user.student_id})")
                continue
                
            if user.student_id == "20240001": # TEST_STUDENT_01
                print(f"Skipping Test Student: {user.username} ({user.student_id})")
                continue
            
            # Delete associated attendance records first (though cascade might handle it, explicitly is safer)
            Attendance.query.filter_by(user_id=user.id).delete()
            
            # Delete user
            print(f"Deleting user: {user.username} ({user.student_id})")
            db.session.delete(user)
            deleted_count += 1
            
        db.session.commit()
        print(f"Cleanup complete. Deleted {deleted_count} users and their attendance records.")

if __name__ == "__main__":
    confirm = input("Are you sure you want to delete all users except Admin and TEST_STUDENT_01? (yes/no): ")
    if confirm.lower() == 'yes':
        cleanup_users()
    else:
        print("Cancelled.")

from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # Check if test user exists
    user = User.query.filter_by(student_id='99999999').first()
    if user:
        print("User 99999999 already exists. Updating password...")
        user.set_password('password123')
    else:
        print("Creating user 99999999...")
        user = User(student_id='99999999', username='Test Mobile User', email='test_mobile@example.com')
        user.set_password('password123')
        db.session.add(user)
    
    db.session.commit()
    print("Test user 99999999 ready with password 'password123'.")

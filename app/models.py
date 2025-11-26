from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(64), index=True, unique=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    # role: 0 for student, 1 for teacher
    role = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<User {self.username}>'
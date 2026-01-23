from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(64), index=True, unique=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    # role: 0 は学生、1 は教員
    role = db.Column(db.Integer, default=0) # 0: Student, 1: Teacher
    is_password_changed = db.Column(db.Boolean, default=False)
    last_login_at = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    status = db.Column(db.String(20)) # 'present' (出席), 'late' (遅刻), 'absent' (欠席)
    period = db.Column(db.Integer) # 1, 2, 3, 4
    recorded_by = db.Column(db.String(64)) # 例: 'raspi_01'

    user = db.relationship('User', backref=db.backref('attendances', lazy=True))

    def __repr__(self):
        return f'<Attendance {self.user_id} {self.timestamp} {self.status}>'

class SystemSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), index=True, unique=True) # e.g. 'warning_threshold'
    value = db.Column(db.String(256)) # e.g. '20'

    def __repr__(self):
        return f'<SystemSetting {self.key}: {self.value}>'
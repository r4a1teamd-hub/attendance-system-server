from flask import Blueprint, request, jsonify, current_app, g
from app import db, mail
from app.models import User, Attendance
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask_mail import Message

bp = Blueprint('main', __name__)

# トークンを検証し、リクエストのコンテキストにユーザー情報を付与するデコレータ
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers and request.headers['Authorization'].startswith('Bearer '):
            token = request.headers['Authorization'].split(' ')[1]

        if not token:
            print("DEBUG: Token missing in header")
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            print(f"DEBUG: Received token: {token}")
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            print(f"DEBUG: Decoded data: {data}")
            g.current_user = User.query.get(data['sub'])
        except jwt.ExpiredSignatureError:
            print("DEBUG: Token expired")
            return jsonify({'message': 'Token is invalid or expired!'}), 401
        except jwt.InvalidTokenError as e:
            print(f"DEBUG: Invalid token error: {e}")
            return jsonify({'message': 'Token is invalid or expired!'}), 401
        except Exception as e:
            print(f"DEBUG: Unexpected error in token decode: {e}")
            return jsonify({'message': 'Token is invalid or expired!'}), 401
        return f(*args, **kwargs)
    return decorated

@bp.route('/api/register', methods=['POST'])
def register():
    # 1. POSTリクエストのJSONボディからデータを取得
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    student_id = data.get('student_id')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # 2. 必須項目が揃っているかチェック
    if not all([student_id, username, email, password]):
        return jsonify({"error": "Missing data"}), 400

    # 3. ユーザー名やメールアドレスが既に使われていないかチェック
    if User.query.filter_by(student_id=student_id).first():
        return jsonify({"error": "Student ID already registered"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    # 4. 新しいユーザーを作成してデータベースに保存
    new_user = User(student_id=student_id, username=username, email=email)
    new_user.set_password(password) # パスワードをハッシュ化して設定
    db.session.add(new_user)
    db.session.commit()

    # 5. 成功レスポンスを返す
    return jsonify({"message": "User registered successfully!", "user_id": new_user.id}), 201

@bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    student_id = data.get('student_id')
    password = data.get('password')

    if not student_id or not password:
        return jsonify({"error": "Missing student ID or password"}), 400

    # 1. 学籍番号でユーザーを検索
    user = User.query.filter_by(student_id=student_id).first()

    # 2. ユーザーが存在し、かつパスワードが正しいかチェック
    if user is None or not user.check_password(password):
        return jsonify({"error": "Invalid student ID or password"}), 401 # 401 Unauthorized

    # 3. JWT（アクセストークン）を生成
    token = jwt.encode({
        'sub': str(user.id), # トークンの主体 (subject) としてユーザーIDを格納 (文字列である必要がある)
        'iat': datetime.now(timezone.utc), # トークンの発行時刻
        'exp': datetime.now(timezone.utc) + timedelta(hours=24) # トークンの有効期限 (ここでは24時間)
    }, current_app.config['SECRET_KEY'], algorithm='HS256')

    # 4. トークンをクライアントに返す
    return jsonify({'token': token})

@bp.route('/api/me', methods=['GET'])
@token_required
def get_current_user():
    # @token_required デコレータによって g.current_user にユーザーオブジェクトがセットされている
    user = g.current_user
    return jsonify({
        'id': user.id,
        'student_id': user.student_id,
        'username': user.username,
        'email': user.email,
        'role': user.role
    })

@bp.route('/api/record_attendance', methods=['POST'])
def record_attendance():
    # 1. Try API Key authentication (for Raspberry Pi)
    auth_success = False
    recorded_by = 'raspi_unknown'
    token_user = None

    api_key = request.headers.get('X-API-KEY')
    if api_key and api_key == current_app.config['RASPBERRY_PI_API_KEY']:
        auth_success = True
        recorded_by = request.get_json().get('recorded_by', 'raspi_client')
    
    # 2. If API Key fails, try JWT authentication (for Mobile App)
    if not auth_success:
        token = None
        if 'Authorization' in request.headers and request.headers['Authorization'].startswith('Bearer '):
            token = request.headers['Authorization'].split(' ')[1]
        
        if token:
            try:
                data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
                token_user = User.query.get(data['sub'])
                if token_user:
                    auth_success = True
                    recorded_by = 'mobile_app'
            except:
                pass # JWT invalid or expired

    if not auth_success:
        return jsonify({'error': 'Unauthorized'}), 401

    # Main logic
    data = request.get_json()
    student_id = data.get('student_id')
    status = data.get('status', 'present')
    
    # If authenticated via JWT, use the logged-in user's student_id if not provided
    if token_user and not student_id:
        student_id = token_user.student_id

    if not student_id:
        return jsonify({'error': 'Missing student_id'}), 400

    user = User.query.filter_by(student_id=student_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    # Security check: If using JWT, ensure users can only record their own attendance (optional, depending on requirements)
    # For now, we allow it if they are authenticated.

    # Create record
    attendance = Attendance(user_id=user.id, status=status, recorded_by=recorded_by)
    db.session.add(attendance)
    db.session.commit()

    return jsonify({'message': 'Attendance recorded', 'id': attendance.id}), 201

@bp.route('/api/attendance/me', methods=['GET'])
@token_required
def get_my_attendance():
    user = g.current_user
    attendances = Attendance.query.filter_by(user_id=user.id).order_by(Attendance.timestamp.desc()).all()
    
    results = []
    for att in attendances:
        results.append({
            'id': att.id,
            'timestamp': att.timestamp.isoformat(),
            'status': att.status,
            'recorded_by': att.recorded_by
        })
    
    return jsonify(results)

@bp.route('/api/admin/attendance', methods=['GET'])
@token_required
def get_all_attendance():
    user = g.current_user
    if user.role != 1: # 1 は教員
        return jsonify({'error': 'Unauthorized'}), 403

    attendances = Attendance.query.order_by(Attendance.timestamp.desc()).all()
    results = []
    for att in attendances:
        results.append({
            'id': att.id,
            'student_id': att.user.student_id,
            'username': att.user.username,
            'timestamp': att.timestamp.isoformat(),
            'status': att.status,
            'recorded_by': att.recorded_by
        })
    return jsonify(results)

# Aliases for compatibility
@bp.route('/api/user/profile', methods=['GET'])
@token_required
def get_user_profile_alias():
    return get_current_user()

@bp.route('/api/attendance/history', methods=['GET'])
@token_required
def get_attendance_history_alias():
    return get_my_attendance()

@bp.route('/api/admin/send_warning', methods=['POST'])
@token_required
def send_warning():
    user = g.current_user
    if user.role != 1:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    target_user_id = data.get('user_id')
    
    target_user = User.query.get(target_user_id)
    if not target_user:
        return jsonify({'error': 'User not found'}), 404

    # 欠席回数を取得
    absent_count = Attendance.query.filter_by(user_id=target_user.id, status='absent').count()

    # メール送信処理
    try:
        msg = Message("【重要】出席状況に関する警告",
                      recipients=[target_user.email])
        msg.body = f"""
{target_user.username} (学籍番号: {target_user.student_id}) 様

あなたの出席状況について、欠席回数が規定を超えています。
現在の欠席回数: {absent_count}回

至急、教務課まで連絡してください。

※このメールは自動送信されています。
"""
        mail.send(msg)
        print(f"WARNING EMAIL SENT TO: {target_user.email} for Student {target_user.student_id}")
        return jsonify({'message': f'Warning sent to {target_user.email}'})
    except Exception as e:
        print(f"ERROR sending email: {e}")
        return jsonify({'error': 'Failed to send email', 'details': str(e)}), 500

@bp.route('/api/admin/users', methods=['GET'])
@token_required
def get_all_users():
    user = g.current_user
    if user.role != 1:
        return jsonify({'error': 'Unauthorized'}), 403

    users = User.query.all()
    results = []
    for u in users:
        results.append({
            'id': u.id,
            'student_id': u.student_id,
            'username': u.username,
            'email': u.email,
            'role': u.role
        })
    return jsonify(results)

@bp.route('/api/admin/stats', methods=['GET'])
@token_required
def get_stats():
    user = g.current_user
    if user.role != 1:
        return jsonify({'error': 'Unauthorized'}), 403

    students = User.query.filter_by(role=0).all()
    stats = []
    for student in students:
        attendances = Attendance.query.filter_by(user_id=student.id).all()
        present = sum(1 for a in attendances if a.status == 'present')
        late = sum(1 for a in attendances if a.status == 'late')
        absent = sum(1 for a in attendances if a.status == 'absent')
        
        # 欠席回数が20回以上かどうか
        warning_level = 'high' if absent >= 20 else 'normal'
        
        stats.append({
            'id': student.id,
            'student_id': student.student_id,
            'username': student.username,
            'email': student.email,
            'present': present,
            'late': late,
            'absent': absent,
            'warning_level': warning_level
        })
    
    return jsonify(stats)

@bp.route('/api/admin/daily_stats', methods=['GET'])
@token_required
def get_daily_stats():
    user = g.current_user
    if user.role != 1:
        return jsonify({'error': 'Unauthorized'}), 403

    today = datetime.now().date()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())

    attendances = Attendance.query.filter(
        Attendance.timestamp >= start_of_day,
        Attendance.timestamp <= end_of_day
    ).all()

    present = sum(1 for a in attendances if a.status == 'present')
    late = sum(1 for a in attendances if a.status == 'late')
    absent = sum(1 for a in attendances if a.status == 'absent')
    
    # 登録されている全学生数を取得（分母用）
    total_students = User.query.filter_by(role=0).count()
    
    # まだ記録がない学生は「未記録」扱いだが、ここでは単純なカウントを返す
    # 必要であれば「未記録」の数も計算可能: total_students - (present + late + absent)

    return jsonify({
        'date': today.isoformat(),
        'total_students': total_students,
        'present': present,
        'late': late,
        'absent': absent
    })

@bp.route('/api/admin/monthly_attendance', methods=['GET'])
@token_required
def get_monthly_attendance():
    user = g.current_user
    if user.role != 1:
        return jsonify({'error': 'Unauthorized'}), 403

    year = request.args.get('year', type=int, default=datetime.now().year)
    month = request.args.get('month', type=int, default=datetime.now().month)

    # 月の初日と末日を計算
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)

    students = User.query.filter_by(role=0).all()
    results = []

    for student in students:
        attendances = Attendance.query.filter(
            Attendance.user_id == student.id,
            Attendance.timestamp >= start_date,
            Attendance.timestamp <= end_date
        ).all()

        # 日付ごとのステータスマップを作成 (例: {1: 'present', 5: 'late'})
        daily_status = {}
        present_count = 0
        late_count = 0
        absent_count = 0

        for att in attendances:
            day = att.timestamp.day
            # 同日に複数記録がある場合は最新を採用するロジックなどが考えられるが、
            # ここではシンプルに上書き（または最初の1件）とする。
            # 実際には timestamp順で取得してループすれば最新が残る等の制御が可能
            daily_status[day] = att.status
            
            if att.status == 'present':
                present_count += 1
            elif att.status == 'late':
                late_count += 1
            elif att.status == 'absent':
                absent_count += 1

        results.append({
            'id': student.id,
            'student_id': student.student_id,
            'username': student.username,
            'summary': {
                'present': present_count,
                'late': late_count,
                'absent': absent_count
            },
            'daily_status': daily_status
        })

    return jsonify({
        'year': year,
        'month': month,
        'students': results
    })
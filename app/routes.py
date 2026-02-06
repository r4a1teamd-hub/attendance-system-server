from flask import Blueprint, request, jsonify, current_app, g
from app import db, mail
from app.models import User, Attendance, SystemSetting
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
            user = User.query.get(data['sub'])
            if not user:
                print("DEBUG: User not found (deleted?)")
                return jsonify({'message': 'User invalid!'}), 401
            g.current_user = user
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

    # Record last login time
    now = datetime.now(timezone.utc)
    user.last_login_at = now
    db.session.commit()

    # Generate token
    token = jwt.encode({
        'sub': f'{user.id}',
        'iat': datetime.now(timezone.utc),
        'exp': datetime.now(timezone.utc) + timedelta(hours=24)
    }, current_app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'token': token,
        'user': {
            'id': user.id,
            'student_id': user.student_id,
            'role': user.role,
            'is_password_changed': user.is_password_changed,
            'last_login_at': now.isoformat()
        },
        'server_time': now.isoformat()
    })

@bp.route('/api/admin/reset_password', methods=['POST'])
@token_required
def reset_password():
    user = g.current_user
    if user.role != 1:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    target_user_id = data.get('user_id')
    
    target_user = User.query.get(target_user_id)
    if not target_user:
        return jsonify({'error': 'User not found'}), 404

    # Reset password to student_id and set is_password_changed to False
    target_user.set_password(target_user.student_id)
    target_user.is_password_changed = False
    
    db.session.commit()
    
    return jsonify({'message': f'Password reset for student {target_user.student_id}'})

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

    # Time Slot Definitions
    # Format: (period, start_time_str, late_limit_str, attend_start_str)
    # attend_start: 20 mins before start_time
    # ... (existing content) ...

@bp.route('/api/qr_token', methods=['GET'])
@token_required
def get_qr_token():
    user = g.current_user
    
    # Generate a short-lived token (e.g., 5 minutes)
    # This token contains the user ID and is signed by the server
    expiration = datetime.now(timezone.utc) + timedelta(minutes=5)
    
    token_payload = {
        'sub': str(user.id),
        'type': 'qr_attendance',
        'exp': expiration,
        'iat': datetime.now(timezone.utc)
    }
    
    token = jwt.encode(token_payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'token': token,
        'expires_in': 300 # seconds
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
    print(f"DEBUG: record_attendance received data: {data}") # Add this debug line
    student_id = data.get('student_id')
    qr_token = data.get('qr_token')
    rfid_uid = data.get('rfid_uid')

    # Logic to handle RFID UID
    if rfid_uid:
        user = User.query.filter_by(rfid_uid=rfid_uid).first()
        if user:
            student_id = user.student_id
        else:
            return jsonify({'error': 'Registered card not found'}), 404

    # Logic to handle QR Token
    if qr_token:
        try:
            # Decode the QR token
            qr_data = jwt.decode(qr_token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            
            # Verify token type
            if qr_data.get('type') != 'qr_attendance':
                 return jsonify({'error': 'Invalid token type'}), 400
            
            # Extract user ID from token
            user_id = qr_data['sub']
            user = User.query.get(user_id)
            
            if not user:
                 return jsonify({'error': 'User not found from token'}), 404
                 
            student_id = user.student_id
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'QR Token expired'}), 400
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid QR Token'}), 400
        except Exception as e:
            return jsonify({'error': f'Error processing QR token: {str(e)}'}), 500

    if not student_id:
         return jsonify({'error': 'Missing student_id, rfid_uid or valid qr_token'}), 400
    
    # Determine status based on current time (JST)
    now_utc = datetime.now(timezone.utc)
    jst_offset = timedelta(hours=9)
    now_jst = now_utc + jst_offset
    current_time = now_jst.time()
    current_date_str = now_jst.strftime('%Y/%m/%d')
    current_time_str = now_jst.strftime('%H:%M')

    # Time Slot Definitions
    # Format: (period, start_time_str, late_limit_str, attend_start_str)
    # attend_start: 20 mins before start_time
    time_slots = [
        (1, "09:15", "09:45", "08:55"),
        (2, "11:00", "11:30", "10:40"),
        (3, "13:30", "14:00", "13:10"),
        (4, "15:15", "15:45", "14:55")
    ]

    detected_period = None
    detected_status = None

    for period, start_str, late_limit_str, attend_start_str in time_slots:
        start_t = datetime.strptime(start_str, "%H:%M").time()
        late_limit_t = datetime.strptime(late_limit_str, "%H:%M").time()
        attend_start_t = datetime.strptime(attend_start_str, "%H:%M").time()

        # Check Present range: Attend Start <= t <= Start Time
        # Note: Spec says "Until start time exactly (09:15:00) is present"
        # So: attend_start <= t <= start_t
        if attend_start_t <= current_time <= start_t:
            detected_period = period
            detected_status = 'present'
            break
        
        # Check Late range: Start Time < t <= Late Limit
        # 09:15:01 ...
        if start_t < current_time <= late_limit_t:
            detected_period = period
            detected_status = 'late'
            break

    if not detected_period:
        # Secondary Check: "Gap Time" -> Absent for previous period
        # Example: 09:50 is after Period 1 Late Limit (09:45) and before Period 2 Start (10:40)
        # We record this as "Period 1: Absent"
        for period, start_str, late_limit_str, attend_start_str in time_slots:
            late_limit_t = datetime.strptime(late_limit_str, "%H:%M").time()
            
            # Find next period's start time to define the "gap" end
            # If it's the last period, the gap might be undefined or up to end of day?
            # For simplicity, we just check if it's AFTER the late limit of Period N.
            # And to avoid overriding specific period logic, we must ensure it doesn't overlap with next period's attedance start.
            
            # Logic: If current_time > late_limit_t AND current_time < next_period_attend_start
            
            next_period_start = None
            if period < len(time_slots): # Periods are 1-based, index 0 to 3
                # Get Attend Start of next period
                next_p_idx = period # period is 1-based, so this gets index of next
                _, _, _, next_attend_start_str = time_slots[next_p_idx]
                next_period_start = datetime.strptime(next_attend_start_str, "%H:%M").time()
            
            # Condition: After Late Limit
            if current_time > late_limit_t:
                # And Before Next Period (if exists)
                if next_period_start and current_time < next_period_start:
                    detected_period = period
                    detected_status = 'absent'
                    break
                elif not next_period_start:
                    # After last period's late limit -> Absent for last period
                     # (Optional: limit this to some reasonable time, e.g. 18:00?)
                    detected_period = period
                    detected_status = 'absent'
                    break

    if not detected_period:
        return jsonify({'message': '現在、出席受付時間外です'}), 400

    # If authenticated via JWT, use the logged-in user's student_id if not provided
    if token_user and not student_id:
        student_id = token_user.student_id

    if not student_id:
        return jsonify({'error': 'Missing student_id'}), 400

    user = User.query.filter_by(student_id=student_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Check for duplicate attendance for this PERIOD today (JST)
    start_of_day_jst = now_jst.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_day_utc = start_of_day_jst - jst_offset
    
    existing_attendance = Attendance.query.filter_by(user_id=user.id, period=detected_period).filter(Attendance.timestamp >= start_of_day_utc).first()
    
    if existing_attendance:
        return jsonify({
            'message': '既に登録済みです',
            'data': {
                'date': current_date_str,
                'time': current_time_str,
                'period': existing_attendance.period,
                'status': existing_attendance.status
            }
        }), 200

    # Create record
    attendance = Attendance(
        user_id=user.id, 
        status=detected_status, 
        period=detected_period,
        recorded_by=recorded_by
    )
    db.session.add(attendance)
    db.session.commit()

    return jsonify({
        'message': 'Attendance recorded',
        'data': {
            'date': current_date_str,
            'time': current_time_str,
            'period': detected_period,
            'status': detected_status
        }
    }), 201

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
                      recipients=[target_user.email],
                      charset='utf-8')
        msg.body = f"""
{target_user.username} (学籍番号: {target_user.student_id}) 様

あなたの出席状況について、欠席回数が規定を超えています。
現在の欠席回数: {absent_count}回

至急、教務課まで連絡してください。

※このメールは自動送信されています。
"""
        mail.send(msg)
        try:
            print(f"WARNING EMAIL SENT TO: {target_user.email} for Student {target_user.student_id}")
        except UnicodeEncodeError:
            print(f"WARNING EMAIL SENT TO: {target_user.email} (Name printing failed due to encoding)")
        return jsonify({'message': f'Warning sent to {target_user.email}'})
    except Exception as e:
        print(f"ERROR sending email: {e}")
        return jsonify({'error': 'Failed to send email', 'details': str(e)}), 500

@bp.route('/api/admin/users', methods=['GET', 'POST'])
@token_required
def manage_users():
    user = g.current_user
    if user.role != 1:
        return jsonify({'error': 'Unauthorized'}), 403

    if request.method == 'GET':
        users = User.query.all()
        results = []
        for u in users:
            results.append({
                'id': u.id,
                'student_id': u.student_id,
                'username': u.username,
                'email': u.email,
                'role': u.role,
                'rfid_uid': u.rfid_uid
            })
        return jsonify(results)

    elif request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid input'}), 400

        student_id = data.get('student_id')
        username = data.get('username')
        email = data.get('email')

        if not all([student_id, username, email]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Check for duplicates
        if User.query.filter_by(student_id=student_id).first():
            return jsonify({'error': 'Student ID already registered'}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400

        # Create new user
        # Default password is the student_id
        new_user = User(student_id=student_id, username=username, email=email)
        new_user.set_password(student_id) 
        
        try:
            db.session.add(new_user)
            db.session.commit()
            return jsonify({'message': 'User created successfully', 'user': {
                'id': new_user.id,
                'student_id': new_user.student_id,
                'username': new_user.username,
                'email': new_user.email
            }}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

@bp.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(user_id):
    user = g.current_user
    if user.role != 1:
        return jsonify({'error': 'Unauthorized'}), 403

    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({'error': 'User not found'}), 404
        
    if target_user.id == user.id:
         return jsonify({'error': 'Cannot delete yourself'}), 400

    try:
        # Delete associated attendance records first
        Attendance.query.filter_by(user_id=user_id).delete()
        
        # Delete the user
        db.session.delete(target_user)
        db.session.commit()
        return jsonify({'message': f'User {target_user.student_id} deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/api/admin/stats', methods=['GET'])
@token_required
def get_stats():
    user = g.current_user
    if user.role != 1:
        return jsonify({'error': 'Unauthorized'}), 403

    # Get warning threshold from settings (default to 20)
    setting = SystemSetting.query.filter_by(key='warning_threshold').first()
    try:
        threshold = int(setting.value) if setting else 20
    except ValueError:
        threshold = 20

    students = User.query.filter_by(role=0).all()
    stats = []
    for student in students:
        attendances = Attendance.query.filter_by(user_id=student.id).all()
        present = sum(1 for a in attendances if a.status == 'present')
        late = sum(1 for a in attendances if a.status == 'late')
        absent = sum(1 for a in attendances if a.status == 'absent')
        
        # Determine warning level based on dynamic threshold
        warning_level = 'high' if absent >= threshold else 'normal'
        
        stats.append({
            'id': student.id,
            'student_id': student.student_id,
            'username': student.username,
            'email': student.email,
            'present': present,
            'late': late,
            'absent': absent,
            'warning_level': warning_level,
            'threshold': threshold # Optional: return threshold for frontend info
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
    
    # Calculate unique users who have ANY record today (meaning they arrived at school)
    # This includes 'present', 'late', and even 'absent' (if we recorded 'absent' for P1 but they are here)
    # Wait, if they only have 'absent' record (e.g. came late for P1), are they "Arrived"?
    # Yes, because the system detected them. "Truly Absent" means no detection at all.
    arrived_user_ids = set(a.user_id for a in attendances)
    arrived_count = len(arrived_user_ids)

    return jsonify({
        'date': today.isoformat(),
        'total_students': total_students,
        'present': present,
        'late': late,
        'absent': absent,
        'arrived_count': arrived_count
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

        # 日付ごとのステータスマップを作成 (例: {1: [{'period': 1, 'status': 'present'}, ...]})
        daily_status = {}
        present_count = 0
        late_count = 0
        absent_count = 0

        for att in attendances:
            day = att.timestamp.day
            
            if day not in daily_status:
                daily_status[day] = []
            
            # Store period and status for detailed display
            daily_status[day].append({
                'period': att.period,
                'status': att.status
            })
            
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

@bp.route('/api/admin/system_settings', methods=['GET', 'POST'])
@token_required
def system_settings():
    user = g.current_user
    if user.role != 1:
        return jsonify({'error': 'Unauthorized'}), 403

    from app.models import SystemSetting

    if request.method == 'GET':
        settings = SystemSetting.query.all()
        result = {}
        for s in settings:
            result[s.key] = s.value
        
        # Default values if not present
        if 'warning_threshold' not in result:
            result['warning_threshold'] = '20'
            
        return jsonify(result)
    
    elif request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        try:
            for key, value in data.items():
                setting = SystemSetting.query.filter_by(key=key).first()
                if setting:
                    setting.value = str(value)
                else:
                    setting = SystemSetting(key=key, value=str(value))
                    db.session.add(setting)
            
            db.session.commit()
            return jsonify({'message': 'Settings updated successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

@bp.route('/api/admin/export_csv', methods=['GET'])
@token_required
def export_csv():
    user = g.current_user
    if user.role != 1:
        return jsonify({'error': 'Unauthorized'}), 403

    import csv
    import io
    from flask import make_response

    # Query all attendance records sorted by timestamp
    attendances = Attendance.query.order_by(Attendance.timestamp.desc()).all()

    # Create CSV in memory
    si = io.StringIO()
    cw = csv.writer(si)
    
    # Header
    cw.writerow(['ID', 'Student ID', 'Name', 'Date', 'Time', 'Status', 'Recorded By'])
    
    # Data
    for att in attendances:
        cw.writerow([
            att.id,
            att.user.student_id,
            att.user.username,
            att.timestamp.strftime('%Y-%m-%d'),
            att.timestamp.strftime('%H:%M:%S'),
            att.status,
            att.recorded_by
        ])
    
    output = si.getvalue()
    
    # Create response with CSV file
    response = make_response(output)
    response.headers["Content-Disposition"] = "attachment; filename=attendance_export.csv"
    response.headers["Content-type"] = "text/csv"
    
    return response

@bp.route('/api/change_password', methods=['POST'])
@token_required
def change_password():
    user = g.current_user
    
    # Allow any user to change their own password
    # data: { current_password, new_password }
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Missing password fields'}), 400
        
    # Verify current password
    if not user.check_password(current_password):
        return jsonify({'error': 'Current password is incorrect'}), 401
        
    # Set new password and mark as changed
    user.set_password(new_password)
    user.is_password_changed = True
    db.session.commit()
    
    return jsonify({'message': 'Password updated successfully'})

@bp.route('/api/admin/users/<int:user_id>/rfid', methods=['POST'])
@token_required
def register_user_rfid(user_id):
    user = g.current_user
    if user.role != 1:
        return jsonify({'error': 'Unauthorized'}), 403

    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    rfid_uid = data.get('rfid_uid')

    if not rfid_uid:
        return jsonify({'error': 'Missing rfid_uid'}), 400

    # Check if this RFID is already registered to SOMEONE ELSE
    existing_user = User.query.filter_by(rfid_uid=rfid_uid).first()
    if existing_user and existing_user.id != target_user.id:
        return jsonify({'error': f'This card is already registered to user {existing_user.student_id}'}), 400

    target_user.rfid_uid = rfid_uid
    try:
        db.session.commit()
        return jsonify({'message': f'RFID registered for {target_user.student_id}'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
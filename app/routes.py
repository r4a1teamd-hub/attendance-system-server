from flask import Blueprint

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return "Attendance System Server is running!"
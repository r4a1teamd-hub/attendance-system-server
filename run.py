from dotenv import load_dotenv
import os

load_dotenv()
print(f"DEBUG: MAIL_USERNAME from env: {os.environ.get('MAIL_USERNAME')}")

from app import create_app, db, migrate
from app.models import User

app = create_app()

if __name__ == '__main__':
    # host='0.0.0.0' allows access from other devices on the same network
    app.run(host='0.0.0.0', port=5000, debug=True)
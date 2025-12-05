from dotenv import load_dotenv
import os

load_dotenv()
print(f"DEBUG: MAIL_USERNAME from env: {os.environ.get('MAIL_USERNAME')}")

from app import create_app, db, migrate
from app.models import User

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
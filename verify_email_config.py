import os
from dotenv import load_dotenv

load_dotenv()

password = os.environ.get('MAIL_PASSWORD')
email = os.environ.get('MAIL_USERNAME')

print(f"Checking configuration for: {email}")

if not password:
    print("ERROR: MAIL_PASSWORD is not set.")
else:
    print(f"Password length: {len(password)}")
    if len(password) != 16:
        print("WARNING: Password length is not 16 characters.")
        print("Google App Passwords are typically 16 characters long.")
        print("If you are using your regular Google account password, it will NOT work.")
        print("Please generate an App Password from your Google Account settings.")
    else:
        print("Password length looks correct for an App Password.")
        print("If it still fails, please check if the password is correct or if 2FA is enabled.")

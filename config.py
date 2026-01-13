import os

class Config:
    # JWTの署名に使うシークレットキー。本番環境では必ず環境変数から読み込むこと
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-secret-string-for-jwt'

    # PostgreSQLへの接続URI。環境変数から取得するか、デフォルト値（SQLite）を使用
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    #     'postgresql://vscode:vscode@localhost:5432/vscode'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')
    
    # Raspberry Pi API Key
    RASPBERRY_PI_API_KEY = os.environ.get('RASPBERRY_PI_API_KEY') or 'default-insecure-api-key'
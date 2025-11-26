import os

class Config:
    # PostgreSQLへの接続URI。環境変数から取得するか、デフォルト値を使用
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://vscode:vscode@localhost:5432/vscode'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
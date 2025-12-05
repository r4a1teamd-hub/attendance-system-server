# 出席管理システム 実行ガイド

このドキュメントでは、出席管理システムの各コンポーネントの実行と検証方法について説明します。

## 前提条件

- Python 3.x
- Node.js & npm
- Expo Go アプリ (モバイルテスト用)

## 1. バックエンドサーバー

バックエンドはデータベースとAPIを管理します。

1. **サーバーの起動**:
    `attendance-system-server` ディレクトリでターミナルを開き、以下を実行します:

    ```bash
    python run.py
    ```

    サーバーが `http://127.0.0.1:5000` で起動します。

2. **データベースの確認**:
    データベース `app.db` は初期化され、必要なテーブル (`User`, `Attendance`) が作成されています。

## 2. 管理者用Webアプリ

管理者ダッシュボードでは、教員が出席状況を確認し、警告を送信できます。

1. **Webアプリの起動**:
    新しいターミナルを開き、`admin-client` ディレクトリに移動してから起動します:

    ```bash
    cd admin-client
    npm run dev
    ```

    ブラウザで表示されたURL（通常は `http://localhost:5173`）を開きます。

2. **テストフロー**:
    - **ログイン**: 教員の認証情報を使用します（APIまたはDB経由で事前に登録するか、登録エンドポイントを使用してください）。
    - **ダッシュボード**: 出席表を確認します。
    - **警告**: 欠席している学生に対して「警告送信」をクリックします。

## 3. 学生用モバイルアプリ

モバイルアプリでは、学生が自分の出席履歴を確認できます。

1. **モバイルアプリの起動**:
    新しいターミナルを開き、`mobile-client` ディレクトリに移動してから起動します:

    ```bash
    cd mobile-client
    npx expo start
    ```

    - スマートフォンの **Expo Go** アプリでQRコードをスキャンします (Android/iOS)。
    - または、Androidエミュレータなら `a`、iOSシミュレータなら `i` を押します。

2. **テストフロー**:
    - **ログイン**: 学籍番号とパスワードを入力します。
    - **ダッシュボード**: 自分の出席記録を確認します。

## 4. Raspberry Pi シミュレーション

Raspberry Piからの出席データ送信をシミュレートするには:

1. **出席記録の送信**:
    `curl` または Postman を使用して POST リクエストを送信します:

    ```bash
    curl -X POST http://127.0.0.1:5000/api/record_attendance \
      -H "Content-Type: application/json" \
      -d '{"student_id": "student123", "status": "present", "recorded_by": "raspi_01"}'
    ```

## 5. テストユーザーの作成

DBは新規の状態なので、ユーザーが必要です。API経由で登録できます:

```bash
# 学生の登録
curl -X POST http://127.0.0.1:5000/register \
  -H "Content-Type: application/json" \
  -d '{"student_id": "student123", "username": "John Doe", "email": "john@example.com", "password": "password"}'

# 教員の登録 (Role=1 は手動でのDB更新または専用エンドポイントが必要ですが、現時点では学生として登録後にDBを更新します)
# Pythonシェル:
# >>> from app import db
# >>> from app.models import User
# >>> u = User.query.filter_by(username='Teacher').first()
# >>> u.role = 1
# >>> db.session.commit()
```

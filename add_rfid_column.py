import sqlite3
import os

# Database path
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if column exists
cursor.execute("PRAGMA table_info(user)")
columns = [info[1] for info in cursor.fetchall()]

if 'rfid_uid' in columns:
    print("Column 'rfid_uid' already exists.")
else:
    print("Adding 'rfid_uid' column...")
    try:
        # Add column
        cursor.execute("ALTER TABLE user ADD COLUMN rfid_uid VARCHAR(64)")
        # Create index (SQLite doesn't strictly need explicit CREATE INDEX for unique constraint in ALTER TABLE usually, 
        # but SQLAlchemy models define it. We'll add a simple index manually if needed or just let it be)
        # Adding a unique index
        cursor.execute("CREATE UNIQUE INDEX ix_user_rfid_uid ON user (rfid_uid)")
        
        conn.commit()
        print("Success: 'rfid_uid' column added.")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()

conn.close()

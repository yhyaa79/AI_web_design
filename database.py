# database.py
import mysql.connector
from config import DATABASE_CONFIG, DATABASE_NAME

def create_database_if_not_exists():
    try:
        conn = mysql.connector.connect(**{k: v for k, v in DATABASE_CONFIG.items() if k != 'database'})
        cursor = conn.cursor()

        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DATABASE_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE `{DATABASE_NAME}`")

        # ساخت جدول users با تمام ستون‌ها
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ip_address VARCHAR(45) NOT NULL UNIQUE,
            username VARCHAR(50) NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            message_count INT DEFAULT 0,
            last_message_time DATETIME NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # اضافه کردن ستون‌ها اگر وجود نداشته باشند (این بخش مهم است!)
        cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS message_count INT DEFAULT 0")
        cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_message_time DATETIME NULL")

        # ساخت جدول messages
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            role ENUM('user', 'assistant') NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        conn.commit()
        print("دیتابیس و ستون‌های rate limit با موفقیت چک/به‌روزرسانی شدند.")

    except mysql.connector.Error as err:
        print(f"خطا در دیتابیس: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
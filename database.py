# database.py
import mysql.connector
from config import DATABASE_CONFIG, DATABASE_NAME

def create_database_if_not_exists():
    """اتصال به MySQL و ساخت دیتابیس + جداول اگر وجود نداشته باشن"""
    try:
        # اول بدون نام دیتابیس متصل می‌شیم
        conn = mysql.connector.connect(**{k: v for k, v in DATABASE_CONFIG.items() if k != 'database'})
        cursor = conn.cursor()

        # ساخت دیتابیس اگر وجود نداشته باشه
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DATABASE_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE `{DATABASE_NAME}`")

        # ساخت جدول کاربران
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ip_address VARCHAR(45) NOT NULL UNIQUE,      -- IPv4 یا IPv6
            username VARCHAR(50) NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # ساخت جدول پیام‌ها
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            role ENUM('user', 'assistant') NOT NULL,     -- کاربر یا AI
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        conn.commit()
        print(f"دیتابیس '{DATABASE_NAME}' و جداول با موفقیت ساخته یا بررسی شدند.")
        
    except mysql.connector.Error as err:
        print(f"خطا در اتصال یا ساخت دیتابیس: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
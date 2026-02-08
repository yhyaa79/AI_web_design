import os
from pathlib import Path
from datetime import datetime, timedelta
import zipfile
from io import BytesIO
import secrets
import string

PROJECTS_DIR = Path("user_projects")
PROJECTS_DIR.mkdir(exist_ok=True)

RATE_LIMIT_ENABLED = True
DAILY_LIMIT = 2
LIMIT_PERIOD = timedelta(days=1)

def get_user_folder(username):
    folder = PROJECTS_DIR / username
    folder.mkdir(exist_ok=True)
    return folder

def generate_username():
    random_part = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
    return f"Guest_{random_part}"

def extract_and_save_code(ai_response, username):
    """استخراج کد + برگرداندن فقط متن توضیحی برای نمایش در چت"""
    user_folder = get_user_folder(username)

    files_saved = []
    current_file = None
    current_content = []
    in_code_block = False

    text_parts = []  # فقط متن عادی (برای نمایش در چت)
    lines = ai_response.split("\n")

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_code_block:
                # پایان بلوک کد → ذخیره فایل
                if current_file:
                    file_path = user_folder / current_file
                    content_to_save = "\n".join(current_content).strip()
                    if content_to_save:  # فقط اگر محتوا داشت
                        file_path.write_text(content_to_save + "\n", encoding="utf-8")
                        files_saved.append(current_file)
                in_code_block = False
                current_file = None
                current_content = []
            else:
                # شروع بلوک کد
                in_code_block = True
                potential_filename = stripped[3:].strip()
                if potential_filename:
                    current_file = potential_filename
                else:
                    current_file = "unnamed.txt"
        elif in_code_block:
            current_content.append(line)
        else:
            # متن عادی → برای نمایش در چت
            text_parts.append(line)

    clean_text = "\n".join(text_parts).strip()
    if not clean_text:
        clean_text = "فایل‌های جدید با موفقیت ساخته/به‌روزرسانی شدند!"

    return clean_text, files_saved

# توابع دیگر مثل ایجاد فایل‌های پیش‌فرض برای کاربر جدید را هم اینجا بگذارید
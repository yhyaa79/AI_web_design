# app.py
from flask import Flask, render_template, request, jsonify, session
import mysql.connector
from config import DATABASE_CONFIG, DATABASE_NAME
from database import create_database_if_not_exists
from models import db, User, Message
import secrets
import string
from chat_bot import get_ai_response, SYSTEM_PROMPT

app = Flask(__name__)
app.secret_key = 'your_very_secret_key_here'  # حتماً تغییر بده


import os
from pathlib import Path

# مسیر اصلی ذخیره پروژه‌های کاربران
PROJECTS_DIR = Path("user_projects")
PROJECTS_DIR.mkdir(exist_ok=True)

def get_user_folder(username):
    """فولدر اختصاصی کاربر رو برگردون یا بساز"""
    user_folder = PROJECTS_DIR / username
    user_folder.mkdir(exist_ok=True)
    return user_folder

def extract_and_save_code(ai_response, username):
    """استخراج کد + برگرداندن فقط متن توضیحی برای نمایش در چت"""
    user_folder = get_user_folder(username)
    
    files_saved = []
    current_file = None
    current_content = []
    in_code_block = False

    text_parts = []  # فقط متن عادی (برای نمایش در چت)
    lines = ai_response.split('\n')

    for line in lines:
        stripped = line.strip()

        if stripped.startswith('```'):
            if in_code_block:
                # پایان بلوک کد → ذخیره فایل
                if current_file:
                    file_path = user_folder / current_file
                    content_to_save = '\n'.join(current_content).strip()
                    if content_to_save:  # فقط اگر محتوا داشت
                        file_path.write_text(content_to_save + '\n', encoding='utf-8')
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

    clean_text = '\n'.join(text_parts).strip()
    if not clean_text:
        clean_text = "فایل‌های جدید با موفقیت ساخته/به‌روزرسانی شدند!"

    return clean_text, files_saved


# تنظیمات SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+mysqlconnector://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}"
    f"@{DATABASE_CONFIG['host']}/{DATABASE_NAME}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ساخت دیتابیس در اولین اجرا
with app.app_context():
    create_database_if_not_exists()
    db.create_all()  # اگر جدول‌ها از قبل ساخته نشده باشن (backup)

def generate_username():
    """ساخت نام کاربری تصادفی مثل Guest_abcd1234"""
    random_part = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
    return f"Guest_{random_part}"

def get_or_create_user(ip):
    user = User.query.filter_by(ip_address=ip).first()
    if not user:
        username = generate_username()
        while User.query.filter_by(username=username).first():
            username = generate_username()
        
        user = User(ip_address=ip, username=username)
        db.session.add(user)
        db.session.commit()

        # ساخت فولدر و فایل‌های پیش‌فرض برای کاربر جدید
        user_folder = PROJECTS_DIR / username
        user_folder.mkdir(exist_ok=True)

        # فایل index.html پیش‌فرض
        (user_folder / "index.html").write_text("""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>سایت من</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>سلام! این سایت شما است</h1>
    <p>با هوش مصنوعی آن را طراحی کنید.</p>
    <script src="script.js"></script>
</body>
</html>""", encoding='utf-8')

        # فایل style.css پیش‌فرض
        (user_folder / "style.css").write_text("""body {
    font-family: 'Vazir', sans-serif;
    background: #f0f0f0;
    text-align: center;
    padding: 50px;
}

h1 {
    color: #333;
}""", encoding='utf-8')

        # فایل script.js پیش‌فرض
        (user_folder / "script.js").write_text("""console.log("سایت آماده است!");""", encoding='utf-8')

    return user

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message_text = data.get('message', '').strip()
    if not message_text:
        return jsonify({'error': 'پیام خالی است'}), 400

    ip = request.remote_addr
    user = get_or_create_user(ip)

    # ذخیره پیام کاربر
    user_msg = Message(user_id=user.id, role='user', content=message_text)
    db.session.add(user_msg)
    db.session.commit()

    # ساخت history
    messages = Message.query.filter_by(user_id=user.id).order_by(Message.timestamp).all()
    history = [{"role": msg.role, "content": msg.content} for msg in messages]

    # اضافه کردن system prompt فقط یک بار
    if len(history) == 1:
        history.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

    # دریافت پاسخ AI
    ai_response = get_ai_response(history)

    # جدا کردن متن و ذخیره کدها
    display_text, new_files = extract_and_save_code(ai_response, user.username)

    # ذخیره فقط متن توضیحی در دیتابیس (نه کد کامل)
    assistant_msg = Message(user_id=user.id, role='assistant', content=display_text)
    db.session.add(assistant_msg)
    db.session.commit()

    return jsonify({
        'username': user.username,
        'user_message': message_text,
        'assistant_message': display_text,  # فقط متن توضیحی
        'new_files': new_files  # فایل‌های جدید/به‌روزشده
    })

@app.route('/history')
def history():
    ip = request.remote_addr
    user = User.query.filter_by(ip_address=ip).first()
    if not user:
        return jsonify({'messages': []})
    
    messages = Message.query.filter_by(user_id=user.id).order_by(Message.timestamp).all()
    history = [
        {'role': msg.role, 'content': msg.content}
        for msg in messages
    ]
    return jsonify({'messages': history, 'username': user.username})



@app.route('/clear_chat', methods=['POST'])
def clear_chat():
    ip = request.remote_addr
    user = User.query.filter_by(ip_address=ip).first()
    
    if not user:
        return jsonify({'status': 'error', 'message': 'کاربری یافت نشد'}), 404

    try:
        # حذف تمام پیام‌های کاربر
        Message.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'تمام مکالمات با موفقیت پاک شد'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'خطا در پاک کردن مکالمات'}), 500
    

@app.route('/get_files')
def get_user_files():
    ip = request.remote_addr
    user = User.query.filter_by(ip_address=ip).first()
    if not user:
        return jsonify({'files': []})
    
    user_folder = PROJECTS_DIR / user.username
    if not user_folder.exists():
        return jsonify({'files': []})
    
    files = [f.name for f in user_folder.iterdir() if f.is_file()]
    return jsonify({'files': sorted(files)})


@app.route('/get_file/<filename>')
def get_file(filename):
    ip = request.remote_addr
    user = User.query.filter_by(ip_address=ip).first()
    if not user:
        return "کاربر یافت نشد", 404
    
    user_folder = PROJECTS_DIR / user.username
    file_path = user_folder / filename
    
    if not file_path.exists() or not file_path.is_file():
        return "فایل یافت نشد", 404
    
    if filename.endswith('.html'):
        mimetype = 'text/html'
    elif filename.endswith('.css'):
        mimetype = 'text/css'
    elif filename.endswith('.js'):
        mimetype = 'text/javascript'
    else:
        mimetype = 'text/plain'
    
    return file_path.read_text(encoding='utf-8'), 200, {'Content-Type': mimetype}



@app.route('/preview')
def preview():
    ip = request.remote_addr
    user = User.query.filter_by(ip_address=ip).first()
    if not user:
        return "کاربر یافت نشد", 404
    
    user_folder = PROJECTS_DIR / user.username
    index_path = user_folder / 'index.html'
    
    if not index_path.exists():
        return "<h1>فایل index.html وجود ندارد</h1>", 404
    
    html = index_path.read_text(encoding='utf-8')
    
    # Inline کردن style.css اگر وجود داشت
    css_path = user_folder / 'style.css'
    if css_path.exists() and '<link rel="stylesheet" href="style.css">' in html:
        css_content = css_path.read_text(encoding='utf-8')
        html = html.replace('<link rel="stylesheet" href="style.css">', 
                            f'<style>\n{css_content}\n</style>')
    
    # Inline کردن script.js اگر وجود داشت
    js_path = user_folder / 'script.js'
    if js_path.exists() and '<script src="script.js"></script>' in html:
        js_content = js_path.read_text(encoding='utf-8')
        html = html.replace('<script src="script.js"></script>', 
                            f'<script>\n{js_content}\n</script>')
    
    return html, 200, {'Content-Type': 'text/html; charset=utf-8'}


if __name__ == '__main__':
    app.run(debug=True)
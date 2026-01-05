# app.py
from flask import Flask, render_template, request, jsonify, session, send_file
import mysql.connector
from config import DATABASE_CONFIG, DATABASE_NAME
from database import create_database_if_not_exists
from models import db, User, Message
import secrets
import string
from chat_bot import get_ai_response, SYSTEM_PROMPT
import zipfile
from io import BytesIO


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


    return user

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message_text = data.get('message', '').strip()
    selected_model = data.get('model', 'gpt-4o-mini')  # مدل پیش‌فرض اگر ارسال نشده باشد

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

    # دریافت پاسخ AI با مدل انتخاب‌شده توسط کاربر
    ai_response = get_ai_response(history, selected_model)  # اینجا model را پاس می‌دهیم

    # جدا کردن متن و ذخیره کدها
    display_text, new_files = extract_and_save_code(ai_response, user.username)

    # ذخیره فقط متن توضیحی در دیتابیس
    assistant_msg = Message(user_id=user.id, role='assistant', content=display_text)
    db.session.add(assistant_msg)
    db.session.commit()

    return jsonify({
        'username': user.username,
        'user_message': message_text,
        'assistant_message': display_text,
        'new_files': new_files
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
        # حذف تمام پیام‌های کاربر از دیتابیس
        Message.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        
        # مسیر فولدر کاربر
        user_folder = PROJECTS_DIR / user.username
        
        # اگر فولدر وجود داشت، تمام فایل‌های داخلش را حذف کن
        if user_folder.exists() and user_folder.is_dir():
            for file_path in user_folder.iterdir():
                if file_path.is_file():
                    file_path.unlink()  # حذف فایل
                elif file_path.is_dir():
                    # اگر زیرپوشه‌ای بود (که معمولاً نیست، اما برای ایمنی)
                    import shutil
                    shutil.rmtree(file_path)
        
        return jsonify({
            'status': 'success', 
            'message': 'تمام مکالمات و فایل‌های پروژه با موفقیت پاک شد و پروژه پیش‌فرض بازسازی شد.'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'خطا در پاک کردن مکالمات یا فایل‌ها'}), 500    

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
        info_html = """
        <div style="text-align: center; max-width: 700px; margin: 0 auto; padding: 20px;">
            <p style="font-size: 1.35em; line-height: 1.8; color: #333; margin: 20px 0;">
                این صفحه پیش‌نمایش زنده‌ی سایت شماست.
            </p>
            
            <p style="font-size: 1.35em; line-height: 1.8; color: #333; margin: 20px 0;">
                همین حالا با هوش مصنوعی چت کنید، بگید چه سایتی می‌خواهید بسازید،<br>
                و تغییرات را لحظه‌ای اینجا ببینید.
            </p>
            
            <p style="font-size: 1.15em; line-height: 1.7; color: #555; margin: 30px 0 0 0;">
                هر وقت آماده بودید، فقط بگویید «پیش‌نمایش رو ببینم»<br>
                یا مستقیم کد <code style="background:#f0f0f0; padding:2px 8px; border-radius:4px;">HTML</code>، 
                <code style="background:#f0f0f0; padding:2px 8px; border-radius:4px;">CSS</code> و 
                <code style="background:#f0f0f0; padding:2px 8px; border-radius:4px;">JS</code> را بخواهید.
            </p>
        </div>
        """
        return info_html, 200, {'Content-Type': 'text/html; charset=utf-8'}
    
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


@app.route('/save_file', methods=['POST'])
def save_file():
    ip = request.remote_addr
    user = User.query.filter_by(ip_address=ip).first()
    if not user:
        return jsonify({'status': 'error', 'message': 'کاربر یافت نشد'}), 404

    data = request.get_json()
    filename = data.get('filename')
    content = data.get('content', '')

    if not filename:
        return jsonify({'status': 'error', 'message': 'نام فایل الزامی است'}), 400

    user_folder = PROJECTS_DIR / user.username
    file_path = user_folder / filename

    try:
        file_path.write_text(content + '\n', encoding='utf-8')
        return jsonify({'status': 'success', 'message': f'فایل {filename} با موفقیت ذخیره شد'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'خطا در ذخیره فایل'}), 500




@app.route('/download_project')
def download_project():
    ip = request.remote_addr
    user = User.query.filter_by(ip_address=ip).first()
    if not user:
        return jsonify({'error': 'کاربر یافت نشد'}), 404

    user_folder = PROJECTS_DIR / user.username
    
    if not user_folder.exists() or not any(user_folder.iterdir()):
        return jsonify({'error': 'پروژه خالی است یا وجود ندارد'}), 400

    # ساخت ZIP در حافظه (بدون ذخیره روی دیسک)
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in user_folder.rglob('*'):  # همه فایل‌ها و زیرپوشه‌ها
            if file_path.is_file():
                # مسیر نسبی داخل ZIP (بدون پیشوند user_projects/username)
                arcname = str(file_path.relative_to(PROJECTS_DIR.parent))
                zipf.write(file_path, arcname)

    memory_file.seek(0)

    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f"{user.username}_project.zip"
    )

if __name__ == '__main__':
    app.run(debug=True)
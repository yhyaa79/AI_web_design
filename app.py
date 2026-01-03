# app.py
from flask import Flask, render_template, request, jsonify, session
import mysql.connector
from config import DATABASE_CONFIG, DATABASE_NAME
from database import create_database_if_not_exists
from models import db, User, Message
import secrets
import string

app = Flask(__name__)
app.secret_key = 'your_very_secret_key_here'  # حتماً تغییر بده

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
    """بر اساس IP کاربر رو پیدا یا ایجاد کن"""
    user = User.query.filter_by(ip_address=ip).first()
    if not user:
        username = generate_username()
        # مطمئن شو نام کاربری تکراری نباشه
        while User.query.filter_by(username=username).first():
            username = generate_username()
        
        user = User(ip_address=ip, username=username)
        db.session.add(user)
        db.session.commit()
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

    # دریافت IP کاربر
    ip = request.remote_addr
    
    # اگر در محیط توسعه با پراکسی هستی (مثل nginx)، این رو فعال کن:
    # if request.headers.get('X-Forwarded-For'):
    #     ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()

    user = get_or_create_user(ip)

    # ذخیره پیام کاربر
    user_msg = Message(user_id=user.id, role='user', content=message_text)
    db.session.add(user_msg)

    # اینجا باید پاسخ AI رو بگیری (مثلاً از Grok یا OpenAI)
    # فعلاً یک پاسخ نمونه می‌ذارم
    assistant_reply = f"شما گفتید: {message_text}\nاین یک پاسخ آزمایشی از AI است."

    assistant_msg = Message(user_id=user.id, role='assistant', content=assistant_reply)
    db.session.add(assistant_msg)

    db.session.commit()

    return jsonify({
        'username': user.username,
        'user_message': message_text,
        'assistant_message': assistant_reply
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
    
    

if __name__ == '__main__':
    app.run(debug=True)
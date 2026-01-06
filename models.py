# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # ستون‌های جدید برای rate limit
    message_count = db.Column(db.Integer, default=0)          # تعداد پیام‌های کاربر در ۲۴ ساعت جاری
    last_message_time = db.Column(db.DateTime, nullable=True) # زمان آخرین پیام موفق کاربر
    
    messages = db.relationship('Message', backref='user', lazy=True, cascade="all, delete-orphan")

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.Enum('user', 'assistant'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
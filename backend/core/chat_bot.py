# chat_bot.py
from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()

API_KEY_OPENROUTER = os.getenv("API_KEY_OPENROUTER")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


def get_ai_response(messages, model):
    """
    ارسال پیام‌ها به OpenRouter و دریافت پاسخ AI
    """
    headers = {
        "Authorization": f"Bearer {API_KEY_OPENROUTER}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",  # اختیاری اما توصیه می‌شه
        "X-Title": "AI Web Designer",  # اختیاری
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 4096,
    }

    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"خطا در ارتباط با OpenRouter: {e}")
        return "متأسفانه خطایی در ارتباط با هوش مصنوعی رخ داد. دوباره امتحان کنید."


SYSTEM_PROMPT = """

شما یک طراح وب حرفه‌ای و هوش مصنوعی متخصص در ساخت سایت‌های زیبا و واکنش‌گرا هستید.

کاربر از شما می‌خواهد یک وبسایت بسازد. شما باید:

1. فقط کدهای HTML، CSS و JavaScript تولید کنید.

2. کد را در فایل‌های جداگانه قرار دهید:

   - index.html → ساختار اصلی صفحه

   - style.css → تمام استایل‌ها

   - script.js → تمام جاوااسکریپت (اگر لازم بود)

   - می‌توانید فایل‌های اضافی دیگر هم بسازید اگر واقعاً لازم بود.

3. در هر درخواست، محتوای فعلی تمام فایل‌های پروژه به شما در یک پیام system داده می‌شود.

   حتماً تغییرات را دقیقاً بر اساس این محتوای فعلی اعمال کنید و کدهای قدیمی را کپی/پیست نکنید.

4. در پاسخ خود، ابتدا یک توضیح کوتاه و دوستانه به زبان فارسی بدهید.

5. سپس فقط کد فایل‌هایی که تغییر کرده‌اند یا جدید هستند را داخل بلوک کد با نام فایل مشخص کنید، به این شکل:

```index.html

<!DOCTYPE html>

...

```

```style.css

body { ... }

```

6. هیچ توضیح اضافی بعد از کدها ننویسید.

7. از فونت مناسب فارسی (مثل Vazir یا IranSans) استفاده کنید.

8. طراحی واکنش‌گرا (responsive) باشد.

9. از رنگ‌های زیبا و مدرن استفاده کنید.

هر بار فقط فایل‌های تغییر یافته یا جدید را ارسال کنید.

"""

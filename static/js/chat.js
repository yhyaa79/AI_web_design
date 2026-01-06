// تابع ارسال پیام
const originalSendHTML = sendButton.innerHTML; // SVG اصلی فلش

// تابع ارسال پیام (اصلاح‌شده)
async function sendMessage() {
    const textarea = document.querySelector('.write-message');
    const message = textarea.value.trim();
    if (!message) return;

    // گرفتن مدل انتخاب‌شده
    const selectedModel = document.getElementById('model-select').value || 'openai/gpt-4o-mini';

    // اضافه کردن پیام کاربر
    addMessage('user', message);
    textarea.value = '';

    // اضافه کردن پیام لودینگ
    const loadingMessageElement = addMessage('assistant', 'لطفا صبر کنید...');

    // تغییر دکمه به حالت لودینگ
    sendButton.disabled = true;
    sendButton.classList.add('loading'); // می‌توانید در CSS استایل لودینگ تعریف کنید
    sendButton.innerHTML = `
        <svg class="spinner" viewBox="0 0 50 50">
            <circle cx="25" cy="25" r="20" fill="none" stroke="currentColor" stroke-width="5"></circle>
        </svg>
    `;

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                message: message,
                model: selectedModel 
            })
        });

        if (response.ok) {
            const data = await response.json();

            // حذف پیام لودینگ
            loadingMessageElement.remove();

            // اضافه کردن پاسخ واقعی
            addMessage('assistant', data.assistant_message);

            // اگر فایل‌های جدید ایجاد شد
            if (data.new_files && data.new_files.length > 0) {
                loadFileList();
            }
        } else {
            loadingMessageElement.remove();
            addMessage('assistant', 'خطایی رخ داد. دوباره امتحان کنید.');
        }
    } catch (err) {
        console.error('خطا در ارسال پیام:', err);
        loadingMessageElement.remove();
        addMessage('assistant', 'خطا در ارتباط با سرور.');
    } finally {
        // برگرداندن دکمه به حالت اولیه در هر شرایطی
        sendButton.disabled = false;
        sendButton.classList.remove('loading');
        sendButton.innerHTML = originalSendHTML; // SVG اصلی فلش
    }
}

// تابع لود تاریخچه چت
async function loadHistory() {
    try {
        const response = await fetch('/history');
        if (response.ok) {
            const data = await response.json();
            data.messages.forEach(msg => {
                addMessage(msg.role, msg.content);
            });
        }
    } catch (err) {
        console.error('خطا در لود تاریخچه:', err);
    }
}

// راه‌اندازی رویدادها
sendButton.addEventListener('click', sendMessage);

textarea.addEventListener('keypress', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// وقتی صفحه لود شد
document.addEventListener('DOMContentLoaded', () => {
    // راه‌اندازی CodeMirror
    editor = CodeMirror(document.getElementById("code-editor-container"), {
        value: "فایل مورد نظر خود را از نوار کناری انتخاب کنید",
        mode: "htmlmixed",
        theme: "default",
        lineNumbers: true,
        lineWrapping: true,
        autoCloseBrackets: true,
        matchBrackets: true,
        indentUnit: 2,
        tabSize: 2
    });

    // لود اولیه
    loadHistory();
    loadFileList();
});
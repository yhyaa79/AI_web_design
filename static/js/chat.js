// تابع ارسال پیام
async function sendMessage() {
    const message = textarea.value.trim();
    if (!message) return;

    // گرفتن مدل انتخاب‌شده
    const selectedModel = document.getElementById('model-select').value || 'gpt-4o-mini'; // پیش‌فرض اگر خالی بود

    addMessage('user', message);
    textarea.value = '';

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                message: message,
                model: selectedModel  // اضافه کردن مدل
            })
        });

        if (response.ok) {
            const data = await response.json();
            addMessage('assistant', data.assistant_message);

            if (data.new_files && data.new_files.length > 0) {
                loadFileList();
            }
        } else {
            addMessage('assistant', 'خطایی رخ داد. دوباره امتحان کنید.');
        }
    } catch (err) {
        console.error('خطا در ارسال پیام:', err);
        addMessage('assistant', 'خطا در ارتباط با سرور.');
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
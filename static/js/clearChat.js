// clearChat.js

// چت جدید / پاک کردن چت
const clearChatBtn = document.getElementById('clear-chat-btn');

clearChatBtn.addEventListener('click', async () => {
    
    // تأیید از کاربر
    const confirmDelete = confirm('آیا مطمئن هستید که می‌خواهید تمام مکالمات و پروژه فعلی را پاک کنید؟\nاین عمل قابل بازگشت نیست!');
    
    if (!confirmDelete) return;

    try {
        const response = await fetch('/clear_chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (data.status === 'success') {
            alert('تمام مکالمات و فایل‌های پروژه با موفقیت پاک شد!\nپروژه پیش‌فرض بازسازی شد.');

            // ۱. پاک کردن تمام پیام‌ها از صفحه
            messagesContainer.innerHTML = '';

            // ۲. پاک کردن تمام فایل‌ها از لیست UI (به جز پیش‌فرض‌ها)
            const allFileItems = filesContainer.querySelectorAll('.file-name');
            allFileItems.forEach(item => {
                const fileName = item.querySelector('.p-btn').textContent.trim();
                // فقط فایل‌های غیرپیش‌فرض را حذف کن
                if (!['index.html', 'style.css', 'script.js'].includes(fileName)) {
                    item.remove();
                }
            });


            // ۴. پاک کردن محتوای ادیتور (اختیاری – بهتره خالی بشه)
            editor.setValue("فایل مورد نظر خود را از نوار کناری انتخاب کنید");
            editor.setOption('mode', 'htmlmixed');

        } else {
            alert('خطا: ' + data.message);
        }
    } catch (error) {
        console.error('خطا در ارتباط با سرور:', error);
        alert('خطا در ارتباط با سرور. لطفاً دوباره امتحان کنید.');
    }
});
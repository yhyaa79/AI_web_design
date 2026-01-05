

console.log('aaabbbbaaa');
// چت جدید
const clearChatBtn = document.getElementById('clear-chat-btn');

clearChatBtn.addEventListener('click', async () => {
    console.log('aaaaaa');
    
    // تأیید از کاربر
    const confirmDelete = confirm('آیا مطمئن هستید که می‌خواهید تمام مکالمات را پاک کنید؟ این عمل قابل بازگشت نیست!');
    
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
            alert('تمام مکالمات با موفقیت پاک شد!');
            // پاک کردن پیام‌ها از صفحه
            messagesContainer.innerHTML = '';
        } else {
            alert('خطا: ' + data.message);
        }
    } catch (error) {
        console.error('خطا در ارتباط با سرور:', error);
        alert('خطا در ارتباط با سرور. لطفاً دوباره امتحان کنید.');
    }
});
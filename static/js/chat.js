



const sendButton = document.querySelector('.send-message');
const textarea = document.querySelector('.write-message');
const messagesContainer = document.querySelector('.messages');

async function sendMessage() {
    const message = textarea.value.trim();
    if (!message) return;

    // نمایش پیام کاربر
    addMessage('user', message);
    textarea.value = '';

    const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
    });

    const data = await response.json();
    addMessage('assistant', data.assistant_message);
}

function addMessage(role, content) {
    const div = document.createElement('div');
    div.className = `message ${role}`;
    div.textContent = content;
    messagesContainer.appendChild(div);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

sendButton.addEventListener('click', sendMessage);
textarea.addEventListener('keypress', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// لود تاریخچه چت هنگام بارگذاری صفحه
async function loadHistory() {
    const response = await fetch('/history');
    const data = await response.json();
    data.messages.forEach(msg => {
        addMessage(msg.role, msg.content);
    });
}

loadHistory();





// چت جدید
const clearChatBtn = document.getElementById('clear-chat-btn');

clearChatBtn.addEventListener('click', async () => {
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
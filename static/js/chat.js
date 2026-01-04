
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
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message
        })
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






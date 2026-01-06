// static/js/script.js

const sendButton = document.querySelector('.send-message');
const textarea = document.querySelector('.write-message');
const messagesContainer = document.querySelector('.messages');
const filesContainer = document.querySelector('.files-display > div:nth-child(2)'); // محل لیست فایل‌ها

// متغیر برای CodeMirror
let editor;



// تابع اضافه کردن پیام به چت
// ابتدا تابع addMessage را به این شکل تغییر دهید (تا المنت را برگرداند)
function addMessage(role, content) {
    const messagesContainer = document.querySelector('.messages');
    const div = document.createElement('div');
    div.className = `message ${role}`;
    div.textContent = content;

    // اگر پیام لودینگ است، یک کلاس خاص اضافه می‌کنیم تا بعداً راحت‌تر پیدا کنیم
    if (content === 'لطفا صبر کنید...') {
        div.classList.add('loading-message');
    }

    messagesContainer.appendChild(div);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    return div; // المنت ساخته‌شده را برمی‌گردانیم
}

// تابع آپدیت لیست فایل‌ها در UI
function updateFileList(files) {
    if (!filesContainer) return;

    // پاک کردن تمام فایل‌ها به جز دو تای پیش‌فرض (index.html و style.css)
    const allFileItems = filesContainer.querySelectorAll('.file-name');
    allFileItems.forEach(item => {
        const fileName = item.querySelector('.p-btn').textContent;
        if (fileName !== 'index.html' && fileName !== 'style.css' && fileName !== 'script.js') {
            item.remove();
        }
    });

    // اضافه کردن فایل‌های جدید
    files.forEach(filename => {
        // اگر قبلاً وجود داشت، اضافه نکن
        const exists = Array.from(allFileItems).some(item => 
            item.querySelector('.p-btn').textContent === filename
        );
        if (exists) return;

        const div = document.createElement('div');
        div.className = 'file-name';
        div.innerHTML = `
            <div class="icon-files">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                     class="bi bi-file-earmark-text" viewBox="0 0 16 16">
                    <path d="M5.5 7a.5.5 0 0 0 0 1h5a.5.5 0 0 0 0-1zM5 9.5a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5m0 2a.5.5 0 0 1 .5-.5h2a.5.5 0 0 1 0 1h-2a.5.5 0 0 1-.5-.5"/>
                    <path d="M9.5 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V4.5zm0 1v2A1.5 1.5 0 0 0 11 4.5h2V14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1z"/>
                </svg>
            </div>
            <p class="p-btn">${filename}</p>
        `;

        // کلیک برای لود محتوا در CodeMirror
        div.addEventListener('click', async () => {
            try {
                const response = await fetch(`/get_file/${encodeURIComponent(filename)}`);
                if (response.ok) {
                    const content = await response.text();
                    editor.setValue(content);

                    // تنظیم مود مناسب
                    let mode = 'htmlmixed';
                    if (filename.endsWith('.css')) mode = 'css';
                    else if (filename.endsWith('.js')) mode = 'javascript';
                    editor.setOption('mode', mode);
                } else {
                    editor.setValue(`// فایل ${filename} یافت نشد یا خالی است`);
                }
            } catch (err) {
                console.error('خطا در لود فایل:', err);
                editor.setValue('// خطا در بارگذاری فایل');
            }
        });

        filesContainer.appendChild(div);
    });
}

// تابع لود لیست فایل‌ها از سرور
async function loadFileList() {
    try {
        const response = await fetch('/get_files');
        if (response.ok) {
            const data = await response.json();
            updateFileList(data.files);
        }
    } catch (err) {
        console.error('خطا در دریافت لیست فایل‌ها:', err);
    }
}


// اضافه کردن حالت active به قسمت tab-btn 
document.querySelectorAll('.tab-btn').forEach(button => {
    button.addEventListener('click', () => {
        // اول کلاس active را از همه دکمه‌ها بردار
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        // سپس به دکمه کلیک‌شده اضافه کن
        button.classList.add('active');
    });
});


// اضافه کردن حالت active به قسمت file-name 
document.querySelectorAll('.file-name').forEach(button => {
    button.addEventListener('click', () => {
        // اول کلاس active را از همه دکمه‌ها بردار
        document.querySelectorAll('.file-name').forEach(btn => {
            btn.classList.remove('active');
        });
        // سپس به دکمه کلیک‌شده اضافه کن
        button.classList.add('active');
    });
});





// نمایش لیست فایل‌ها
let currentFiles = [];

// لود اولیه لیست فایل‌ها
async function loadFileList() {
    const response = await fetch('/get_files');
    const data = await response.json();
    currentFiles = data.files;
    updateFileList(currentFiles);
}

// آپدیت لیست فایل‌ها در UI
function updateFileList(files) {
    const container = document.querySelector('.files-display > div:nth-child(2)');
    if (!container) return;

    // پاک کردن فایل‌های قبلی (به جز فایل‌های پیش‌فرض اگر داشتی)
    container.innerHTML = `
        <div class="file-name">
            <div class="icon-files">/* آیکون */</div>
            <p class="p-btn">index.html</p>
        </div>
        <div class="file-name">
            <div class="icon-files">/* آیکون */</div>
            <p class="p-btn">style.css</p>
        </div>
    `;

    files.forEach(filename => {
        if (filename === 'index.html' || filename === 'style.css' || filename === 'script.js') return; // اگر می‌خوای تکراری نشه

        const div = document.createElement('div');
        div.className = 'file-name';
        div.innerHTML = `
            <div class="icon-files">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-file-earmark-text" viewBox="0 0 16 16">
                    <path d="M5.5 7a.5.5 0 0 0 0 1h5a.5.5 0 0 0 0-1zM5 9.5a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5m0 2a.5.5 0 0 1 .5-.5h2a.5.5 0 0 1 0 1h-2a.5.5 0 0 1-.5-.5"/>
                    <path d="M9.5 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V4.5zm0 1v2A1.5 1.5 0 0 0 11 4.5h2V14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1z"/>
                </svg>
            </div>
            <p class="p-btn">${filename}</p>
        `;
        div.onclick = async () => {
            const content = await fetch(`/get_file/${encodeURIComponent(filename)}`).then(r => r.text());
            editor.setValue(content);
            editor.setOption("mode", filename.endsWith('.css') ? 'css' : 
                                    filename.endsWith('.js') ? 'javascript' : 'htmlmixed');
        };
        container.appendChild(div);
    });
}

// در تابع sendMessage بعد از دریافت پاسخ:
const data = await response.json();
addMessage('assistant', data.assistant_message);
if (data.new_files && data.new_files.length > 0) {
    loadFileList();  // لیست فایل‌ها رو آپدیت کن
}

// هنگام لود صفحه
loadFileList();
loadHistory();
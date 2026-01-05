

// --- اضافه کردن قابلیت Save ---
let currentEditingFile = null;  // نام فایلی که الان در ادیتور باز است

// وقتی روی یک فایل کلیک می‌شود، نامش رو ذخیره کن
document.querySelectorAll('.file-name').forEach(item => {
    item.addEventListener('click', () => {
        const filename = item.querySelector('.p-btn').textContent;
        currentEditingFile = filename;
        
        // تغییر ظاهر: هایلایت فایل جاری
        document.querySelectorAll('.file-name').forEach(f => f.classList.remove('active-file'));
        item.classList.add('active-file');
    });
});

// اگر بعداً فایل‌های جدید اضافه شدن (مثل وقتی AI فایل ساخت)، دوباره listener اضافه کن
const observer = new MutationObserver(() => {
    document.querySelectorAll('.file-name').forEach(item => {
        item.addEventListener('click', () => {
            const filename = item.querySelector('.p-btn').textContent;
            currentEditingFile = filename;
            document.querySelectorAll('.file-name').forEach(f => f.classList.remove('active-file'));
            item.classList.add('active-file');
        });
    });
});
observer.observe(filesContainer, { childList: true });

// دکمه Save
document.getElementById('save-file-btn').addEventListener('click', async () => {
    if (!currentEditingFile) {
        alert('لطفاً ابتدا یک فایل را از لیست انتخاب کنید');
        return;
    }

    const content = editor.getValue();

    try {
        const response = await fetch('/save_file', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: currentEditingFile,
                content: content
            })
        });

        const result = await response.json();
        
        if (result.status === 'success') {
            addMessage('system', `✅ ${result.message}`);
            // آپدیت پیش‌نمایش خودکار
            document.getElementById('preview-iframe').contentWindow.location.reload();
        } else {
            addMessage('system', `خطا: ${result.message}`);
        }
    } catch (err) {
        console.error(err);
        addMessage('system', 'خطا در ارتباط با سرور');
    }
});
// codePreview.js

// مدیریت تب‌های code و preview
const codeTab = document.querySelector('.code-heder');
const previewTab = document.querySelector('.preview-heder');
const codeContainer = document.querySelector('.code-display');
const filesDisplay = document.querySelector('.files-display');
const previewContainer = document.querySelector('#preview-container');
const iframe = document.getElementById('preview-iframe');

function showCodeEditor() {
    codeContainer.style.display = 'block';
    filesDisplay.style.display = 'block';
    previewContainer.style.display = 'none';
    codeTab.classList.add('active');
    previewTab.classList.remove('active');
}

function showPreview() {
    codeContainer.style.display = 'none';
    filesDisplay.style.display = 'none';
    previewContainer.style.display = 'block';
    // رفرش iframe برای نمایش آخرین تغییرات
    iframe.src = '/preview?' + new Date().getTime();
    previewTab.classList.add('active');
    codeTab.classList.remove('active');
}

// رویداد کلیک روی تب‌ها
codeTab.addEventListener('click', showCodeEditor);
previewTab.addEventListener('click', showPreview);

// وضعیت اولیه: اگر preview فعال بود، پیش‌نمایش رو نشون بده
document.addEventListener('DOMContentLoaded', () => {
    if (previewTab.classList.contains('active')) {
        showPreview();
    } else {
        showCodeEditor();
    }

    // بعد از هر پاسخ AI، اگر در حالت preview هستیم، iframe رو رفرش کن
    const originalSendMessage = sendMessage;
    sendMessage = async function() {
        await originalSendMessage();
        if (previewTab.classList.contains('active')) {
            iframe.src = '/preview?' + new Date().getTime();
        }
    };
});
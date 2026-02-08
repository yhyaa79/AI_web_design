// downloadProject.js

// دانلود کل پروژه به صورت ZIP
document.querySelector('.download-btn').addEventListener('click', function() {
    // اختیاری: تغییر ظاهر دکمه موقع لودینگ
    this.disabled = true;
    this.innerHTML = '<p class="p-btn">در حال آماده‌سازی...</p>';

    fetch('/download_project')
        .then(response => {
            if (!response.ok) {
                throw new Error('خطا در دریافت فایل');
            }
            return response.blob();
        })
        .then(blob => {
            // ساخت لینک دانلود موقت
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = ''; // نام فایل توسط سرور تعیین می‌شه (download_name در Flask)
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);

            // برگرداندن دکمه به حالت عادی
            this.disabled = false;
            this.innerHTML = `
                <p class="p-btn">download</p>
                <div class="icon-files">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                        class="bi bi-download" viewBox="0 0 16 16">
                        <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5"/>
                        <path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708z"/>
                    </svg>
                </div>
            `;
        })
        .catch(err => {
            console.error(err);
            alert('خطا در دانلود پروژه. لطفاً دوباره تلاش کنید.');
            this.disabled = false;
            this.innerHTML = `
                <p class="p-btn">download</p>
                <div class="icon-files">...</div>
            `;
        });
});

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






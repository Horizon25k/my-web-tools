document.addEventListener('DOMContentLoaded', () => {
    const toggleBtn = document.getElementById('theme-toggle');
    const body = document.body;

    // เช็กค่าที่เคยบันทึกไว้ในเบราว์เซอร์
    if (localStorage.getItem('theme') === 'dark') {
        body.classList.add('dark-mode');
    }

    // เมื่อกดปุ่มให้สลับคลาสและบันทึกค่า
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            body.classList.toggle('dark-mode');
            const isDark = body.classList.contains('dark-mode');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
        });
    }
});
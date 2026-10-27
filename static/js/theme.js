document.addEventListener('DOMContentLoaded', () => {
    const toggleBtn = document.getElementById('theme-toggle');
    const htmlEl = document.documentElement;
    const bodyEl = document.body;

    // ซิงก์คลาส dark-mode ให้ตรงกันทั้ง html และ body
    if (localStorage.getItem('theme') === 'dark') {
        htmlEl.classList.add('dark-mode');
        bodyEl.classList.add('dark-mode');
    }

    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            htmlEl.classList.toggle('dark-mode');
            bodyEl.classList.toggle('dark-mode');
            
            const isDark = htmlEl.classList.contains('dark-mode');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
        });
    }
});
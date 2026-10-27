document.addEventListener('DOMContentLoaded', () => {
    const toggleBtn = document.getElementById('theme-toggle');
    const htmlEl = document.documentElement;
    const bodyEl = document.body;

    // ฟังก์ชันอัปเดตไอคอนดวงอาทิตย์ / ดวงจันทร์
    function updateToggleIcon(isDark) {
        if (!toggleBtn) return;
        toggleBtn.innerHTML = isDark 
            ? `<svg class="w-5 h-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>` // ไอคอนดวงอาทิตย์สำหรับโหมดมืด
            : `<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path></svg>`; // ไอคอนดวงจันทร์สำหรับโหมดสว่าง
    }

    // ซิงก์สถานะเริ่มต้น
    const isDarkInitial = localStorage.getItem('theme') === 'dark';
    if (isDarkInitial) {
        htmlEl.classList.add('dark-mode');
        bodyEl.classList.add('dark-mode');
    }
    updateToggleIcon(isDarkInitial);

    // Event Listener เมื่อกดปุ่มสลับโหมด
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            htmlEl.classList.toggle('dark-mode');
            bodyEl.classList.toggle('dark-mode');
            
            const isDark = htmlEl.classList.contains('dark-mode');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            updateToggleIcon(isDark);
        });
    }
});
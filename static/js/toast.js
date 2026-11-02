/**
 * ระบบแจ้งเตือน Toast Notification
 * @param {string} message - ข้อความที่ต้องการแสดง
 * @param {'success' | 'error' | 'info'} type - ประเภทการแจ้งเตือน (default: 'success')
 * @param {number} duration - ระยะเวลาแสดงผล (ms) (default: 3000)
 */
function showToast(message, type = 'success', duration = 3000) {
    // 1. ตรวจสอบหรือสร้าง Container สำหรับใส่ Toast ที่มุมขวาล่าง
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'fixed bottom-5 right-5 z-50 flex flex-col gap-2.5 pointer-events-none max-w-xs sm:max-w-sm w-full px-4';
        document.body.appendChild(container);
    }

    // 2. กำหนดสีและไอคอนตามประเภท
    let bgColors = '';
    let iconSvg = '';

    if (type === 'success') {
        bgColors = 'bg-emerald-600/90 dark:bg-emerald-500/90 border-emerald-400/30 text-white';
        iconSvg = `<svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>`;
    } else if (type === 'error') {
        bgColors = 'bg-rose-600/90 dark:bg-rose-500/90 border-rose-400/30 text-white';
        iconSvg = `<svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>`;
    } else {
        bgColors = 'bg-indigo-600/90 dark:bg-indigo-500/90 border-indigo-400/30 text-white';
        iconSvg = `<svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`;
    }

    // 3. สร้าง Element ของ Toast
    const toast = document.createElement('div');
    toast.className = `pointer-events-auto flex items-center justify-between gap-3 px-4 py-3 rounded-2xl shadow-xl shadow-black/10 border backdrop-blur-md transition-all duration-300 transform translate-y-6 opacity-0 text-xs sm:text-sm font-medium ${bgColors}`;
    
    toast.innerHTML = `
        <div class="flex items-center gap-2.5">
            ${iconSvg}
            <span>${message}</span>
        </div>
        <button onclick="this.parentElement.remove()" class="opacity-70 hover:opacity-100 transition-opacity p-0.5">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
    `;

    container.appendChild(toast);

    // 4. เล่น Animation Fade In & Slide Up
    requestAnimationFrame(() => {
        toast.classList.remove('translate-y-6', 'opacity-0');
    });

    // 5. ลบ Toast ออกเมื่อครบกำหนดเวลา
    setTimeout(() => {
        toast.classList.add('translate-y-2', 'opacity-0');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, duration);
}
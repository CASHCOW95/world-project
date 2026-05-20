// Global Persistence Layer (Must load first)
window.AppStorage = {
    save: (key, data) => {
        localStorage.setItem(`world_ai_${key}`, JSON.stringify(data));
        showToast('💾 데이터가 안전하게 저장되었습니다.');
    },
    load: (key) => {
        const data = localStorage.getItem(`world_ai_${key}`);
        return data ? JSON.parse(data) : null;
    }
};

function showToast(msg) {
    const toast = document.createElement('div');
    toast.className = 'fixed bottom-8 left-1/2 -translate-x-1/2 px-6 py-3 rounded-full bg-indigo-600 text-white font-black text-xs shadow-2xl z-[1000] animate-in';
    toast.innerText = msg;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 500);
    }, 2000);
}

document.addEventListener('DOMContentLoaded', () => {
    const isLoggedIn = sessionStorage.getItem('isAdminLoggedIn') === 'true';
    const adminNickname = sessionStorage.getItem('adminNickname');
    const pathParts = window.location.pathname.split('/');
    const currentPage = pathParts[pathParts.length - 1] || 'index.html';

    // 1. Initial Visibility
    document.body.style.opacity = '1';
    const mainContent = document.querySelector('main');
    if (mainContent) mainContent.style.opacity = '1';

    // 2. Service Locking (index.html)
    if (currentPage === 'index.html' || currentPage === '') {
        document.querySelectorAll('.feature-card').forEach(card => {
            const lockOverlay = card.querySelector('.lock-overlay');
            const icon = card.querySelector('.feature-icon');
            if (!isLoggedIn) {
                if(lockOverlay) lockOverlay.style.opacity = '1';
                if(lockOverlay) lockOverlay.style.pointerEvents = 'auto';
                if(icon) icon.style.filter = 'grayscale(1) blur(4px)';
                card.onclick = (e) => {
                    e.preventDefault();
                    if(confirm('관리자 전용 서비스입니다. 로그인하시겠습니까?')) window.location.href = 'login.html';
                    return false;
                };
            }
        });
        updateDashboardSummary();
    }

    // 3. Auth Guard
    const protectedPages = ['meetup-calendar.html', 'asset-mgmt.html', 'profit-mgmt.html', 'diary.html', 'tiktok-mgmt.html', 'timer.html'];
    if (protectedPages.includes(currentPage) && !isLoggedIn) {
        window.location.href = `login.html?redirect=${currentPage}`;
        return;
    }

    // 4. Header UI
    const authBtn = document.querySelector('.open-auth');
    if (authBtn && isLoggedIn) {
        authBtn.innerHTML = `<span class="text-indigo-500 font-black mr-2">●</span> ${adminNickname} 관리자`;
        const logoutBtn = document.createElement('button');
        logoutBtn.className = 'px-4 py-1.5 rounded-full border border-red-500/20 text-red-500 hover:bg-red-500 hover:text-white transition text-[11px] font-bold ml-2';
        logoutBtn.innerText = 'LOGOUT';
        logoutBtn.onclick = () => { sessionStorage.clear(); window.location.href = 'index.html'; };
        authBtn.parentNode.appendChild(logoutBtn);
    }

    // 5. Theme Toggle
    const themeToggle = document.getElementById('theme-toggle');
    const html = document.documentElement;
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const isDark = html.classList.toggle('dark');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
        });
    }

    // 6. Dashboard Summary (Logic for index.html footer)
    function updateDashboardSummary() {
        const profitData = AppStorage.load('profit_data') || [];
        const summaryEl = document.getElementById('dashboard-summary-content');
        if (!summaryEl) return;

        if (profitData.length === 0) {
            summaryEl.innerHTML = '<p class="text-slate-500">데이터가 없습니다.</p>';
            return;
        }

        const totalProfit = profitData.reduce((acc, d) => acc + (Number(d.amount) || 0), 0);
        const totalEntry = profitData.reduce((acc, d) => acc + (Number(d.entry) || 0), 0);
        const totalWinners = profitData.reduce((acc, d) => acc + (Number(d.winners) || 0), 0);
        const rate = totalEntry > 0 ? ((totalWinners / totalEntry) * 100).toFixed(1) : 0;

        summaryEl.innerHTML = `
            <div class="grid grid-cols-3 gap-8">
                <div class="text-left">
                    <p class="text-[10px] font-black text-slate-500 uppercase mb-1">총 누적 수익</p>
                    <p class="text-2xl font-black text-indigo-500">₩${totalProfit.toLocaleString()}</p>
                </div>
                <div class="text-left">
                    <p class="text-[10px] font-black text-slate-500 uppercase mb-1">평균 당첨률</p>
                    <p class="text-2xl font-black text-emerald-500">${rate}%</p>
                </div>
                <div class="text-left">
                    <p class="text-[10px] font-black text-slate-500 uppercase mb-1">최근 활동</p>
                    <p class="text-sm font-bold text-white truncate">${profitData[0].item}</p>
                </div>
            </div>
        `;
    }
});
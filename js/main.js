// Global Persistence Layer (Available immediately)
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
    const existing = document.getElementById('app-toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.id = 'app-toast';
    toast.className = 'fixed bottom-8 left-1/2 -translate-x-1/2 px-6 py-3 rounded-full bg-indigo-600 text-white font-black text-xs shadow-2xl z-[3000] transition-opacity duration-500';
    toast.style.opacity = '0';
    toast.innerText = msg;
    document.body.appendChild(toast);
    
    requestAnimationFrame(() => {
        toast.style.opacity = '1';
    });

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 500);
    }, 2500);
}

document.addEventListener('DOMContentLoaded', () => {
    const isLoggedIn = sessionStorage.getItem('isAdminLoggedIn') === 'true';
    const adminNickname = sessionStorage.getItem('adminNickname');
    const pathParts = window.location.pathname.split('/');
    const currentPage = pathParts[pathParts.length - 1] || 'index.html';

    // 1. Core Visibility & Theme
    document.body.style.opacity = '1';
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.style.opacity = '1';
        mainContent.style.visibility = 'visible';
    }

    const themeToggle = document.getElementById('theme-toggle');
    const html = document.documentElement;
    const savedTheme = localStorage.getItem('theme') || 'dark';
    if (savedTheme === 'light') html.classList.remove('dark');
    else html.classList.add('dark');

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const isDark = html.classList.toggle('dark');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
        });
    }

    // 2. Auth Guard for Protected Pages
    const protectedPages = [
        'meetup-calendar.html', 'asset-mgmt.html', 'profit-mgmt.html', 
        'diary.html', 'tiktok-mgmt.html', 'timer.html',
        'online-meetup.html', 'profile-mgmt.html', 'offline-meetup.html', 'gifticon-mgmt.html'
    ];

    if (protectedPages.includes(currentPage) && !isLoggedIn) {
        window.location.href = `login.html?redirect=${currentPage}`;
        return;
    }

    // 3. Header Auth UI
    const authBtn = document.querySelector('.open-auth');
    if (authBtn) {
        if (isLoggedIn) {
            authBtn.innerHTML = `<span class="text-indigo-500 font-black mr-2">●</span> ${adminNickname} 관리자`;
            authBtn.classList.replace('open-auth', 'admin-profile');
            const logoutBtn = document.createElement('button');
            logoutBtn.className = 'px-4 py-1.5 rounded-full border border-red-500/20 text-red-500 hover:bg-red-500 hover:text-white transition text-[11px] font-bold ml-2';
            logoutBtn.innerText = 'LOGOUT';
            logoutBtn.onclick = () => {
                sessionStorage.clear();
                window.location.href = 'index.html';
            };
            authBtn.parentNode.appendChild(logoutBtn);
        } else {
            authBtn.onclick = () => { window.location.href = 'login.html'; };
        }
    }

    // 4. Feature Locking (on index.html)
    if (currentPage === 'index.html' || currentPage === '') {
        document.querySelectorAll('.feature-card').forEach(card => {
            const featureType = card.getAttribute('data-feature');
            if (featureType === 'download') return; // Allow public download access

            const lockOverlay = card.querySelector('.lock-overlay');
            const icon = card.querySelector('.feature-icon');
            if (!isLoggedIn) {
                if(lockOverlay) lockOverlay.style.opacity = '1';
                if(lockOverlay) lockOverlay.style.pointerEvents = 'auto';
                if(icon) icon.style.filter = 'grayscale(1) blur(4px)';
                card.onclick = (e) => {
                    e.preventDefault();
                    if(confirm('관리자 전용 서비스입니다. 로그인하시겠습니까?')) {
                        window.location.href = 'login.html';
                    }
                    return false;
                };
            }
        });
        updateDashboardSummary();
    }

    // 7. Feedback Modal Logic
    const feedbackModal = document.getElementById('feedback-modal');
    const openFeedbackBtn = document.getElementById('open-feedback');
    const closeFeedbackBtn = document.getElementById('close-feedback');
    const submitFeedbackBtn = document.getElementById('submit-feedback');

    if (openFeedbackBtn && feedbackModal) {
        openFeedbackBtn.addEventListener('click', () => {
            feedbackModal.classList.add('active');
        });
    }

    if (closeFeedbackBtn && feedbackModal) {
        closeFeedbackBtn.addEventListener('click', () => {
            feedbackModal.classList.remove('active');
        });
    }

    if (submitFeedbackBtn) {
        submitFeedbackBtn.addEventListener('click', () => {
            const title = document.getElementById('feedback-title').value;
            const content = document.getElementById('feedback-content').value;

            if (!title || !content) {
                alert('제목과 내용을 모두 입력해주세요.');
                return;
            }

            const mailtoLink = `mailto:ydh2455@naver.com?subject=${encodeURIComponent('[문의] ' + title)}&body=${encodeURIComponent(content)}`;
            window.location.href = mailtoLink;
            
            feedbackModal.classList.remove('active');
            showToast('📧 메일 클라이언트가 열립니다.');
        });
    }

    // 8. Scroll Animations (CRITICAL: Required for .scroll-reveal elements to show)
    const observerOptions = { threshold: 0.1, rootMargin: '0px 0px -50px 0px' };
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    const revealElements = document.querySelectorAll('.scroll-reveal');
    revealElements.forEach(el => observer.observe(el));

    // Fallback for animations
    setTimeout(() => {
        revealElements.forEach(el => {
            if (!el.classList.contains('animate-in')) el.classList.add('animate-in');
        });
    }, 800);

    // 6. Dashboard Summary Helper
    function updateDashboardSummary() {
        const summaryContainer = document.getElementById('dashboard-summary-content');
        if (!summaryContainer) return;

        const profitData = AppStorage.load('profit_data') || [];
        if (profitData.length === 0) {
            summaryContainer.innerHTML = '<p class="text-slate-500 text-sm">기록된 수익 데이터가 없습니다. 로그인하여 내역을 추가해 보세요.</p>';
            return;
        }

        const totalProfit = profitData.reduce((acc, d) => acc + (Number(d.amount) || 0), 0);
        const totalEntry = profitData.reduce((acc, d) => acc + (Number(d.entry) || 0), 0);
        const totalWinners = profitData.reduce((acc, d) => acc + (Number(d.winners) || 0), 0);
        const rate = totalEntry > 0 ? ((totalWinners / totalEntry) * 100).toFixed(1) : 0;

        summaryContainer.innerHTML = `
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div class="p-6 rounded-3xl bg-indigo-500/5 border border-indigo-500/10">
                    <p class="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">총 누적 수익</p>
                    <p class="text-2xl font-black text-indigo-500">₩${totalProfit.toLocaleString()}</p>
                </div>
                <div class="p-6 rounded-3xl bg-emerald-500/5 border border-emerald-500/10">
                    <p class="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">평균 성공률</p>
                    <p class="text-2xl font-black text-emerald-500">${rate}%</p>
                </div>
                <div class="p-6 rounded-3xl bg-pink-500/5 border border-pink-500/10">
                    <p class="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">최근 활동</p>
                    <p class="text-sm font-bold text-white truncate">${profitData[0].item}</p>
                </div>
            </div>
        `;
    }
});
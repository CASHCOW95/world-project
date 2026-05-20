document.addEventListener('DOMContentLoaded', () => {
    // 1. Initial Visibility Fix
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.style.opacity = '1';
    }

    // 2. Authentication Logic
    const protectedPages = ['online-meetup.html', 'profile-mgmt.html', 'offline-meetup.html', 'gifticon-mgmt.html'];
    const pathParts = window.location.pathname.split('/');
    const currentPage = pathParts[pathParts.length - 1] || 'index.html';
    const isLoggedIn = sessionStorage.getItem('isAdminLoggedIn') === 'true';
    const adminNickname = sessionStorage.getItem('adminNickname');

    if (protectedPages.includes(currentPage) && !isLoggedIn) {
        document.body.classList.add('auth-locked');
        const lockUI = document.createElement('div');
        lockUI.id = 'access-denied-message';
        lockUI.className = 'glass-card p-10 rounded-[2.5rem] border border-white/10 shadow-2xl animate-in';
        lockUI.innerHTML = `
            <div class="text-6xl mb-6">🔒</div>
            <h2 class="text-2xl font-black mb-4 text-white">접근 권한이 없습니다</h2>
            <p class="text-slate-400 text-sm mb-8 leading-relaxed">해당 서비스는 관리자 로그인이 필요합니다.<br>관리자 계정으로 로그인 후 다시 시도해주세요.</p>
            <div class="flex gap-3 justify-center">
                <a href="index.html" class="px-6 py-3 rounded-xl bg-white/10 hover:bg-white/20 text-white font-bold transition text-sm">홈으로</a>
                <a href="login.html?redirect=${currentPage}" class="px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold transition text-sm shadow-lg shadow-indigo-500/20">관리자 로그인</a>
            </div>
        `;
        document.body.appendChild(lockUI);
        if(mainContent) mainContent.style.display = 'none'; // Completely hide protected content
        return;
    }

    // 3. Update Header UI for Auth
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
            authBtn.addEventListener('click', () => {
                window.location.href = 'login.html';
            });
        }
    }

    // 4. Theme Logic
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const html = document.documentElement;

    const savedTheme = localStorage.getItem('theme') || 'dark';
    if (savedTheme === 'light') {
        html.classList.remove('dark');
        if(themeIcon) themeIcon.textContent = '☀️';
    } else {
        html.classList.add('dark');
        if(themeIcon) themeIcon.textContent = '🌙';
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const isDark = html.classList.toggle('dark');
            if(themeIcon) themeIcon.textContent = isDark ? '🌙' : '☀️';
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
        });
    }

    // 5. Scroll Animations (Intersection Observer)
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    const revealElements = document.querySelectorAll('.scroll-reveal');
    revealElements.forEach(el => {
        observer.observe(el);
    });

    // Fallback: If elements are still not visible after 1s, force them (handles cases where observer might fail)
    setTimeout(() => {
        revealElements.forEach(el => {
            if (!el.classList.contains('animate-in')) {
                el.classList.add('animate-in');
            }
        });
    }, 1000);

    // 6. Header scroll effect
    const header = document.querySelector('header');
    if (header) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                header.classList.add('py-2', 'bg-white/80', 'dark:bg-[#030509]/60');
                header.classList.remove('py-3.5', 'bg-white/60', 'dark:bg-[#030509]/30');
            } else {
                header.classList.remove('py-2', 'bg-white/80', 'dark:bg-[#030509]/60');
                header.classList.add('py-3.5', 'bg-white/60', 'dark:bg-[#030509]/30');
            }
        });
    }
});
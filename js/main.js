document.addEventListener('DOMContentLoaded', () => {
    // Authentication Check
    const protectedPages = ['online-meetup.html', 'profile-mgmt.html', 'offline-meetup.html', 'gifticon-mgmt.html'];
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
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
        // Ensure header is still visible if needed, but usually we want full lock
        return;
    }

    // Ensure content is visible
    document.body.classList.remove('page-loading');
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.style.opacity = '1';
    }

    // Update Header UI for Auth
    const authBtn = document.querySelector('.open-auth');
    if (authBtn) {
        if (isLoggedIn) {
            authBtn.innerHTML = `<span class="text-indigo-500 font-black mr-2">●</span> ${adminNickname} 관리자`;
            authBtn.classList.replace('open-auth', 'admin-profile');
            
            // Add Logout Button
            const logoutBtn = document.createElement('button');
            logoutBtn.className = 'px-4 py-1.5 rounded-full border border-red-500/20 text-red-500 hover:bg-red-500 hover:text-white transition text-[11px] font-bold';
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

    // Theme Logic
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const html = document.documentElement;

    // Load saved theme or default to dark
    const savedTheme = localStorage.getItem('theme') || 'dark';
    if (savedTheme === 'light') {
        html.classList.remove('dark');
        themeIcon.textContent = '☀️';
    } else {
        html.classList.add('dark');
        themeIcon.textContent = '🌙';
    }

    themeToggle.addEventListener('click', () => {
        const isDark = html.classList.toggle('dark');
        themeIcon.textContent = isDark ? '🌙' : '☀️';
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });

    // Modal Logic
    const authModal = document.getElementById('auth-modal');
    const openAuthBtns = document.querySelectorAll('.open-auth');
    const closeModalBtn = document.querySelector('.close-modal');

    const openModal = () => {
        authModal.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent scrolling
    };

    const closeModal = () => {
        authModal.classList.remove('active');
        document.body.style.overflow = ''; // Restore scrolling
    };

    openAuthBtns.forEach(btn => btn.addEventListener('click', openModal));
    closeModalBtn.addEventListener('click', closeModal);

    // Close on outside click
    window.addEventListener('click', (e) => {
        if (e.target === authModal) closeModal();
    });

    // Close on Escape key
    window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && authModal.classList.contains('active')) {
            closeModal();
        }
    });

    // Scroll Animations (Intersection Observer)
    const observerOptions = {
        threshold: 0.15,
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

    document.querySelectorAll('.scroll-reveal').forEach(el => {
        observer.observe(el);
    });

    // Header scroll effect
    const header = document.querySelector('header');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            header.classList.add('py-2', 'bg-white/80', 'dark:bg-[#030509]/60');
            header.classList.remove('py-3.5', 'bg-white/60', 'dark:bg-[#030509]/30');
        } else {
            header.classList.remove('py-2', 'bg-white/80', 'dark:bg-[#030509]/60');
            header.classList.add('py-3.5', 'bg-white/60', 'dark:bg-[#030509]/30');
        }
    });

    // Feature Modal Logic
    window.openFeatureModal = (modalId) => {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    };

    const closeFeatureModals = () => {
        document.querySelectorAll('.feature-modal').forEach(modal => {
            modal.classList.remove('active');
        });
        document.body.style.overflow = '';
    };

    document.querySelectorAll('.close-feature').forEach(btn => {
        btn.addEventListener('click', closeFeatureModals);
    });

    // Close feature modals on outside click
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('feature-modal')) {
            closeFeatureModals();
        }
    });

    // Basic File Upload Previews
    const excelUpload = document.getElementById('excel-upload');
    const gifticonUpload = document.getElementById('gifticon-upload');

    if (excelUpload) {
        excelUpload.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                alert(`'${file.name}' 파일이 선택되었습니다. 엑셀 분석 로직을 연동할 수 있습니다.`);
                document.getElementById('excel-preview').classList.remove('hidden');
            }
        });
    }

    if (gifticonUpload) {
        gifticonUpload.addEventListener('change', (e) => {
            const files = e.target.files;
            const grid = document.getElementById('gifticon-grid');
            if (files.length > 0) {
                grid.innerHTML = ''; // Clear placeholder
                Array.from(files).forEach(file => {
                    const reader = new FileReader();
                    reader.onload = (event) => {
                        const div = document.createElement('div');
                        div.className = 'aspect-square rounded-xl overflow-hidden border border-black/5 dark:border-white/10';
                        div.innerHTML = `<img src="${event.target.result}" class="w-full h-full object-cover">`;
                        grid.appendChild(div);
                    };
                    reader.readAsDataURL(file);
                });
            }
        });
    }
});


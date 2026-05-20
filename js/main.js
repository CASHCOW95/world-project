document.addEventListener('DOMContentLoaded', () => {
    // Theme Logic
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const body = document.body;

    const currentTheme = localStorage.getItem('theme') || 'dark';
    if (currentTheme === 'light') {
        body.classList.add('light-mode');
        themeIcon.textContent = '☀️';
    }

    themeToggle.addEventListener('click', () => {
        body.classList.toggle('light-mode');
        const isLight = body.classList.contains('light-mode');
        themeIcon.textContent = isLight ? '☀️' : '🌙';
        localStorage.setItem('theme', isLight ? 'light' : 'dark');
    });

    // Modal Logic
    const authModal = document.getElementById('auth-modal');
    const openAuthBtns = document.querySelectorAll('.open-auth');
    const closeModal = document.querySelector('.close-modal');

    openAuthBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            authModal.classList.add('active');
        });
    });

    closeModal.addEventListener('click', () => {
        authModal.classList.remove('active');
    });

    window.addEventListener('click', (e) => {
        if (e.target === authModal) {
            authModal.classList.remove('active');
        }
    });

    // Scroll Animations (AOS replacement simple logic)
    const observerOptions = {
        threshold: 0.1
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
});

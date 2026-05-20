document.addEventListener('DOMContentLoaded', () => {
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
});


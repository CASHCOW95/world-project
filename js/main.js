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

    // Force Dark Mode only
    const html = document.documentElement;
    html.classList.add('dark');
    localStorage.setItem('theme', 'dark');

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
            if (featureType === 'download' || featureType === 'feedback') return; // Allow public download and feedback access

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

        // 9. Value Simulator & ROI Calculator Sliders
        const hoursSlider = document.getElementById('hours-slider');
        const costSlider = document.getElementById('cost-slider');
        const hoursValDisplay = document.getElementById('hours-val-display');
        const costValDisplay = document.getElementById('cost-val-display');
        const timeSavedDisplay = document.getElementById('time-saved-display');
        const moneySavedDisplay = document.getElementById('money-saved-display');

        if (hoursSlider && costSlider) {
            const updateROI = () => {
                const hours = parseInt(hoursSlider.value);
                const cost = parseInt(costSlider.value);

                if (hoursValDisplay) hoursValDisplay.innerText = `${hours}시간`;
                if (costValDisplay) costValDisplay.innerText = `${cost}만원`;

                // Calculate savings
                const timeSaved = Math.round(hours * 338.33);
                const moneySaved = Math.round((cost * 12) + (timeSaved * 2.65));

                if (timeSavedDisplay) {
                    timeSavedDisplay.innerHTML = `<span>${timeSaved.toLocaleString()}</span> <span class="text-base font-bold text-cyan-600 dark:text-cyan-500">시간 확보</span>`;
                }
                if (moneySavedDisplay) {
                    moneySavedDisplay.innerHTML = `<span class="text-base text-amber-600 dark:text-amber-500 font-black">~</span> <span>${moneySaved.toLocaleString()}</span> <span class="text-base font-bold text-amber-600 dark:text-amber-500">만원 세이브</span>`;
                }
            };

            hoursSlider.addEventListener('input', updateROI);
            costSlider.addEventListener('input', updateROI);
            updateROI(); // Initial run
        }

        updateDashboardSummary();
    }

    // 7. Feedback Modal Logic
    const feedbackModal = document.getElementById('feedback-modal');
    const openFeedbackBtn = document.getElementById('open-feedback');
    const navFeedbackBtn = document.getElementById('nav-feedback');
    const closeFeedbackBtn = document.getElementById('close-feedback');
    const submitFeedbackBtn = document.getElementById('submit-feedback');

    const openFeedback = (e) => {
        if (e) e.preventDefault();
        if (feedbackModal) feedbackModal.classList.add('active');
    };

    if (openFeedbackBtn) openFeedbackBtn.addEventListener('click', openFeedback);
    if (navFeedbackBtn) navFeedbackBtn.addEventListener('click', openFeedback);

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

    // ========================================================
    // 서버 운영센터 (Server Ops Center)
    // ========================================================
    (function initServerOps() {
        // 환경변수 기반 URL (Cloudflare Pages에서는 빌드 시 주입, 로컬에서는 기본값 사용)
        const MAC_MINI_DASHBOARD_URL = window.PUBLIC_MAC_MINI_DASHBOARD_URL || 'http://macmini:8000';
        const MAC_MINI_HEALTH_URL = window.PUBLIC_MAC_MINI_HEALTH_URL || 'http://macmini:8000/health';

        // DOM 요소
        const statusDot = document.getElementById('ops-status-dot');
        const statusText = document.getElementById('ops-status-text');
        const lastCheckEl = document.getElementById('ops-last-check');
        const uptimeEl = document.getElementById('ops-uptime');
        const checkHealthBtn = document.getElementById('ops-check-health');
        const openHealthLink = document.getElementById('ops-open-health');
        const openDashboard = document.getElementById('ops-open-dashboard');
        const refreshWorkersBtn = document.getElementById('ops-refresh-workers');
        const openRecoveryBtn = document.getElementById('ops-open-recovery');
        const recoveryModal = document.getElementById('recovery-modal');
        const closeRecoveryBtn = document.getElementById('close-recovery');
        const closeRecoveryBottomBtn = document.getElementById('close-recovery-bottom');
        const workersRunningEl = document.getElementById('ops-workers-running');
        const workersErrorEl = document.getElementById('ops-workers-error');

        if (!statusDot) return; // 서버 운영센터가 없는 페이지에서는 종료

        // 링크에 URL 바인딩
        if (openHealthLink) openHealthLink.href = MAC_MINI_HEALTH_URL;
        if (openDashboard) openDashboard.href = MAC_MINI_DASHBOARD_URL;

        // 상태 업데이트 함수
        function setStatus(state, responseTime) {
            const now = new Date();
            const timeStr = now.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });

            statusDot.className = 'ops-status-dot ' + state;
            if (lastCheckEl) lastCheckEl.textContent = timeStr;

            if (state === 'online') {
                statusText.textContent = 'ONLINE';
                statusText.style.color = '#4ade80';
                if (uptimeEl) uptimeEl.textContent = responseTime ? `${responseTime}ms` : '정상';
            } else if (state === 'offline') {
                statusText.textContent = 'OFFLINE';
                statusText.style.color = '#f87171';
                if (uptimeEl) uptimeEl.textContent = '응답 없음';
            } else {
                statusText.textContent = 'CHECKING';
                statusText.style.color = '#fbbf24';
                if (uptimeEl) uptimeEl.textContent = '확인 중...';
            }
        }

        // 워커 상태 업데이트 함수
        function updateWorkers(data) {
            if (!data || !data.workers) return;

            const workerList = document.getElementById('ops-worker-list');
            if (!workerList) return;

            let runningCount = 0;
            let errorCount = 0;
            const workerNames = ['크롤러', '블로그', '유튜브', 'ADB'];
            const workerKeys = ['crawler', 'blog', 'youtube', 'adb'];

            const rows = workerList.querySelectorAll('.ops-worker-row');
            workerKeys.forEach((key, i) => {
                const workerState = data.workers[key] || 'idle';
                if (workerState === 'running') runningCount++;
                if (workerState === 'error') errorCount++;

                if (rows[i]) {
                    const badge = rows[i].querySelector('.ops-worker-badge');
                    if (badge) {
                        badge.className = 'ops-worker-badge ' + workerState;
                        badge.textContent = workerState.toUpperCase();
                    }
                }
            });

            if (workersRunningEl) workersRunningEl.textContent = runningCount;
            if (workersErrorEl) workersErrorEl.textContent = errorCount;
        }

        // 상태 확인 및 워커 새로고침 통합 함수
        async function fetchHealth() {
            setStatus('checking');
            if (checkHealthBtn) {
                checkHealthBtn.disabled = true;
                checkHealthBtn.textContent = '⏳ 확인 중...';
            }
            if (refreshWorkersBtn) {
                refreshWorkersBtn.disabled = true;
                refreshWorkersBtn.textContent = '⏳ 확인 중...';
            }

            const startTime = performance.now();
            try {
                const controller = new AbortController();
                const timeout = setTimeout(() => controller.abort(), 8000);

                const res = await fetch(MAC_MINI_HEALTH_URL, {
                    signal: controller.signal,
                    mode: 'cors'
                });
                clearTimeout(timeout);

                const elapsed = Math.round(performance.now() - startTime);

                if (res.ok) {
                    setStatus('online', elapsed);
                    try {
                        const data = await res.json();
                        updateWorkers(data);
                    } catch (_) {
                        // JSON 파싱 실패해도 ONLINE은 유지
                    }
                } else {
                    setStatus('offline');
                }
            } catch (err) {
                setStatus('offline');
            }

            if (checkHealthBtn) {
                checkHealthBtn.disabled = false;
                checkHealthBtn.textContent = '🔍 상태 확인';
            }
            if (refreshWorkersBtn) {
                refreshWorkersBtn.disabled = false;
                refreshWorkersBtn.textContent = '🔄 워커 상태 새로고침';
            }
        }

        if (checkHealthBtn) {
            checkHealthBtn.addEventListener('click', fetchHealth);
        }
        if (refreshWorkersBtn) {
            refreshWorkersBtn.addEventListener('click', fetchHealth);
        }

        // 복구 안내 모달
        const openRecovery = () => { if (recoveryModal) recoveryModal.classList.add('active'); };
        const closeRecovery = () => { if (recoveryModal) recoveryModal.classList.remove('active'); };

        if (openRecoveryBtn) openRecoveryBtn.addEventListener('click', openRecovery);
        if (closeRecoveryBtn) closeRecoveryBtn.addEventListener('click', closeRecovery);
        if (closeRecoveryBottomBtn) closeRecoveryBottomBtn.addEventListener('click', closeRecovery);

        // 모달 배경 클릭 시 닫기
        if (recoveryModal) {
            recoveryModal.addEventListener('click', (e) => {
                if (e.target === recoveryModal) closeRecovery();
            });
        }
    })();
});
(function () {
  const STORAGE_PREFIX = 'world_ai_';
  const PROTECTED_PAGES = new Set([
    'meetup-calendar.html',
    'asset-mgmt.html',
    'profit-mgmt.html',
    'diary.html',
    'tiktok-mgmt.html',
    'timer.html',
    'online-meetup.html',
    'profile-mgmt.html',
    'offline-meetup.html',
    'gifticon-mgmt.html',
  ]);
  const PUBLIC_FEATURES = new Set(['download', 'feedback']);
  const OPS_DEFAULTS = {
    dashboardUrl: window.PUBLIC_MAC_MINI_DASHBOARD_URL || 'http://macmini:8000',
    healthUrl: window.PUBLIC_MAC_MINI_HEALTH_URL || 'http://macmini:8000/health',
    timeoutMs: 8000,
  };

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

  window.AppStorage = {
    save(key, data) {
      localStorage.setItem(`${STORAGE_PREFIX}${key}`, JSON.stringify(data));
      showToast('데이터가 저장되었습니다.');
    },
    load(key, fallback = null) {
      try {
        const raw = localStorage.getItem(`${STORAGE_PREFIX}${key}`);
        return raw ? JSON.parse(raw) : fallback;
      } catch (error) {
        console.warn(`Failed to load ${key} from localStorage`, error);
        return fallback;
      }
    },
  };

  function getCurrentPage() {
    const pathParts = window.location.pathname.split('/');
    return pathParts[pathParts.length - 1] || 'index.html';
  }

  function getAuthState() {
    return {
      isLoggedIn: sessionStorage.getItem('isAdminLoggedIn') === 'true',
      nickname: sessionStorage.getItem('adminNickname') || 'Admin',
    };
  }

  function showToast(message, type = 'info') {
    const existing = $('#app-toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.id = 'app-toast';
    toast.className = `app-toast app-toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    requestAnimationFrame(() => toast.classList.add('is-visible'));
    window.setTimeout(() => {
      toast.classList.remove('is-visible');
      window.setTimeout(() => toast.remove(), 250);
    }, 2600);
  }

  function forceVisibleDarkTheme() {
    document.body.style.opacity = '1';
    document.documentElement.classList.add('dark');
    localStorage.setItem('theme', 'dark');

    const main = $('main');
    if (main) {
      main.style.opacity = '1';
      main.style.visibility = 'visible';
    }
  }

  function guardProtectedPage(currentPage, auth) {
    if (!PROTECTED_PAGES.has(currentPage) || auth.isLoggedIn) return false;
    window.location.href = `login.html?redirect=${encodeURIComponent(currentPage)}`;
    return true;
  }

  function initAuthUi(auth) {
    const authBtn = $('.open-auth');
    if (!authBtn) return;

    if (!auth.isLoggedIn) {
      authBtn.addEventListener('click', () => {
        window.location.href = 'login.html';
      });
      return;
    }

    authBtn.innerHTML = `<span class="text-indigo-500 font-black mr-2">●</span> ${auth.nickname} 관리자`;
    authBtn.classList.remove('open-auth');
    authBtn.classList.add('admin-profile');

    if ($('.admin-logout')) return;
    const logoutBtn = document.createElement('button');
    logoutBtn.type = 'button';
    logoutBtn.className = 'admin-logout px-4 py-1.5 rounded-full border border-red-500/20 text-red-500 hover:bg-red-500 hover:text-white transition text-[11px] font-bold ml-2';
    logoutBtn.textContent = 'LOGOUT';
    logoutBtn.addEventListener('click', () => {
      sessionStorage.clear();
      window.location.href = 'index.html';
    });
    authBtn.parentNode.appendChild(logoutBtn);
  }

  function initFeatureLocks(auth, currentPage) {
    if (currentPage !== 'index.html') return;

    $$('.feature-card').forEach((card) => {
      const featureType = card.getAttribute('data-feature');
      if (PUBLIC_FEATURES.has(featureType) || auth.isLoggedIn) return;

      const lockOverlay = $('.lock-overlay', card);
      const icon = $('.feature-icon', card);
      card.setAttribute('aria-disabled', 'true');
      card.classList.add('is-locked');
      if (lockOverlay) {
        lockOverlay.style.opacity = '1';
        lockOverlay.style.pointerEvents = 'auto';
      }
      if (icon) icon.style.filter = 'grayscale(1) blur(4px)';

      card.addEventListener('click', (event) => {
        event.preventDefault();
        const wantsLogin = window.confirm('관리자 전용 서비스입니다. 로그인하시겠습니까?');
        if (wantsLogin) window.location.href = 'login.html';
      });
    });
  }

  function initRoiCalculator() {
    const hoursSlider = $('#hours-slider');
    const costSlider = $('#cost-slider');
    if (!hoursSlider || !costSlider) return;

    const nodes = {
      hours: $('#hours-val-display'),
      cost: $('#cost-val-display'),
      timeSaved: $('#time-saved-display'),
      moneySaved: $('#money-saved-display'),
    };

    const update = () => {
      const hours = Number.parseInt(hoursSlider.value, 10) || 0;
      const cost = Number.parseInt(costSlider.value, 10) || 0;
      const timeSaved = Math.round(hours * 338.33);
      const moneySaved = Math.round((cost * 12) + (timeSaved * 2.65));

      if (nodes.hours) nodes.hours.textContent = `${hours}시간`;
      if (nodes.cost) nodes.cost.textContent = `${cost}만원`;
      if (nodes.timeSaved) {
        nodes.timeSaved.innerHTML = `<span>${timeSaved.toLocaleString()}</span> <span class="text-base font-bold text-cyan-600 dark:text-cyan-500">시간 확보</span>`;
      }
      if (nodes.moneySaved) {
        nodes.moneySaved.innerHTML = `<span class="text-base text-amber-600 dark:text-amber-500 font-black">~</span> <span>${moneySaved.toLocaleString()}</span> <span class="text-base font-bold text-amber-600 dark:text-amber-500">만원 세이브</span>`;
      }
    };

    hoursSlider.addEventListener('input', update);
    costSlider.addEventListener('input', update);
    update();
  }

  function initDashboardSummary() {
    const container = $('#dashboard-summary-content');
    if (!container) return;

    const profitData = window.AppStorage.load('profit_data', []);
    if (!Array.isArray(profitData) || profitData.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <strong>수익 데이터 없음</strong>
          <span>아직 저장된 수익 기록이 없습니다. 수익정산 화면에서 첫 기록을 추가하면 요약이 표시됩니다.</span>
        </div>
      `;
      return;
    }

    const totalProfit = profitData.reduce((acc, item) => acc + (Number(item.amount) || 0), 0);
    const totalEntry = profitData.reduce((acc, item) => acc + (Number(item.entry) || 0), 0);
    const totalWinners = profitData.reduce((acc, item) => acc + (Number(item.winners) || 0), 0);
    const rate = totalEntry > 0 ? ((totalWinners / totalEntry) * 100).toFixed(1) : '0.0';

    container.innerHTML = `
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="summary-card">
          <p>총 누적 수익</p>
          <strong>₩${totalProfit.toLocaleString()}</strong>
        </div>
        <div class="summary-card summary-card-success">
          <p>평균 성공률</p>
          <strong>${rate}%</strong>
        </div>
        <div class="summary-card summary-card-muted">
          <p>최근 활동</p>
          <strong>${profitData[0]?.item || '기록 없음'}</strong>
        </div>
      </div>
    `;
  }

  function initFeedbackModal() {
    const modal = $('#feedback-modal');
    const openButtons = ['#open-feedback', '#nav-feedback'].map((selector) => $(selector)).filter(Boolean);
    const closeBtn = $('#close-feedback');
    const submitBtn = $('#submit-feedback');
    if (!modal) return;

    const open = (event) => {
      if (event) event.preventDefault();
      modal.classList.add('active');
      $('#feedback-title')?.focus();
    };
    const close = () => modal.classList.remove('active');

    openButtons.forEach((button) => button.addEventListener('click', open));
    closeBtn?.addEventListener('click', close);
    modal.addEventListener('click', (event) => {
      if (event.target === modal) close();
    });

    submitBtn?.addEventListener('click', () => {
      const title = $('#feedback-title')?.value.trim();
      const content = $('#feedback-content')?.value.trim();
      if (!title || !content) {
        showToast('제목과 내용을 모두 입력해 주세요.', 'error');
        return;
      }

      window.location.href = `mailto:ydh2455@naver.com?subject=${encodeURIComponent(`[문의] ${title}`)}&body=${encodeURIComponent(content)}`;
      close();
      showToast('메일 클라이언트를 여는 중입니다.');
    });
  }

  function initScrollReveal() {
    const revealElements = $$('.scroll-reveal');
    if (revealElements.length === 0) return;

    if (!('IntersectionObserver' in window)) {
      revealElements.forEach((element) => element.classList.add('animate-in'));
      return;
    }

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('animate-in');
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

    revealElements.forEach((element) => observer.observe(element));
    window.setTimeout(() => {
      revealElements.forEach((element) => element.classList.add('animate-in'));
    }, 900);
  }

  function setButtonBusy(button, busy, label) {
    if (!button) return;
    if (!button.dataset.idleLabel) button.dataset.idleLabel = button.textContent.trim();
    button.disabled = busy;
    button.classList.toggle('is-busy', busy);
    button.textContent = busy ? label : button.dataset.idleLabel;
  }

  async function fetchJsonWithTimeout(url, { timeoutMs = 8000 } = {}) {
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), timeoutMs);
    const startedAt = performance.now();

    try {
      const response = await fetch(url, { signal: controller.signal, mode: 'cors' });
      const elapsedMs = Math.round(performance.now() - startedAt);
      const contentType = response.headers.get('content-type') || '';
      const data = contentType.includes('application/json') ? await response.json() : null;

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      return { data, elapsedMs };
    } finally {
      window.clearTimeout(timer);
    }
  }

  function initServerOps() {
    const statusDot = $('#ops-status-dot');
    if (!statusDot) return;

    const nodes = {
      statusDot,
      statusText: $('#ops-status-text'),
      lastCheck: $('#ops-last-check'),
      uptime: $('#ops-uptime'),
      checkHealthBtn: $('#ops-check-health'),
      openHealthLink: $('#ops-open-health'),
      openDashboard: $('#ops-open-dashboard'),
      refreshWorkersBtn: $('#ops-refresh-workers'),
      openRecoveryBtn: $('#ops-open-recovery'),
      recoveryModal: $('#recovery-modal'),
      closeRecoveryBtn: $('#close-recovery'),
      closeRecoveryBottomBtn: $('#close-recovery-bottom'),
      workersRunning: $('#ops-workers-running'),
      workersError: $('#ops-workers-error'),
      workerList: $('#ops-worker-list'),
      panel: $('#server-ops .ops-center-panel'),
    };

    const alertEl = ensureOpsAlert(nodes.panel);
    if (nodes.openHealthLink) nodes.openHealthLink.href = OPS_DEFAULTS.healthUrl;
    if (nodes.openDashboard) nodes.openDashboard.href = OPS_DEFAULTS.dashboardUrl;

    const setAlert = (message, state = 'info') => {
      if (!alertEl) return;
      alertEl.textContent = message;
      alertEl.dataset.state = state;
      alertEl.hidden = !message;
    };

    const setStatus = (state, responseTime = null) => {
      const time = new Date().toLocaleTimeString('ko-KR', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      });

      nodes.statusDot.className = `ops-status-dot ${state}`;
      if (nodes.lastCheck) nodes.lastCheck.textContent = time;

      const statusMap = {
        online: ['ONLINE', '#4ade80', responseTime ? `${responseTime}ms` : '정상'],
        offline: ['OFFLINE', '#f87171', '응답 없음'],
        checking: ['CHECKING', '#fbbf24', '확인 중...'],
      };
      const [label, color, detail] = statusMap[state] || statusMap.offline;

      if (nodes.statusText) {
        nodes.statusText.textContent = label;
        nodes.statusText.style.color = color;
      }
      if (nodes.uptime) nodes.uptime.textContent = detail;
    };

    const updateWorkers = (data) => {
      const workers = data?.workers || {};
      const workerKeys = ['crawler', 'blog', 'youtube', 'adb'];
      const workerNames = ['크롤러', '블로그', '유튜브', 'ADB'];
      const rows = $$('.ops-worker-row', nodes.workerList || document);
      let runningCount = 0;
      let errorCount = 0;

      workerKeys.forEach((key, index) => {
        const state = workers[key] || 'idle';
        if (state === 'running') runningCount += 1;
        if (state === 'error') errorCount += 1;

        const row = rows[index];
        const badge = row ? $('.ops-worker-badge', row) : null;
        if (badge) {
          badge.className = `ops-worker-badge ${state}`;
          badge.textContent = state.toUpperCase();
          badge.setAttribute('title', `${workerNames[index]} 상태: ${state}`);
        }
      });

      if (nodes.workersRunning) nodes.workersRunning.textContent = String(runningCount);
      if (nodes.workersError) nodes.workersError.textContent = String(errorCount);
    };

    const checkHealth = async () => {
      setStatus('checking');
      setAlert('Mac mini 상태를 확인하는 중입니다.');
      setButtonBusy(nodes.checkHealthBtn, true, '확인 중...');
      setButtonBusy(nodes.refreshWorkersBtn, true, '확인 중...');

      try {
        const { data, elapsedMs } = await fetchJsonWithTimeout(OPS_DEFAULTS.healthUrl, { timeoutMs: OPS_DEFAULTS.timeoutMs });
        setStatus('online', elapsedMs);
        updateWorkers(data);
        setAlert('서버가 정상 응답했습니다.', 'success');
      } catch (error) {
        setStatus('offline');
        setAlert(`서버 상태 확인 실패: ${error.name === 'AbortError' ? '요청 시간이 초과되었습니다.' : error.message}`, 'error');
      } finally {
        setButtonBusy(nodes.checkHealthBtn, false);
        setButtonBusy(nodes.refreshWorkersBtn, false);
      }
    };

    nodes.checkHealthBtn?.addEventListener('click', checkHealth);
    nodes.refreshWorkersBtn?.addEventListener('click', checkHealth);
    initRecoveryModal(nodes);
    setAlert('대기 중입니다. 상태 확인 버튼을 눌러 서버 응답을 확인하세요.');
  }

  function ensureOpsAlert(panel) {
    if (!panel) return null;
    let alertEl = $('#ops-alert', panel);
    if (alertEl) return alertEl;

    alertEl = document.createElement('div');
    alertEl.id = 'ops-alert';
    alertEl.className = 'ops-alert';
    alertEl.setAttribute('role', 'status');
    alertEl.setAttribute('aria-live', 'polite');
    panel.appendChild(alertEl);
    return alertEl;
  }

  function initRecoveryModal(nodes) {
    const modal = nodes.recoveryModal;
    if (!modal) return;

    const open = () => modal.classList.add('active');
    const close = () => modal.classList.remove('active');

    nodes.openRecoveryBtn?.addEventListener('click', open);
    nodes.closeRecoveryBtn?.addEventListener('click', close);
    nodes.closeRecoveryBottomBtn?.addEventListener('click', close);
    modal.addEventListener('click', (event) => {
      if (event.target === modal) close();
    });
  }

  function initGlobalKeyboard() {
    document.addEventListener('keydown', (event) => {
      if (event.key !== 'Escape') return;
      $$('.modal.active').forEach((modal) => modal.classList.remove('active'));
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    const currentPage = getCurrentPage();
    const auth = getAuthState();

    forceVisibleDarkTheme();
    if (guardProtectedPage(currentPage, auth)) return;

    initAuthUi(auth);
    initFeatureLocks(auth, currentPage);
    initRoiCalculator();
    initDashboardSummary();
    initFeedbackModal();
    initScrollReveal();
    initServerOps();
    initGlobalKeyboard();
  });
})();

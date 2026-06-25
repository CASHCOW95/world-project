import React, { useState, useEffect } from 'react';
import { Settings, HelpCircle, Heart } from 'lucide-react';
import { useTimer } from './hooks/useTimer';
import TimerDisplay from './components/TimerDisplay';
import TimerControls from './components/TimerControls';
import SettingsModal from './components/SettingsModal';
import StatsPanel from './components/StatsPanel';
import StylerDashboard from './components/StylerDashboard';

/**
 * Main App Component
 * Integrates hooks, layouts, glass cards, and the Kodari AI status banner.
 */
export default function App() {
  const {
    timeLeft,
    isRunning,
    mode,
    focusDuration,
    breakDuration,
    history,
    start,
    pause,
    reset,
    skip,
    updateSettings,
    clearHistory
  } = useTimer();

  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [currentView, setCurrentView] = useState(() => {
    const params = new URLSearchParams(window.location.search);
    return params.get('view') === 'styler' ? 'styler' : 'timer';
  });
  const hasViewParam = new URLSearchParams(window.location.search).has('view');
  const isFocus = mode === 'focus';

  // Secure redirect if user is not logged in as admin
  useEffect(() => {
    const isLoggedIn = sessionStorage.getItem('isAdminLoggedIn') === 'true';
    if (!isLoggedIn) {
      const view = new URLSearchParams(window.location.search).get('view') || 'timer';
      window.location.href = `../login.html?redirect=workspace/index.html?view=${view}`;
    }
  }, []);

  // Dynamic Kodari Assistant configuration based on timer state
  const getKodariStatus = () => {
    if (currentView === 'styler') {
      return {
        avatar: "https://raw.githubusercontent.com/wonseokjung/solopreneur-ai-agents/main/agents/kodari/assets/kodari_typing.png",
        message: "대표님, 키워드만 입력해 주십시오! 복잡한 블로그 원고 작성과 가독성 편집은 코다리가 한 번에 해내겠습니다! 🫡✍️",
        statusClass: "border-indigo-500/25 bg-indigo-950/20 text-indigo-300"
      };
    }

    if (isFocus) {
      if (isRunning) {
        return {
          avatar: "https://raw.githubusercontent.com/wonseokjung/solopreneur-ai-agents/main/agents/kodari/assets/kodari_typing.png",
          message: "대표님, 지금은 고도의 몰입 시간입니다! 코다리가 타이머 지키고 있으니 집중하시죠! 🔥🚀",
          statusClass: "border-violet-500/25 bg-violet-950/20 text-violet-300"
        };
      } else {
        return {
          avatar: "https://raw.githubusercontent.com/wonseokjung/solopreneur-ai-agents/main/agents/kodari/assets/kodari_thinking.png",
          message: "집중할 준비가 되셨다면 재생 버튼을 눌러주십시오! 코다리 대기 중입니다. 😎",
          statusClass: "border-slate-800 bg-slate-900/40 text-slate-300"
        };
      }
    } else {
      return {
        avatar: "https://raw.githubusercontent.com/wonseokjung/solopreneur-ai-agents/main/agents/kodari/assets/kodari_coffee.png",
        message: "대표님, 훌륭한 몰입이었습니다! 커피 한 잔 하시면서 푹 쉬십시오! ☕🫡",
        statusClass: "border-emerald-500/25 bg-emerald-950/20 text-emerald-300"
      };
    }
  };

  const kodari = getKodariStatus();

  return (
    <div className="min-h-screen relative flex flex-col items-center justify-center p-4 bg-slate-950 overflow-hidden">
      
      {/* Background Decorative Glowing Blobs */}
      <div className="absolute top-1/4 left-1/4 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] rounded-full bg-violet-600/10 blur-[100px] pointer-events-none transition-all duration-1000" />
      <div className="absolute bottom-1/4 right-1/4 translate-x-1/2 translate-y-1/2 w-[400px] h-[400px] rounded-full bg-emerald-600/10 blur-[100px] pointer-events-none transition-all duration-1000" />

      {/* Main Container */}
      <main className={`w-full z-10 flex flex-col gap-4 transition-all duration-500 ${currentView === 'styler' ? 'max-w-7xl' : 'max-w-md'}`}>
        
        {/* App Bar / Header */}
        <header className="flex items-center justify-between px-2">
          <div className="flex items-center gap-2">
            <span className="text-xl font-bold tracking-tight text-white">
              Antigravity <span className={`transition-colors duration-500 ${isFocus ? 'text-violet-400' : 'text-emerald-400'}`}>Workspace</span>
            </span>
            <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full border border-slate-700/50">v2.0</span>
          </div>

          <button
            onClick={() => setIsSettingsOpen(true)}
            className="p-2 rounded-xl glass-panel text-slate-400 hover:text-white transition-all duration-200 focus:outline-none hover:scale-105 active:scale-95"
            title="Open Settings"
          >
            <Settings size={18} />
          </button>
        </header>

        {/* View Switcher Tab bar */}
        {!hasViewParam && (
          <nav className="flex bg-slate-900/60 p-1.5 rounded-2xl border border-slate-850 gap-1.5 shadow-inner">
            <button
              onClick={() => setCurrentView('timer')}
              className={`flex-1 py-2.5 rounded-xl text-xs font-bold transition-all ${currentView === 'timer' ? 'bg-violet-600 text-white shadow-lg' : 'text-slate-400 hover:text-slate-200'}`}
            >
              ⏱️ 몰입 타이머
            </button>
            <button
              onClick={() => setCurrentView('styler')}
              className={`flex-1 py-2.5 rounded-xl text-xs font-bold transition-all ${currentView === 'styler' ? 'bg-violet-600 text-white shadow-lg' : 'text-slate-400 hover:text-slate-200'}`}
            >
              ✍️ 스타일러 프로
            </button>
          </nav>
        )}

        {/* Kodari Assistant Status Block */}
        <section className={`flex items-center gap-3.5 p-3 rounded-2xl border transition-all duration-700 ${kodari.statusClass}`}>
          <img 
            src={kodari.avatar} 
            alt="Kodari AI Avatar" 
            className="w-11 h-11 object-contain rounded-xl bg-slate-950/60 p-0.5 border border-slate-800/80 shadow-md"
          />
          <div className="flex-1 min-w-0">
            <div className="text-[10px] text-slate-500 font-bold tracking-wider uppercase">Kodari AI Assistant</div>
            <p className="text-xs font-medium leading-relaxed truncate-2-lines">{kodari.message}</p>
          </div>
        </section>

        {/* Dynamic View Rendering */}
        {currentView === 'timer' ? (
          <>
            {/* Primary Timer Card */}
            <section className="glass-card rounded-3xl p-6 shadow-2xl border border-slate-800/80">
              <TimerDisplay
                timeLeft={timeLeft}
                mode={mode}
                focusDuration={focusDuration}
                breakDuration={breakDuration}
                isRunning={isRunning}
              />

              <TimerControls
                isRunning={isRunning}
                onStart={start}
                onPause={pause}
                onReset={reset}
                onSkip={skip}
                mode={mode}
              />
            </section>

            {/* Activity & Stats Dashboard */}
            <section className="glass-card rounded-3xl p-5 shadow-xl border border-slate-800/60">
              <StatsPanel 
                history={history}
                onClearHistory={clearHistory}
              />
            </section>
          </>
        ) : (
          <StylerDashboard />
        )}

        {/* Footer */}
        <footer className="flex justify-center items-center gap-1.5 py-2 text-[10px] text-slate-600">
          <span>Made with</span>
          <Heart size={10} className="text-red-500 fill-red-500" />
          <span>for AI Solopreneurs by Kodari</span>
        </footer>

      </main>

      {/* Settings Dialog Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        focusDuration={focusDuration}
        breakDuration={breakDuration}
        onSave={updateSettings}
      />
    </div>
  );
}

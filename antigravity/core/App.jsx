import React, { useEffect } from 'react';
import { Heart } from 'lucide-react';
import StylerDashboard from './components/StylerDashboard';

/**
 * Main App Component
 * Integrates layouts, glass cards, and the Kodari AI status banner for AI Blog Publishing Agent.
 */
export default function App() {
  // Secure redirect if user is not logged in as admin
  useEffect(() => {
    // 로컬 호스트 환경의 개발 편의를 위해 자동 로그인 플래그를 주입합니다.
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      sessionStorage.setItem('isAdminLoggedIn', 'true');
    }
    const isLoggedIn = sessionStorage.getItem('isAdminLoggedIn') === 'true';
    if (!isLoggedIn) {
      window.location.href = `../login.html?redirect=workspace/index.html?view=styler`;
    }
  }, []);

  // Dynamic Kodari Assistant configuration
  const kodari = {
    avatar: "https://raw.githubusercontent.com/wonseokjung/solopreneur-ai-agents/main/agents/kodari/assets/kodari_typing.png",
    message: "대표님, 키워드만 입력해 주십시오! 복잡한 블로그 원고 작성과 가독성 편집은 코다리가 한 번에 해내겠습니다! 🫡✍️",
    statusClass: "border-indigo-500/25 bg-indigo-950/20 text-indigo-300"
  };

  return (
    <div className="min-h-screen relative flex flex-col items-center justify-center p-4 bg-slate-950 overflow-hidden">
      
      {/* Background Decorative Glowing Blobs */}
      <div className="absolute top-1/4 left-1/4 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] rounded-full bg-violet-600/10 blur-[100px] pointer-events-none transition-all duration-1000" />
      <div className="absolute bottom-1/4 right-1/4 translate-x-1/2 translate-y-1/2 w-[400px] h-[400px] rounded-full bg-emerald-600/10 blur-[100px] pointer-events-none transition-all duration-1000" />

      {/* Main Container */}
      <main className="w-full z-10 flex flex-col gap-4 transition-all duration-500 max-w-7xl">
        
        {/* App Bar / Header */}
        <header className="flex items-center justify-between px-2">
          <div className="flex items-center gap-2">
            <span className="text-xl font-bold tracking-tight text-white">
              AI 블로그 <span className="transition-colors duration-500 text-indigo-400">자동발행</span>
            </span>
            <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full border border-slate-700/50">v1.0.0</span>
          </div>
        </header>

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

        {/* Styler Dashboard View */}
        <StylerDashboard />

        {/* Footer */}
        <footer className="flex justify-center items-center gap-1.5 py-2 text-[10px] text-slate-600">
          <span>Made with</span>
          <Heart size={10} className="text-red-500 fill-red-500" />
          <span>for AI Solopreneurs by Kodari</span>
        </footer>

      </main>
    </div>
  );
}

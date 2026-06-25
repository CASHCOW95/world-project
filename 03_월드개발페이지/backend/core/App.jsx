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

  return (
    <div className="min-h-screen relative flex flex-col items-center justify-start p-4 bg-slate-950 overflow-y-auto">
      
      {/* Background Decorative Glow */}
      <div className="absolute top-1/4 left-1/3 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] rounded-full bg-indigo-500/5 blur-[120px] pointer-events-none" />

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

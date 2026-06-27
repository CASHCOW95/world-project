import React, { useEffect, useState } from 'react';
import { Cpu, PenTool } from 'lucide-react';

import OriginalStylerDashboard from './OriginalStylerDashboard';
import V2AgentDashboard from './V2AgentDashboard';

const DASHBOARD_MODES = {
  styler: {
    label: '원고 자동 집필기',
    icon: PenTool,
    component: OriginalStylerDashboard,
  },
  agent: {
    label: '에이전트 운영센터',
    icon: Cpu,
    component: V2AgentDashboard,
  },
};

function ModeButton({ mode, activeMode, onSelect }) {
  const config = DASHBOARD_MODES[mode];
  const Icon = config.icon;
  const isActive = activeMode === mode;

  return (
    <button
      type="button"
      onClick={() => onSelect(mode)}
      aria-pressed={isActive}
      className={`flex-1 rounded-xl px-3 py-2.5 text-xs font-black transition-all flex items-center justify-center gap-1.5 ${
        isActive
          ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20'
          : 'text-slate-400 hover:bg-slate-850 hover:text-slate-200'
      }`}
    >
      <Icon size={14} />
      {config.label}
    </button>
  );
}

export default function StylerDashboard() {
  const [dashboardMode, setDashboardMode] = useState('styler');
  const ActiveDashboard = DASHBOARD_MODES[dashboardMode].component;

  useEffect(() => {
    document.documentElement.dataset.theme = 'dark';
    localStorage.setItem('styler_theme_mode', 'dark');
  }, []);

  return (
    <div className="flex w-full flex-col gap-4">
      <div className="mx-auto flex w-full max-w-md gap-1.5 rounded-2xl border border-slate-800/80 bg-slate-900/70 p-1.5 shadow-inner">
        <ModeButton mode="styler" activeMode={dashboardMode} onSelect={setDashboardMode} />
        <ModeButton mode="agent" activeMode={dashboardMode} onSelect={setDashboardMode} />
      </div>

      <ActiveDashboard />
    </div>
  );
}

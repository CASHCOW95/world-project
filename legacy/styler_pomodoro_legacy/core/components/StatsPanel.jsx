import React from 'react';
import { History, Trash2, Award, Clock } from 'lucide-react';

/**
 * StatsPanel component
 * Visualizes completed focus/break cycles and total focus time.
 */
export default function StatsPanel({ history, onClearHistory }) {
  // Aggregate stats
  const focusSessions = history.filter(item => item.type === 'focus');
  const breakSessions = history.filter(item => item.type === 'break');
  const totalFocusMinutes = focusSessions.reduce((acc, item) => acc + item.duration, 0);

  return (
    <div className="w-full space-y-4">
      {/* Summary Cards */}
      <div className="grid grid-cols-2 gap-3">
        {/* Total Focus Minutes */}
        <div className="flex items-center gap-3 p-3.5 rounded-2xl glass-panel border border-violet-500/10">
          <div className="p-2 rounded-xl bg-violet-500/10 text-violet-400">
            <Clock size={18} />
          </div>
          <div>
            <div className="text-[10px] text-slate-400 font-medium uppercase tracking-wider">Total Focus</div>
            <div className="text-sm font-semibold text-white font-mono">{totalFocusMinutes} mins</div>
          </div>
        </div>

        {/* Focus Counts */}
        <div className="flex items-center gap-3 p-3.5 rounded-2xl glass-panel border border-emerald-500/10">
          <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400">
            <Award size={18} />
          </div>
          <div>
            <div className="text-[10px] text-slate-400 font-medium uppercase tracking-wider">Completed</div>
            <div className="text-sm font-semibold text-white font-mono">
              {focusSessions.length} Focus / {breakSessions.length} Break
            </div>
          </div>
        </div>
      </div>

      {/* History Log */}
      <div className="p-4 rounded-2xl glass-panel">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2 text-slate-300 text-xs font-semibold uppercase tracking-wider">
            <History size={14} className="text-violet-400" />
            <span>Activity Log</span>
          </div>
          {history.length > 0 && (
            <button
              onClick={onClearHistory}
              title="Clear History"
              className="text-slate-500 hover:text-red-400 transition-colors duration-200"
            >
              <Trash2 size={14} />
            </button>
          )}
        </div>

        {history.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-6 text-center">
            <p className="text-xs text-slate-500 font-medium">No sessions logged yet.</p>
            <p className="text-[10px] text-slate-600 mt-0.5">Your progress will appear here.</p>
          </div>
        ) : (
          <div className="max-h-40 overflow-y-auto space-y-2 pr-1">
            {history.map((session) => (
              <div 
                key={session.id} 
                className="flex items-center justify-between p-2 rounded-lg bg-slate-900/50 border border-slate-800/50 text-xs hover:border-slate-800 transition-all duration-200"
              >
                <div className="flex items-center gap-2">
                  <span className={`w-1.5 h-1.5 rounded-full ${
                    session.type === 'focus' ? 'bg-violet-500 shadow-[0_0_8px_rgba(139,92,246,0.5)]' : 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]'
                  }`} />
                  <span className="font-semibold text-slate-200 capitalize">
                    {session.type === 'focus' ? 'Focus Session' : 'Short Break'}
                  </span>
                </div>
                <div className="flex items-center gap-3 text-slate-400 font-mono text-[10px]">
                  <span>{session.timeLabel}</span>
                  <span>{session.timestamp}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

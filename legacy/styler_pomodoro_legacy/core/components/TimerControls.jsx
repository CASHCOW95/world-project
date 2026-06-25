import React from 'react';
import { Play, Pause, RotateCcw, SkipForward } from 'lucide-react';

/**
 * TimerControls component
 * Handles triggering start, pause, reset, and skip actions.
 */
export default function TimerControls({ isRunning, onStart, onPause, onReset, onSkip, mode }) {
  const isFocus = mode === 'focus';
  
  return (
    <div className="flex items-center justify-center gap-6 mt-4">
      {/* Reset button */}
      <button
        onClick={onReset}
        title="Reset Timer"
        className="p-3.5 rounded-full glass-panel text-gray-400 hover:text-white hover:scale-105 hover:bg-slate-800/60 active:scale-95 transition-all duration-300 focus:outline-none"
      >
        <RotateCcw size={20} />
      </button>

      {/* Main Play/Pause Action */}
      {isRunning ? (
        <button
          onClick={onPause}
          title="Pause"
          className={`p-5 rounded-full text-white shadow-lg transform hover:scale-110 active:scale-95 transition-all duration-300 focus:outline-none ${
            isFocus 
              ? 'bg-gradient-to-r from-violet-600 to-indigo-600 hover:shadow-violet-500/25 glow-focus' 
              : 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:shadow-emerald-500/25 glow-break'
          }`}
        >
          <Pause size={28} fill="currentColor" />
        </button>
      ) : (
        <button
          onClick={onStart}
          title="Start"
          className={`p-5 rounded-full text-white shadow-lg transform hover:scale-110 active:scale-95 transition-all duration-300 focus:outline-none ${
            isFocus 
              ? 'bg-gradient-to-r from-violet-600 to-indigo-600 hover:shadow-violet-500/25 glow-focus' 
              : 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:shadow-emerald-500/25 glow-break'
          }`}
        >
          <Play size={28} className="ml-1" fill="currentColor" />
        </button>
      )}

      {/* Skip button */}
      <button
        onClick={onSkip}
        title="Skip Session"
        className="p-3.5 rounded-full glass-panel text-gray-400 hover:text-white hover:scale-105 hover:bg-slate-800/60 active:scale-95 transition-all duration-300 focus:outline-none"
      >
        <SkipForward size={20} />
      </button>
    </div>
  );
}

import React, { useState } from 'react';
import { X, Sliders } from 'lucide-react';

/**
 * SettingsModal component
 * Handles adjusting focus and break times with inputs.
 */
export default function SettingsModal({ isOpen, onClose, focusDuration, breakDuration, onSave }) {
  const [focusInput, setFocusInput] = useState(focusDuration);
  const [breakInput, setBreakInput] = useState(breakDuration);

  if (!isOpen) return null;

  const handleSave = (e) => {
    e.preventDefault();
    // Validate inputs
    const validFocus = Math.max(1, Math.min(120, Number(focusInput)));
    const validBreak = Math.max(1, Math.min(60, Number(breakInput)));
    onSave(validFocus, validBreak);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm transition-opacity duration-300">
      {/* Modal Card */}
      <div className="w-full max-w-md glass-card rounded-2xl overflow-hidden shadow-2xl border border-slate-800 transition-transform duration-300 transform scale-100">
        
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800/80 bg-slate-900/40">
          <div className="flex items-center gap-2 text-white font-semibold">
            <Sliders size={18} className="text-violet-400" />
            <span>Timer Settings</span>
          </div>
          <button 
            onClick={onClose} 
            className="text-slate-400 hover:text-white transition-colors duration-200"
          >
            <X size={18} />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSave} className="p-6 space-y-6">
          {/* Focus Duration Input */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <label className="text-slate-300 font-medium">Focus Duration</label>
              <span className="text-violet-400 font-semibold">{focusInput} min</span>
            </div>
            <input
              type="range"
              min="1"
              max="60"
              step="1"
              value={focusInput}
              onChange={(e) => setFocusInput(Number(e.target.value))}
              className="w-full h-1.5 rounded-lg bg-slate-800 accent-violet-500 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>1 min</span>
              <span>60 min</span>
            </div>
          </div>

          {/* Break Duration Input */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <label className="text-slate-300 font-medium">Break Duration</label>
              <span className="text-emerald-400 font-semibold">{breakInput} min</span>
            </div>
            <input
              type="range"
              min="1"
              max="30"
              step="1"
              value={breakInput}
              onChange={(e) => setBreakInput(Number(e.target.value))}
              className="w-full h-1.5 rounded-lg bg-slate-800 accent-emerald-500 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>1 min</span>
              <span>30 min</span>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2.5 rounded-xl border border-slate-700/60 text-slate-300 hover:text-white hover:bg-slate-800/40 active:scale-95 transition-all duration-200 text-sm font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white shadow-lg active:scale-95 transition-all duration-200 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-violet-500/50"
            >
              Save Settings
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

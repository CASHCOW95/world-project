import React from 'react';
import { Brain, Coffee } from 'lucide-react';

/**
 * TimerDisplay component
 * Renders the circular progress and large time text (MM:SS).
 */
export default function TimerDisplay({ timeLeft, mode, focusDuration, breakDuration, isRunning }) {
  // Calculate total seconds for the current mode
  const totalSeconds = (mode === 'focus' ? focusDuration : breakDuration) * 60;
  // Compute progress ratio (from 1 down to 0)
  const progress = timeLeft / totalSeconds;
  
  // Format seconds to MM:SS string
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Circular progress configuration
  const radius = 110;
  const strokeWidth = 8;
  const circumference = 2 * Math.PI * radius;
  // Offset calculated from progress
  const strokeDashoffset = circumference * (1 - progress);

  const isFocus = mode === 'focus';

  return (
    <div className="relative flex flex-col items-center justify-center my-6 select-none">
      {/* Outer Glowing Circle Container */}
      <div 
        className={`relative flex items-center justify-center w-72 h-72 rounded-full transition-all duration-700 ${
          isFocus 
            ? 'glow-focus bg-purple-950/20' 
            : 'glow-break bg-emerald-950/20'
        }`}
      >
        {/* Progress Circle SVG */}
        <svg className="absolute w-full h-full -rotate-90" viewBox="0 0 240 240">
          {/* Background track circle */}
          <circle
            cx="120"
            cy="120"
            r={radius}
            className="stroke-gray-800/40 fill-transparent"
            strokeWidth={strokeWidth}
          />
          {/* Active progress track */}
          <circle
            cx="120"
            cy="120"
            r={radius}
            className={`fill-transparent transition-all duration-300 ${
              isFocus ? 'stroke-violet-500' : 'stroke-emerald-500'
            }`}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
          />
        </svg>

        {/* Text and Icon Inner Content */}
        <div className="relative flex flex-col items-center text-center z-10">
          {/* Icon indicator */}
          <div 
            className={`p-2 rounded-full mb-2 transition-all duration-500 ${
              isFocus 
                ? 'bg-violet-500/10 text-violet-400' 
                : 'bg-emerald-500/10 text-emerald-400'
            } ${isRunning ? 'animate-pulse' : ''}`}
          >
            {isFocus ? <Brain size={28} /> : <Coffee size={28} />}
          </div>

          {/* Time digits */}
          <h1 className="text-5xl font-mono font-bold tracking-wider leading-none text-white drop-shadow-md">
            {formatTime(timeLeft)}
          </h1>

          {/* Session label */}
          <span 
            className={`text-xs font-semibold uppercase tracking-[0.25em] mt-3 transition-colors duration-500 ${
              isFocus ? 'text-violet-400' : 'text-emerald-400'
            }`}
          >
            {isFocus ? 'Focus Session' : 'Take a Break'}
          </span>
        </div>
      </div>
    </div>
  );
}

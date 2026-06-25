import { useState, useEffect, useRef } from 'react';

/**
 * Custom hook managing the Pomodoro timer states and mechanics.
 * Rules of engagement: all code commented and clearly explained.
 */
export function useTimer() {
  // Focus session duration in minutes (default: 25)
  const [focusDuration, setFocusDuration] = useState(25);
  // Break session duration in minutes (default: 5)
  const [breakDuration, setBreakDuration] = useState(5);
  // Current active mode: 'focus' or 'break'
  const [mode, setMode] = useState('focus');
  // Seconds remaining in the current session
  const [timeLeft, setTimeLeft] = useState(25 * 60);
  // Is the timer ticking
  const [isRunning, setIsRunning] = useState(false);
  
  // History log initialized from local storage to keep completed sessions persistent
  const [history, setHistory] = useState(() => {
    try {
      const saved = localStorage.getItem('pomodoro_history');
      return saved ? JSON.parse(saved) : [];
    } catch (e) {
      return [];
    }
  });

  const timerRef = useRef(null);

  // Synchronize timeLeft whenever focus/break durations or session mode changes, provided the timer is idle
  useEffect(() => {
    if (!isRunning) {
      setTimeLeft(mode === 'focus' ? focusDuration * 60 : breakDuration * 60);
    }
  }, [focusDuration, breakDuration, mode]);

  // Persist focus logs locally
  useEffect(() => {
    localStorage.setItem('pomodoro_history', JSON.stringify(history));
  }, [history]);

  /**
   * Sound alert utilizing Web Audio API. 
   * Play two soft, melodic chime notes to celebrate completion without using bulky, flaky audio files.
   */
  const playAlertSound = () => {
    try {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      if (!AudioContextClass) return;
      const ctx = new AudioContextClass();
      
      // Note 1: Focus = violet chime, Break = green chirp
      const isFocusFinished = mode === 'focus';
      const freq1 = isFocusFinished ? 523.25 : 659.25; // C5 or E5
      const freq2 = isFocusFinished ? 659.25 : 880.00; // E5 or A5

      const osc1 = ctx.createOscillator();
      const gain1 = ctx.createGain();
      osc1.connect(gain1);
      gain1.connect(ctx.destination);
      osc1.type = 'sine';
      osc1.frequency.setValueAtTime(freq1, ctx.currentTime);
      gain1.gain.setValueAtTime(0.12, ctx.currentTime);
      gain1.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.4);
      osc1.start();
      osc1.stop(ctx.currentTime + 0.4);

      const osc2 = ctx.createOscillator();
      const gain2 = ctx.createGain();
      osc2.connect(gain2);
      gain2.connect(ctx.destination);
      osc2.type = 'sine';
      osc2.frequency.setValueAtTime(freq2, ctx.currentTime + 0.15);
      gain2.gain.setValueAtTime(0.12, ctx.currentTime + 0.15);
      gain2.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.55);
      osc2.start(ctx.currentTime + 0.15);
      osc2.stop(ctx.currentTime + 0.55);
    } catch (err) {
      console.warn("Audio chime prevented or unsupported by browser: ", err);
    }
  };

  // Main countdown ticking logic
  useEffect(() => {
    if (isRunning) {
      timerRef.current = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            // Timer reached 0! Trigger transition.
            clearInterval(timerRef.current);
            setIsRunning(false);
            playAlertSound();

            const nextMode = mode === 'focus' ? 'break' : 'focus';
            
            // Add session to log
            const logEntry = {
              id: Date.now(),
              type: mode,
              duration: mode === 'focus' ? focusDuration : breakDuration,
              timeLabel: `${mode === 'focus' ? focusDuration : breakDuration}m`,
              timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              date: new Date().toLocaleDateString()
            };
            
            setHistory((prevHistory) => [logEntry, ...prevHistory]);
            setMode(nextMode);
            return nextMode === 'focus' ? focusDuration * 60 : breakDuration * 60;
          }
          return prev - 1;
        });
      }, 1000);
    } else {
      clearInterval(timerRef.current);
    }

    return () => clearInterval(timerRef.current);
  }, [isRunning, mode, focusDuration, breakDuration]);

  // Control functions
  const start = () => setIsRunning(true);
  const pause = () => setIsRunning(false);
  
  const reset = () => {
    setIsRunning(false);
    setTimeLeft(mode === 'focus' ? focusDuration * 60 : breakDuration * 60);
  };

  const skip = () => {
    setIsRunning(false);
    const nextMode = mode === 'focus' ? 'break' : 'focus';
    setMode(nextMode);
    setTimeLeft(nextMode === 'focus' ? focusDuration * 60 : breakDuration * 60);
  };

  const updateSettings = (newFocus, newBreak) => {
    setIsRunning(false);
    setFocusDuration(newFocus);
    setBreakDuration(newBreak);
    setTimeLeft(mode === 'focus' ? newFocus * 60 : newBreak * 60);
  };

  const clearHistory = () => {
    setHistory([]);
  };

  return {
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
  };
}

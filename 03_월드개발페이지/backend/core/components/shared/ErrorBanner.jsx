import React from 'react';
import { AlertTriangle } from 'lucide-react';

export default function ErrorBanner({ message }) {
  if (!message) return null;

  return (
    <div role="alert" className="flex items-start gap-2 rounded-2xl border border-rose-900/40 bg-rose-950/30 px-4 py-3 text-sm font-semibold leading-relaxed text-rose-200">
      <AlertTriangle size={16} className="mt-0.5 shrink-0 text-rose-400" />
      <span>{message}</span>
    </div>
  );
}

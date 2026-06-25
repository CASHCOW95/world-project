import React, { useState, memo } from 'react';
import { BadgeHelp } from 'lucide-react';

/**
 * 툴팁을 표시하는 독립 컴포넌트.
 * 기존 renderTooltip 함수를 컴포넌트로 분리하여 재사용성을 높임.
 */
const Tooltip = memo(function Tooltip({ id, label, title, desc, iconColor = "text-slate-500", align = "center" }) {
  const [active, setActive] = useState(false);

  const alignClass =
    align === "left" ? "left-0 translate-x-0" :
    align === "right" ? "right-0 translate-x-0" :
    "left-1/2 -translate-x-1/2";

  return (
    <span
      className="relative inline-flex items-center gap-1 cursor-help select-none"
      onMouseEnter={() => setActive(true)}
      onMouseLeave={() => setActive(false)}
      onClick={(e) => {
        e.stopPropagation();
        setActive(prev => !prev);
      }}
    >
      <span className="font-bold">{label}</span>
      <BadgeHelp size={12} className={`${iconColor} hover:text-slate-300 transition-colors`} />
      {active && (
        <span className={`absolute bottom-full mb-2.5 w-60 p-3 bg-slate-900 border border-slate-800 text-slate-300 rounded-2xl shadow-2xl text-[11px] font-semibold leading-relaxed z-50 text-left border-l-4 border-l-indigo-500 whitespace-normal ${alignClass}`}>
          <span className="font-extrabold text-white mb-1 text-[12px] block">{title}</span>
          <span className="block">{desc}</span>
        </span>
      )}
    </span>
  );
});

export default Tooltip;

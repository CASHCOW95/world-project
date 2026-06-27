import React, { memo } from 'react';
import { Cpu, Compass, Layers } from 'lucide-react';

/**
 * 카테고리 선택 헤더 UI.
 * title, subtitle, badge를 커스터마이징 가능하며,
 * 우측에 추가 버튼을 삽입할 수 있는 rightSlot 지원.
 */
const CategoryHeader = memo(function CategoryHeader({
  title = 'Styler Pro X',
  badge = 'v3.0 Premium',
  subtitle = '수익형 블로그 기획 → 키워드 발굴 → 제목 선정 → 자동 발행 Suite',
  mainCategory,
  onMainCategoryChange,
  subCategory,
  onSubCategoryChange,
  sortedMainCategories,
  sortedSubCategories,
  disabled = false,
  rightSlot = null,
}) {
  return (
    <header className="relative w-full rounded-3xl p-5 overflow-hidden border border-white/5 bg-slate-950/40 shadow-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div className="absolute inset-0 pointer-events-none" />
      <div className="flex items-center gap-4 relative">
        <div className="p-3.5 rounded-2xl bg-indigo-600 shadow-lg text-white">
          <Cpu size={26} />
        </div>
        <div>
          <h1 className="text-xl md:text-2xl font-black tracking-tight text-white leading-tight">
            {title}{' '}
            <span className="text-xs bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 px-2 py-0.5 rounded-full font-bold ml-1.5 align-middle">
              {badge}
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">{subtitle}</p>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-3.5 w-full md:w-3/5 relative z-20 items-end">
        <div className="flex-1 flex flex-col gap-1 w-full">
          <span className="text-[12px] font-bold text-slate-500 uppercase tracking-wider pl-1 flex items-center gap-1">
            <Compass size={12} /> 대분류 카테고리
          </span>
          <select
            value={mainCategory}
            onChange={(e) => onMainCategoryChange(e.target.value)}
            disabled={disabled}
            className="w-full px-3.5 py-2.5 rounded-2xl bg-slate-950/90 border border-slate-800 focus:border-indigo-500 focus:outline-none text-slate-200 text-xs font-bold transition-all shadow-inner cursor-pointer"
            style={{ colorScheme: 'dark' }}
          >
            {sortedMainCategories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>

        <div className="flex-1 flex flex-col gap-1 w-full">
          <span className="text-[12px] font-bold text-slate-500 uppercase tracking-wider pl-1 flex items-center gap-1">
            <Layers size={11} /> 소분류 카테고리
          </span>
          <select
            value={subCategory}
            onChange={(e) => onSubCategoryChange(e.target.value)}
            disabled={disabled}
            className="w-full px-3.5 py-2.5 rounded-2xl bg-slate-950/90 border border-slate-800 focus:border-indigo-500 focus:outline-none text-slate-200 text-xs font-bold transition-all shadow-inner cursor-pointer"
            style={{ colorScheme: 'dark' }}
          >
            {sortedSubCategories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>

        {rightSlot && (
          <div className="flex-none flex flex-col gap-1 w-full sm:w-auto justify-end">
            {rightSlot}
          </div>
        )}
      </div>
    </header>
  );
});

export default CategoryHeader;

import React, { memo } from 'react';
import { Sparkles } from 'lucide-react';

const TITLE_FILTERS = ['전체', '정보형', '비교형', '리스트형', '후기형', '충격형', '실수방지형', '전문가형', '최신뉴스형', '질문형', '가이드형'];

/**
 * 제목 100선 목록 UI.
 * 필터 탭, 제목 카드 렌더링, 선택 기능 제공.
 */
const TitleList = memo(function TitleList({
  titlesLoading,
  filteredTitles,
  selectedTitle,
  onSelectTitle,
  titleFilter,
  onFilterChange,
}) {
  return (
    <section className="glass-card rounded-3xl border border-white/5 shadow-2xl p-5 flex flex-col h-[650px] gap-4">
      <div className="flex flex-col gap-2 shrink-0">
        <h3 className="text-xs font-bold text-slate-300 flex items-center gap-1.5 uppercase tracking-wider">
          <Sparkles size={14} className="text-violet-400 animate-spin" />
          유입 극대화 제목 100선 (CHATGPT STYLE)
        </h3>
      </div>

      <div className="flex gap-1 overflow-x-auto pb-1.5 border-b border-slate-900 shrink-0">
        {TITLE_FILTERS.map(cat => (
          <button
            key={cat}
            onClick={() => onFilterChange(cat)}
            className={`px-3 py-1 rounded-xl text-[10px] font-extrabold transition-all shrink-0 cursor-pointer ${titleFilter === cat ? 'bg-indigo-600 text-white shadow-md' : 'bg-slate-900 text-slate-400 hover:text-slate-200'}`}
          >
            {cat}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto max-h-[480px] border border-slate-900 rounded-2xl bg-slate-950/60 p-3 scrollbar-thin scrollbar-thumb-slate-800">
        {titlesLoading ? (
          <div className="text-xs text-slate-500 italic text-center py-4">추천 제목 분석 설계 중...</div>
        ) : filteredTitles.length === 0 ? (
          <div className="flex h-full min-h-48 flex-col items-center justify-center gap-2 rounded-2xl border border-dashed border-slate-800 bg-slate-950/50 px-4 text-center">
            <strong className="text-xs font-black text-slate-300">추천 제목이 없습니다.</strong>
            <span className="text-[11px] font-semibold leading-relaxed text-slate-500">
              키워드를 선택하거나 제목 유형 필터를 전체로 변경해 주세요.
            </span>
          </div>
        ) : (
          <div className="flex flex-col gap-2.5">
            {filteredTitles.map((t, idx) => {
              const isSelected = selectedTitle?.title === t.title;
              return (
                <div
                  key={t.title + idx}
                  onClick={() => onSelectTitle(t)}
                  className={`p-3 rounded-2xl border text-xs font-medium flex justify-between items-center transition-all cursor-pointer ${isSelected ? 'bg-indigo-950/30 border-indigo-500/40 text-white' : 'bg-slate-900/40 border-slate-850 hover:bg-slate-900/70 text-slate-300'}`}
                >
                  <div className="flex flex-col gap-1 pr-4">
                    <div className="flex gap-2 items-center">
                      <span className="text-[10px] bg-slate-950 border border-slate-800 px-2 py-0.5 rounded-full text-slate-400 font-bold">{t.type}</span>
                      <span className="text-[10px] text-emerald-400 font-black">CTR 예상 {t.ctr}%</span>
                      <span className="text-[10px] text-indigo-400 font-black">SEO {t.seo}점</span>
                    </div>
                    <div className="text-slate-200 font-bold select-all leading-normal mt-1">{t.title}</div>
                  </div>
                  <button
                    type="button"
                    className={`px-3 py-1.5 rounded-xl text-[10px] font-black shrink-0 transition-all ${isSelected ? 'bg-indigo-600 text-white shadow-md' : 'bg-slate-950 border border-slate-800 text-slate-400'}`}
                  >
                    [선택]
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <button
        type="button"
        disabled={titlesLoading || filteredTitles.length === 0}
        className="w-full py-2.5 rounded-xl border border-slate-800 bg-slate-900/40 hover:bg-slate-900/80 text-slate-400 hover:text-slate-200 text-xs font-bold transition-all text-center block cursor-pointer"
      >
        ▼ 전체 100개 제목 보기
      </button>
    </section>
  );
});

export default TitleList;

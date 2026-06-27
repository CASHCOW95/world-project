import React, { memo } from 'react';
import { Flame, Search } from 'lucide-react';

const SORT_TABS = [
  { id: 'recommend', label: '⭐ 추천순' },
  { id: 'latest', label: '🆕 최신순' },
  { id: 'volume', label: '📊 검색량순' },
  { id: 'cpc', label: '💵 CPC순' },
];

/**
 * 키워드 카드 목록 UI.
 * 검색, 정렬 탭, 키워드 카드 렌더링을 담당.
 */
const KeywordList = memo(function KeywordList({
  categoryName = '',
  keywordLoading,
  visibleKeywords,
  selectedKeyword,
  onSelectKeyword,
  keywordSearch,
  onSearchChange,
  keywordSortType,
  onSortChange,
  showAllKeywords,
  onToggleShowAll,
  totalCount = 0,
  disabled = false,
}) {
  return (
    <section className="glass-card rounded-3xl border border-white/5 shadow-2xl p-5 flex flex-col h-[650px] gap-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 shrink-0">
        <div>
          <h3 className="text-xs font-bold text-slate-300 flex items-center gap-1.5 uppercase tracking-wider">
            <Flame size={14} className="text-orange-500 animate-bounce" />
            {categoryName || '정부지원금'} 황금 키워드 분석
          </h3>
          <p className="text-[10px] text-slate-500 mt-0.5">수익률이 극대화되는 황금 키워드 자동 발굴</p>
        </div>
        <div className="relative w-full sm:w-44">
          <input
            type="text"
            placeholder="키워드 검색 (예: 대출)"
            value={keywordSearch}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full pl-8 pr-3 py-1.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs font-bold focus:border-indigo-500 focus:outline-none placeholder-slate-600 text-slate-300"
          />
          <Search size={12} className="absolute left-3 top-2.5 text-slate-600" />
        </div>
      </div>

      <div className="flex gap-1 overflow-x-auto pb-1.5 border-b border-slate-900 shrink-0">
        {SORT_TABS.map(tab => (
          <button
            key={tab.id}
            onClick={() => onSortChange(tab.id)}
            className={`px-3 py-1 rounded-xl text-[10px] font-extrabold transition-all cursor-pointer ${keywordSortType === tab.id ? 'bg-indigo-600 text-white shadow-md' : 'bg-slate-900 text-slate-400 hover:text-slate-200'}`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto max-h-[480px] border border-slate-900 rounded-2xl bg-slate-950/60 p-3 scrollbar-thin scrollbar-thumb-slate-800">
        {keywordLoading ? (
          <div className="flex items-center justify-center h-full text-xs text-slate-500 italic">
            실시간 황금키워드 지수 연산 중...
          </div>
        ) : visibleKeywords.length === 0 ? (
          <div className="flex h-full min-h-48 flex-col items-center justify-center gap-2 rounded-2xl border border-dashed border-slate-800 bg-slate-950/50 px-4 text-center">
            <strong className="text-xs font-black text-slate-300">표시할 키워드가 없습니다.</strong>
            <span className="text-[11px] font-semibold leading-relaxed text-slate-500">
              검색어를 바꾸거나 다른 카테고리를 선택해 주세요.
            </span>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {visibleKeywords.map((kw, i) => {
              const isSelected = selectedKeyword?.keyword === kw.keyword;
              return (
                <div
                  key={kw.keyword + i}
                  onClick={() => !disabled && onSelectKeyword(kw)}
                  className={`p-3.5 rounded-2xl border transition-all cursor-pointer flex flex-col gap-2.5 ${isSelected ? 'bg-indigo-600/15 border-indigo-500/50 text-indigo-300 shadow-lg' : 'bg-slate-900/40 border-slate-850 hover:bg-slate-900/70 hover:border-slate-800/80 text-slate-300'}`}
                >
                  <div className="flex justify-between items-center">
                    <span className="font-extrabold text-[12px] text-white flex items-center gap-1">
                      <span className="text-yellow-400">🏆</span> 추천 {i + 1}
                    </span>
                    <span className="text-[10px] bg-slate-950 border border-slate-800 text-emerald-400 px-2 py-0.5 rounded-full font-bold">
                      {kw.ai_badge}
                    </span>
                  </div>
                  <div className="text-xs font-black text-slate-100 pl-0.5 select-all">{kw.keyword}</div>
                  <div className="grid grid-cols-4 gap-2 text-center text-[10px] bg-slate-950/60 p-2 rounded-xl border border-slate-900">
                    <div>
                      <span className="text-slate-500 block text-[9px] uppercase font-bold">수익등급</span>
                      <strong className="text-white font-extrabold">S등급</strong>
                    </div>
                    <div>
                      <span className="text-slate-500 block text-[9px] uppercase font-bold">검색량</span>
                      <strong className="text-slate-400">{kw.search_volume.toLocaleString()}</strong>
                    </div>
                    <div>
                      <span className="text-slate-500 block text-[9px] uppercase font-bold">CPC</span>
                      <strong className="text-slate-400">${kw.cpc_dollar.toFixed(1)}</strong>
                    </div>
                    <div>
                      <span className="text-slate-500 block text-[9px] uppercase font-bold">블루오션</span>
                      <strong className="text-indigo-400 font-extrabold">{kw.blue_ocean_score}점</strong>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <button
        type="button"
        onClick={onToggleShowAll}
        disabled={keywordLoading || totalCount === 0}
        className="w-full py-2.5 rounded-xl border border-slate-800 bg-slate-900/40 hover:bg-slate-900/80 text-slate-400 hover:text-slate-200 text-xs font-bold transition-all text-center block cursor-pointer"
      >
        {showAllKeywords ? '👆 접기' : `👇 전체 ${totalCount}개 키워드 보기`}
      </button>
    </section>
  );
});

export default KeywordList;

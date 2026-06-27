import React, { memo } from 'react';
import { TrendingUp, Award, Users, MousePointer, DollarSign } from 'lucide-react';
import Tooltip from './Tooltip';

/**
 * 수익성 & 경쟁도 프리미엄 분석 센터 UI.
 */
const ProfitAnalysis = memo(function ProfitAnalysis({
  currentRevenue = 0,
  currentProfitScore = 50,
  currentVolume = 0,
  currentVisitors = 0,
  currentCTR = 3.2,
  currentCPC = 1.6,
  currentBadge = '🔵 작성 추천',
  currentBlueOcean = 50,
  currentAffiliate = '추천 제휴상품 연동 대기',
  seoScore = '-',
}) {
  const gradeLabel = currentRevenue >= 250000 ? "S등급 (최고수익)" :
    currentRevenue >= 150000 ? "A등급 (우수)" :
    currentRevenue >= 50000 ? "B등급 (보통)" : "C등급 (일반)";

  const oceanColor = currentBlueOcean >= 90 ? { bg: 'bg-emerald-950', text: 'text-emerald-400', border: 'border-emerald-900/50', gradient: 'from-emerald-500 to-teal-400', label: '🟢 진입 매우 쉬움' } :
    currentBlueOcean >= 70 ? { bg: 'bg-indigo-950', text: 'text-indigo-400', border: 'border-indigo-900/50', gradient: 'from-indigo-500 to-violet-400', label: '🔵 진입 쉬움' } :
    currentBlueOcean >= 50 ? { bg: 'bg-amber-950', text: 'text-amber-400', border: 'border-amber-900/50', gradient: 'from-amber-500 to-yellow-400', label: '🟡 보통' } :
    { bg: 'bg-rose-950', text: 'text-rose-400', border: 'border-rose-900/50', gradient: 'from-rose-500 to-pink-400', label: '🔴 경쟁 치열' };

  return (
    <section className="relative w-full rounded-3xl p-6 border border-emerald-500/15 bg-slate-950/70 shadow-2xl flex flex-col gap-5">
      <div className="absolute inset-0 pointer-events-none" />
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/80 pb-4 relative z-10">
        <div>
          <h3 className="text-sm font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
            <TrendingUp size={16} className="text-emerald-400" />
            수익성 & 경쟁도 프리미엄 분석 센터
          </h3>
          <p className="text-[12px] text-slate-400 mt-0.5">선택된 키워드의 실시간 예상 애드센스 매출 시뮬레이션</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[12px] text-slate-500 font-bold">공략 지표:</span>
          <span className="px-3.5 py-1.5 rounded-full text-[12px] font-black tracking-tight bg-slate-900 border border-slate-800 text-white flex items-center gap-1 shadow-inner">
            {currentBadge}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 relative z-10">
        {/* 수익성 평가 등급 */}
        <div className="col-span-2 md:col-span-1 p-5 rounded-2xl bg-gradient-to-br from-emerald-950/40 to-slate-900/60 border border-emerald-500/30 flex flex-col justify-between gap-2 shadow-lg hover:border-emerald-500/50 transition-all">
          <div className="flex items-center justify-between text-emerald-300">
            <span className="text-xs font-black uppercase tracking-wider">💰 수익성 평가 등급 (AdSense 가치)</span>
            <Award size={20} className="text-emerald-400 animate-pulse" />
          </div>
          <div className="flex items-baseline gap-1.5 my-2">
            <span className="text-2xl font-black text-emerald-400 select-all">{gradeLabel}</span>
            <span className="text-xs text-emerald-300 font-bold">({currentProfitScore}점 / 100점)</span>
          </div>
          <span className="text-[11px] font-bold text-slate-500 leading-tight">트래픽, CTR, CPC 가중 수익 지수</span>
        </div>

        {/* 월 예상 검색량 */}
        <div className="p-4 rounded-2xl bg-slate-900/50 border border-slate-800 flex flex-col justify-between gap-1.5 shadow-sm hover:border-slate-700/80 transition-all">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[11px] font-bold uppercase">월 예상 검색량</span>
            <Users size={14} className="text-indigo-400" />
          </div>
          <div className="flex items-baseline gap-1 my-1">
            <span className="text-lg font-black text-white">{currentVolume.toLocaleString()}</span>
            <span className="text-[10px] text-slate-500">회 / 월</span>
          </div>
          <span className="text-[10px] font-semibold text-slate-500">유입량: {currentVisitors.toLocaleString()}명 예상</span>
        </div>

        {/* 예상 클릭율 */}
        <div className="p-4 rounded-2xl bg-slate-900/50 border border-slate-800 flex flex-col justify-between gap-1.5 shadow-sm hover:border-slate-700/80 transition-all">
          <div className="flex items-center justify-between text-slate-400">
            <Tooltip id="ctr" label="예상 클릭율(CTR)" title="CTR (클릭률)" desc="방문자 중 광고를 클릭하는 비율입니다. 블로그 글의 배치와 가독성에 따라 보통 2% ~ 5% 수준을 유지합니다." iconColor="text-violet-400" />
            <MousePointer size={14} className="text-violet-400" />
          </div>
          <div className="flex items-baseline gap-1 my-1">
            <span className="text-lg font-black text-white">{currentCTR}%</span>
          </div>
          <span className="text-[10px] font-semibold text-slate-500">타겟 사이트 구조화 보정</span>
        </div>

        {/* 예상 클릭단가 */}
        <div className="p-4 rounded-2xl bg-slate-900/50 border border-slate-800 flex flex-col justify-between gap-1.5 shadow-sm hover:border-slate-700/80 transition-all">
          <div className="flex items-center justify-between text-slate-400">
            <Tooltip id="cpc" label="예상 클릭단가(CPC)" title="CPC (클릭 단가)" desc="광고 클릭 1회당 지급받는 예상 수익 달러($) 금액입니다. 금융, 대출, 건강 키워드가 상대적으로 높습니다." iconColor="text-amber-500" />
            <DollarSign size={14} className="text-amber-500" />
          </div>
          <div className="flex items-baseline gap-1 my-1">
            <span className="text-lg font-black text-white">${currentCPC.toFixed(1)}</span>
            <span className="text-[10px] text-slate-500">USD</span>
          </div>
          <span className="text-[10px] font-semibold text-slate-500">실시간 광고 상위 단가</span>
        </div>

        {/* 블루오션 지수 */}
        <div className="col-span-2 p-4 rounded-2xl bg-slate-900/30 border border-slate-900 flex flex-col gap-2.5 justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-slate-400 uppercase">블루오션 지수 및 진입 장벽 분석</span>
            <span className={`text-[12px] font-black px-2.5 py-1 rounded-full ${oceanColor.bg} ${oceanColor.text} border ${oceanColor.border}`}>
              {oceanColor.label}
            </span>
          </div>
          <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden border border-slate-700/50 my-1">
            <div className={`h-full rounded-full bg-gradient-to-r transition-all duration-500 ${oceanColor.gradient}`} style={{ width: currentBlueOcean + '%' }} />
          </div>
          <div className="grid grid-cols-3 text-[11px] text-slate-500 text-center font-bold">
            <div className="text-left">블루오션 점수: <strong className="text-white">{currentBlueOcean}점</strong></div>
            <div className="text-center font-extrabold">경쟁 강도: <strong className="text-white">{currentBlueOcean >= 70 ? '낮음' : '높음'}</strong></div>
            <div className="text-right">진입 가능성: <strong className="text-white">높음</strong></div>
          </div>
        </div>

        {/* 제휴상품 링크 */}
        <div className="col-span-2 md:col-span-1 p-4 rounded-2xl bg-slate-900/30 border border-slate-900 flex flex-col justify-between gap-1.5">
          <div className="flex justify-between items-center text-[11px]">
            <span className="font-bold text-slate-400">제휴상품 링크</span>
            <span className="text-[9px] bg-indigo-500/20 text-indigo-300 px-1 py-0.5 rounded font-black">HIGH</span>
          </div>
          <p className="text-[11px] text-white font-bold leading-normal truncate" title={currentAffiliate}>{currentAffiliate}</p>
          <div className="flex justify-between items-center text-[10px] text-slate-500 border-t border-slate-850 pt-1">
            <span>수익 점수: <strong className="text-white">${currentProfitScore}점</strong></span>
            <span>SEO: <strong className="text-white">{seoScore}점</strong></span>
          </div>
        </div>
      </div>
    </section>
  );
});

export default ProfitAnalysis;

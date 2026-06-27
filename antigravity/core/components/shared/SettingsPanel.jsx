import React, { memo } from 'react';
import { Settings } from 'lucide-react';

/**
 * 제어 설정 패널 공통 UI.
 * 8개 설정 항목을 표시.
 */
const SettingsPanel = memo(function SettingsPanel({
  style, onStyleChange,
  platform, onPlatformChange,
  ctaStyle, onCtaStyleChange,
  seoStrength, onSeoStrengthChange,
  articleLength, onArticleLengthChange,
  faqCount, onFaqCountChange,
  generateImgPrompt, onToggleImgPrompt,
  disabled = false,
  extraSlot = null,
}) {
  const selectClass = "w-full px-3 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-xs font-bold cursor-pointer";

  return (
    <section className="glass-card rounded-3xl border border-white/5 p-6 shadow-2xl flex flex-col gap-4">
      <div className="flex items-center gap-2 border-b border-slate-900 pb-3">
          <div className="p-2 rounded-xl bg-indigo-600 text-white shadow-md">
          <Settings size={16} />
        </div>
        <div>
          <h4 className="text-xs font-black text-slate-300 uppercase tracking-wider">월드 개발 페이지 제어 설정</h4>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-5">
        {/* 글 서술 스타일 */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[12px] font-bold text-slate-400 uppercase tracking-wider">글 서술 스타일</label>
          <select value={style} onChange={(e) => onStyleChange(e.target.value)} disabled={disabled} className={selectClass} style={{ colorScheme: 'dark' }}>
            <option value="friendly">😊 친근 대화체</option>
            <option value="professional">🎓 전문 격조체</option>
            <option value="informative">📋 정보 요약체</option>
          </select>
        </div>

        {/* 자동 발행 플랫폼 */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[12px] font-bold text-slate-400 uppercase tracking-wider">자동 발행 플랫폼</label>
          <select value={platform} onChange={(e) => onPlatformChange(e.target.value)} disabled={disabled} className={selectClass} style={{ colorScheme: 'dark' }}>
            <option value="tistory">티스토리</option>
            <option value="blogspot">블로그스팟</option>
            <option value="wordpress">워드프레스</option>
          </select>
        </div>

        {/* CTA 디자인 */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[12px] font-bold text-slate-400 uppercase tracking-wider">CTA 디자인</label>
          <select value={ctaStyle} onChange={(e) => onCtaStyleChange(e.target.value)} disabled={disabled} className={selectClass} style={{ colorScheme: 'dark' }}>
            <option value="card">🎴 카드형</option>
            <option value="banner">🖼️ 배너형</option>
            <option value="inline">🔗 인라인형</option>
            <option value="button">🔘 버튼형</option>
          </select>
        </div>

        {/* SEO 진단 강도 */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[12px] font-bold text-slate-400 uppercase tracking-wider">SEO 진단 강도</label>
          <select value={seoStrength} onChange={(e) => onSeoStrengthChange(e.target.value)} disabled={disabled} className={selectClass} style={{ colorScheme: 'dark' }}>
            <option value="normal">약함 (1회/65점)</option>
            <option value="strong">보통 (2회/75점)</option>
            <option value="extreme">강함 (3회/85점)</option>
          </select>
        </div>

        {/* 글 길이 */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[12px] font-bold text-slate-400 uppercase tracking-wider">글 길이</label>
          <select value={articleLength} onChange={(e) => onArticleLengthChange(e.target.value)} disabled={disabled} className={selectClass} style={{ colorScheme: 'dark' }}>
            <option value="3000">3000자</option>
            <option value="5000">5000자</option>
            <option value="10000">10000자</option>
          </select>
        </div>

        {/* FAQ 생성 */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[12px] font-bold text-slate-400 uppercase tracking-wider">FAQ 생성</label>
          <select value={faqCount} onChange={(e) => onFaqCountChange(e.target.value)} disabled={disabled} className={selectClass} style={{ colorScheme: 'dark' }}>
            <option value="none">사용 안함</option>
            <option value="5">5개</option>
            <option value="10">10개</option>
            <option value="20">20개</option>
            <option value="auto">자동 추천</option>
          </select>
        </div>

        {/* 대표 이미지 생성 */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[12px] font-bold text-slate-400 uppercase tracking-wider">대표 이미지 생성</label>
          <button
            type="button"
            onClick={onToggleImgPrompt}
            disabled={disabled}
            className={`w-full py-2.5 rounded-xl text-xs font-bold border transition-all ${generateImgPrompt === 'ON' ? 'bg-emerald-600/30 text-emerald-300 border-emerald-500/50' : 'bg-slate-950 text-slate-500 border-slate-800'}`}
          >
            {generateImgPrompt === 'ON' ? 'ON (Imagen API)' : 'OFF (미생성)'}
          </button>
        </div>

        {/* 프롬프트 삼형제 추출 */}
        <div className="flex flex-col gap-2.5 justify-center pl-1">
          <label className="flex items-center gap-2 cursor-pointer text-slate-300 font-bold text-xs select-none">
            <input type="checkbox" defaultChecked className="rounded border-slate-800 bg-slate-950 accent-indigo-500" />
            프롬프트 삼형제 추출
          </label>
        </div>
      </div>

      {extraSlot}
    </section>
  );
});

export default SettingsPanel;

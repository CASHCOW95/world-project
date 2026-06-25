import React, { useEffect, useMemo, useCallback } from 'react';
import { PenTool, Copy, Check, FileText, Sparkles, Layers } from 'lucide-react';
import useSettings from '../hooks/useSettings';
import useCategories from '../hooks/useCategories';
import useKeywords from '../hooks/useKeywords';
import useTitles from '../hooks/useTitles';
import usePipeline from '../hooks/usePipeline';
import useApi from '../hooks/useApi';
import CategoryHeader from './shared/CategoryHeader';
import KeywordList from './shared/KeywordList';
import TitleList from './shared/TitleList';
import SettingsPanel from './shared/SettingsPanel';
import TerminalLog from './shared/TerminalLog';
import ProfitAnalysis from './shared/ProfitAnalysis';

export default function OriginalStylerDashboard() {
  const settings = useSettings();
  const categories = useCategories();
  const titles = useTitles();
  const pipeline = usePipeline();
  const api = useApi();

  // Keywords hook with auto title generation on select
  const handleKeywordSelected = useCallback((kwObj, catName) => {
    titles.handleGenerateTitles(kwObj, catName);
  }, [titles.handleGenerateTitles]);

  const keywords = useKeywords({ onKeywordSelected: handleKeywordSelected });

  // History drawer state
  const [showHistoryDrawer, setShowHistoryDrawer] = React.useState(false);
  const [selectedHistoryItem, setSelectedHistoryItem] = React.useState(null);

  // Load history on mount
  useEffect(() => {
    api.fetchHistory();
  }, [api.fetchHistory]);

  // Reload keywords when subcategory changes
  useEffect(() => {
    if (categories.subCategory) {
      keywords.fetchKeywords(categories.subCategory);
      keywords.setSelectedKeyword(null);
      titles.resetTitles();
      pipeline.setResult(null);
    }
  }, [categories.subCategory]);

  // Derived active content
  const activeContent = selectedHistoryItem || pipeline.result;
  const isPostGenerated = !!activeContent;
  const selectedKw = keywords.selectedKeyword;

  const profitData = useMemo(() => ({
    currentCPC: isPostGenerated ? activeContent.cpc_dollar : (selectedKw?.cpc_dollar || 1.6),
    currentVolume: selectedKw?.search_volume || 0,
    currentVisitors: isPostGenerated ? activeContent.estimated_visitors : (selectedKw?.estimated_visitors || 0),
    currentCTR: isPostGenerated ? activeContent.ctr : (selectedKw?.ctr || 3.2),
    currentRevenue: isPostGenerated ? activeContent.estimated_revenue : (selectedKw?.estimated_revenue || 0),
    currentAffiliate: isPostGenerated ? activeContent.affiliate_product : (selectedKw?.affiliate_product || "추천 제휴상품 연동 대기"),
    currentBadge: isPostGenerated ? activeContent.ai_badge : (selectedKw?.ai_badge || "🔵 작성 추천"),
    currentBlueOcean: isPostGenerated ? activeContent.blue_ocean_score : (selectedKw?.blue_ocean_score || 50),
    currentProfitScore: isPostGenerated ? activeContent.profit_score : (selectedKw?.golden_score || 50),
    seoScore: activeContent?.seo_score || "-",
  }), [activeContent, isPostGenerated, selectedKw]);

  const handleSelectKeyword = useCallback((kw) => {
    if (!pipeline.pipelineRunning) {
      keywords.setSelectedKeyword(kw);
      setSelectedHistoryItem(null);
      titles.handleGenerateTitles(kw, categories.subCategory);
    }
  }, [pipeline.pipelineRunning, categories.subCategory, titles.handleGenerateTitles]);

  const handleStartPipeline = useCallback((e, publishFlag = false) => {
    if (e) e.preventDefault();
    if (!keywords.selectedKeyword || !titles.selectedTitle) return;

    pipeline.runSinglePipeline({
      keyword: keywords.selectedKeyword.keyword,
      platform: settings.platform,
      style: settings.style,
      search_volume: keywords.selectedKeyword.search_volume,
      competition: keywords.selectedKeyword.competition,
      cpc: keywords.selectedKeyword.cpc,
      category: keywords.selectedKeyword.category || categories.currentCategory,
      golden_score: keywords.selectedKeyword.golden_score,
      length: settings.getFinalLength() || '5000',
      faq_count: settings.faqCount,
      img_prompt: settings.generateImgPrompt,
      title: titles.customTitle || titles.selectedTitle.title,
      seo_strength: settings.seoStrength,
      publish: publishFlag,
    }, api.fetchHistory);
  }, [keywords.selectedKeyword, titles.selectedTitle, titles.customTitle, settings, categories.currentCategory, pipeline.runSinglePipeline, api.fetchHistory]);

  const handleCategoryChange = useCallback((mainCat) => {
    if (!pipeline.pipelineRunning) {
      categories.setMainCategory(mainCat);
      setSelectedHistoryItem(null);
    }
  }, [pipeline.pipelineRunning, categories.setMainCategory]);

  const handleSubCategoryChange = useCallback((subCat) => {
    if (!pipeline.pipelineRunning) {
      categories.setSubCategory(subCat);
      setSelectedHistoryItem(null);
    }
  }, [pipeline.pipelineRunning, categories.setSubCategory]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 w-full text-slate-100 font-sans items-start">
      <div className="lg:col-span-12 flex flex-col gap-6 w-full animate-fadeIn">

        {/* 카테고리 선택 헤더 */}
        <CategoryHeader
          title="Styler Pro X"
          badge="v3.0 Premium"
          subtitle="수익형 블로그 기획 → 키워드 발굴 → 제목 선정 → 자동 발행 Suite"
          mainCategory={categories.mainCategory}
          onMainCategoryChange={handleCategoryChange}
          subCategory={categories.subCategory}
          onSubCategoryChange={handleSubCategoryChange}
          sortedMainCategories={categories.sortedMainCategories}
          sortedSubCategories={categories.sortedSubCategories}
          disabled={pipeline.pipelineRunning}
          rightSlot={
            <>
              <span className="text-[12px] font-bold text-slate-500 uppercase tracking-wider pl-1 flex items-center gap-1">
                <Layers size={11} /> 발행 이력
              </span>
              <button
                type="button"
                onClick={() => setShowHistoryDrawer(true)}
                className="px-4 py-2.5 rounded-2xl bg-slate-900 hover:bg-slate-850 text-indigo-400 hover:text-indigo-300 text-xs font-black transition-all shadow-inner border border-slate-800 cursor-pointer flex items-center justify-center gap-1.5 h-[38px] w-full"
              >
                <Layers size={14} /> 이력 보기
              </button>
            </>
          }
        />

        {/* 수익성 분석 센터 */}
        {(selectedKw || isPostGenerated) && <ProfitAnalysis {...profitData} />}

        {/* 키워드 + 제목 2단 구조 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full items-start">
          <div className="flex flex-col gap-6 w-full">
            <KeywordList
              categoryName={categories.subCategory}
              keywordLoading={keywords.keywordLoading}
              visibleKeywords={keywords.visibleKeywords}
              selectedKeyword={keywords.selectedKeyword}
              onSelectKeyword={handleSelectKeyword}
              keywordSearch={keywords.keywordSearch}
              onSearchChange={keywords.setKeywordSearch}
              keywordSortType={keywords.keywordSortType}
              onSortChange={keywords.setKeywordSortType}
              showAllKeywords={keywords.showAllKeywords}
              onToggleShowAll={() => keywords.setShowAllKeywords(prev => !prev)}
              totalCount={keywords.filteredKeywords.length}
              disabled={pipeline.pipelineRunning}
            />

            {/* AI 추천 분석 카드 */}
            {selectedKw && (
              <section className="glass-card rounded-3xl border border-emerald-500/20 bg-emerald-950/10 p-4.5 flex flex-col gap-3 animate-fadeIn shadow-lg">
                <div className="flex justify-between items-center border-b border-slate-900 pb-2">
                  <h4 className="text-xs font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-300 flex items-center gap-1.5 uppercase tracking-wider">
                    <Sparkles size={14} className="text-emerald-400 animate-pulse" />
                    AI 키워드 추천 이유 분석
                  </h4>
                  <span className="text-[10px] bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 px-2 py-0.5 rounded-full font-black">
                    {selectedKw.ai_badge}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-[11px]">
                  <div className="bg-slate-950/50 border border-slate-900 px-3 py-2 rounded-xl text-slate-300 flex items-center gap-1.5 font-bold">
                    <span className="text-emerald-400 font-extrabold">✓</span> 검색량: 안정적
                  </div>
                  <div className="bg-slate-950/50 border border-slate-900 px-3 py-2 rounded-xl text-slate-300 flex items-center gap-1.5 font-bold">
                    <span className="text-emerald-400 font-extrabold">✓</span> 경쟁도: 낮음 (블루오션)
                  </div>
                </div>
              </section>
            )}
          </div>

          <TitleList
            titlesLoading={titles.titlesLoading}
            filteredTitles={titles.filteredTitles}
            selectedTitle={titles.selectedTitle}
            onSelectTitle={titles.selectTitle}
            titleFilter={titles.titleFilter}
            onFilterChange={titles.setTitleFilter}
          />
        </div>

        {/* 제어 설정 */}
        <SettingsPanel
          style={settings.style} onStyleChange={settings.setStyle}
          platform={settings.platform} onPlatformChange={settings.setPlatform}
          ctaStyle={settings.ctaStyle} onCtaStyleChange={settings.setCtaStyle}
          seoStrength={settings.seoStrength} onSeoStrengthChange={settings.setSeoStrength}
          articleLength={settings.articleLength} onArticleLengthChange={settings.setArticleLength}
          faqCount={settings.faqCount} onFaqCountChange={settings.setFaqCount}
          generateImgPrompt={settings.generateImgPrompt}
          onToggleImgPrompt={() => settings.setGenerateImgPrompt(prev => prev === 'ON' ? 'OFF' : 'ON')}
          disabled={pipeline.pipelineRunning}
        />

        {/* 아웃라인 미리보기 + 터미널 2단 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full items-start">
          <div className="flex flex-col gap-6 w-full">
            <section className="glass-card rounded-3xl border border-white/5 p-5 shadow-2xl flex flex-col h-[520px]">
              <div className="flex justify-between items-center mb-3.5 shrink-0 border-b border-slate-900 pb-3">
                <div>
                  <span className="text-[12px] text-indigo-400 font-bold uppercase tracking-wider">
                    {selectedHistoryItem ? '과거 백업 히스토리 조회' : isPostGenerated ? '생성 완료 포스팅 프리뷰' : '블로그 구조 기획 아웃라인 미리보기'}
                  </span>
                  <h3 className="text-xs font-bold text-slate-300">
                    {activeContent ? activeContent.title : titles.selectedTitle ? titles.selectedTitle.title : '기획 및 실시간 미리보기'}
                  </h3>
                </div>
                <div className="flex gap-2">
                  {activeContent && (
                    <button
                      onClick={() => pipeline.handleCopy(activeContent.html_content)}
                      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all shadow-md ${pipeline.copied ? 'bg-emerald-600 text-white' : 'bg-slate-800 hover:bg-slate-700 text-slate-200'}`}
                    >
                      {pipeline.copied ? <Check size={12} /> : <Copy size={12} />}
                      코드 복사
                    </button>
                  )}
                </div>
              </div>
              <div className="flex-1 bg-slate-950 border border-slate-900 rounded-2xl p-5 overflow-y-auto text-slate-300 text-xs leading-relaxed scrollbar-thin scrollbar-thumb-slate-800">
                {activeContent ? (
                  <div className="prose prose-invert prose-xs max-w-none text-slate-300 animate-fadeIn" dangerouslySetInnerHTML={{ __html: activeContent.html_content }} />
                ) : (
                  <div className="flex flex-col items-center justify-center w-full h-full text-slate-600 gap-2.5">
                    <FileText size={36} className="opacity-20 animate-bounce" />
                    <p className="text-[13px] text-center italic">
                      좌측 키워드를 선택하고 제목을 클릭 시<br />
                      구조화된 블로그 포스트의 기획 아웃라인 및 실시간 렌더링이 제공됩니다.
                    </p>
                  </div>
                )}
              </div>
              {titles.selectedTitle && !activeContent && (
                <div className="grid grid-cols-2 gap-4 mt-4 shrink-0 pt-3 border-t border-slate-900">
                  <button onClick={(e) => handleStartPipeline(e, false)} disabled={pipeline.pipelineRunning} className="py-4 rounded-2xl bg-indigo-600 hover:bg-indigo-500 text-white font-extrabold text-xs sm:text-sm shadow-xl shadow-indigo-500/10 transition-all text-center flex items-center justify-center gap-2 cursor-pointer animate-pulse">
                    <FileText size={16} /> [글 생성] (임시 저장)
                  </button>
                  <button onClick={(e) => handleStartPipeline(e, true)} disabled={pipeline.pipelineRunning} className="py-4 rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-extrabold text-xs sm:text-sm shadow-xl shadow-emerald-500/10 transition-all text-center flex items-center justify-center gap-2 cursor-pointer">
                    <PenTool size={16} /> [자동 발행] (플랫폼 전송)
                  </button>
                </div>
              )}
            </section>

            {/* 이미지 프롬프트 카드 */}
            {activeContent && activeContent.image_prompts && (
              <section className="glass-card rounded-3xl border border-white/5 p-5 shadow-2xl flex flex-col gap-3.5 animate-fadeIn">
                <h4 className="text-[13px] font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                  <PenTool size={13} className="text-violet-400" />
                  대표 이미지 및 썸네일 생성 AI 프롬프트
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {[
                    { label: 'Midjourney 프롬프트', color: 'text-indigo-400', key: 'midjourney' },
                    { label: 'ChatGPT (DALL-E) 프롬프트', color: 'text-teal-400', key: 'chatgpt' },
                    { label: 'Flux 프롬프트', color: 'text-violet-400', key: 'flux' },
                  ].map(p => (
                    <div key={p.key} className="p-3.5 rounded-2xl bg-slate-900/40 border border-slate-850 flex flex-col gap-2 justify-between">
                      <span className={`font-bold ${p.color} text-xs`}>{p.label}</span>
                      <p className="text-[11px] text-slate-300 font-mono line-clamp-3 bg-black/30 p-2 rounded-lg border border-slate-900/50">
                        {activeContent.image_prompts[p.key]}
                      </p>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </div>

          <TerminalLog logs={pipeline.logs} terminalStep={pipeline.terminalStep} terminalEndRef={pipeline.terminalEndRef} />
        </div>
      </div>

      {/* 히스토리 드로워 */}
      {showHistoryDrawer && (
        <div className="fixed inset-0 z-50 flex justify-end bg-black/70 backdrop-blur-sm animate-fadeIn">
          <div className="absolute inset-0 cursor-pointer" onClick={() => setShowHistoryDrawer(false)} />
          <div className="relative w-full max-w-md h-full bg-slate-950/95 border-l border-white/5 p-6 flex flex-col gap-4 shadow-2xl animate-slideInRight">
            <div className="flex justify-between items-center border-b border-slate-900 pb-4">
              <h3 className="text-sm font-black text-slate-300 flex items-center gap-1.5 uppercase tracking-wider">
                <Layers size={14} className="text-indigo-400 animate-pulse" />
                로컬 DB 백업 발행 이력
              </h3>
              <button onClick={() => setShowHistoryDrawer(false)} className="text-xs font-bold text-slate-400 hover:text-white transition-all bg-slate-900 border border-slate-800 hover:border-slate-700 px-3 py-1.5 rounded-xl cursor-pointer">
                닫기 ✕
              </button>
            </div>
            <div className="flex-1 overflow-y-auto flex flex-col gap-3.5 pr-1 scrollbar-thin scrollbar-thumb-slate-800">
              {api.history.length === 0 ? (
                <div className="text-xs text-slate-600 italic text-center py-8">발행 이력이 없습니다.</div>
              ) : (
                api.history.map((item, i) => (
                  <div
                    key={item.id || i}
                    onClick={() => {
                      if (!pipeline.pipelineRunning) {
                        setSelectedHistoryItem(item);
                        setShowHistoryDrawer(false);
                      }
                    }}
                    className={`p-4 rounded-2xl border text-xs flex flex-col gap-2 transition-all cursor-pointer ${selectedHistoryItem?.id === item.id ? 'bg-indigo-950/40 border-indigo-500/50 text-white' : 'bg-slate-900/40 border-slate-850 hover:bg-slate-900/70 text-slate-400 hover:text-slate-200'}`}
                  >
                    <div className="flex justify-between items-center text-[10px]">
                      <span className="bg-slate-950 border border-slate-800 px-2 py-0.5 rounded-full font-black text-slate-500">{(item.platform || 'tistory').toUpperCase()}</span>
                      <span className="font-bold text-slate-500">{new Date(item.created_at).toLocaleDateString()}</span>
                    </div>
                    <div className="font-black text-slate-100 leading-normal truncate" title={item.title}>{item.title}</div>
                    <div className="flex justify-between items-center text-[9px] text-slate-500 border-t border-slate-850/30 pt-2 mt-0.5">
                      <span>SEO: <strong className="text-emerald-400">{item.seo_score}점</strong></span>
                      <span>수익: <strong className="text-indigo-400">{item.profit_score}점</strong></span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

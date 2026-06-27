import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  PenTool, Copy, Check, ExternalLink, Flame, TrendingUp, Cpu, Award, 
  FileText, BadgeHelp, RefreshCw, Layers, Sparkles, Clock, Compass, 
  Settings, Link, ShieldAlert, Search
} from 'lucide-react';

import useSettings from '../hooks/useSettings';
import useCategories from '../hooks/useCategories';
import useKeywords from '../hooks/useKeywords';
import useTitles from '../hooks/useTitles';
import usePipeline from '../hooks/usePipeline';
import useApi from '../hooks/useApi';

import CategoryHeader from './shared/CategoryHeader';
import KeywordList from './shared/KeywordList';
import TerminalLog from './shared/TerminalLog';
import ErrorBanner from './shared/ErrorBanner';

export default function V2AgentDashboard() {
  const [activeTab, setActiveTab] = useState('cluster'); // cluster, publish, links, performance, settings
  
  // Custom Hooks
  const settings = useSettings();
  const categories = useCategories();
  const titles = useTitles();
  const pipeline = usePipeline();
  const api = useApi();

  // Cluster states
  const [workMode, setWorkMode] = useState('single'); // single or cluster
  const [minSubs, setMinSubs] = useState(3);
  const [maxSubs, setMaxSubs] = useState(6);
  const [clusterLoading, setClusterLoading] = useState(false);
  const [clusterData, setClusterData] = useState(null);
  const [useCodexImages, setUseCodexImages] = useState(true);
  const [useContextualLinks, setUseContextualLinks] = useState(true);
  const [publishType, setPublishType] = useState('scheduled'); // immediate or scheduled
  
  const getInitialPublishTime = () => {
    const now = new Date();
    now.setMinutes(now.getMinutes() + 30);
    const yyyy = now.getFullYear();
    const mm = String(now.getMonth() + 1).padStart(2, '0');
    const dd = String(now.getDate()).padStart(2, '0');
    const hh = String(now.getHours()).padStart(2, '0');
    const min = String(now.getMinutes()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}T${hh}:${min}`;
  };
  const [firstPublishTime, setFirstPublishTime] = useState(getInitialPublishTime());
  const [clusterInterval, setClusterInterval] = useState(1);
  const [clusterTotal, setClusterTotal] = useState(5);

  // Settings
  const [telegramToken, setTelegramToken] = useState(localStorage.getItem('styler_telegramToken') || '');
  const [telegramChatId, setTelegramChatId] = useState(localStorage.getItem('styler_telegramChatId') || '');
  const [telegramTesting, setTelegramTesting] = useState(false);
  const [telegramTestResult, setTelegramTestResult] = useState(null);

  // Handle keyword selection and generate cluster/titles
  const handleKeywordSelected = useCallback((kwObj, catName) => {
    if (workMode === 'cluster' && kwObj) {
      setClusterData(null);
      setClusterLoading(true);
      fetch('/api/cluster-generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          keyword: kwObj.keyword,
          category: catName || categories.currentCategory,
          min_subs: minSubs,
          max_subs: maxSubs
        })
      })
      .then(res => res.json())
      .then(data => {
        if (!data.error) setClusterData(data);
        setClusterLoading(false);
      })
      .catch(err => {
        console.error("Cluster generation error:", err);
        setClusterLoading(false);
      });
    } else if (kwObj) {
      titles.handleGenerateTitles(kwObj, catName || categories.currentCategory);
    }
  }, [workMode, categories.currentCategory, minSubs, maxSubs, titles.handleGenerateTitles]);

  const keywords = useKeywords({ onKeywordSelected: handleKeywordSelected });

  // Handle manual keyword selection (click event)
  const handleSelectKeyword = useCallback((kw) => {
    if (!pipeline.pipelineRunning) {
      keywords.setSelectedKeyword(kw);
      handleKeywordSelected(kw, categories.subCategory);
    }
  }, [pipeline.pipelineRunning, keywords.setSelectedKeyword, handleKeywordSelected, categories.subCategory]);

  const handleWorkModeSelect = (modeValue) => {
    if (modeValue === 'single') {
      setWorkMode('single');
      setClusterTotal(1);
    } else {
      setWorkMode('cluster');
      const total = parseInt(modeValue);
      setClusterTotal(total);
      setMinSubs(total - 1);
      setMaxSubs(total - 1);
    }
  };

  // V2 Telegram Connection Test
  const handleTestTelegram = async () => {
    setTelegramTesting(true);
    setTelegramTestResult(null);
    try {
      const res = await fetch('/api/telegram-test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token: telegramToken,
          chat_id: telegramChatId
        })
      });
      const data = await res.json();
      setTelegramTestResult(data);
    } catch (err) {
      setTelegramTestResult({ ok: false, error: err.message });
    } finally {
      setTelegramTesting(false);
    }
  };

  const handleSaveTelegramConfig = () => {
    localStorage.setItem('styler_telegramToken', telegramToken);
    localStorage.setItem('styler_telegramChatId', telegramChatId);
    alert('텔레그램 설정이 로컬에 저장되었습니다.');
  };

  // Execute Pipeline (Single or Cluster)
  const handleStartPipeline = useCallback((e, publishFlag = false) => {
    if (e) e.preventDefault();
    if (!keywords.selectedKeyword) return;

    const finalLength = settings.getFinalLength();
    const finalTitle = titles.customTitle || (titles.selectedTitle ? titles.selectedTitle.title : `${keywords.selectedKeyword.keyword} 완벽 가이드`);

    if (workMode === 'cluster') {
      pipeline.runClusterPipeline({
        keyword: keywords.selectedKeyword.keyword,
        platform: settings.platform,
        style: settings.style,
        category: keywords.selectedKeyword.category || categories.currentCategory,
        length: finalLength || '5000',
        faq_count: settings.faqCount,
        img_prompt: useCodexImages ? 'ON' : 'OFF',
        contextual_links: useContextualLinks ? 'ON' : 'OFF',
        scheduled_at: publishType === 'scheduled' ? firstPublishTime.replace('T', ' ') + ':00' : null,
        seo_strength: settings.seoStrength,
        publish: publishFlag,
        min_subs: minSubs,
        max_subs: maxSubs,
        search_volume: keywords.selectedKeyword.search_volume,
        competition: keywords.selectedKeyword.competition,
        cpc: keywords.selectedKeyword.cpc
      }, clusterTotal, () => {
        api.fetchDashboardStats();
        api.fetchPostsList();
      });
    } else {
      pipeline.runSinglePipeline({
        keyword: keywords.selectedKeyword.keyword,
        platform: settings.platform,
        style: settings.style,
        search_volume: keywords.selectedKeyword.search_volume,
        competition: keywords.selectedKeyword.competition,
        cpc: keywords.selectedKeyword.cpc,
        category: keywords.selectedKeyword.category || categories.currentCategory,
        golden_score: keywords.selectedKeyword.golden_score,
        length: finalLength || '5000',
        faq_count: settings.faqCount,
        img_prompt: settings.generateImgPrompt,
        title: finalTitle,
        seo_strength: settings.seoStrength,
        publish: publishFlag
      }, () => {
        api.fetchDashboardStats();
        api.fetchPostsList();
      });
    }
  }, [
    keywords.selectedKeyword,
    titles.customTitle,
    titles.selectedTitle,
    settings,
    categories.currentCategory,
    workMode,
    useCodexImages,
    useContextualLinks,
    publishType,
    firstPublishTime,
    minSubs,
    maxSubs,
    clusterTotal,
    pipeline.runClusterPipeline,
    pipeline.runSinglePipeline,
    api.fetchDashboardStats,
    api.fetchPostsList
  ]);

  // Sync category changes to reload keywords
  useEffect(() => {
    if (categories.subCategory) {
      keywords.fetchKeywords(categories.subCategory);
      keywords.setSelectedKeyword(null);
      titles.resetTitles();
      setClusterData(null);
    }
  }, [categories.subCategory]);

  // Tab changes loaders
  useEffect(() => {
    if (activeTab === 'publish') {
      api.fetchDashboardStats();
      api.fetchPostsList();
    } else if (activeTab === 'links') {
      api.fetchLinksList();
    }
  }, [activeTab]);

  return (
    <div className="flex flex-col gap-6 w-full text-slate-100 font-sans">
      
      {/* Top Header Section with category picker */}
      <CategoryHeader
        title="AI Blog Operator"
        badge="v2.0 Agent"
        subtitle="토픽 클러스터 기획 → 사실 기반 RAG 수집 → 양산형 회피 생성 → 내부링크 그래프 → 텔레그램 리포트"
        mainCategory={categories.mainCategory}
        onMainCategoryChange={categories.setMainCategory}
        subCategory={categories.subCategory}
        onSubCategoryChange={categories.setSubCategory}
        sortedMainCategories={categories.sortedMainCategories}
        sortedSubCategories={categories.sortedSubCategories}
        disabled={pipeline.pipelineRunning}
      />
      <ErrorBanner message={pipeline.error} />

      {/* Tabs navigation */}
      <nav className="flex bg-slate-900/60 p-1.5 rounded-2xl border border-slate-850 gap-2 shadow-inner z-10">
        <button
          onClick={() => setActiveTab('cluster')}
          className={`flex-1 py-3 rounded-xl text-xs font-black transition-all flex items-center justify-center gap-1.5 ${activeTab === 'cluster' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20' : 'text-slate-400 hover:text-slate-200'}`}
        >
          <Sparkles size={14}/> 🎯 키워드 & 클러스터
        </button>
        <button
          onClick={() => setActiveTab('publish')}
          className={`flex-1 py-3 rounded-xl text-xs font-black transition-all flex items-center justify-center gap-1.5 ${activeTab === 'publish' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20' : 'text-slate-400 hover:text-slate-200'}`}
        >
          <Clock size={14}/> 📊 발행 관리
        </button>
        <button
          onClick={() => setActiveTab('links')}
          className={`flex-1 py-3 rounded-xl text-xs font-black transition-all flex items-center justify-center gap-1.5 ${activeTab === 'links' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20' : 'text-slate-400 hover:text-slate-200'}`}
        >
          <Link size={14}/> 🔗 링크 관리
        </button>
        <button
          onClick={() => setActiveTab('performance')}
          className={`flex-1 py-3 rounded-xl text-xs font-black transition-all flex items-center justify-center gap-1.5 ${activeTab === 'performance' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20' : 'text-slate-400 hover:text-slate-200'}`}
        >
          <TrendingUp size={14}/> 📈 성과 분석
        </button>
        <button
          onClick={() => setActiveTab('settings')}
          className={`flex-1 py-3 rounded-xl text-xs font-black transition-all flex items-center justify-center gap-1.5 ${activeTab === 'settings' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20' : 'text-slate-400 hover:text-slate-200'}`}
        >
          <Settings size={14}/> ⚙️ 설정
        </button>
      </nav>

      {/* Tab 1: 🎯 키워드 & 클러스터 */}
      {activeTab === 'cluster' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 w-full items-start animate-fadeIn">
          
          {/* 좌측 메인 영역: 8/12 컬럼 */}
          <div className="lg:col-span-8 flex flex-col gap-6 w-full">
            
            {/* 황금 키워드 발굴기 검색 및 제어 카드 */}
            <section className="glass-card rounded-3xl border border-white/5 shadow-2xl p-5 flex flex-col gap-4">
              <div className="flex flex-col gap-1.5">
                <label className="text-[11px] font-black text-slate-400 uppercase tracking-wider pl-0.5">관심 분야 (선택) 예: 여행 할인, 가전, 카드 혜택</label>
                <div className="flex gap-3">
                  <div className="relative flex-1">
                    <input
                      type="text"
                      placeholder="관심 분야 키워드를 입력해 주십시오."
                      value={keywords.keywordSearch}
                      onChange={(e) => keywords.setKeywordSearch(e.target.value)}
                      className="w-full pl-9 pr-3 py-3 rounded-2xl bg-slate-950 border border-slate-800 text-xs font-bold text-slate-300 focus:border-indigo-500 focus:outline-none transition-all placeholder-slate-655"
                    />
                    <Search size={14} className="absolute left-3.5 top-3.5 text-slate-650" />
                  </div>
                  <button
                    type="button"
                    onClick={() => {
                      if (!pipeline.pipelineRunning) {
                        keywords.fetchKeywords(keywords.keywordSearch || '정부지원금');
                      }
                    }}
                    className="px-6 py-3 rounded-2xl bg-amber-750 hover:bg-amber-650 active:scale-95 text-white font-extrabold text-xs transition-all shadow-lg flex items-center justify-center gap-1.5 cursor-pointer border border-amber-600/30"
                  >
                    <Flame size={14} />
                    황금 키워드 발굴
                  </button>
                </div>
              </div>
              <div className="text-[10px] text-slate-550 font-bold pl-0.5">
                기준일 2026년 06월 17일 · 키워드를 클릭하면 주제·제목·서브키워드가 자동 입력됩니다.
              </div>
            </section>

            {/* 실시간 발행 진행 카드 (프로그레스 바) */}
            {pipeline.pipelineRunning && workMode === 'cluster' && (
              <section className="glass-card rounded-3xl border border-orange-500/10 bg-orange-950/5 p-5 shadow-2xl flex flex-col gap-4 animate-fadeIn">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-black text-orange-400 flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-orange-500 animate-ping" />
                    {pipeline.clusterStatusLabel} ({pipeline.clusterCurrent}/{clusterTotal})
                  </span>
                  <button
                    type="button"
                    onClick={() => pipeline.abortPipeline()}
                    className="text-xs font-black text-rose-500 hover:text-rose-455 hover:underline cursor-pointer"
                  >
                    중지
                  </button>
                </div>
                <div className="w-full h-3 rounded-full bg-slate-900 border border-slate-800 overflow-hidden relative shadow-inner">
                  <div
                    className="h-full bg-gradient-to-r from-orange-600 to-amber-500 transition-all duration-500 rounded-full"
                    style={{ width: `${Math.min(100, (pipeline.clusterCurrent / clusterTotal) * 100)}%` }}
                  />
                </div>
              </section>
            )}

            {/* 실시간 터미널 로그 */}
            <TerminalLog 
              logs={pipeline.logs} 
              terminalStep={pipeline.terminalStep} 
              terminalEndRef={pipeline.terminalEndRef} 
              height="h-[220px]" 
            />

            {/* 황금틈새 판단 이유 카드 */}
            {clusterData && clusterData.niche_reason && (
              <section className="bg-sky-955/20 border border-sky-500/15 rounded-3xl p-5 shadow-2xl flex flex-col gap-4 animate-fadeIn">
                <h3 className="text-xs font-black text-sky-300 flex items-center gap-1.5 uppercase tracking-wider border-b border-sky-900/40 pb-3">
                  💡 황금틈새 판단 이유
                </h3>
                <div className="flex flex-col gap-2.5 text-xs text-slate-355 leading-relaxed font-medium">
                  <div>
                    <strong className="text-orange-400/95 font-bold">대부분이 쓰는 내용:</strong> {clusterData.niche_reason.what_most_write}
                  </div>
                  <div>
                    <strong className="text-sky-300 font-bold">놓친 사실:</strong> {clusterData.niche_reason.missed_facts}
                  </div>
                  <div>
                    <strong className="text-sky-300 font-bold">실제 질문:</strong> {clusterData.niche_reason.real_question}
                  </div>
                  <div className="mt-1 border-t border-sky-900/20 pt-2 text-slate-400 text-[11px] font-normal leading-relaxed italic">
                    {clusterData.niche_reason.strategy}
                  </div>
                </div>
                {clusterData.tags && clusterData.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-1 pt-1.5 border-t border-sky-900/10">
                    {clusterData.tags.map((tag, tidx) => (
                      <span key={tidx} className="bg-sky-500/10 border border-sky-500/20 text-sky-400 px-3.5 py-1 rounded-full text-[10.5px] font-black cursor-pointer hover:bg-sky-500/20 transition-all">
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </section>
            )}

            {/* 콘텐츠 설계 프리뷰 리스트 */}
            {clusterData && (
              <section className="glass-card rounded-3xl border border-white/5 shadow-2xl p-5 flex flex-col gap-4 animate-fadeIn">
                <div className="flex flex-col gap-1 border-l-4 border-indigo-500 pl-3">
                  <span className="text-[10px] text-indigo-400 font-extrabold tracking-wider uppercase">메인 종합 가이드 포스트</span>
                  <span className="text-xs font-black text-slate-100">{clusterData.main.title}</span>
                  <span className="text-[10px] text-slate-500 leading-normal">{clusterData.main.summary}</span>
                </div>

                <div className="flex flex-col gap-2.5 mt-2">
                  <span className="text-[10px] text-slate-400 font-extrabold uppercase pl-1">서브글 상세 링크 매핑 ({clusterData.subs.length}개)</span>
                  <div className="flex flex-col gap-2 max-h-72 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-855">
                    {clusterData.subs.map((sub, sidx) => (
                      <div key={sidx} className="bg-slate-900/50 border border-slate-855 p-3 rounded-2xl flex flex-col gap-1 text-[11px]">
                        <div className="flex justify-between items-center text-slate-400 gap-2">
                          <span className="font-bold text-white truncate">서브 #{sidx+1}: {sub.title}</span>
                          <span className="bg-indigo-600/20 text-indigo-300 border border-indigo-500/20 px-2 py-0.5 rounded font-black text-[9px] shrink-0">{sub.intent}</span>
                        </div>
                        <p className="text-[10px] text-slate-500 mt-0.5 leading-relaxed">{sub.summary}</p>
                        <div className="text-[10px] text-slate-500 mt-1 border-t border-slate-850/30 pt-1.5">
                          유도 앵커 CTA: <strong className="text-slate-350 font-bold select-all">"{sub.anchor}"</strong>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </section>
            )}

            {/* 황금 키워드 분석 카드 목록 */}
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

          </div>

          {/* 우측 사이드바 영역: 4/12 컬럼 (스마트 발행 설정) */}
          <div className="lg:col-span-4 flex flex-col gap-6 w-full relative z-20">
            <section className="glass-card rounded-3xl border border-white/5 shadow-2xl p-5 flex flex-col gap-5">
              
              {/* Codex AI Image Toggle */}
              <div className="flex items-center justify-between border-b border-slate-900/50 pb-4">
                <div className="flex flex-col gap-0.5">
                  <span className="text-xs font-bold text-slate-200">Codex AI 이미지 2개</span>
                  <span className="text-[10px] text-slate-500 leading-normal">대표 썸네일(한글 문구) + 본문 연관 이미지</span>
                </div>
                <button
                  type="button"
                  onClick={() => setUseCodexImages(!useCodexImages)}
                  className={`w-12 h-6.5 rounded-full p-0.5 transition-all duration-300 focus:outline-none ${useCodexImages ? 'bg-emerald-600' : 'bg-slate-800'}`}
                >
                  <div className={`w-5.5 h-5.5 rounded-full bg-white shadow-md transform transition-all duration-300 ${useCodexImages ? 'translate-x-5.5' : 'translate-x-0'}`} />
                </button>
              </div>

              {/* Contextual links toggle */}
              <div className="flex items-center justify-between border-b border-slate-900/50 pb-4">
                <div className="flex flex-col gap-0.5">
                  <span className="text-xs font-bold text-slate-200">문맥형 내부링크 자동 구성</span>
                  <span className="text-[10px] text-slate-500 leading-normal font-medium">서브글마다 메인 1개 + 최적 글 연결</span>
                </div>
                <button
                  type="button"
                  onClick={() => useContextualLinks ? setUseContextualLinks(false) : setUseContextualLinks(true)}
                  className={`w-12 h-6.5 rounded-full p-0.5 transition-all duration-300 focus:outline-none ${useContextualLinks ? 'bg-emerald-600' : 'bg-slate-800'}`}
                >
                  <div className={`w-5.5 h-5.5 rounded-full bg-white shadow-md transform transition-all duration-300 ${useContextualLinks ? 'translate-x-5.5' : 'translate-x-0'}`} />
                </button>
              </div>

              {/* Work Mode */}
              <div className="flex flex-col gap-1.5">
                <label className="text-[11px] font-black text-slate-455 uppercase tracking-wider pl-0.5">작업 모드</label>
                <select
                  value={workMode === 'single' ? 'single' : String(clusterTotal)}
                  onChange={(e) => handleWorkModeSelect(e.target.value)}
                  disabled={pipeline.pipelineRunning}
                  className="w-full px-3 py-2.5 rounded-xl bg-slate-950 border border-slate-850 focus:border-indigo-500 focus:outline-none text-xs font-black text-slate-250 cursor-pointer"
                  style={{ colorScheme: 'dark' }}
                >
                  <option value="5">5개 클러스터 · 서브글 4개 + 메인글 1개</option>
                  <option value="4">4개 클러스터 · 서브글 3개 + 메인글 1개</option>
                  <option value="3">3개 클러스터 · 서브글 2개 + 메인글 1개</option>
                  <option value="single">단일 글 발행</option>
                </select>
              </div>

              {/* Publish Type */}
              <div className="flex flex-col gap-1.5">
                <label className="text-[11px] font-black text-slate-455 uppercase tracking-wider pl-0.5">발행 방식</label>
                <select
                  value={publishType}
                  onChange={(e) => setPublishType(e.target.value)}
                  disabled={pipeline.pipelineRunning}
                  className="w-full px-3 py-2.5 rounded-xl bg-slate-950 border border-slate-855 focus:border-indigo-500 focus:outline-none text-xs font-black text-slate-250 cursor-pointer"
                  style={{ colorScheme: 'dark' }}
                >
                  <option value="scheduled">날짜·시간 예약 발행</option>
                  <option value="immediate">즉시 발행</option>
                </select>
              </div>

              {/* Scheduled time */}
              {publishType === 'scheduled' && (
                <div className="flex flex-col gap-1.5 animate-fadeIn">
                  <label className="text-[11px] font-black text-slate-455 uppercase tracking-wider pl-0.5">첫 발행 날짜·시간</label>
                  <input
                    type="datetime-local"
                    value={firstPublishTime}
                    onChange={(e) => setFirstPublishTime(e.target.value)}
                    disabled={pipeline.pipelineRunning}
                    className="w-full px-3 py-2.5 rounded-xl bg-slate-950 border border-slate-850 text-xs text-slate-200 focus:border-indigo-500 focus:outline-none"
                    style={{ colorScheme: 'dark' }}
                  />
                  <span className="text-[9.5px] text-slate-500 leading-normal pl-0.5 mt-0.5">
                    글 생성과 링크 후처리 시간을 고려해 현재 시각보다 30분 이상 뒤를 권장합니다.
                  </span>
                </div>
              )}

              {/* Cluster interval */}
              {workMode === 'cluster' && publishType === 'scheduled' && (
                <div className="flex flex-col gap-1.5 animate-fadeIn">
                  <label className="text-[11px] font-black text-slate-455 uppercase tracking-wider pl-0.5">클러스터 글 사이 간격</label>
                  <div className="relative flex items-center">
                    <input
                      type="number"
                      min="1"
                      max="48"
                      value={clusterInterval}
                      onChange={(e) => setClusterInterval(parseInt(e.target.value) || 1)}
                      disabled={pipeline.pipelineRunning}
                      className="w-full pl-3 pr-12 py-2.5 rounded-xl bg-slate-950 border border-slate-855 text-xs font-bold text-slate-200 focus:border-indigo-500 focus:outline-none"
                    />
                    <span className="absolute right-3.5 text-xs text-slate-400 font-extrabold select-none">시간</span>
                  </div>
                  <span className="text-[9.5px] text-slate-500 leading-normal pl-0.5 mt-0.5">
                    1시간 단위로 직접 설정합니다. 예약 시 메인글이 먼저 공개되고 서브글들이 순서대로 공개됩니다.
                  </span>
                </div>
              )}

              {/* Execution Actions */}
              <div className="flex flex-col gap-3 mt-3 pt-3 border-t border-slate-900 relative z-20 shrink-0">
                <button
                  type="button"
                  onClick={(e) => handleStartPipeline(e, false)}
                  disabled={pipeline.pipelineRunning || !keywords.selectedKeyword}
                  className={`py-3.5 rounded-2xl text-white font-extrabold text-xs shadow-xl transition-all text-center flex items-center justify-center gap-1.5 cursor-pointer ${pipeline.pipelineRunning || !keywords.selectedKeyword ? 'bg-indigo-950/40 text-slate-500 border border-slate-900/50 cursor-not-allowed opacity-50' : 'bg-slate-900 hover:bg-slate-855 border border-slate-800'}`}
                >
                  <FileText size={13}/>
                  {workMode === 'cluster' ? '클러스터 임시 저장' : '단일글 임시 저장'}
                </button>
                <button
                  type="button"
                  onClick={(e) => handleStartPipeline(e, true)}
                  disabled={pipeline.pipelineRunning || !keywords.selectedKeyword}
                  className={`py-3.5 rounded-2xl text-white font-extrabold text-xs shadow-xl transition-all text-center flex items-center justify-center gap-1.5 cursor-pointer ${pipeline.pipelineRunning || !keywords.selectedKeyword ? 'bg-emerald-950/40 text-slate-500 border border-slate-900/50 cursor-not-allowed opacity-50' : 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 shadow-emerald-500/10'}`}
                >
                  <PenTool size={13}/>
                  {workMode === 'cluster' ? '클러스터 일괄 자동 발행' : '단일글 자동 발행'}
                </button>
              </div>

            </section>
          </div>
        </div>
      )}

      {/* Tab 2: 📊 발행 관리 */}
      {activeTab === 'publish' && (
        <div className="flex flex-col gap-6 w-full animate-fadeIn">
          
          {/* Stats grid */}
          <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
            <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-850/80 flex flex-col justify-between shadow-sm">
              <span className="text-[10px] font-bold text-slate-400 uppercase">전체 클러스터</span>
              <span className="text-2xl font-black text-white mt-1">{api.dashboardStats.total_clusters}</span>
            </div>
            <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-850/80 flex flex-col justify-between shadow-sm">
              <span className="text-[10px] font-bold text-slate-400 uppercase">발행 완료</span>
              <span className="text-2xl font-black text-emerald-400 mt-1">{api.dashboardStats.total_published}</span>
            </div>
            <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-850/80 flex flex-col justify-between shadow-sm">
              <span className="text-[10px] font-bold text-slate-400 uppercase">내부링크 삽입 수</span>
              <span className="text-2xl font-black text-indigo-400 mt-1">{api.dashboardStats.total_links}</span>
            </div>
            <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-850/80 flex flex-col justify-between shadow-sm">
              <span className="text-[10px] font-bold text-slate-400 uppercase">오늘 발행 수</span>
              <span className="text-2xl font-black text-teal-400 mt-1">{api.dashboardStats.today_published || 0}</span>
            </div>
            <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-850/80 flex flex-col justify-between shadow-sm">
              <span className="text-[10px] font-bold text-slate-400 uppercase">발행 대기</span>
              <span className="text-2xl font-black text-amber-400 mt-1">{api.dashboardStats.total_pending}</span>
            </div>
            <div className="p-4 rounded-2xl bg-rose-950/20 border border-rose-900/20 flex flex-col justify-between shadow-sm">
              <span className="text-[10px] font-bold text-rose-300 uppercase">발행 실패</span>
              <span className="text-2xl font-black text-rose-400 mt-1">{api.dashboardStats.total_failed}</span>
            </div>
          </div>

          {/* Posts list table */}
          <section className="glass-card rounded-3xl border border-white/5 p-5 shadow-2xl flex flex-col gap-4">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-xs font-black text-slate-300 flex items-center gap-1.5 uppercase tracking-wider">
                  <FileText size={14} className="text-indigo-400" />
                  플랫폼 발행 포스트 이력 목록
                </h3>
              </div>
              <button 
                onClick={api.fetchPostsList}
                className="p-1.5 rounded-lg border border-slate-800 bg-slate-900 hover:bg-slate-850 text-slate-400"
              >
                <RefreshCw size={12}/>
              </button>
            </div>

            <div className="overflow-x-auto border border-slate-900 rounded-2xl">
              {api.postsList.length === 0 ? (
                <div className="p-10 text-center text-xs text-slate-500 italic">발행 이력이 없습니다. 첫 번째 클러스터를 발행해 보십시오.</div>
              ) : (
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="bg-slate-950 border-b border-slate-900 text-slate-400 font-bold">
                      <th className="p-3">역할</th>
                      <th className="p-3">플랫폼</th>
                      <th className="p-3">키워드</th>
                      <th className="p-3">글 제목</th>
                      <th className="p-3 text-center">외부 라이브 링크</th>
                      <th className="p-3 text-center">상태</th>
                      <th className="p-3">발행시간</th>
                    </tr>
                  </thead>
                  <tbody>
                    {api.postsList.map((post, idx) => (
                      <tr key={idx} className="border-b border-slate-900/50 hover:bg-white/5 text-slate-300 transition-all">
                        <td className="p-3">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-black uppercase ${post.role === 'main' ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/20' : 'bg-slate-950 text-slate-400'}`}>
                            {post.role === 'main' ? 'Main 종합' : 'Sub 서브'}
                          </span>
                        </td>
                        <td className="p-3 uppercase text-[10px] font-bold text-slate-400">{post.platform}</td>
                        <td className="p-3 font-semibold text-slate-200">{post.keyword}</td>
                        <td className="p-3 truncate max-w-[200px]" title={post.title}>{post.title}</td>
                        <td className="p-3 text-center">
                          {post.url && !post.url.startsWith('local://') ? (
                            <a href={post.url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 text-indigo-400 hover:text-indigo-300 font-bold hover:underline select-all">
                              URL 보기 <ExternalLink size={10}/>
                            </a>
                          ) : (
                            <span className="text-slate-600 italic text-[10px]">로컬 저장 (Mock)</span>
                          )}
                        </td>
                        <td className="p-3 text-center">
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-black ${post.status === 'published' ? 'bg-emerald-950 text-emerald-400 border border-emerald-900/30' : 'bg-rose-950 text-rose-450 border-rose-900/30'}`}>
                            {post.status === 'published' ? '발행완료' : '실패'}
                          </span>
                        </td>
                        <td className="p-3 text-slate-500 font-medium">{post.published_at || '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </section>
        </div>
      )}

      {/* Tab 3: 🔗 내부링크 그래프 */}
      {activeTab === 'links' && (
        <div className="flex flex-col gap-6 w-full animate-fadeIn">
          <section className="glass-card rounded-3xl border border-white/5 p-5 shadow-2xl flex flex-col gap-4">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-xs font-black text-slate-300 flex items-center gap-1.5 uppercase tracking-wider">
                  <Link size={14} className="text-indigo-400" />
                  클러스터 내부링크(CTA) 자동 매핑 네트워크 로그
                </h3>
              </div>
              <button 
                onClick={api.fetchLinksList}
                className="p-1.5 rounded-lg border border-slate-800 bg-slate-900 hover:bg-slate-850 text-slate-400"
              >
                <RefreshCw size={12}/>
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {api.linksList.length === 0 ? (
                <div className="col-span-2 p-10 text-center text-xs text-slate-500 italic border border-dashed border-slate-855 rounded-2xl">
                  삽입된 내부링크 그래프 이력이 존재하지 않습니다.
                </div>
              ) : (
                api.linksList.map((link, idx) => (
                  <div key={idx} className="p-4 rounded-2xl bg-slate-900/30 border border-slate-855 flex flex-col gap-3 justify-between shadow-sm">
                    <div className="flex justify-between items-center">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-black uppercase ${
                        link.link_type === 'main_to_sub' ? 'bg-indigo-600/20 text-indigo-300' :
                        link.link_type === 'sub_to_main' ? 'bg-emerald-600/20 text-emerald-300' :
                        'bg-slate-950 text-slate-400'
                      }`}>
                        {link.link_type === 'main_to_sub' ? 'Main → Sub' :
                         link.link_type === 'sub_to_main' ? 'Sub → Main' :
                         'Sub ↔ Sub'}
                      </span>
                      <span className="text-[10px] text-slate-550 font-semibold">{link.inserted_at}</span>
                    </div>

                    <div className="flex flex-col gap-1.5">
                      <div className="text-[11px] text-slate-400">
                        출발 포스트: <strong className="text-slate-200 font-bold select-all">{link.source_title}</strong>
                      </div>
                      <div className="text-[11px] text-slate-400">
                        목적 포스트: <strong className="text-slate-200 font-bold select-all">{link.target_title}</strong>
                      </div>
                      {link.target_url && (
                        <a href={link.target_url} target="_blank" rel="noopener noreferrer" className="text-[10px] text-indigo-400 hover:text-indigo-300 flex items-center gap-1 w-max font-bold hover:underline select-all">
                          목적 페이지 주소: {link.target_url} <ExternalLink size={8}/>
                        </a>
                      )}
                    </div>

                    <div className="bg-slate-950/60 p-2.5 rounded-xl border border-slate-900/50 text-xs text-slate-300 font-bold leading-normal">
                      유도 앵커 텍스트: <span className="text-indigo-400 font-black">"{link.anchor_text}"</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </section>
        </div>
      )}

      {/* Tab 4: 📈 성과 분석 */}
      {activeTab === 'performance' && (
        <div className="flex flex-col gap-6 w-full animate-fadeIn">
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-5 rounded-2xl bg-gradient-to-br from-indigo-950/20 to-slate-900/40 border border-indigo-500/20 flex flex-col justify-between gap-4 shadow-sm">
              <div>
                <span className="text-[11px] font-bold text-slate-400 uppercase">예상 일일 유입량</span>
                <h4 className="text-3xl font-black text-indigo-400 mt-1 select-all">14,280명</h4>
              </div>
              <span className="text-[10px] text-slate-500 leading-relaxed">상위 노출 점유 시 포지셔닝에 따른 월 총 {(14280*30).toLocaleString()}명 유입 시뮬레이션.</span>
            </div>

            <div className="p-5 rounded-2xl bg-gradient-to-br from-emerald-950/20 to-slate-900/40 border border-emerald-500/20 flex flex-col justify-between gap-4 shadow-sm">
              <div>
                <span className="text-[11px] font-bold text-slate-400 uppercase">월 예상 애드센스 매출</span>
                <h4 className="text-3xl font-black text-emerald-400 mt-1 select-all">$2,250.40</h4>
              </div>
              <span className="text-[10px] text-slate-500 leading-relaxed">월 약 2,700,000원 상당. 평균 CTR 3.2% 및 금융 카테고리 광고 우선 매칭 지수 적용.</span>
            </div>

            <div className="p-5 rounded-2xl bg-gradient-to-br from-teal-950/20 to-slate-900/40 border border-teal-500/20 flex flex-col justify-between gap-4 shadow-sm">
              <div>
                <span className="text-[11px] font-bold text-slate-400 uppercase">누적 발행 글 가치 환산</span>
                <h4 className="text-3xl font-black text-teal-400 mt-1 select-all">9,840,000원</h4>
              </div>
              <span className="text-[10px] text-slate-500 leading-relaxed">축적된 디지털 에셋의 예상 평생 광고 기여 가치 연산 점수.</span>
            </div>
          </div>

          <section className="glass-card rounded-3xl border border-white/5 p-5 shadow-2xl">
            <h3 className="text-xs font-black text-slate-300 flex items-center gap-1.5 uppercase tracking-wider mb-4">
              <TrendingUp size={14} className="text-indigo-400" />
              카테고리별 광고가치 및 단가 시뮬레이션 지표
            </h3>
            
            <div className="overflow-x-auto border border-slate-900 rounded-2xl text-xs">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-950 border-b border-slate-900 text-slate-400 font-bold">
                    <th className="p-3">카테고리 구분</th>
                    <th className="p-3 text-center">평균 CPC 달러</th>
                    <th className="p-3 text-center">추천 포스팅 단축기</th>
                    <th className="p-3 text-center">예상 가치가 등급</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-slate-900/50 text-slate-300 hover:bg-white/5 transition-all">
                    <td className="p-3 font-semibold">금융/대출/재테크</td>
                    <td className="p-3 text-center text-emerald-400 font-bold">$3.20 - $5.50</td>
                    <td className="p-3 text-center text-indigo-400 font-bold">청년내일채움공제, 정부 대출지원금</td>
                    <td className="p-3 text-center font-black text-white">S등급</td>
                  </tr>
                  <tr className="border-b border-slate-900/50 text-slate-300 hover:bg-white/5 transition-all">
                    <td className="p-3 font-semibold">부동산/청약/재개발</td>
                    <td className="p-3 text-center text-emerald-400 font-bold">$1.80 - $2.80</td>
                    <td className="p-3 text-center text-indigo-400 font-bold">청년 우대형 청약 종합 가이드</td>
                    <td className="p-3 text-center font-black text-slate-300">A등급</td>
                  </tr>
                  <tr className="border-b border-slate-900/50 text-slate-300 hover:bg-white/5 transition-all">
                    <td className="p-3 font-semibold">건강/다이어트/질병</td>
                    <td className="p-3 text-center text-emerald-400 font-bold">$1.50 - $2.20</td>
                    <td className="p-3 text-center text-indigo-400 font-bold">당뇨 환자 과일, 대상포진 초기증상</td>
                    <td className="p-3 text-center font-black text-slate-300">A등급</td>
                  </tr>
                  <tr className="border-b border-slate-900/50 text-slate-300 hover:bg-white/5 transition-all">
                    <td className="p-3 font-semibold">생활/자동차/여행</td>
                    <td className="p-3 text-center text-slate-500 font-bold">$0.80 - $1.30</td>
                    <td className="p-3 text-center text-indigo-400 font-bold">겨울 난방비 절약 팁, 캠핑장 추천</td>
                    <td className="p-3 text-center font-black text-slate-450">B등급</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>
        </div>
      )}

      {/* Tab 5: ⚙️ 설정 */}
      {activeTab === 'settings' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 w-full items-start animate-fadeIn">
          
          <div className="lg:col-span-6 flex flex-col gap-6 w-full">
            <section className="glass-card rounded-3xl border border-white/5 p-5 shadow-2xl flex flex-col gap-4">
              <h3 className="text-xs font-black text-slate-300 flex items-center gap-1.5 uppercase tracking-wider border-b border-slate-800 pb-3">
                <Settings size={14} className="text-indigo-400 animate-spin" />
                외부 텔레그램 연동 및 채널 경고 알림 설정
              </h3>

              <div className="flex flex-col gap-3">
                <div className="flex flex-col gap-1.5">
                  <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">텔레그램 봇 토큰 (TELEGRAM_BOT_TOKEN)</label>
                  <input
                    type="password"
                    value={telegramToken}
                    onChange={(e) => setTelegramToken(e.target.value)}
                    placeholder="텔레그램 HTTP API 봇 토큰 입력"
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 focus:border-indigo-500 focus:outline-none text-xs font-bold text-slate-200"
                  />
                </div>

                <div className="flex flex-col gap-1.5">
                  <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">텔레그램 대화 ID (TELEGRAM_CHAT_ID)</label>
                  <input
                    type="text"
                    value={telegramChatId}
                    onChange={(e) => setTelegramChatId(e.target.value)}
                    placeholder="알림을 수신받을 Chat ID 입력 (예: 55431230)"
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 focus:border-indigo-500 focus:outline-none text-xs font-bold text-slate-200"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3 mt-2">
                  <button
                    type="button"
                    onClick={handleTestTelegram}
                    disabled={telegramTesting || !telegramToken}
                    className="py-2.5 rounded-xl bg-slate-900 hover:bg-slate-850 text-slate-300 font-extrabold text-xs border border-slate-800 cursor-pointer flex items-center justify-center gap-1"
                  >
                    <RefreshCw size={12} className={telegramTesting ? 'animate-spin' : ''} />
                    연결 상태 테스트
                  </button>
                  <button
                    type="button"
                    onClick={handleSaveTelegramConfig}
                    className="py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-extrabold text-xs cursor-pointer"
                  >
                    설정값 로컬 저장
                  </button>
                </div>

                {telegramTestResult && (
                  <div className={`p-3 rounded-xl border mt-2 text-xs font-semibold leading-relaxed animate-fadeIn ${telegramTestResult.ok ? 'bg-emerald-950/20 border-emerald-900/30 text-emerald-400' : 'bg-rose-950/20 border-rose-900/30 text-rose-450'}`}>
                    {telegramTestResult.ok ? '✅ 텔레그램 테스트 메시지가 채널로 정상 발송되었습니다.' : `❌ 텔레그램 연동 실패: ${telegramTestResult.error || '토큰이나 Chat ID를 다시 확인하십시오.'}`}
                  </div>
                )}
              </div>
            </section>
          </div>

          <div className="lg:col-span-6 flex flex-col gap-6 w-full">
            <section className="glass-card rounded-3xl border border-white/5 p-5 shadow-2xl flex flex-col gap-4">
              <h3 className="text-xs font-black text-slate-300 flex items-center gap-1.5 uppercase tracking-wider border-b border-slate-800 pb-3">
                <Cpu size={14} className="text-indigo-400" />
                기타 연동 API 환경 변수 가이드
              </h3>
              
              <div className="flex flex-col gap-3 text-xs leading-relaxed text-slate-400 font-medium pl-1">
                <p>본 블로그 에이전트는 자동화 동작을 위해 로컬 환경 변수 파일(<strong className="text-slate-200">.env</strong>)을 로드하여 기동합니다.</p>
                <div className="flex flex-col gap-2 bg-slate-950/60 p-3 rounded-2xl border border-slate-900 font-mono text-[11px] text-indigo-300 leading-normal select-all mt-1">
                  <div>GEMINI_API_KEY=AI_Studio_발급_키_값</div>
                  <div>TISTORY_ACCESS_TOKEN=Tistory_OAuth_토큰</div>
                  <div>TISTORY_BLOG_NAME=Tistory_블로그_이름</div>
                  <div>TELEGRAM_BOT_TOKEN=텔레그램_토큰</div>
                  <div>TELEGRAM_CHAT_ID=텔레그램_챗ID</div>
                </div>
                <p className="mt-1 flex items-center gap-1.5 text-slate-500 text-[11px] font-bold">
                  <ShieldAlert size={14} className="text-amber-500 animate-pulse" />
                  API 키 유출 예방을 위해 해당 .env 파일은 빌드 타겟 배포 파일에서 제외하여 관리하십시오.
                </p>
              </div>
            </section>
          </div>

        </div>
      )}

    </div>
  );
}

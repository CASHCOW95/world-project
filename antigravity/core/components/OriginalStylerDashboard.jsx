import React, { useState, useEffect, useRef, useCallback } from 'react';
import { PenTool, Copy, Check, Search, Flame, TrendingUp, Cpu, Award, FileText, BadgeHelp, DollarSign, Users, MousePointer, Layers, Sparkles, Compass, Settings } from 'lucide-react';
import { CATEGORY_MAP, CATEGORY_WEIGHTS, formatHistoryPlatform, formatHistoryDate, normalizeHistoryItem, getStoredValue, getSortedSubCategories } from './dashboardUtils';

export default function OriginalStylerDashboard() {
  // 40 Categories database state
  const [categories, setCategories] = useState({});
  const [mainCategory, setMainCategory] = useState('정부정책');
  const [subCategory, setSubCategory] = useState('정부지원금');
  const currentCategory = subCategory;
  const [keywordLoading, setKeywordLoading] = useState(false);
  const [keywords, setKeywords] = useState([]);
  const [selectedKeyword, setSelectedKeyword] = useState(null);
  const [keywordSearch, setKeywordSearch] = useState('');

  const [keywordSortType, setKeywordSortType] = useState('recommend'); // recommend, latest, volume, cpc
  const [customTitle, setCustomTitle] = useState('');
  const [activeTooltip, setActiveTooltip] = useState(null);

  const renderTooltip = (id, label, title, desc, iconColor = "text-slate-500") => {
    return (
      <span 
        className="relative inline-flex items-center gap-1 cursor-help select-none"
        onMouseEnter={() => setActiveTooltip(id)}
        onMouseLeave={() => setActiveTooltip(null)}
        onClick={(e) => {
          e.stopPropagation();
          setActiveTooltip(activeTooltip === id ? null : id);
        }}
      >
        <span className="font-bold">{label}</span>
        <BadgeHelp size={12} className={`${iconColor} hover:text-slate-300 transition-colors`} />
        {activeTooltip === id && (
          <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2.5 w-60 p-3 bg-slate-900 border border-slate-800 text-slate-300 rounded-2xl shadow-2xl text-[11px] font-semibold leading-relaxed z-50 text-left border-l-4 border-l-indigo-500 whitespace-normal">
            <span className="font-extrabold text-white mb-1 text-[12px] block">{title}</span>
            <span className="block">{desc}</span>
          </span>
        )}
      </span>
    );
  };

  // Title generation states
  const [titles, setTitles] = useState([]);
  const [titlesLoading, setTitlesLoading] = useState(false);
  const [selectedTitle, setSelectedTitle] = useState(null);
  const [titleFilter, setTitleFilter] = useState('전체');

  // Publisher configurations
  const [style, setStyle] = useState(() => getStoredValue('styler_style_v3', 'friendly'));
  const [platform, setPlatform] = useState(() => getStoredValue('styler_platform_v3', 'tistory'));
  const [ctaStyle, setCtaStyle] = useState(() => getStoredValue('styler_ctaStyle_v3', 'card'));
  const [articleLength, setArticleLength] = useState(() => getStoredValue('styler_articleLength_v3', '5000'));
  const [customLength] = useState(() => getStoredValue('styler_customLength_v3', ''));
  const [faqCount, setFaqCount] = useState(() => getStoredValue('styler_faqCount_v3', '10'));
  const [generateImgPrompt, setGenerateImgPrompt] = useState(() => getStoredValue('styler_generateImgPrompt_v3', 'OFF'));
  const [seoStrength, setSeoStrength] = useState(() => getStoredValue('styler_seoStrength_v3', 'strong')); // normal, strong, extreme
  const [selectedProfileId, setSelectedProfileId] = useState(localStorage.getItem('styler_selectedProfileId_v3') || '');

  // Pipeline execution state
  const [pipelineRunning, setPipelineRunning] = useState(false);
  const [logs, setLogs] = useState([]);
  const [result, setResult] = useState(null);
  const [, setError] = useState('');
  const [copied, setCopied] = useState(false);
  const [terminalStep, setTerminalStep] = useState('');

  // History state
  const [history, setHistory] = useState([]);
  const [selectedHistoryItem, setSelectedHistoryItem] = useState(null);

  const terminalEndRef = useRef(null);

  // Save options on change
  useEffect(() => {
    localStorage.setItem('styler_style_v3', style);
    localStorage.setItem('styler_platform_v3', platform);
    localStorage.setItem('styler_ctaStyle_v3', ctaStyle);
    localStorage.setItem('styler_articleLength_v3', articleLength);
    localStorage.setItem('styler_customLength_v3', customLength);
    localStorage.setItem('styler_faqCount_v3', faqCount);
    localStorage.setItem('styler_generateImgPrompt_v3', generateImgPrompt);
    localStorage.setItem('styler_seoStrength_v3', seoStrength);
  }, [style, platform, ctaStyle, articleLength, customLength, faqCount, generateImgPrompt, seoStrength]);

  useEffect(() => {
    const loadPublisherProfiles = async () => {
      try {
        const res = await fetch('/api/publisher-profiles');
        const data = await res.json();
        const profilesForPlatform = (data.profiles || []).filter(p => p.platform === platform && p.enabled !== false);
        const savedProfile = profilesForPlatform.find(p => p.id === selectedProfileId);
        const nextProfile = savedProfile || profilesForPlatform[0] || null;
        if (nextProfile) {
          setSelectedProfileId(nextProfile.id);
        } else {
          setSelectedProfileId('');
        }
      } catch (err) {
        console.error('Failed to load publisher profiles:', err);
      }
    };
    loadPublisherProfiles();
  }, [platform, selectedProfileId]);

  useEffect(() => {
    if (selectedProfileId) {
      localStorage.setItem('styler_selectedProfileId_v3', selectedProfileId);
    }
  }, [selectedProfileId]);

  const handleGenerateTitles = useCallback(async (kwObj, catName) => {
    if (!kwObj) return;
    setTitlesLoading(true);
    setTitles([]);
    setSelectedTitle(null);
    setCustomTitle('');
    try {
      const res = await fetch('/api/generate-titles', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          keyword: kwObj.keyword,
          category: catName || currentCategory
        })
      });
      const data = await res.json();
      if (data && Array.isArray(data)) {
        const scored = data.map((t) => {
          const scoreFactor = t.title.length % 7;
          const ctr = parseFloat((8.5 + (scoreFactor * 0.2)).toFixed(1));
          const seo = 75 + (t.title.length % 5) * 5;
          const score = ctr * 10 + seo;
          return { ...t, ctr, seo, score };
        }).sort((a, b) => b.score - a.score);

        setTitles(scored);
        if (scored.length > 0) {
          setSelectedTitle(scored[0]);
          setCustomTitle(scored[0].title);
        }
      }
    } catch (err) {
      console.error("Failed to generate titles:", err);
    } finally {
      setTitlesLoading(false);
    }
  }, [currentCategory]);

  const fetchHistory = useCallback(async () => {
    try {
      const res = await fetch('/api/history');
      const data = await res.json();
      setHistory(data);
    } catch (err) {
      console.error("Failed to fetch history:", err);
    }
  }, []);

  const handleMainCategoryChange = useCallback((nextMainCategory) => {
    setMainCategory(nextMainCategory);
    const subCategories = getSortedSubCategories(categories, nextMainCategory);
    if (subCategories.length > 0) {
      setSubCategory(subCategories[0]);
    }
  }, [categories]);

  // Load 40 Categories database on mount
  useEffect(() => {
    const loadCategories = async () => {
      try {
        const res = await fetch('/api/categories');
        const data = await res.json();
        setCategories(data);
      } catch (err) {
        console.error("Failed to load categories.json database:", err);
      }
    };

    const loadHistory = async () => {
      try {
        const res = await fetch('/api/history');
        const data = await res.json();
        setHistory(data);
      } catch (err) {
        console.error("Failed to fetch history:", err);
      }
    };

    loadCategories();
    loadHistory();
  }, []);

  // Reload keywords on category changes
  useEffect(() => {
    if (!subCategory) return;

    const loadKeywords = async () => {
      setKeywordLoading(true);
      setSelectedKeyword(null);
      setTitles([]);
      setSelectedTitle(null);
      setResult(null);

      try {
        const res = await fetch(`/api/keywords?category=${encodeURIComponent(subCategory)}`);
        const data = await res.json();
        setKeywords(data);
        if (data.length > 0) {
          setSelectedKeyword(data[0]);
          handleGenerateTitles(data[0], subCategory);
        }
      } catch (err) {
        console.error("Failed to fetch keywords:", err);
      } finally {
        setKeywordLoading(false);
      }
    };

    loadKeywords();
  }, [subCategory, handleGenerateTitles]);

  useEffect(() => {
    if (terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  const handleStartPipeline = async (e, publishFlag = false) => {
    if (e) e.preventDefault();
    if (!selectedKeyword || !selectedTitle) return;

    setPipelineRunning(true);
    setError('');
    setResult(null);
    setLogs([]);
    setTerminalStep('역분석');

    const finalLength = articleLength === 'custom' ? customLength : articleLength;

    try {
      const response = await fetch('/api/publish-pipeline', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          keyword: selectedKeyword.keyword,
          platform,
          style,
          search_volume: selectedKeyword.search_volume,
          competition: selectedKeyword.competition,
          cpc: selectedKeyword.cpc,
          category: selectedKeyword.category || currentCategory,
          golden_score: selectedKeyword.golden_score,
          length: finalLength || '5000',
          faq_count: faqCount,
          img_prompt: generateImgPrompt,
          title: customTitle || selectedTitle.title,
          seo_strength: seoStrength,
          publish: publishFlag
        })
      });

      if (!response.body) {
        throw new Error("서버 스트리밍이 차단되었습니다.");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop(); // Keep last incomplete chunk

        lines.forEach(line => {
          if (line.startsWith('data: ')) {
            try {
              const payload = JSON.parse(line.replace('data: ', ''));
              
              if (payload.log) {
                const logText = payload.log;
                setLogs(prev => [...prev, logText]);

                if (logText.includes('[STEP-1]')) setTerminalStep('역분석');
                else if (logText.includes('[STEP-2]')) setTerminalStep('글생성');
                else if (logText.includes('[STEP-3]')) setTerminalStep('이미지생성');
                else if (logText.includes('[STEP-4]')) setTerminalStep('평가');
                else if (logText.includes('[STEP-5]')) setTerminalStep('평가');
                else if (logText.includes('[STEP-6]')) setTerminalStep('발행');
              }
              
              if (payload.success && payload.result) {
                setResult(payload.result);
                setTerminalStep('완료');
                fetchHistory(); // Refresh history
              }
              
              if (payload.error) {
                setError(payload.error);
                setTerminalStep('에러');
              }
            } catch (e) {
              console.error("Streaming JSON parse error:", e);
            }
          }
        });
      }

    } catch (err) {
      setError(err.message);
      setTerminalStep('에러');
    } finally {
      setPipelineRunning(false);
    }
  };

  const handleCopy = (html) => {
    if (!html) return;
    navigator.clipboard.writeText(html);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const activeContent = selectedHistoryItem ? selectedHistoryItem : result;


  const isPostGenerated = !!activeContent;
  const currentCPC = isPostGenerated ? activeContent.cpc_dollar : (selectedKeyword?.cpc_dollar || 1.6);
  const currentVolume = selectedKeyword?.search_volume || 0;
  const currentVisitors = isPostGenerated ? activeContent.estimated_visitors : (selectedKeyword?.estimated_visitors || 0);
  const currentCTR = isPostGenerated ? activeContent.ctr : (selectedKeyword?.ctr || 3.2);
  const currentRevenue = isPostGenerated ? activeContent.estimated_revenue : (selectedKeyword?.estimated_revenue || 0);
  const currentAffiliate = isPostGenerated ? activeContent.affiliate_product : (selectedKeyword?.affiliate_product || "추천 제휴상품 연동 대기");
  const currentBadge = isPostGenerated ? activeContent.ai_badge : (selectedKeyword?.ai_badge || "🔵 작성 추천");
  const currentBlueOcean = isPostGenerated ? activeContent.blue_ocean_score : (selectedKeyword?.blue_ocean_score || 50);
  const currentProfitScore = isPostGenerated ? activeContent.profit_score : (selectedKeyword?.golden_score || 50);

  const filteredTitles = titles.filter(t => {
    if (titleFilter === '전체') return true;
    return t.type === titleFilter;
  });

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 w-full text-slate-100 font-sans items-start">
      
      {/* 10/12 좌측 메인 대시보드 영역 */}
      <div className="lg:col-span-10 flex flex-col gap-6 w-full animate-fadeIn">
        
        {/* 카테고리 선택 헤더 */}
        <header className="relative w-full rounded-3xl p-5 overflow-hidden border border-white/5 bg-slate-950/40 shadow-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="absolute inset-0 pointer-events-none" />
          <div className="flex items-center gap-4 relative">
            <div className="p-3.5 rounded-2xl bg-indigo-600 shadow-lg text-white">
              <Cpu size={26} />
            </div>
            <div>
              <h1 className="text-xl md:text-2xl font-black tracking-tight text-white leading-tight">
                Styler Pro X <span className="text-xs bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 px-2 py-0.5 rounded-full font-bold ml-1.5 align-middle">v3.0 Premium</span>
              </h1>
              <p className="text-xs text-slate-400 mt-1">수익형 블로그 기획 → 키워드 발굴 → 제목 선정 → 자동 발행 Suite</p>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-3.5 w-full md:w-3/5 relative z-20">
            <div className="flex-1 flex flex-col gap-1">
              <span className="text-[12px] font-bold text-slate-500 uppercase tracking-wider pl-1 flex items-center gap-1">
                <Compass size={12}/> 대분류 카테고리
              </span>
              <select
                value={mainCategory}
                onChange={(e) => {
                  if (!pipelineRunning) {
                    handleMainCategoryChange(e.target.value);
                    setSelectedHistoryItem(null);
                  }
                }}
                disabled={pipelineRunning}
                className="w-full px-3.5 py-2.5 rounded-2xl bg-slate-950/90 border border-slate-800 focus:border-indigo-500 focus:outline-none text-slate-200 text-xs font-bold transition-all shadow-inner cursor-pointer"
                style={{ colorScheme: 'dark' }}
              >
                {Object.keys(categories).length > 0 
                  ? Object.keys(categories).sort((a, b) => (CATEGORY_WEIGHTS[b] || 0) - (CATEGORY_WEIGHTS[a] || 0)).map(mainCat => (
                      <option key={mainCat} value={mainCat}>{mainCat}</option>
                    ))
                  : Object.keys(CATEGORY_MAP).sort((a, b) => (CATEGORY_WEIGHTS[b] || 0) - (CATEGORY_WEIGHTS[a] || 0)).map(mainCat => (
                      <option key={mainCat} value={mainCat}>{mainCat}</option>
                    ))
                }
              </select>
            </div>

            <div className="flex-1 flex flex-col gap-1">
              <span className="text-[12px] font-bold text-slate-500 uppercase tracking-wider pl-1 flex items-center gap-1">
                <Layers size={11}/> 소분류 카테고리
              </span>
              <select
                value={subCategory}
                onChange={(e) => {
                  if (!pipelineRunning) {
                    setSubCategory(e.target.value);
                    setSelectedHistoryItem(null);
                  }
                }}
                disabled={pipelineRunning}
                className="w-full px-3.5 py-2.5 rounded-2xl bg-slate-950/90 border border-slate-800 focus:border-indigo-500 focus:outline-none text-slate-200 text-xs font-bold transition-all shadow-inner cursor-pointer"
                style={{ colorScheme: 'dark' }}
              >
                {getSortedSubCategories(categories, mainCategory).map(subCat => (
                  <option key={subCat} value={subCat}>{subCat}</option>
                ))}
              </select>
            </div>
          </div>
        </header>

        {/* 수익성 & 경쟁도 프리미엄 분석 센터 */}
        {(selectedKeyword || isPostGenerated) && (
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
              <div className="col-span-2 md:col-span-1 p-5 rounded-2xl bg-emerald-950/40 border border-emerald-500/30 flex flex-col justify-between gap-2 shadow-lg hover:border-emerald-500/50 transition-all">
                <div className="flex items-center justify-between text-emerald-300">
                  <span className="text-xs font-black uppercase tracking-wider">💰 수익성 평가 등급 (AdSense 가치)</span>
                  <Award size={20} className="text-emerald-400 animate-pulse" />
                </div>
                <div className="flex items-baseline gap-1.5 my-2">
                  <span className="text-2xl font-black text-emerald-400 select-all">
                    {currentRevenue >= 250000 ? "S등급 (최고수익)" : currentRevenue >= 150000 ? "A등급 (우수)" : currentRevenue >= 50000 ? "B등급 (보통)" : "C등급 (일반)"}
                  </span>
                  <span className="text-xs text-emerald-300 font-bold">({currentProfitScore}점 / 100점)</span>
                </div>
                <span className="text-[11px] font-bold text-slate-500 leading-tight">
                  트래픽, CTR, CPC 가중 수익 지수
                </span>
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
                <span className="text-[10px] font-semibold text-slate-500">
                  유입량: {currentVisitors.toLocaleString()}명 예상
                </span>
              </div>

              {/* 예상 클릭율 */}
              <div className="p-4 rounded-2xl bg-slate-900/50 border border-slate-800 flex flex-col justify-between gap-1.5 shadow-sm hover:border-slate-700/80 transition-all">
                <div className="flex items-center justify-between text-slate-400">
                  {renderTooltip('ctr', '예상 클릭율(CTR)', 'CTR (클릭률)', '방문자 중 광고를 클릭하는 비율입니다. 블로그 글의 배치와 가독성에 따라 보통 2% ~ 5% 수준을 유지합니다.', 'text-violet-400')}
                  <MousePointer size={14} className="text-violet-400" />
                </div>
                <div className="flex items-baseline gap-1 my-1">
                  <span className="text-lg font-black text-white">{currentCTR}%</span>
                </div>
                <span className="text-[10px] font-semibold text-slate-500">
                  타겟 사이트 구조화 보정
                </span>
              </div>

              {/* 예상 클릭단가 */}
              <div className="p-4 rounded-2xl bg-slate-900/50 border border-slate-800 flex flex-col justify-between gap-1.5 shadow-sm hover:border-slate-700/80 transition-all">
                <div className="flex items-center justify-between text-slate-400">
                  {renderTooltip('cpc', '예상 클릭단가(CPC)', 'CPC (클릭 단가)', '광고 클릭 1회당 지급받는 예상 수익 달러($) 금액입니다. 금융, 대출, 건강 키워드가 상대적으로 높습니다.', 'text-amber-500')}
                  <DollarSign size={14} className="text-amber-500" />
                </div>
                <div className="flex items-baseline gap-1 my-1">
                  <span className="text-lg font-black text-white">${currentCPC.toFixed(1)}</span>
                  <span className="text-[10px] text-slate-500">USD</span>
                </div>
                <span className="text-[10px] font-semibold text-slate-500">
                  실시간 광고 상위 단가
                </span>
              </div>

              {/* 블루오션 지수 및 진입 장벽 분석 */}
              <div className="col-span-2 p-4 rounded-2xl bg-slate-900/30 border border-slate-900 flex flex-col gap-2.5 justify-between">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-bold text-slate-400 uppercase">블루오션 지수 및 진입 장벽 분석</span>
                  <span className={"text-[12px] font-black px-2.5 py-1 rounded-full " + (
                    currentBlueOcean >= 90 ? 'bg-emerald-950 text-emerald-400 border border-emerald-900/50' :
                    currentBlueOcean >= 70 ? 'bg-indigo-950 text-indigo-400 border border-indigo-900/50' :
                    currentBlueOcean >= 50 ? 'bg-amber-950 text-amber-400 border border-amber-900/50' :
                    'bg-rose-950 text-rose-400 border border-rose-900/50'
                  )}>
                    {currentBlueOcean >= 90 ? '🟢 진입 매우 쉬움' :
                     currentBlueOcean >= 70 ? '🔵 진입 쉬움' :
                     currentBlueOcean >= 50 ? '🟡 보통' :
                     '🔴 경쟁 치열'}
                  </span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden border border-slate-700/50 my-1">
                  <div 
                    className={`h-full rounded-full bg-gradient-to-r transition-all duration-500 ${
                      currentBlueOcean >= 90 ? 'from-emerald-500 to-teal-400' :
                      currentBlueOcean >= 70 ? 'from-indigo-500 to-violet-400' :
                      currentBlueOcean >= 50 ? 'from-amber-500 to-yellow-400' :
                      'from-rose-500 to-pink-400'
                    }`}
                    style={{ width: `${currentBlueOcean}%` }}
                  />
                </div>
                <div className="grid grid-cols-3 text-[11px] text-slate-500 text-center font-bold">
                  <div className="text-left">블루오션 점수: <strong className="text-white">${currentBlueOcean}점</strong></div>
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
                  <span>SEO: <strong className="text-white">{activeContent?.seo_score || "-"}점</strong></span>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* 하단 2단 구조 (황금 키워드 분석 + 제목 100선) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full items-start">
          
          {/* 황금 키워드 분석 리스트 */}
          <div className="flex flex-col gap-6 w-full">
            <section className="glass-card rounded-3xl border border-white/5 shadow-2xl p-5 flex flex-col h-[650px] gap-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 shrink-0">
                <div>
                  <h3 className="text-xs font-bold text-slate-300 flex items-center gap-1.5 uppercase tracking-wider">
                    <Flame size={14} className="text-orange-500 animate-bounce" />
                    {subCategory || '정부지원금'} 황금 키워드 분석
                  </h3>
                  <p className="text-[10px] text-slate-500 mt-0.5">수익률이 극대화되는 황금 키워드 자동 발굴</p>
                </div>
                <div className="relative w-full sm:w-44">
                  <input
                    type="text"
                    placeholder="키워드 검색 (예: 대출)"
                    value={keywordSearch}
                    onChange={(e) => setKeywordSearch(e.target.value)}
                    className="w-full pl-8 pr-3 py-1.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs font-bold focus:border-indigo-500 focus:outline-none placeholder-slate-600 text-slate-300"
                  />
                  <Search size={12} className="absolute left-3 top-2.5 text-slate-600" />
                </div>
              </div>

              <div className="flex gap-1 overflow-x-auto pb-1.5 border-b border-slate-900 shrink-0">
                {[
                  { id: 'recommend', label: '⭐ 추천순' },
                  { id: 'latest', label: '🆕 최신순' },
                  { id: 'volume', label: '📊 검색량순' },
                  { id: 'cpc', label: '💵 CPC순' }
                ].map(tab => (
                  <button
                    key={tab.id}
                    onClick={() => setKeywordSortType(tab.id)}
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
                ) : (
                  <div className="flex flex-col gap-3">
                    {(() => {
                      let sorted = [...keywords];
                      if (keywordSortType === 'volume') {
                        sorted.sort((a, b) => b.search_volume - a.search_volume);
                      } else if (keywordSortType === 'cpc') {
                        sorted.sort((a, b) => b.cpc_dollar - a.cpc_dollar);
                      } else if (keywordSortType === 'latest') {
                        sorted.sort((a, b) => a.keyword.localeCompare(b.keyword));
                      } else {
                        sorted.sort((a, b) => b.golden_score - a.golden_score || b.search_volume - a.search_volume);
                      }
                      return sorted;
                    })()
                      .filter(kw => kw.keyword.toLowerCase().includes(keywordSearch.toLowerCase()))
                      .map((kw, i) => {
                        const isSelected = selectedKeyword?.keyword === kw.keyword;
                        return (
                          <div
                            key={i}
                            onClick={() => {
                              if (!pipelineRunning) {
                                setSelectedKeyword(kw);
                                setSelectedHistoryItem(null);
                                handleGenerateTitles(kw, subCategory);
                              }
                            }}
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
                className="w-full py-2.5 rounded-xl border border-slate-800 bg-slate-900/40 hover:bg-slate-900/80 text-slate-400 hover:text-slate-200 text-xs font-bold transition-all text-center block cursor-pointer"
              >
                👇 전체 100개 키워드 보기
              </button>
            </section>
            
            {/* AI 추천 분석 카드 */}
            {selectedKeyword && (
              <section className="glass-card rounded-3xl border border-emerald-500/20 bg-emerald-950/10 p-4.5 flex flex-col gap-3 animate-fadeIn shadow-lg">
                <div className="flex justify-between items-center border-b border-slate-900 pb-2">
                  <h4 className="text-xs font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-300 flex items-center gap-1.5 uppercase tracking-wider">
                    <Sparkles size={14} className="text-emerald-400 animate-pulse" />
                    AI 키워드 추천 이유 분석
                  </h4>
                  <span className="text-[10px] bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 px-2 py-0.5 rounded-full font-black">
                    {selectedKeyword.ai_badge}
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

          {/* 제목 100선 분석 리스트 */}
          <div className="flex flex-col gap-6 w-full">
            <section className="glass-card rounded-3xl border border-white/5 shadow-2xl p-5 flex flex-col h-[650px] gap-4">
              <div className="flex flex-col gap-2 shrink-0">
                <h3 className="text-xs font-bold text-slate-300 flex items-center gap-1.5 uppercase tracking-wider">
                  <Sparkles size={14} className="text-violet-400 animate-spin" />
                  유입 극대화 제목 100선 (CHATGPT STYLE)
                </h3>
              </div>

              <div className="flex gap-1 overflow-x-auto pb-1.5 border-b border-slate-900 shrink-0">
                {['전체', '정보형', '비교형', '리스트형', '후기형', '충격형', '실수방지형', '전문가형', '최신뉴스형', '질문형', '가이드형'].map(cat => (
                  <button
                    key={cat}
                    onClick={() => setTitleFilter(cat)}
                    className={`px-3 py-1 rounded-xl text-[10px] font-extrabold transition-all shrink-0 cursor-pointer ${titleFilter === cat ? 'bg-indigo-600 text-white shadow-md' : 'bg-slate-900 text-slate-400 hover:text-slate-200'}`}
                  >
                    {cat}
                  </button>
                ))}
              </div>

              <div className="flex-1 overflow-y-auto max-h-[480px] border border-slate-900 rounded-2xl bg-slate-950/60 p-3 scrollbar-thin scrollbar-thumb-slate-800">
                {titlesLoading ? (
                  <div className="text-xs text-slate-500 italic text-center py-4">추천 제목 분석 설계 중...</div>
                ) : (
                  <div className="flex flex-col gap-2.5">
                    {filteredTitles.map((t, idx) => {
                      const isSelected = selectedTitle?.title === t.title;
                      return (
                        <div
                          key={idx}
                          onClick={() => {
                            setSelectedTitle(t);
                            setCustomTitle(t.title);
                          }}
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
                className="w-full py-2.5 rounded-xl border border-slate-800 bg-slate-900/40 hover:bg-slate-900/80 text-slate-400 hover:text-slate-200 text-xs font-bold transition-all text-center block cursor-pointer"
              >
                ▼ 전체 100개 제목 보기
              </button>
            </section>
          </div>
        </div>

        {/* 제어 설정 카드 */}
        <section className="glass-card rounded-3xl border border-white/5 p-6 shadow-2xl flex flex-col gap-4">
          <div className="flex items-center gap-2 border-b border-slate-900 pb-3">
            <div className="p-2 rounded-xl bg-gradient-to-tr from-violet-600 to-indigo-600 text-white shadow-md">
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
              <select
                value={style}
                onChange={(e) => setStyle(e.target.value)}
                disabled={pipelineRunning}
                className="w-full px-3 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-xs font-bold cursor-pointer"
                style={{ colorScheme: 'dark' }}
              >
                <option value="friendly">😊 친근 대화체</option>
                <option value="professional">🎓 전문 격조체</option>
                <option value="informative">📋 정보 요약체</option>
              </select>
            </div>

            {/* 자동 발행 플랫폼 */}
            <div className="flex flex-col gap-1.5">
              <label className="text-[12px] font-bold text-slate-400 uppercase tracking-wider">자동 발행 플랫폼</label>
              <select
                value={platform}
                onChange={(e) => setPlatform(e.target.value)}
                disabled={pipelineRunning}
                className="w-full px-3 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-xs font-bold cursor-pointer"
                style={{ colorScheme: 'dark' }}
              >
                <option value="tistory">티스토리</option>
                <option value="blogspot">블로그스팟</option>
                <option value="wordpress">워드프레스</option>
              </select>
            </div>

            {/* CTA 디자인 */}
            <div className="flex flex-col gap-1.5">
              <label className="text-[12px] font-bold text-slate-400 uppercase tracking-wider">CTA 디자인</label>
              <select
                value={ctaStyle}
                onChange={(e) => setCtaStyle(e.target.value)}
                disabled={pipelineRunning}
                className="w-full px-3 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-xs font-bold cursor-pointer"
                style={{ colorScheme: 'dark' }}
              >
                <option value="card">🎴 카드형</option>
                <option value="banner">🖼️ 배너형</option>
                <option value="inline">🔗 인라인형</option>
                <option value="button">🔘 버튼형</option>
              </select>
            </div>

            {/* SEO 진단 강도 */}
            <div className="flex flex-col gap-1.5">
              <label className="text-[12px] font-bold text-slate-400 uppercase tracking-wider">SEO 진단 강도</label>
              <select
                value={seoStrength}
                onChange={(e) => setSeoStrength(e.target.value)}
                disabled={pipelineRunning}
                className="w-full px-3 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-xs font-bold cursor-pointer"
                style={{ colorScheme: 'dark' }}
              >
                <option value="normal">약함 (1회/65점)</option>
                <option value="strong">보통 (2회/75점)</option>
                <option value="extreme">강함 (3회/85점)</option>
              </select>
            </div>

            {/* 글 길이 */}
            <div className="flex flex-col gap-1.5">
              <label className="text-[12px] font-bold text-slate-400 uppercase tracking-wider">글 길이</label>
              <select
                value={articleLength}
                onChange={(e) => setArticleLength(e.target.value)}
                disabled={pipelineRunning}
                className="w-full px-3 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-xs font-bold cursor-pointer"
                style={{ colorScheme: 'dark' }}
              >
                <option value="3000">3000자</option>
                <option value="5000">5000자</option>
                <option value="10000">10000자</option>
              </select>
            </div>

            {/* FAQ 생성 */}
            <div className="flex flex-col gap-1.5">
              <label className="text-[12px] font-bold text-slate-400 uppercase tracking-wider">FAQ 생성</label>
              <select
                value={faqCount}
                onChange={(e) => setFaqCount(e.target.value)}
                disabled={pipelineRunning}
                className="w-full px-3 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-xs font-bold cursor-pointer"
                style={{ colorScheme: 'dark' }}
              >
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
                onClick={() => setGenerateImgPrompt(generateImgPrompt === 'ON' ? 'OFF' : 'ON')}
                disabled={pipelineRunning}
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
        </section>

        {/* 아웃라인 미리보기 + 터미널 로그 2단 구조 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full items-start">
          
          {/* 블로그 구조 기획 아웃라인 미리보기 */}
          <div className="flex flex-col gap-6 w-full">
            <section className="glass-card rounded-3xl border border-white/5 p-5 shadow-2xl flex flex-col h-[520px]">
              <div className="flex justify-between items-center mb-3.5 shrink-0 border-b border-slate-900 pb-3">
                <div>
                  <span className="text-[12px] text-indigo-400 font-bold uppercase tracking-wider">
                    {selectedHistoryItem ? '과거 백업 히스토리 조회' : isPostGenerated ? '생성 완료 포스팅 프리뷰' : '블로그 구조 기획 아웃라인 미리보기'}
                  </span>
                  <h3 className="text-xs font-bold text-slate-300">
                    {activeContent ? activeContent.title : selectedTitle ? selectedTitle.title : '기획 및 실시간 미리보기'}
                  </h3>
                </div>
                
                <div className="flex gap-2">
                  {activeContent && (
                    <button
                      onClick={() => handleCopy(activeContent.html_content)}
                      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all shadow-md ${copied ? 'bg-emerald-600 text-white' : 'bg-slate-800 hover:bg-slate-700 text-slate-200'}`}
                    >
                      {copied ? <Check size={12} /> : <Copy size={12} />}
                      코드 복사
                    </button>
                  )}
                </div>
              </div>

              <div className="flex-1 bg-slate-950 border border-slate-900 rounded-2xl p-5 overflow-y-auto text-slate-300 text-xs leading-relaxed scrollbar-thin scrollbar-thumb-slate-800">
                {activeContent ? (
                  <div 
                    className="prose prose-invert prose-xs max-w-none text-slate-300 animate-fadeIn"
                    dangerouslySetInnerHTML={{ __html: activeContent.html_content }}
                  />
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

              {selectedTitle && !activeContent && (
                <div className="grid grid-cols-2 gap-4 mt-4 shrink-0 pt-3 border-t border-slate-900">
                  <button
                    onClick={(e) => handleStartPipeline(e, false)}
                    disabled={pipelineRunning}
                    className="py-4 rounded-2xl bg-indigo-600 hover:bg-indigo-500 text-white font-extrabold text-xs sm:text-sm shadow-xl shadow-indigo-500/10 transition-all text-center flex items-center justify-center gap-2 cursor-pointer animate-pulse"
                  >
                    <FileText size={16}/>
                    [글 생성] (임시 저장)
                  </button>
                  <button
                    onClick={(e) => handleStartPipeline(e, true)}
                    disabled={pipelineRunning}
                    className="py-4 rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-extrabold text-xs sm:text-sm shadow-xl shadow-emerald-500/10 transition-all text-center flex items-center justify-center gap-2 cursor-pointer"
                  >
                    <PenTool size={16}/>
                    [자동 발행] (플랫폼 전송)
                  </button>
                </div>
              )}
            </section>
            
            {/* 이미지 프롬프트 카드 */}
            {activeContent && activeContent.image_prompts && (
              <section className="glass-card rounded-3xl border border-white/5 p-5 shadow-2xl flex flex-col gap-3.5 animate-fadeIn">
                <div>
                  <h4 className="text-[13px] font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                    <PenTool size={13} className="text-violet-400" />
                    대표 이미지 및 썸네일 생성 AI 프롬프트
                  </h4>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div className="p-3.5 rounded-2xl bg-slate-900/40 border border-slate-850 flex flex-col gap-2 justify-between">
                    <span className="font-bold text-indigo-400 text-xs">Midjourney 프롬프트</span>
                    <p className="text-[11px] text-slate-300 font-mono line-clamp-3 bg-black/30 p-2 rounded-lg border border-slate-900/50">
                      {activeContent.image_prompts.midjourney}
                    </p>
                  </div>
                  <div className="p-3.5 rounded-2xl bg-slate-900/40 border border-slate-850 flex flex-col gap-2 justify-between">
                    <span className="font-bold text-teal-400 text-xs">ChatGPT (DALL-E) 프롬프트</span>
                    <p className="text-[11px] text-slate-300 font-mono line-clamp-3 bg-black/30 p-2 rounded-lg border border-slate-900/50">
                      {activeContent.image_prompts.chatgpt}
                    </p>
                  </div>
                  <div className="p-3.5 rounded-2xl bg-slate-900/40 border border-slate-850 flex flex-col gap-2 justify-between">
                    <span className="font-bold text-violet-400 text-xs">Flux 프롬프트</span>
                    <p className="text-[11px] text-slate-300 font-mono line-clamp-3 bg-black/30 p-2 rounded-lg border border-slate-900/50">
                      {activeContent.image_prompts.flux}
                    </p>
                  </div>
                </div>
              </section>
            )}
          </div>

          {/* 자동화 파이프라인 실시간 터미널 로그 */}
          <div className="flex flex-col gap-6 w-full">
            <section className="glass-card rounded-3xl border border-white/5 p-5 shadow-2xl flex flex-col h-[520px]">
              <div className="flex items-center justify-between mb-3.5 shrink-0 border-b border-slate-900 pb-3">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping" />
                  <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                    자동화 파이프라인 실시간 터미널 로그
                  </h3>
                </div>
                <div className="flex gap-1.5">
                  {['역분석', '글생성', '이미지생성', '평가', '발행', '완료'].map(step => (
                    <span
                      key={step}
                      className={`text-[11px] px-1.5 py-0.5 rounded-md font-bold uppercase transition-all ${terminalStep === step ? 'bg-indigo-600 text-white font-extrabold scale-110 shadow-md' : 'bg-slate-900 text-slate-600'}`}
                    >
                      {step}
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex-1 bg-black/80 border border-slate-900 rounded-2xl p-4 overflow-y-auto font-mono text-[12px] text-emerald-400 flex flex-col gap-1.5 select-all scrollbar-thin scrollbar-thumb-slate-800">
                {logs.length === 0 ? (
                  <div className="text-slate-600 italic">대기 중: 하단 [글 생성] 버튼을 누르면 실시간 로그가 출력됩니다.</div>
                ) : (
                  logs.map((log, i) => (
                    <div key={i} className="leading-relaxed whitespace-pre-wrap">
                      <span className="text-slate-600 select-none">&gt;</span> {log}
                    </div>
                  ))
                )}
                <div ref={terminalEndRef} />
              </div>
            </section>
          </div>
        </div>

      </div>

      {/* 2/12 우측 히스토리 사이드바 영역 */}
      <div className="lg:col-span-2 w-full h-full min-h-[90vh] bg-slate-950/40 border border-white/5 rounded-3xl p-4 flex flex-col gap-4 shadow-2xl">
        <h3 className="text-xs font-black text-slate-300 flex items-center gap-1.5 uppercase tracking-wider border-b border-slate-900 pb-3">
          <Layers size={14} className="text-indigo-400" />
          로컬 DB 백업 발행 이력
        </h3>
        <div className="flex-1 overflow-y-auto max-h-[1600px] flex flex-col gap-3.5 scrollbar-thin scrollbar-thumb-slate-800">
          {history.length === 0 ? (
            <div className="text-xs text-slate-600 italic text-center py-8">발행 이력이 없습니다.</div>
          ) : (
            history.map((rawItem, i) => {
              const item = normalizeHistoryItem(rawItem);
              return (
              <div 
                key={i}
                onClick={() => {
                  if (!pipelineRunning) {
                    setSelectedHistoryItem(item);
                  }
                }}
                className={`p-3 rounded-2xl border text-xs flex flex-col gap-1.5 transition-all cursor-pointer ${selectedHistoryItem?.id === item.id ? 'bg-indigo-950/30 border-indigo-500/40 text-white' : 'bg-slate-900/40 border-slate-850 hover:bg-slate-900/70 text-slate-400 hover:text-slate-200'}`}
              >
                <div className="flex justify-between items-center text-[10px]">
                  <span className="bg-slate-950 border border-slate-800 px-2 py-0.5 rounded-full font-black text-slate-500">{formatHistoryPlatform(item.platform)}</span>
                  <span className="font-bold text-slate-500">{formatHistoryDate(item.created_at)}</span>
                </div>
                <div className="font-black text-slate-100 leading-normal truncate" title={item.title}>
                  {item.title}
                </div>
                <div className="flex justify-between items-center text-[9px] text-slate-500">
                  <span>SEO: {item.seo_score}점</span>
                  <span>수익: {item.profit_score}점</span>
                </div>
              </div>
            );
            })
          )}
        </div>
      </div>
      
    </div>
  );

}

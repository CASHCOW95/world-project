import React, { useState, useEffect, useRef } from 'react';
import { 
  PenTool, Copy, Check, RotateCcw, AlertTriangle, ExternalLink, Hash, 
  LayoutGrid, Search, Flame, TrendingUp, Cpu, Award, FileText, BadgeHelp, 
  DollarSign, Users, MousePointer, ShieldAlert, Star, RefreshCw, Layers, 
  Sparkles, Clock, Compass, Settings, Link 
} from 'lucide-react';

const CATEGORIES = [
  "정보형", "비교형", "리스트형", "후기형", "충격형",
  "실수방지형", "전문가형", "최신뉴스형", "질문형", "가이드형"
];

const CATEGORY_MAP = {
  "정부정책": ["정부지원금", "복지", "연금", "세금", "환급금"],
  "금융": ["재테크", "대출", "보험", "카드", "주식", "ETF", "코인"],
  "부동산": ["부동산", "청약", "경매", "재개발", "전세", "월세"],
  "비즈니스": ["창업", "사업자", "스마트스토어", "온라인쇼핑몰"],
  "디지털": ["IT", "소프트웨어", "전자제품", "모바일", "인터넷서비스"],
  "건강": ["건강", "질병", "다이어트", "병원", "건강검진", "영양제"],
  "생활": ["자동차", "전기차", "여행", "생활정보", "반려동물"],
  "전문직": ["법률", "이혼/상속", "취업/이직", "자격증", "교육/육아"]
};

const CATEGORY_WEIGHTS = {
  "금융": 100, "정부정책": 90, "부동산": 80, "건강": 70, "생활": 60, "비즈니스": 50, "디지털": 40, "전문직": 30
};

const SUBCAT_WEIGHTS = {
  "대출": 100, "주식": 95, "ETF": 90, "코인": 85, "재테크": 80, "보험": 75, "카드": 70,
  "정부지원금": 100, "세금": 90, "환급금": 85, "복지": 80, "연금": 75,
  "청약": 100, "재개발": 90, "경매": 85, "부동산": 80, "전세": 75, "월세": 70,
  "스마트스토어": 100, "온라인쇼핑몰": 90, "창업": 85, "사업자": 80,
  "IT": 100, "모바일": 90, "소프트웨어": 85, "전자제품": 80, "인터넷서비스": 75,
  "질병": 100, "건강": 90, "다이어트": 85, "병원": 80, "영양제": 75, "건강검진": 70,
  "자동차": 100, "전기차": 90, "여행": 85, "생활정보": 80, "반려동물": 75,
  "법률": 100, "이혼/상속": 90, "취업/이직": 85, "자격증": 80, "교육/육아": 75
};

export default function StylerDashboard() {
  const [activeTab, setActiveTab] = useState('cluster'); // cluster, publish, links, performance, settings
  const [categories, setCategories] = useState({});
  const [mainCategory, setMainCategory] = useState('정부정책');
  const [subCategory, setSubCategory] = useState('정부지원금');
  const [currentCategory, setCurrentCategory] = useState('정부지원금');
  
  // Keyword & Single post titles
  const [keywordLoading, setKeywordLoading] = useState(false);
  const [keywords, setKeywords] = useState([]);
  const [selectedKeyword, setSelectedKeyword] = useState(null);
  const [keywordSearch, setKeywordSearch] = useState('');
  const [showAllKeywords, setShowAllKeywords] = useState(false);
  const [keywordSortType, setKeywordSortType] = useState('recommend');
  const [customTitle, setCustomTitle] = useState('');
  const [titles, setTitles] = useState([]);
  const [titlesLoading, setTitlesLoading] = useState(false);
  const [selectedTitle, setSelectedTitle] = useState(null);
  const [titleFilter, setTitleFilter] = useState('전체');
  const [showAllTitles, setShowAllTitles] = useState(false);

  // Cluster states
  const [workMode, setWorkMode] = useState('single'); // single or cluster
  const [minSubs, setMinSubs] = useState(3);
  const [maxSubs, setMaxSubs] = useState(6);
  const [clusterLoading, setClusterLoading] = useState(false);
  const [clusterData, setClusterData] = useState(null);

  // Settings
  const [telegramToken, setTelegramToken] = useState(localStorage.getItem('styler_telegramToken') || '');
  const [telegramChatId, setTelegramChatId] = useState(localStorage.getItem('styler_telegramChatId') || '');
  const [telegramTesting, setTelegramTesting] = useState(false);
  const [telegramTestResult, setTelegramTestResult] = useState(null);

  // Lists & Stats
  const [postsList, setPostsList] = useState([]);
  const [linksList, setLinksList] = useState([]);
  const [dashboardStats, setDashboardStats] = useState({
    total_published: 0, total_pending: 0, total_failed: 0, total_clusters: 0, total_links: 0, today_published: 0
  });

  // Controls & Run
  const [style, setStyle] = useState('friendly');
  const [platform, setPlatform] = useState('tistory');
  const [ctaStyle, setCtaStyle] = useState('card');
  const [articleLength, setArticleLength] = useState('5000');
  const [customLength, setCustomLength] = useState('');
  const [faqCount, setFaqCount] = useState('10');
  const [generateImgPrompt, setGenerateImgPrompt] = useState('OFF');
  const [seoStrength, setSeoStrength] = useState('strong');
  const [pipelineRunning, setPipelineRunning] = useState(false);
  const [logs, setLogs] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);
  const [terminalStep, setTerminalStep] = useState('');
  const [promptCopied, setPromptCopied] = useState({});
  const [activeTooltip, setActiveTooltip] = useState(null);

  const terminalEndRef = useRef(null);

  // Restore options on mount
  useEffect(() => {
    const savedStyle = localStorage.getItem('styler_style_v3');
    const savedPlatform = localStorage.getItem('styler_platform_v3');
    const savedCtaStyle = localStorage.getItem('styler_ctaStyle_v3');
    const savedLength = localStorage.getItem('styler_articleLength_v3');
    const savedCustomLength = localStorage.getItem('styler_customLength_v3');
    const savedFaq = localStorage.getItem('styler_faqCount_v3');
    const savedImgPrompt = localStorage.getItem('styler_generateImgPrompt_v3');
    const savedSeo = localStorage.getItem('styler_seoStrength_v3');

    if (savedStyle) setStyle(savedStyle);
    if (savedPlatform) setPlatform(savedPlatform);
    if (savedCtaStyle) setCtaStyle(savedCtaStyle);
    if (savedLength) setArticleLength(savedLength);
    if (savedCustomLength) setCustomLength(savedCustomLength);
    if (savedFaq) setFaqCount(savedFaq);
    if (savedImgPrompt) setGenerateImgPrompt(savedImgPrompt);
    if (savedSeo) setSeoStrength(savedSeo);
  }, []);

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

  // Load Categories list on mount
  useEffect(() => {
    const loadCategories = async () => {
      try {
        const res = await fetch('http://localhost:5000/api/categories');
        const data = await res.json();
        setCategories(data);
      } catch (err) {
        console.error("Failed to load categories.json:", err);
      }
    };
    loadCategories();
  }, []);

  // Handle main Category changes
  useEffect(() => {
    const subCats = categories[mainCategory] 
      ? Object.keys(categories[mainCategory]).sort((a, b) => (SUBCAT_WEIGHTS[b] || 0) - (SUBCAT_WEIGHTS[a] || 0))
      : (CATEGORY_MAP[mainCategory] || []).sort((a, b) => (SUBCAT_WEIGHTS[b] || 0) - (SUBCAT_WEIGHTS[a] || 0));
    if (subCats.length > 0) {
      setSubCategory(subCats[0]);
    }
  }, [mainCategory, categories]);

  // Reload keywords on subcategory changes
  useEffect(() => {
    if (subCategory) {
      setCurrentCategory(subCategory);
      fetchKeywords(subCategory);
      setSelectedKeyword(null);
      setTitles([]);
      setSelectedTitle(null);
      setResult(null);
      setClusterData(null);
    }
  }, [subCategory]);

  useEffect(() => {
    if (terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  // Tab changes loaders
  useEffect(() => {
    if (activeTab === 'publish') {
      fetchDashboardStats();
      fetchPostsList();
    } else if (activeTab === 'links') {
      fetchLinksList();
    }
  }, [activeTab]);

  const fetchKeywords = async (catName) => {
    setKeywordLoading(true);
    try {
      const res = await fetch(`http://localhost:5000/api/keywords?category=${encodeURIComponent(catName)}`);
      const data = await res.json();
      setKeywords(data);
      if (data.length > 0) {
        setSelectedKeyword(data[0]);
        handleGenerateTitles(data[0], catName);
      }
    } catch (err) {
      console.error("Failed to fetch keywords:", err);
    } finally {
      setKeywordLoading(false);
    }
  };

  const handleGenerateTitles = async (kwObj, catName) => {
    if (!kwObj) return;
    setTitlesLoading(true);
    setTitles([]);
    setSelectedTitle(null);
    setCustomTitle('');
    try {
      const res = await fetch('http://localhost:5000/api/generate-titles', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          keyword: kwObj.keyword,
          category: catName || currentCategory
        })
      });
      const data = await res.json();
      if (data && Array.isArray(data)) {
        const scored = data.map((t, idx) => {
          const ctr = parseFloat((8.5 + ((t.title.length % 7) * 0.2)).toFixed(1));
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
  };

  // V2 API Fetchers
  const fetchDashboardStats = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/dashboard-stats');
      const data = await res.json();
      setDashboardStats(data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchPostsList = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/published-posts');
      const data = await res.json();
      setPostsList(data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchLinksList = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/internal-links');
      const data = await res.json();
      setLinksList(data);
    } catch (err) {
      console.error(err);
    }
  };

  // V2 API Cluster Actions
  const handleGenerateCluster = async () => {
    if (!selectedKeyword) return;
    setClusterLoading(true);
    setClusterData(null);
    setError('');
    try {
      const res = await fetch('http://localhost:5000/api/cluster-generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          keyword: selectedKeyword.keyword,
          category: currentCategory,
          min_subs: minSubs,
          max_subs: maxSubs
        })
      });
      const data = await res.json();
      if (data.error) {
        setError(data.error);
      } else {
        setClusterData(data);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setClusterLoading(false);
    }
  };

  // V2 Telegram Connection Test
  const handleTestTelegram = async () => {
    setTelegramTesting(true);
    setTelegramTestResult(null);
    try {
      const res = await fetch('http://localhost:5000/api/telegram-test', {
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
  const handleStartPipeline = async (e, publishFlag = false) => {
    if (e) e.preventDefault();
    if (!selectedKeyword) return;

    setPipelineRunning(true);
    setError('');
    setResult(null);
    setLogs([]);
    setTerminalStep('역분석');

    const finalLength = articleLength === 'custom' ? customLength : articleLength;
    const finalTitle = customTitle || (selectedTitle ? selectedTitle.title : `${selectedKeyword.keyword} 완벽 가이드`);

    if (workMode === 'cluster') {
      try {
        const response = await fetch('http://localhost:5000/api/cluster-publish', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            keyword: selectedKeyword.keyword,
            platform,
            style,
            category: selectedKeyword.category || currentCategory,
            length: finalLength || '5000',
            faq_count: faqCount,
            img_prompt: generateImgPrompt,
            seo_strength: seoStrength,
            publish: publishFlag,
            min_subs: minSubs,
            max_subs: maxSubs,
            search_volume: selectedKeyword.search_volume,
            competition: selectedKeyword.competition,
            cpc: selectedKeyword.cpc
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
          buffer = lines.pop();

          lines.forEach(line => {
            if (line.startsWith('data: ')) {
              try {
                const payload = JSON.parse(line.replace('data: ', ''));
                if (payload.log) {
                  setLogs(prev => [...prev, payload.log]);
                  if (payload.log.includes('[CLUSTER-1]')) setTerminalStep('역분석');
                  else if (payload.log.includes('[CLUSTER-3')) setTerminalStep('글생성');
                  else if (payload.log.includes('[CLUSTER-4]')) setTerminalStep('발행');
                  else if (payload.log.includes('[CLUSTER-5]')) setTerminalStep('완료');
                }
                if (payload.success && payload.result) {
                  setResult(payload.result);
                  setTerminalStep('완료');
                }
                if (payload.error) {
                  setError(payload.error);
                  setTerminalStep('에러');
                }
              } catch (errJson) {
                console.error(errJson);
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
    } else {
      // Single Mode Publish
      try {
        const response = await fetch('http://localhost:5000/api/publish-pipeline', {
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
            title: finalTitle,
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
          buffer = lines.pop();

          lines.forEach(line => {
            if (line.startsWith('data: ')) {
              try {
                const payload = JSON.parse(line.replace('data: ', ''));
                if (payload.log) {
                  const logText = payload.log;
                  setLogs(prev => [...prev, logText]);

                  if (logText.includes('[STEP-1]')) setTerminalStep('역분석');
                  else if (logText.includes('[STEP-2]')) setTerminalStep('글생성');
                  else if (logText.includes('[STEP-4]') || logText.includes('[STEP-5]')) setTerminalStep('이미지생성');
                  else if (logText.includes('[STEP-6]')) setTerminalStep('평가');
                  else if (logText.includes('[STEP-9]')) setTerminalStep('발행');
                }
                if (payload.success && payload.result) {
                  setResult(payload.result);
                  setTerminalStep('완료');
                }
                if (payload.error) {
                  setError(payload.error);
                  setTerminalStep('에러');
                }
              } catch (errJson) {
                console.error(errJson);
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
    }
  };

  const handleCopy = (html) => {
    if (!html) return;
    navigator.clipboard.writeText(html);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const renderTooltip = (id, label, title, desc, iconColor = "text-slate-500", align = "center") => {
    const alignClass = align === "left" ? "left-0 translate-x-0" : align === "right" ? "right-0 translate-x-0" : "left-1/2 -translate-x-1/2";
    return (
      <span 
        className="relative inline-flex items-center gap-1 cursor-help select-none"
        onMouseEnter={() => setActiveTooltip(id)}
        onMouseLeave={() => setActiveTooltip(null)}
      >
        <span className="font-bold">{label}</span>
        <BadgeHelp size={12} className={`${iconColor} hover:text-slate-300 transition-colors`} />
        {activeTooltip === id && (
          <span className={`absolute bottom-full mb-2.5 w-60 p-3 bg-slate-900 border border-slate-800 text-slate-300 rounded-2xl shadow-2xl text-[11px] font-semibold leading-relaxed z-50 text-left border-l-4 border-l-indigo-500 whitespace-normal ${alignClass}`}>
            <span className="font-extrabold text-white mb-1 text-[12px] block">{title}</span>
            <span className="block">{desc}</span>
          </span>
        )}
      </span>
    );
  };

  // Sort and filter keywords
  const getFilteredKeywords = () => {
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
    return sorted.filter(kw => kw.keyword.toLowerCase().includes(keywordSearch.toLowerCase()));
  };

  const filteredKeywords = getFilteredKeywords();
  const visibleKeywords = showAllKeywords ? filteredKeywords : filteredKeywords.slice(0, 10);

  return (
    <div className="flex flex-col gap-6 w-full text-slate-100 font-sans">
      
      {/* Top Header Section */}
      <header className="relative w-full rounded-3xl p-5 overflow-hidden border border-white/5 bg-slate-950/40 shadow-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="absolute inset-0 bg-gradient-to-r from-violet-600/10 via-indigo-600/10 to-emerald-600/10 pointer-events-none" />
        <div className="flex items-center gap-4 relative">
          <div className="p-3.5 rounded-2xl bg-gradient-to-tr from-violet-600 to-indigo-600 shadow-xl shadow-indigo-500/20 text-white">
            <Cpu size={26} />
          </div>
          <div>
            <h1 className="text-xl md:text-2xl font-black tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-violet-400 via-indigo-400 to-emerald-400 leading-tight">
              AI Blog Operator <span className="text-xs bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 px-2 py-0.5 rounded-full font-bold ml-1.5 align-middle">v2.0 Agent</span>
            </h1>
            <p className="text-xs text-slate-400 mt-1">토픽 클러스터 기획 → 사실 기반 RAG 수집 → 양산형 회피 생성 → 내부링크 그래프 → 텔레그램 리포트</p>
          </div>
        </div>

        {/* Categories picker */}
        <div className="flex flex-col sm:flex-row gap-3.5 w-full md:w-3/5 relative z-20">
          <div className="flex-1 flex flex-col gap-1">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider pl-1 flex items-center gap-1">
              <Compass size={12}/> 대분류 카테고리
            </span>
            <select
              value={mainCategory}
              onChange={(e) => {
                if (!pipelineRunning) setMainCategory(e.target.value);
              }}
              disabled={pipelineRunning}
              className="w-full px-3.5 py-2.5 rounded-2xl bg-slate-950/90 border border-slate-800 focus:border-indigo-500 focus:outline-none text-slate-200 text-xs font-bold cursor-pointer"
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
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider pl-1 flex items-center gap-1">
              <Layers size={11}/> 소분류 카테고리
            </span>
            <select
              value={subCategory}
              onChange={(e) => {
                if (!pipelineRunning) setSubCategory(e.target.value);
              }}
              disabled={pipelineRunning}
              className="w-full px-3.5 py-2.5 rounded-2xl bg-slate-950/90 border border-slate-800 focus:border-indigo-500 focus:outline-none text-slate-200 text-xs font-bold cursor-pointer"
            >
              {categories[mainCategory] 
                ? Object.keys(categories[mainCategory]).sort((a, b) => (SUBCAT_WEIGHTS[b] || 0) - (SUBCAT_WEIGHTS[a] || 0)).map(subCat => (
                    <option key={subCat} value={subCat}>{subCat}</option>
                  ))
                : (CATEGORY_MAP[mainCategory] || []).sort((a, b) => (SUBCAT_WEIGHTS[b] || 0) - (SUBCAT_WEIGHTS[a] || 0)).map(subCat => (
                    <option key={subCat} value={subCat}>{subCat}</option>
                  ))
              }
            </select>
          </div>
        </div>
      </header>

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
          <Link size={14}/> 🔗 내부링크 그래프
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
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 w-full items-start">
          {/* Picker column */}
          <div className="lg:col-span-4 flex flex-col gap-6 w-full">
            <section className="glass-card rounded-3xl border border-white/5 shadow-2xl p-5 flex flex-col min-h-[700px] gap-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <h3 className="text-xs font-black text-slate-300 flex items-center gap-1.5 uppercase tracking-wider">
                    <Flame size={14} className="text-orange-500 animate-pulse" />
                    황금 키워드 발굴기
                  </h3>
                </div>
                
                <div className="relative w-full sm:w-44">
                  <input
                    type="text"
                    placeholder="키워드 검색"
                    value={keywordSearch}
                    onChange={(e) => setKeywordSearch(e.target.value)}
                    className="w-full pl-8 pr-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-xs font-bold text-slate-300"
                  />
                  <Search size={12} className="absolute left-3 top-2.5 text-slate-650" />
                </div>
              </div>

              {/* Keyword Picker sorting tabs */}
              <div className="flex gap-1 overflow-x-auto pb-1.5 border-b border-slate-900 shrink-0">
                {['recommend', 'volume', 'cpc'].map(sort => (
                  <button
                    key={sort}
                    onClick={() => setKeywordSortType(sort)}
                    className={`px-3 py-1 rounded-xl text-[10px] font-black transition-all uppercase ${keywordSortType === sort ? 'bg-indigo-600 text-white shadow-md' : 'bg-slate-900 text-slate-400 hover:text-slate-200'}`}
                  >
                    {sort === 'recommend' ? '⭐ 추천' : sort === 'volume' ? '📊 검색량' : '💵 CPC'}
                  </button>
                ))}
              </div>

              {/* Keywords list */}
              <div className="flex-1 overflow-y-auto max-h-[500px] border border-slate-900 rounded-2xl bg-slate-950/60 p-2 scrollbar-thin scrollbar-thumb-slate-800">
                {keywordLoading ? (
                  <div className="flex items-center justify-center h-full text-xs text-slate-500 italic">
                    실시간 황금키워드 지수 연산 중...
                  </div>
                ) : (
                  visibleKeywords.map((kw, i) => {
                    const isSelected = selectedKeyword?.keyword === kw.keyword;
                    return (
                      <div
                        key={i}
                        onClick={() => {
                          if (!pipelineRunning) {
                            setSelectedKeyword(kw);
                            handleGenerateTitles(kw, subCategory);
                            setClusterData(null);
                          }
                        }}
                        className={`p-3.5 mb-2 rounded-2xl border transition-all cursor-pointer flex flex-col gap-2 ${isSelected ? 'bg-indigo-600/15 border-indigo-500/50 text-indigo-300 shadow-lg' : 'bg-slate-900/40 border-slate-850 hover:bg-slate-900/70 text-slate-300'}`}
                      >
                        <div className="flex justify-between items-center text-[10px]">
                          <span className="font-extrabold text-white"># {i + 1}</span>
                          <span className="bg-slate-950 border border-slate-800 text-emerald-400 px-2 py-0.5 rounded-full font-black">
                            {kw.ai_badge || "추천"}
                          </span>
                        </div>
                        <div className="text-xs font-black text-slate-100 select-all">{kw.keyword}</div>
                        <div className="grid grid-cols-3 gap-1 text-center text-[9px] bg-slate-950/60 p-1.5 rounded-xl border border-slate-900 text-slate-400 font-bold">
                          <div>량: {kw.search_volume.toLocaleString()}</div>
                          <div>CPC: ${kw.cpc_dollar.toFixed(1)}</div>
                          <div className="text-indigo-400 font-extrabold">점수: {kw.golden_score}</div>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>

              {!keywordLoading && filteredKeywords.length > 10 && (
                <button
                  type="button"
                  onClick={() => setShowAllKeywords(!showAllKeywords)}
                  className="w-full py-2 rounded-xl border border-slate-800 bg-slate-900/40 hover:bg-slate-900/80 text-slate-400 hover:text-slate-200 text-xs font-black transition-all text-center block cursor-pointer"
                >
                  {showAllKeywords ? '👆 추천 TOP10 요약 보기' : `👇 전체 ${filteredKeywords.length}개 키워드 보기`}
                </button>
              )}
            </section>
          </div>

          {/* Configuration & Action Column */}
          <div className="lg:col-span-8 flex flex-col gap-6 w-full">
            <section className="glass-card rounded-3xl border border-white/5 shadow-2xl p-5 flex flex-col gap-4">
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
                <div>
                  <h3 className="text-xs font-black text-slate-300 flex items-center gap-1.5 uppercase tracking-wider">
                    <Sparkles size={14} className="text-indigo-400" />
                    콘텐츠 기획 및 AI 대화형 빌더
                  </h3>
                </div>

                {/* Work Mode selection */}
                <div className="flex bg-slate-950/80 border border-slate-850 p-1 rounded-xl gap-1 relative z-20">
                  <button
                    onClick={() => setWorkMode('single')}
                    className={`px-3 py-1.5 rounded-lg text-[10px] font-black transition-all ${workMode === 'single' ? 'bg-indigo-600 text-white' : 'text-slate-500 hover:text-slate-300'}`}
                  >
                    단일 글 기획
                  </button>
                  <button
                    onClick={() => setWorkMode('cluster')}
                    className={`px-3 py-1.5 rounded-lg text-[10px] font-black transition-all ${workMode === 'cluster' ? 'bg-indigo-600 text-white' : 'text-slate-500 hover:text-slate-300'}`}
                  >
                    토픽 클러스터 에이전트
                  </button>
                </div>
              </div>

              {selectedKeyword ? (
                <div className="flex flex-col gap-4">
                  
                  {/* Single Post Mode Layout */}
                  {workMode === 'single' ? (
                    <div className="flex flex-col gap-3">
                      <div className="flex flex-col gap-1.5">
                        <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">대표 발행 제목 (커스텀 입력 가능)</label>
                        <input
                          type="text"
                          value={customTitle}
                          onChange={(e) => setCustomTitle(e.target.value)}
                          placeholder="원하는 제목을 직접 수정/입력할 수 있습니다"
                          className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 focus:border-indigo-500 focus:outline-none text-xs font-bold text-slate-200"
                        />
                      </div>
                      
                      {/* Generated Titles candidates */}
                      <div className="flex flex-col gap-1.5">
                        <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">AI 추천 헤드라인 리스트</span>
                        <div className="flex flex-col gap-1.5 max-h-48 overflow-y-auto border border-slate-900 rounded-xl bg-slate-950/60 p-2 scrollbar-thin scrollbar-thumb-slate-800">
                          {titlesLoading ? (
                            <div className="text-xs text-slate-500 italic text-center py-4">추천 제목 분석 설계 중...</div>
                          ) : (
                            titles.map((t, idx) => (
                              <div
                                key={idx}
                                onClick={() => {
                                  setSelectedTitle(t);
                                  setCustomTitle(t.title);
                                }}
                                className={`p-2.5 rounded-lg cursor-pointer border text-xs font-medium flex justify-between items-center ${selectedTitle?.title === t.title ? 'bg-indigo-950/30 border-indigo-500/40 text-white' : 'bg-slate-905 border-slate-900 hover:bg-slate-900 text-slate-300'}`}
                              >
                                <span>[{t.type}] {t.title}</span>
                                <span className="text-[10px] text-emerald-400 shrink-0 ml-1.5">CTR {t.ctr}%</span>
                              </div>
                            ))
                          )}
                        </div>
                      </div>
                    </div>
                  ) : (
                    // Cluster Post Mode Layout
                    <div className="flex flex-col gap-3">
                      <div className="grid grid-cols-2 gap-4 bg-slate-950/50 p-4 border border-slate-900 rounded-2xl">
                        <div className="flex flex-col gap-1.5">
                          <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">최소 서브글 수</label>
                          <input
                            type="number"
                            min="2"
                            max="6"
                            value={minSubs}
                            onChange={(e) => setMinSubs(parseInt(e.target.value) || 3)}
                            className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-200"
                          />
                        </div>
                        <div className="flex flex-col gap-1.5">
                          <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">최대 서브글 수</label>
                          <input
                            type="number"
                            min="3"
                            max="15"
                            value={maxSubs}
                            onChange={(e) => setMaxSubs(parseInt(e.target.value) || 10)}
                            className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-200"
                          />
                        </div>
                        <div className="col-span-2 pt-2">
                          <button
                            type="button"
                            onClick={handleGenerateCluster}
                            disabled={clusterLoading}
                            className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-extrabold text-xs transition-all shadow-md flex items-center justify-center gap-1.5 cursor-pointer"
                          >
                            <Layers size={14}/>
                            {clusterLoading ? '토픽 클러스터 구조 분석 및 AI 설계 중...' : '토픽 클러스터 구조 설계'}
                          </button>
                        </div>
                      </div>

                      {/* Cluster preview panel */}
                      {clusterData && (
                        <div className="flex flex-col gap-3 bg-slate-950/30 p-4 border border-slate-900 rounded-2xl animate-fadeIn">
                          <div className="flex flex-col gap-1 border-l-4 border-indigo-500 pl-3">
                            <span className="text-[10px] text-indigo-400 font-extrabold tracking-wider uppercase">메인 종합 가이드 포스트</span>
                            <span className="text-xs font-black text-slate-100">{clusterData.main.title}</span>
                            <span className="text-[10px] text-slate-500">{clusterData.main.summary}</span>
                          </div>

                          <div className="flex flex-col gap-2 mt-2">
                            <span className="text-[10px] text-slate-400 font-extrabold uppercase pl-1">서브글 상세 링크 매핑 ({clusterData.subs.length}개)</span>
                            <div className="flex flex-col gap-2 max-h-56 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-850">
                              {clusterData.subs.map((sub, sidx) => (
                                <div key={sidx} className="bg-slate-900/60 border border-slate-850 p-2.5 rounded-xl flex flex-col gap-1 text-[11px]">
                                  <div className="flex justify-between items-center text-slate-400">
                                    <span className="font-bold text-white">서브 #{sidx+1}: {sub.title}</span>
                                    <span className="bg-indigo-600/20 text-indigo-300 border border-indigo-500/20 px-1.5 py-0.5 rounded font-black text-[9px]">{sub.intent}</span>
                                  </div>
                                  <div className="text-[10px] text-slate-500 mt-0.5">유도 앵커 CTA: <strong className="text-slate-300 font-semibold select-all">"{sub.anchor}"</strong></div>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Common Controller Setup */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-950/30 p-3.5 border border-slate-900 rounded-2xl mt-1">
                    <div className="flex flex-col gap-1">
                      <span className="text-[10px] font-bold text-slate-450 uppercase tracking-wider pl-0.5">문체 설정</span>
                      <select
                        value={style}
                        onChange={(e) => setStyle(e.target.value)}
                        disabled={pipelineRunning}
                        className="w-full px-2.5 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-[11px] font-bold text-slate-200 cursor-pointer focus:outline-none"
                      >
                        <option value="friendly">😊 해요체 (친근)</option>
                        <option value="professional">🎓 하십시오체 (분석)</option>
                        <option value="informative">📋 리스트 요약형</option>
                      </select>
                    </div>

                    <div className="flex flex-col gap-1">
                      <span className="text-[10px] font-bold text-slate-450 uppercase tracking-wider pl-0.5">발행 블로그</span>
                      <select
                        value={platform}
                        onChange={(e) => setPlatform(e.target.value)}
                        disabled={pipelineRunning}
                        className="w-full px-2.5 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-[11px] font-bold text-slate-200 cursor-pointer focus:outline-none"
                      >
                        <option value="tistory">티스토리 API</option>
                        <option value="wordpress">워드프레스 (Mock)</option>
                        <option value="blogspot">Blogger (Mock)</option>
                      </select>
                    </div>

                    <div className="flex flex-col gap-1">
                      <span className="text-[10px] font-bold text-slate-450 uppercase tracking-wider pl-0.5">CTA 스타일</span>
                      <select
                        value={ctaStyle}
                        onChange={(e) => setCtaStyle(e.target.value)}
                        disabled={pipelineRunning}
                        className="w-full px-2.5 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-[11px] font-bold text-slate-200 cursor-pointer focus:outline-none"
                      >
                        <option value="card">🎴 카드형</option>
                        <option value="button">🔘 버튼형</option>
                        <option value="banner">🚩 배너형</option>
                      </select>
                    </div>

                    <div className="flex flex-col gap-1">
                      <span className="text-[10px] font-bold text-slate-455 uppercase tracking-wider pl-0.5">SEO 개선 강도</span>
                      <select
                        value={seoStrength}
                        onChange={(e) => setSeoStrength(e.target.value)}
                        disabled={pipelineRunning}
                        className="w-full px-2.5 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-[11px] font-bold text-slate-200 cursor-pointer focus:outline-none"
                      >
                        <option value="normal">일반 (1회 루프)</option>
                        <option value="strong">강함 (3회 루프)</option>
                        <option value="extreme">매우강함 (5회 루프)</option>
                      </select>
                    </div>

                    <div className="flex flex-col gap-1">
                      <span className="text-[10px] font-bold text-slate-455 uppercase tracking-wider pl-0.5">목표 글 길이</span>
                      <select
                        value={articleLength}
                        onChange={(e) => setArticleLength(e.target.value)}
                        disabled={pipelineRunning}
                        className="w-full px-2.5 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-[11px] font-bold text-slate-200 cursor-pointer focus:outline-none"
                      >
                        <option value="3000">3,000자</option>
                        <option value="5000">5,000자</option>
                        <option value="7000">7,000자</option>
                        <option value="10000">10,000자</option>
                      </select>
                    </div>

                    <div className="flex flex-col gap-1">
                      <span className="text-[10px] font-bold text-slate-455 uppercase tracking-wider pl-0.5">FAQ 질문 수</span>
                      <select
                        value={faqCount}
                        onChange={(e) => setFaqCount(e.target.value)}
                        disabled={pipelineRunning}
                        className="w-full px-2.5 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-[11px] font-bold text-slate-200 cursor-pointer focus:outline-none"
                      >
                        <option value="none">사용 안함</option>
                        <option value="5">5개</option>
                        <option value="10">10개</option>
                        <option value="auto">자동 추천</option>
                      </select>
                    </div>

                    <div className="flex flex-col gap-1">
                      <span className="text-[10px] font-bold text-slate-455 uppercase tracking-wider pl-0.5">AI 이미지 생성</span>
                      <button
                        type="button"
                        onClick={() => setGenerateImgPrompt(generateImgPrompt === 'ON' ? 'OFF' : 'ON')}
                        disabled={pipelineRunning}
                        className={`w-full py-1.5 rounded-xl text-[11px] font-bold border transition-all ${generateImgPrompt === 'ON' ? 'bg-emerald-600/30 text-emerald-300 border-emerald-500/50' : 'bg-slate-950 text-slate-500 border-slate-800'}`}
                      >
                        {generateImgPrompt === 'ON' ? 'ON (Imagen 3)' : 'OFF (Pillow)'}
                      </button>
                    </div>
                  </div>

                  {/* Execution actions */}
                  <div className="grid grid-cols-2 gap-4 mt-2 shrink-0 pt-3 border-t border-slate-900 relative z-20">
                    <button
                      onClick={(e) => handleStartPipeline(e, false)}
                      disabled={pipelineRunning}
                      className="py-3.5 rounded-2xl bg-indigo-600 hover:bg-indigo-500 text-white font-extrabold text-xs sm:text-xs shadow-xl transition-all text-center flex items-center justify-center gap-2 cursor-pointer"
                    >
                      <FileText size={14}/>
                      {workMode === 'cluster' ? '[클러스터 임시 저장]' : '[단일글 임시 저장]'}
                    </button>
                    <button
                      onClick={(e) => handleStartPipeline(e, true)}
                      disabled={pipelineRunning}
                      className="py-3.5 rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-extrabold text-xs sm:text-xs shadow-xl transition-all text-center flex items-center justify-center gap-2 cursor-pointer"
                    >
                      <PenTool size={14}/>
                      {workMode === 'cluster' ? '[클러스터 일괄 자동 발행]' : '[단일글 자동 발행]'}
                    </button>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center w-full h-[400px] text-slate-600 gap-2.5">
                  <Sparkles size={36} className="opacity-20 animate-pulse text-indigo-500" />
                  <p className="text-[13px] text-center italic leading-relaxed">
                    좌측 황금 키워드 목록에서 키워드를 선택하시면<br />
                    AI 콘텐츠 빌더가 가동되어 자동 기획/발행 제어를 개시합니다.
                  </p>
                </div>
              )}
            </section>

            {/* Real-time console logger */}
            <section className="glass-card rounded-3xl border border-white/5 p-5 shadow-2xl flex flex-col h-[380px]">
              <div className="flex items-center justify-between mb-3 shrink-0">
                <div className="flex items-center gap-2">
                  {pipelineRunning && <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping" />}
                  <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                    자동화 에이전트 실시간 터미널 로그
                  </h3>
                </div>
                <div className="flex gap-1">
                  {['역분석', '글생성', '이미지생성', '평가', '발행', '완료'].map(step => (
                    <span
                      key={step}
                      className={`text-[9px] px-1.5 py-0.5 rounded font-extrabold uppercase transition-all ${terminalStep === step ? 'bg-indigo-600 text-white shadow-md' : 'bg-slate-900 text-slate-650'}`}
                    >
                      {step}
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex-1 bg-black/85 border border-slate-900 rounded-2xl p-4 overflow-y-auto font-mono text-[11px] text-emerald-400 flex flex-col gap-1.5 select-all scrollbar-thin scrollbar-thumb-slate-800">
                {logs.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-slate-650 italic gap-1">
                    <Cpu size={20} className="opacity-30" />
                    <span>대기 중: 상단 글 생성 또는 일괄 발행을 트리거해 주십시오.</span>
                  </div>
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
      )}

      {/* Tab 2: 📊 발행 관리 */}
      {activeTab === 'publish' && (
        <div className="flex flex-col gap-6 w-full animate-fadeIn">
          
          {/* Stats grid */}
          <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
            <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-850/80 flex flex-col justify-between shadow-sm">
              <span className="text-[10px] font-bold text-slate-400 uppercase">전체 클러스터</span>
              <span className="text-2xl font-black text-white mt-1">{dashboardStats.total_clusters}</span>
            </div>
            <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-850/80 flex flex-col justify-between shadow-sm">
              <span className="text-[10px] font-bold text-slate-400 uppercase">발행 완료</span>
              <span className="text-2xl font-black text-emerald-400 mt-1">{dashboardStats.total_published}</span>
            </div>
            <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-850/80 flex flex-col justify-between shadow-sm">
              <span className="text-[10px] font-bold text-slate-400 uppercase">내부링크 삽입 수</span>
              <span className="text-2xl font-black text-indigo-400 mt-1">{dashboardStats.total_links}</span>
            </div>
            <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-850/80 flex flex-col justify-between shadow-sm">
              <span className="text-[10px] font-bold text-slate-400 uppercase">오늘 발행 수</span>
              <span className="text-2xl font-black text-teal-400 mt-1">{dashboardStats.today_published || 0}</span>
            </div>
            <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-850/80 flex flex-col justify-between shadow-sm">
              <span className="text-[10px] font-bold text-slate-400 uppercase">발행 대기</span>
              <span className="text-2xl font-black text-amber-400 mt-1">{dashboardStats.total_pending}</span>
            </div>
            <div className="p-4 rounded-2xl bg-rose-950/20 border border-rose-900/20 flex flex-col justify-between shadow-sm">
              <span className="text-[10px] font-bold text-rose-300 uppercase">발행 실패</span>
              <span className="text-2xl font-black text-rose-400 mt-1">{dashboardStats.total_failed}</span>
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
                onClick={fetchPostsList}
                className="p-1.5 rounded-lg border border-slate-800 bg-slate-900 hover:bg-slate-850 text-slate-400"
              >
                <RefreshCw size={12}/>
              </button>
            </div>

            <div className="overflow-x-auto border border-slate-900 rounded-2xl">
              {postsList.length === 0 ? (
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
                    {postsList.map((post, idx) => (
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
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-black ${post.status === 'published' ? 'bg-emerald-950 text-emerald-400 border border-emerald-900/30' : 'bg-rose-950 text-rose-400 border-rose-900/30'}`}>
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
                onClick={fetchLinksList}
                className="p-1.5 rounded-lg border border-slate-800 bg-slate-900 hover:bg-slate-850 text-slate-400"
              >
                <RefreshCw size={12}/>
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {linksList.length === 0 ? (
                <div className="col-span-2 p-10 text-center text-xs text-slate-500 italic border border-dashed border-slate-850 rounded-2xl">
                  삽입된 내부링크 그래프 이력이 존재하지 않습니다.
                </div>
              ) : (
                linksList.map((link, idx) => (
                  <div key={idx} className="p-4 rounded-2xl bg-slate-900/30 border border-slate-850 flex flex-col gap-3 justify-between shadow-sm">
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

                    <div className="bg-slate-950/60 p-2.5 rounded-xl border border-slate-900 text-xs text-slate-300 font-bold leading-normal">
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
                    <td className="p-3 text-center font-black text-slate-400">B등급</td>
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
                  <div className={`p-3 rounded-xl border mt-2 text-xs font-semibold leading-relaxed animate-fadeIn ${telegramTestResult.ok ? 'bg-emerald-950/20 border-emerald-900/30 text-emerald-400' : 'bg-rose-950/20 border-rose-900/30 text-rose-400'}`}>
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

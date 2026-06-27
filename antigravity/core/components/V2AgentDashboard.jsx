import React, { useState, useEffect, useRef, useCallback } from 'react';
import { PenTool, ExternalLink, LayoutGrid, Search, Flame, TrendingUp, Cpu, FileText, ShieldAlert, RefreshCw, Layers, Sparkles, Clock, Compass, Settings, Link2, StopCircle, CalendarClock } from 'lucide-react';
import { CATEGORY_MAP, CATEGORY_WEIGHTS, getStoredValue, getSortedSubCategories } from './dashboardUtils';

export default function V2AgentDashboard() {
  const [activeTab, setActiveTab] = useState('cluster'); // cluster, publish, links, performance, settings
  const [categories, setCategories] = useState({});
  const [mainCategory, setMainCategory] = useState('정부정책');
  const [subCategory, setSubCategory] = useState('정부지원금');
  const currentCategory = subCategory;
  
  // Keyword & Single post titles
  const [keywordLoading, setKeywordLoading] = useState(false);
  const [keywords, setKeywords] = useState([]);
  const [selectedKeyword, setSelectedKeyword] = useState(null);
  const [keywordSearch, setKeywordSearch] = useState('');
  const [showAllKeywords, setShowAllKeywords] = useState(false);
  const [keywordSortType] = useState('recommend');
  const [customTitle, setCustomTitle] = useState('');
  const [, setTitles] = useState([]);
  const [, setTitlesLoading] = useState(false);
  const [selectedTitle, setSelectedTitle] = useState(null);

  // Cluster states
  const [workMode, setWorkMode] = useState('single'); // single or cluster
  const [minSubs, setMinSubs] = useState(3);
  const [maxSubs, setMaxSubs] = useState(6);
  const [clusterLoading, setClusterLoading] = useState(false);
  const [clusterData, setClusterData] = useState(null);

  // ── Project #2: 스마트 발행 옵션 상태 ──
  const [useCodexImages, setUseCodexImages] = useState(true);
  const [useContextualLinks, setUseContextualLinks] = useState(true);
  const [publishType, setPublishType] = useState('immediate');
  
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
  const [clusterInterval, setClusterInterval] = useState(30);
  const [clusterTotal, setClusterTotal] = useState(5);
  const [clusterCurrent, setClusterCurrent] = useState(0);
  const [clusterStatusLabel, setClusterStatusLabel] = useState('대기 중...');

  const handleWorkModeSelect = (modeValue) => {
    if (modeValue === 'single') {
      setWorkMode('single');
      setClusterTotal(1);
    } else {
      setWorkMode('cluster');
      const total = parseInt(modeValue);
      setClusterTotal(total);
      // minSubs/maxSubs are derived from total: sub posts = total - 1
      setMinSubs(total - 1);
      setMaxSubs(total - 1);
    }
  };

  // Settings
  const [telegramToken, setTelegramToken] = useState(localStorage.getItem('styler_telegramToken') || '');
  const [telegramChatId, setTelegramChatId] = useState(localStorage.getItem('styler_telegramChatId') || '');
  const [telegramTesting, setTelegramTesting] = useState(false);
  const [telegramTestResult, setTelegramTestResult] = useState(null);
  const [publisherConfig, setPublisherConfig] = useState({ global: { gemini_api_key: '' }, profiles: [] });
  const [selectedProfileId, setSelectedProfileId] = useState(localStorage.getItem('styler_selectedProfileId_v3') || '');
  const [profileForm, setProfileForm] = useState(null);
  const [profileSaveState, setProfileSaveState] = useState('');
  const [profileTestResult, setProfileTestResult] = useState(null);

  // Lists & Stats
  const [postsList, setPostsList] = useState([]);
  const [linksList, setLinksList] = useState([]);
  const [dashboardStats, setDashboardStats] = useState({
    total_published: 0, total_pending: 0, total_failed: 0, total_clusters: 0, total_links: 0, today_published: 0
  });

  // Controls & Run
  const [style] = useState(() => getStoredValue('styler_style_v3', 'friendly'));
  const [platform, setPlatform] = useState(() => getStoredValue('styler_platform_v3', 'tistory'));
  const [ctaStyle] = useState(() => getStoredValue('styler_ctaStyle_v3', 'card'));
  const [articleLength] = useState(() => getStoredValue('styler_articleLength_v3', '5000'));
  const [customLength] = useState(() => getStoredValue('styler_customLength_v3', ''));
  const [faqCount] = useState(() => getStoredValue('styler_faqCount_v3', '10'));
  const [generateImgPrompt] = useState(() => getStoredValue('styler_generateImgPrompt_v3', 'OFF'));
  const [seoStrength] = useState(() => getStoredValue('styler_seoStrength_v3', 'strong'));
  const [pipelineRunning, setPipelineRunning] = useState(false);
  const [logs, setLogs] = useState([]);
  const [, setResult] = useState(null);
  const [, setError] = useState('');
  const [terminalStep, setTerminalStep] = useState('');
  const [terminalExpanded, setTerminalExpanded] = useState(false);

  const terminalEndRef = useRef(null);
  const abortControllerRef = useRef(null);

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
  }, [currentCategory]);

  // V2 API Fetchers
  const fetchDashboardStats = useCallback(async () => {
    try {
      const res = await fetch('/api/dashboard-stats');
      const data = await res.json();
      setDashboardStats(data);
    } catch (err) {
      console.error(err);
    }
  }, []);

  const fetchPostsList = useCallback(async () => {
    try {
      const res = await fetch('/api/published-posts');
      const data = await res.json();
      setPostsList(data);
    } catch (err) {
      console.error(err);
    }
  }, []);

  const fetchLinksList = useCallback(async () => {
    try {
      const res = await fetch('/api/internal-links');
      const data = await res.json();
      setLinksList(data);
    } catch (err) {
      console.error(err);
    }
  }, []);

  const handleMainCategoryChange = useCallback((nextMainCategory) => {
    setMainCategory(nextMainCategory);
    const subCategories = getSortedSubCategories(categories, nextMainCategory);
    if (subCategories.length > 0) {
      setSubCategory(subCategories[0]);
    }
  }, [categories]);

  // Load Categories list on mount
  useEffect(() => {
    const loadCategories = async () => {
      try {
        const res = await fetch('/api/categories');
        const data = await res.json();
        setCategories(data);
      } catch (err) {
        console.error("Failed to load categories.json:", err);
      }
    };
    loadCategories();
  }, []);

  // Reload keywords on subcategory changes
  useEffect(() => {
    if (!subCategory) return;

    const loadKeywords = async () => {
      setKeywordLoading(true);
      setSelectedKeyword(null);
      setTitles([]);
      setSelectedTitle(null);
      setResult(null);
      setClusterData(null);

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

  // Tab changes loaders
  useEffect(() => {
    const loadDashboardStats = async () => {
      try {
        const res = await fetch('/api/dashboard-stats');
        const data = await res.json();
        setDashboardStats(data);
      } catch (err) {
        console.error(err);
      }
    };

    const loadPostsList = async () => {
      try {
        const res = await fetch('/api/published-posts');
        const data = await res.json();
        setPostsList(data);
      } catch (err) {
        console.error(err);
      }
    };

    const loadLinksList = async () => {
      try {
        const res = await fetch('/api/internal-links');
        const data = await res.json();
        setLinksList(data);
      } catch (err) {
        console.error(err);
      }
    };

    if (activeTab === 'publish') {
      loadDashboardStats();
      loadPostsList();
    } else if (activeTab === 'links') {
      loadLinksList();
    }
  }, [activeTab]);

  // V2 API Cluster Actions
  const handleGenerateCluster = async () => {
    if (!selectedKeyword) return;
    setKeywordLoading(true);
    setClusterLoading(true);
    setClusterData(null);
    setError('');
    try {
      const res = await fetch('/api/cluster-generate', {
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
      setKeywordLoading(false);
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

  const getProfilesForPlatform = (targetPlatform = platform) => (
    (publisherConfig.profiles || []).filter(p => p.platform === targetPlatform && p.enabled !== false)
  );

  const handleSelectProfile = (profileId) => {
    const profile = (publisherConfig.profiles || []).find(p => p.id === profileId);
    setSelectedProfileId(profileId);
    if (profile) setProfileForm(profile);
    setProfileTestResult(null);
    setProfileSaveState('');
  };

  const handleNewProfile = (targetPlatform = platform) => {
    const nextProfile = {
      id: `${targetPlatform}-${Date.now()}`,
      platform: targetPlatform,
      label: targetPlatform === 'tistory' ? '새 티스토리 프로필' : '새 워드프레스 프로필',
      blog_name: '',
      access_token: '',
      api_url: '',
      username: '',
      password: '',
      enabled: true
    };
    setPublisherConfig(prev => ({ ...prev, profiles: [...(prev.profiles || []), nextProfile] }));
    setSelectedProfileId(nextProfile.id);
    setProfileForm(nextProfile);
    setProfileTestResult(null);
    setProfileSaveState('새 프로필 작성 중');
  };

  const handleProfileFieldChange = (field, value) => {
    setProfileForm(prev => ({ ...(prev || {}), [field]: value }));
    setProfileSaveState('');
    setProfileTestResult(null);
  };

  const handleSavePublisherConfig = async () => {
    if (!profileForm) return;
    setProfileSaveState('저장 중...');
    const nextConfig = {
      ...publisherConfig,
      profiles: (publisherConfig.profiles || []).map(p => p.id === profileForm.id ? profileForm : p)
    };
    if (!nextConfig.profiles.find(p => p.id === profileForm.id)) {
      nextConfig.profiles.push(profileForm);
    }
    try {
      const res = await fetch('/api/publisher-profiles', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(nextConfig)
      });
      const data = await res.json();
      setPublisherConfig(data);
      setSelectedProfileId(profileForm.id);
      setProfileSaveState('저장 완료');
    } catch (err) {
      setProfileSaveState(`저장 실패: ${err.message}`);
    }
  };

  const handleTestPublisherProfile = async () => {
    if (!profileForm) return;
    setProfileTestResult(null);
    try {
      const res = await fetch('/api/publisher-profiles/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ platform: profileForm.platform, profile_id: profileForm.id })
      });
      const data = await res.json();
      setProfileTestResult(data);
    } catch (err) {
      setProfileTestResult({ ok: false, error: err.message });
    }
  };

  const handleOpenPostPreview = (post) => {
    if (!post?.id) return;
    window.open(`/api/post-preview/${post.id}`, '_blank', 'noopener,noreferrer');
  };

  // 파이프라인 강제 중지 핸들러
  const handleStopPipeline = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setPipelineRunning(false);
    setTerminalStep('중지됨');
    setLogs(prev => [...prev, '⛔ 사용자가 파이프라인을 수동 중지하였습니다.']);
  };

  // Execute Pipeline (Single or Cluster)
  const handleStartPipeline = async (e, publishFlag = false) => {
    if (e) e.preventDefault();
    if (!selectedKeyword) return;

    setPipelineRunning(true);
    setTerminalExpanded(true);
    setError('');
    setResult(null);
    setLogs([]);
    setTerminalStep('역분석');

    const controller = new AbortController();
    abortControllerRef.current = controller;

    const finalLength = articleLength === 'custom' ? customLength : articleLength;
    const finalTitle = customTitle || (selectedTitle ? selectedTitle.title : `${selectedKeyword.keyword} 완벽 가이드`);

    if (workMode === 'cluster') {
      try {
        const response = await fetch('/api/cluster-publish', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            keyword: selectedKeyword.keyword,
            platform,
            profile_id: selectedProfileId,
            style,
            category: selectedKeyword.category || currentCategory,
            length: finalLength || '5000',
            faq_count: faqCount,
            img_prompt: useCodexImages ? 'ON' : 'OFF',
            contextual_links: useContextualLinks ? 'ON' : 'OFF',
            scheduled_at: publishType === 'scheduled' ? firstPublishTime.replace('T', ' ') + ':00' : null,
            seo_strength: seoStrength,
            publish: publishFlag,
            min_subs: minSubs,
            max_subs: maxSubs,
            search_volume: selectedKeyword.search_volume,
            competition: selectedKeyword.competition,
            cpc: selectedKeyword.cpc,
            interval: clusterInterval
          }),
          signal: controller.signal
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
                  
                  if (logText.includes('[CLUSTER-1]')) {
                    setTerminalStep('역분석');
                    setClusterCurrent(0);
                    setClusterStatusLabel('토픽 클러스터 구조 생성 중...');
                  } else if (logText.includes('[CLUSTER-2]')) {
                    setClusterStatusLabel('RAG 기반 자료 수집 및 정보 분석 중...');
                  } else if (logText.includes('[CLUSTER-3-')) {
                    setTerminalStep('글생성');
                    const match = logText.match(/\[CLUSTER-3-(\d+)\]/);
                    if (match && match[1]) {
                      const postIdx = parseInt(match[1]);
                      setClusterCurrent(postIdx);
                      if (postIdx === 1) {
                        setClusterStatusLabel('메인 종합 가이드 포스트 생성 중...');
                      } else {
                        setClusterStatusLabel(`서브글 ${postIdx - 1}/${clusterTotal - 1} 생성 및 분석 중...`);
                      }
                    }
                  } else if (logText.includes('[CLUSTER-4]')) {
                    setTerminalStep('발행');
                    setClusterStatusLabel(`서브글 ${clusterTotal - 1}/${clusterTotal - 1} 메인글 내부링크 연결 중`);
                  } else if (logText.includes('[CLUSTER-5]')) {
                    setTerminalStep('완료');
                    setClusterCurrent(clusterTotal);
                    setClusterStatusLabel('클러스터 전체 발행 및 텔레그램 리포트 완료');
                  }
                }
                if (payload.success && payload.result) {
                  setResult(payload.result);
                  setTerminalStep('완료');
                  fetchDashboardStats(); // Refresh stats on success
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
        if (err.name === 'AbortError') {
           console.log('Fetch aborted');
        } else {
          setError(err.message);
          setTerminalStep('에러');
        }
      } finally {
        setPipelineRunning(false);
      }
    } else {
      // Single Mode Publish
      try {
        const response = await fetch('/api/publish-pipeline', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            keyword: selectedKeyword.keyword,
            platform,
            profile_id: selectedProfileId,
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
          }),
          signal: controller.signal
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
  const visibleKeywords = showAllKeywords ? filteredKeywords : filteredKeywords.slice(0, 5);

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
                if (!pipelineRunning) handleMainCategoryChange(e.target.value);
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
              {getSortedSubCategories(categories, mainCategory).map(subCat => (
                <option key={subCat} value={subCat}>{subCat}</option>
              ))}
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
          <Link2 size={14}/> 🔗 내부링크 그래프
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
          
          {/* Left Column (8/12) */}
          <div className="lg:col-span-8 flex flex-col gap-6 w-full">
            
            {/* Real-time console logger */}
            <section className={`glass-card rounded-3xl border border-white/5 shadow-2xl flex flex-col transition-all duration-300 ${terminalExpanded ? 'p-5 h-[380px]' : 'p-3 h-auto'}`}>
              <div className="flex items-center justify-between shrink-0 cursor-pointer" onClick={() => setTerminalExpanded(!terminalExpanded)}>
                <div className="flex items-center gap-2">
                  {pipelineRunning && <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping" />}
                  <h3 className="text-xs font-black text-slate-300 uppercase tracking-wider">
                    자동화 에이전트 실시간 터미널 로그
                  </h3>
                  {!terminalExpanded && logs.length > 0 && (
                    <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full font-bold">{logs.length}줄</span>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  {terminalExpanded && (
                    <div className="flex gap-1.5">
                      {['역분석', '글생성', '이미지생성', '평가', '발행', '완료'].map(step => (
                        <span
                          key={step}
                          className={`text-[10px] px-2 py-0.5 rounded font-black uppercase transition-all ${terminalStep === step ? 'bg-indigo-600 text-white shadow-md' : 'bg-slate-900 text-slate-650'}`}
                        >
                          {step}
                        </span>
                      ))}
                    </div>
                  )}
                  <button className="p-1.5 rounded-lg border border-slate-800 bg-slate-900 hover:bg-slate-800 text-slate-400 transition-all text-[10px] font-black" onClick={(e) => { e.stopPropagation(); setTerminalExpanded(!terminalExpanded); }}>
                    {terminalExpanded ? '▲ 접기' : '▼ 펼치기'}
                  </button>
                </div>
              </div>

              {terminalExpanded && (
                <div className="flex-1 bg-black/85 border border-slate-900 rounded-2xl p-4 overflow-y-auto font-mono text-[11px] text-emerald-400 flex flex-col gap-1.5 select-all scrollbar-thin scrollbar-thumb-slate-800 mt-3">
                  {logs.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-slate-650 italic gap-2 opacity-50">
                      <Cpu size={24} />
                      <span>대기 중: 우측 설정 후 발행 버튼을 트리거해 주십시오.</span>
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
              )}
            </section>

            {/* 황금틈새 판단 이유 카드 (Project #2 New) */}
            {selectedKeyword && (
              <section className="relative w-full rounded-3xl p-5 overflow-hidden border border-indigo-500/20 bg-indigo-950/10 shadow-xl animate-fadeIn">
                <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/[0.05] to-transparent pointer-events-none" />
                <div className="flex items-start gap-4 relative z-10">
                  <div className="p-3 rounded-2xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
                    <TrendingUp size={24} />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="text-sm font-black text-indigo-300 uppercase tracking-tight">AI 황금틈새 전략 분석 리포트</h4>
                      <span className="text-[10px] bg-indigo-500/30 text-indigo-100 border border-indigo-400/30 px-2 py-0.5 rounded-full font-black">BLUE OCEAN SCORE: {selectedKeyword?.blue_ocean_score || 85}</span>
                    </div>
                    <p className="text-[12px] text-slate-300 font-bold leading-relaxed">
                      "{selectedKeyword?.keyword}" 키워드는 현재 검색량 대비 경쟁 문서의 품질이 낮아 클러스터 공략 시 72시간 내 상위 노출 확률이 매우 높습니다.
                      메인 1개 글과 {clusterTotal - 1}개의 서브글을 통한 내부링크 강화 전략을 추천합니다.
                    </p>
                  </div>
                </div>
              </section>
            )}

            {/* 주황색 프로그레스 바 (Project #2 New) */}
            {pipelineRunning && workMode === 'cluster' && (
              <section className="glass-card rounded-3xl border border-orange-500/30 bg-orange-500/5 p-5 shadow-xl animate-pulse">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className="p-2 rounded-xl bg-orange-500 text-white">
                      <Layers size={16} />
                    </div>
                    <div>
                      <h4 className="text-xs font-black text-orange-200 uppercase tracking-wider">토픽 클러스터 에이전트 가동 중</h4>
                      <p className="text-[10px] text-orange-400/80 font-bold mt-0.5">{clusterStatusLabel}</p>
                    </div>
                  </div>
                  <button 
                    onClick={handleStopPipeline}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-rose-600/20 hover:bg-rose-600/40 text-rose-400 border border-rose-500/30 text-[10px] font-black transition-all"
                  >
                    <StopCircle size={12} />
                    강제 중지
                  </button>
                </div>
                
                <div className="w-full h-2.5 bg-slate-900 rounded-full border border-slate-800 overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-orange-600 to-orange-400 transition-all duration-700"
                    style={{ width: `${(clusterCurrent / clusterTotal) * 100}%` }}
                  />
                </div>
                <div className="flex justify-between items-center mt-2 px-1">
                  <span className="text-[10px] text-orange-400 font-black">진행률: {Math.round((clusterCurrent / clusterTotal) * 100)}%</span>
                  <span className="text-[10px] text-slate-500 font-bold">{clusterCurrent} / {clusterTotal} 포스트 처리 중</span>
                </div>
              </section>
            )}

            {/* 콘텐츠 설계 프리뷰 리스트 (Cluster Preview) */}
            {clusterData && (
              <section className="glass-card rounded-3xl border border-white/5 p-5 shadow-2xl flex flex-col gap-4">
                <h3 className="text-xs font-black text-slate-300 flex items-center gap-1.5 uppercase tracking-wider">
                  <Layers size={14} className="text-indigo-400" />
                  클러스터 콘텐츠 설계 프리뷰
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="col-span-1 md:col-span-2 p-4 rounded-2xl bg-indigo-600/10 border border-indigo-500/30 flex flex-col gap-1">
                    <span className="text-[10px] text-indigo-400 font-black uppercase tracking-widest">CORE MAIN POST</span>
                    <h4 className="text-xs font-black text-white">{clusterData.main.title}</h4>
                    <p className="text-[11px] text-slate-400 line-clamp-1">{clusterData.main.summary}</p>
                  </div>
                  {clusterData.subs.map((sub, sidx) => (
                    <div key={sidx} className="p-3 rounded-2xl bg-slate-900/40 border border-slate-850 flex flex-col gap-1.5">
                      <div className="flex justify-between items-center">
                        <span className="text-[9px] text-slate-500 font-black uppercase tracking-widest">SUB POST #{sidx + 1}</span>
                        <span className="text-[9px] bg-slate-950 px-1.5 py-0.5 rounded text-indigo-300 border border-slate-800 font-black">{sub.intent}</span>
                      </div>
                      <h4 className="text-[11px] font-bold text-slate-200 line-clamp-1">{sub.title}</h4>
                      <div className="text-[9px] text-slate-500 mt-1 border-t border-slate-850 pt-1.5">CTA: <strong className="text-slate-400">"{sub.anchor}"</strong></div>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* 키워드 목록 섹션 (Keywords moved here) */}
            <section className="glass-card rounded-3xl border border-white/5 p-5 shadow-2xl flex flex-col gap-4">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-black text-slate-300 flex items-center gap-1.5 uppercase tracking-wider">
                  <Flame size={14} className="text-orange-500 animate-pulse" />
                  검색 키워드 분석 결과 ({filteredKeywords.length})
                </h3>
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
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {visibleKeywords.map((kw, i) => {
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
                      className={`p-3.5 rounded-2xl border-l-4 border transition-all cursor-pointer flex justify-between items-center hover:shadow-md ${isSelected ? 'bg-indigo-600/15 border-l-indigo-500 border-indigo-500/50 text-indigo-300 shadow-lg' : 'bg-slate-900/30 border-l-indigo-600/60 border-slate-800/50 hover:bg-slate-900/60 text-slate-300'}`}
                    >
                      <div className="flex flex-col gap-1">
                        <span className="text-[13px] font-black text-slate-100">{kw.keyword}</span>
                        <div className="flex gap-3 text-[10px] text-slate-500 font-bold">
                          <span>🔍 {kw.search_volume.toLocaleString()}</span>
                          <span>💰 ${kw.cpc_dollar.toFixed(1)}</span>
                        </div>
                      </div>
                      <div className="flex flex-col items-end gap-1.5">
                        <span className={`text-[10px] px-2.5 py-0.5 rounded-full font-black border ${isSelected ? 'bg-indigo-600/30 border-indigo-500/50 text-indigo-200' : 'bg-slate-950 border-slate-800 text-emerald-400'}`}>{kw.ai_badge || "추천"}</span>
                        <span className="text-[10px] text-indigo-400 font-black">Score: {kw.golden_score}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
              
              {!keywordLoading && filteredKeywords.length > 5 && (
                <button
                  type="button"
                  onClick={() => setShowAllKeywords(!showAllKeywords)}
                  className="w-full py-2.5 rounded-xl border border-slate-800 bg-slate-900/40 hover:bg-slate-900/80 text-slate-400 hover:text-slate-200 text-xs font-black transition-all text-center block cursor-pointer"
                >
                  {showAllKeywords ? '👆 추천 TOP5 요약 보기' : `👇 전체 ${filteredKeywords.length}개 키워드 보기`}
                </button>
              )}
            </section>
          </div>

          {/* Right Column (4/12) - Smart Publish Settings */}
          <div className="lg:col-span-4 flex flex-col gap-6 w-full sticky top-6">
            
            {/* Smart Publish Controller */}
            <section className="glass-card rounded-3xl border border-white/5 p-5 shadow-2xl flex flex-col gap-5">
              <div className="flex items-center gap-2 border-b border-slate-900 pb-3">
                <div className="p-2 rounded-xl bg-gradient-to-tr from-violet-600 to-indigo-600 text-white shadow-md">
                  <Settings size={16} />
                </div>
                <div>
                  <h4 className="text-xs font-black text-slate-300 uppercase tracking-wider">스마트 발행 컨트롤러</h4>
                </div>
              </div>

              <div className="flex flex-col gap-5">

                <div className="flex flex-col gap-2">
                  <label className="text-[11px] font-black text-slate-500 uppercase tracking-widest pl-1">발행 프로필</label>
                  <div className="grid grid-cols-2 gap-2">
                    <select
                      value={platform}
                      onChange={(e) => setPlatform(e.target.value)}
                      className="w-full px-3 py-3 rounded-2xl bg-slate-950 border border-slate-850 text-[11px] font-black text-slate-200 focus:outline-none focus:border-indigo-500"
                    >
                      <option value="tistory">티스토리</option>
                      <option value="wordpress">워드프레스</option>
                    </select>
                    <select
                      value={selectedProfileId}
                      onChange={(e) => handleSelectProfile(e.target.value)}
                      className="w-full px-3 py-3 rounded-2xl bg-slate-950 border border-slate-850 text-[11px] font-black text-slate-200 focus:outline-none focus:border-indigo-500"
                    >
                      {getProfilesForPlatform().length === 0 && <option value="">프로필 없음</option>}
                      {getProfilesForPlatform().map(profile => (
                        <option key={profile.id} value={profile.id}>{profile.label}</option>
                      ))}
                    </select>
                  </div>
                  <button
                    type="button"
                    onClick={() => setActiveTab('settings')}
                    className="py-2 rounded-xl bg-slate-950 border border-slate-850 text-[10px] font-black text-indigo-300 hover:text-white hover:border-indigo-500 transition-all"
                  >
                    프로필/API 설정 열기
                  </button>
                </div>
                 
                {/* Codex & Internal Link Toggles */}
                <div className="flex flex-col gap-3">
                  <div className="flex items-center justify-between p-3.5 rounded-2xl bg-slate-950 border border-slate-800 shadow-inner">
                    <div className="flex flex-col gap-0.5">
                      <span className="text-xs font-black text-slate-200">Codex AI 이미지</span>
                      <span className="text-[10px] text-slate-500 font-bold">포스트당 고품질 이미지 2개</span>
                    </div>
                    <button 
                      onClick={() => setUseCodexImages(!useCodexImages)}
                      className={`w-11 h-6 rounded-full transition-all relative ${useCodexImages ? 'bg-indigo-600' : 'bg-slate-800'}`}
                    >
                      <div className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-all ${useCodexImages ? 'left-6' : 'left-1'}`} />
                    </button>
                  </div>

                  <div className="flex items-center justify-between p-3.5 rounded-2xl bg-slate-950 border border-slate-800 shadow-inner">
                    <div className="flex flex-col gap-0.5">
                      <span className="text-xs font-black text-slate-200">문맥형 내부링크</span>
                      <span className="text-[10px] text-slate-500 font-bold">클러스터 내 글간 자동 CTA</span>
                    </div>
                    <button 
                      onClick={() => setUseContextualLinks(!useContextualLinks)}
                      className={`w-11 h-6 rounded-full transition-all relative ${useContextualLinks ? 'bg-indigo-600' : 'bg-slate-800'}`}
                    >
                      <div className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-all ${useContextualLinks ? 'left-6' : 'left-1'}`} />
                    </button>
                  </div>
                </div>

                {/* Mode Select */}
                <div className="flex flex-col gap-2">
                  <label className="text-[11px] font-black text-slate-500 uppercase tracking-widest pl-1">발행 모드 구성</label>
                  <div className="grid grid-cols-2 gap-2">
                    {[
                      { id: 'single', label: '단일 글 발행', icon: <FileText size={12}/> },
                      { id: '5', label: '5개 클러스터', icon: <Layers size={12}/> },
                      { id: '10', label: '10개 클러스터', icon: <LayoutGrid size={12}/> },
                      { id: '15', label: '15개 클러스터', icon: <Cpu size={12}/> }
                    ].map(m => (
                      <button
                        key={m.id}
                        onClick={() => handleWorkModeSelect(m.id)}
                        className={`flex items-center justify-center gap-2 py-3 rounded-2xl text-[11px] font-black border transition-all ${
                          (workMode === m.id || (workMode === 'cluster' && clusterTotal.toString() === m.id))
                          ? 'bg-indigo-600 border-indigo-500 text-white shadow-lg' 
                          : 'bg-slate-950 border-slate-850 text-slate-400 hover:border-slate-700'
                        }`}
                      >
                        {m.icon}
                        {m.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Publish Type & Time */}
                <div className="flex flex-col gap-2">
                  <label className="text-[11px] font-black text-slate-500 uppercase tracking-widest pl-1">발행 시점 예약</label>
                  <div className="flex bg-slate-950 border border-slate-850 p-1 rounded-2xl gap-1">
                    <button
                      onClick={() => setPublishType('immediate')}
                      className={`flex-1 py-2 rounded-xl text-[10px] font-black transition-all ${publishType === 'immediate' ? 'bg-slate-800 text-white shadow-md' : 'text-slate-500 hover:text-slate-300'}`}
                    >
                      즉시 발행
                    </button>
                    <button
                      onClick={() => setPublishType('scheduled')}
                      className={`flex-1 py-2 rounded-xl text-[10px] font-black transition-all ${publishType === 'scheduled' ? 'bg-slate-800 text-white shadow-md' : 'text-slate-500 hover:text-slate-300'}`}
                    >
                      예약 발행
                    </button>
                  </div>
                  
                  {publishType === 'scheduled' && (
                    <div className="flex flex-col gap-2 mt-1 animate-fadeIn">
                      <div className="relative">
                        <input
                          type="datetime-local"
                          value={firstPublishTime}
                          onChange={(e) => setFirstPublishTime(e.target.value)}
                          className="w-full pl-9 pr-3 py-3 rounded-2xl bg-slate-950 border border-slate-850 text-[11px] font-black text-slate-200 focus:outline-none focus:border-indigo-500"
                        />
                        <CalendarClock size={16} className="absolute left-3 top-3.5 text-indigo-400" />
                      </div>
                      <div className="flex flex-col gap-1.5 px-1 mt-1">
                        <div className="flex justify-between text-[10px] font-bold">
                          <span className="text-slate-500">클러스터 발행 간격</span>
                          <span className="text-indigo-400">{clusterInterval}분</span>
                        </div>
                        <input
                          type="range"
                          min="10"
                          max="180"
                          step="10"
                          value={clusterInterval}
                          onChange={(e) => setClusterInterval(parseInt(e.target.value))}
                          className="w-full h-1.5 bg-slate-900 rounded-full appearance-none cursor-pointer accent-indigo-500"
                        />
                      </div>
                    </div>
                  )}
                </div>

                {/* Action Button */}
                <div className="pt-2">
                  {selectedKeyword ? (
                    <>
                      {workMode === 'cluster' && !clusterData && !pipelineRunning ? (
                        <button
                          onClick={handleGenerateCluster}
                          disabled={clusterLoading}
                          className="w-full py-4 rounded-2xl bg-indigo-600 hover:bg-indigo-500 text-white font-black text-sm shadow-xl transition-all flex items-center justify-center gap-2"
                        >
                          {clusterLoading ? (
                            <>
                              <RefreshCw size={18} className="animate-spin" />
                              클러스터 설계 중...
                            </>
                          ) : (
                            <>
                              <Layers size={18} />
                              토픽 클러스터 구조 설계 시작
                            </>
                          )}
                        </button>
                      ) : (
                        <button
                          onClick={(e) => handleStartPipeline(e, true)}
                          disabled={pipelineRunning}
                          className={`w-full py-4 rounded-2xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-black text-sm shadow-xl transition-all flex items-center justify-center gap-2 group ${pipelineRunning ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                        >
                          {pipelineRunning ? (
                            <>
                              <RefreshCw size={18} className="animate-spin" />
                              에이전트 가동 중...
                            </>
                          ) : (
                            <>
                              <PenTool size={18} className="group-hover:rotate-12 transition-transform" />
                              {workMode === 'single' ? 'AI 단일 글 즉시 발행' : `${clusterTotal}개 클러스터 일괄 발행`}
                            </>
                          )}
                        </button>
                      )}
                    </>
                  ) : (
                    <div className="w-full py-4 rounded-2xl bg-slate-900 border border-slate-850 text-slate-600 text-[11px] font-black text-center italic">
                      키워드를 먼저 선택해 주십시오.
                    </div>
                  )}
                  <p className="text-[10px] text-slate-500 text-center mt-3 font-medium">※ 발행 시 텔레그램 실시간 리포트가 전송됩니다.</p>
                </div>

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
                      <th className="p-3 text-center">내부 검수</th>
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
                          <button
                            type="button"
                            onClick={() => handleOpenPostPreview(post)}
                            className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:border-indigo-500 font-bold text-[10px]"
                          >
                            검수 열기 <FileText size={10}/>
                          </button>
                        </td>
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
                  <Link2 size={14} className="text-indigo-400" />
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
                발행 API 및 다중 프로필 설정
              </h3>
              
              <div className="flex flex-col gap-4 text-xs leading-relaxed text-slate-400 font-medium">
                <div className="flex flex-col gap-1.5">
                  <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Gemini API Key</label>
                  <input
                    type="password"
                    value={publisherConfig.global?.gemini_api_key || ''}
                    onChange={(e) => setPublisherConfig(prev => ({ ...prev, global: { ...(prev.global || {}), gemini_api_key: e.target.value } }))}
                    placeholder="AI Studio에서 발급받은 키"
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 focus:border-indigo-500 focus:outline-none text-xs font-bold text-slate-200"
                  />
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <select
                    value={profileForm?.platform || platform}
                    onChange={(e) => {
                      setPlatform(e.target.value);
                      const next = (publisherConfig.profiles || []).find(p => p.platform === e.target.value);
                      if (next) handleSelectProfile(next.id);
                    }}
                    className="w-full px-3 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs font-bold text-slate-200 focus:border-indigo-500 focus:outline-none"
                  >
                    <option value="tistory">티스토리</option>
                    <option value="wordpress">워드프레스</option>
                  </select>
                  <button
                    type="button"
                    onClick={() => handleNewProfile(profileForm?.platform || platform)}
                    className="py-2.5 rounded-xl bg-slate-900 hover:bg-slate-850 text-slate-300 font-extrabold text-xs border border-slate-800"
                  >
                    새 프로필 추가
                  </button>
                </div>

                <select
                  value={selectedProfileId}
                  onChange={(e) => handleSelectProfile(e.target.value)}
                  className="w-full px-3 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs font-bold text-slate-200 focus:border-indigo-500 focus:outline-none"
                >
                  {getProfilesForPlatform(profileForm?.platform || platform).map(profile => (
                    <option key={profile.id} value={profile.id}>{profile.label}</option>
                  ))}
                </select>

                {profileForm && (
                  <div className="flex flex-col gap-3 p-4 rounded-2xl bg-slate-950/60 border border-slate-900">
                    <div className="flex flex-col gap-1.5">
                      <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">프로필 이름</label>
                      <input
                        type="text"
                        value={profileForm.label || ''}
                        onChange={(e) => handleProfileFieldChange('label', e.target.value)}
                        className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 focus:border-indigo-500 focus:outline-none text-xs font-bold text-slate-200"
                      />
                    </div>

                    {profileForm.platform === 'tistory' ? (
                      <>
                        <div className="flex flex-col gap-1.5">
                          <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">티스토리 블로그 이름</label>
                          <input
                            type="text"
                            value={profileForm.blog_name || ''}
                            onChange={(e) => handleProfileFieldChange('blog_name', e.target.value)}
                            placeholder="예: myblog"
                            className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 focus:border-indigo-500 focus:outline-none text-xs font-bold text-slate-200"
                          />
                        </div>
                        <div className="flex flex-col gap-1.5">
                          <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">티스토리 액세스 토큰</label>
                          <input
                            type="password"
                            value={profileForm.access_token || ''}
                            onChange={(e) => handleProfileFieldChange('access_token', e.target.value)}
                            placeholder="Tistory OAuth Access Token"
                            className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 focus:border-indigo-500 focus:outline-none text-xs font-bold text-slate-200"
                          />
                        </div>
                      </>
                    ) : (
                      <>
                        <div className="flex flex-col gap-1.5">
                          <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">워드프레스 REST API 주소</label>
                          <input
                            type="text"
                            value={profileForm.api_url || ''}
                            onChange={(e) => handleProfileFieldChange('api_url', e.target.value)}
                            placeholder="https://example.com/wp-json/wp/v2"
                            className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 focus:border-indigo-500 focus:outline-none text-xs font-bold text-slate-200"
                          />
                        </div>
                        <div className="grid grid-cols-2 gap-2">
                          <input
                            type="text"
                            value={profileForm.username || ''}
                            onChange={(e) => handleProfileFieldChange('username', e.target.value)}
                            placeholder="사용자명"
                            className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 focus:border-indigo-500 focus:outline-none text-xs font-bold text-slate-200"
                          />
                          <input
                            type="password"
                            value={profileForm.password || ''}
                            onChange={(e) => handleProfileFieldChange('password', e.target.value)}
                            placeholder="앱 비밀번호"
                            className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 focus:border-indigo-500 focus:outline-none text-xs font-bold text-slate-200"
                          />
                        </div>
                      </>
                    )}

                    <div className="grid grid-cols-2 gap-3">
                      <button
                        type="button"
                        onClick={handleTestPublisherProfile}
                        className="py-2.5 rounded-xl bg-slate-900 hover:bg-slate-850 text-slate-300 font-extrabold text-xs border border-slate-800"
                      >
                        필수값 검사
                      </button>
                      <button
                        type="button"
                        onClick={handleSavePublisherConfig}
                        className="py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-extrabold text-xs"
                      >
                        프로필 저장
                      </button>
                    </div>
                  </div>
                )}

                {profileSaveState && (
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-900 text-[11px] font-bold text-indigo-300">
                    {profileSaveState}
                  </div>
                )}
                {profileTestResult && (
                  <div className={`p-3 rounded-xl border text-[11px] font-bold ${profileTestResult.ok ? 'bg-emerald-950/20 border-emerald-900/30 text-emerald-400' : 'bg-rose-950/20 border-rose-900/30 text-rose-400'}`}>
                    {profileTestResult.message || profileTestResult.error}
                  </div>
                )}

                <p className="mt-1 flex items-center gap-1.5 text-slate-500 text-[11px] font-bold">
                  <ShieldAlert size={14} className="text-amber-500 animate-pulse" />
                  저장된 값은 로컬 설정 파일에만 보관되며, 선택한 프로필은 발행 실행 시에만 적용됩니다.
                </p>
              </div>
            </section>
          </div>

        </div>
      )}

    </div>
  );
}

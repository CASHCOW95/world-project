import React, { useState, useEffect, useRef } from 'react';
import { PenTool, Copy, Check, RotateCcw, AlertTriangle, ExternalLink, Hash } from 'lucide-react';

export default function StylerDashboard() {
  const [keyword, setKeyword] = useState('');
  const [style, setStyle] = useState('friendly');
  const [length, setLength] = useState('short');
  const [platform, setPlatform] = useState('tistory');
  
  const [loading, setLoading] = useState(false);
  const [progressStep, setProgressStep] = useState(0);
  const [credits, setCredits] = useState(5);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState('preview');

  const previewRef = useRef(null);

  // Fetch initial credits
  useEffect(() => {
    fetchCredits();
  }, []);

  const fetchCredits = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/credits');
      const data = await res.json();
      setCredits(data.credits);
    } catch (err) {
      console.error("Failed to load credits:", err);
    }
  };

  const resetCredits = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/credits/reset', { method: 'POST' });
      const data = await res.json();
      setCredits(data.credits);
      setError('');
    } catch (err) {
      console.error("Failed to reset credits:", err);
    }
  };

  // Simulated progress sequence during generation
  const steps = [
    "핵심 키워드 조회 및 분석 중...",
    "글의 대주제와 소주제 목차 기획 중...",
    "사용자 타겟 및 서술 스타일 튜닝 중...",
    "스타일러 프로 무인 집필 가동 중...",
    "SEO HTML 코드 포맷팅 및 용어 정제 중..."
  ];

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!keyword.trim()) return;

    setLoading(true);
    setError('');
    setResult(null);
    setProgressStep(0);

    // Increment progress steps over time
    const interval = setInterval(() => {
      setProgressStep(prev => {
        if (prev < steps.length - 1) return prev + 1;
        clearInterval(interval);
        return prev;
      });
    }, 800);

    try {
      const res = await fetch('http://localhost:5000/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keyword, style, length, platform })
      });

      clearInterval(interval);

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.error || '원고 생성 중 오류가 발생했습니다.');
      }

      const data = await res.json();
      setResult(data);
      setCredits(data.credits_left);
      setActiveTab('preview');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (!result) return;
    navigator.clipboard.writeText(result.html_content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 w-full items-start">
      {/* 1열: 제어 및 설정 + 태그/요약 */}
      <div className="flex flex-col gap-4 w-full">
        {/* SaaS Billing & Credit Display Panel */}
        <section className="glass-card rounded-2xl p-4 flex items-center justify-between border border-slate-800/80">
          <div className="flex flex-col">
            <span className="text-[10px] text-violet-400 font-bold uppercase tracking-wider">SaaS 요금제 가입 정보 (Model 1)</span>
            <span className="text-sm font-semibold text-slate-200">
              일일 무료 크레딧: <span className={`font-bold ${credits > 0 ? 'text-violet-400' : 'text-rose-500'}`}>{credits}</span> / 5회
            </span>
          </div>
          
          {credits === 0 ? (
            <button
              onClick={resetCredits}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white text-xs font-bold transition-all shadow-lg hover:scale-105 active:scale-95"
            >
              <RotateCcw size={12} />
              크레딧 충전하기
            </button>
          ) : (
            <span className="text-[10px] bg-slate-900/80 text-slate-500 px-3 py-1 rounded-full border border-slate-800">
              자동 갱신 대기 중
            </span>
          )}
        </section>

        {/* Main Generator Form Card */}
        <section className="glass-card rounded-3xl p-6 border border-slate-800/80 shadow-2xl">
          <div className="flex items-center gap-2 mb-5">
            <div className="p-2 rounded-xl bg-gradient-to-tr from-violet-600 to-indigo-600 text-white shadow-md">
              <PenTool size={18} />
            </div>
            <div>
              <h2 className="text-base font-bold text-white leading-tight">스타일러 프로 (Styler Pro)</h2>
              <p className="text-[10px] text-slate-400">SEO 최적화 블로그 원고 대량 무인 집필기</p>
            </div>
          </div>

          <form onSubmit={handleGenerate} className="flex flex-col gap-4">
            {/* Keyword Input */}
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-bold text-slate-400">대상 핵심 키워드</label>
              <input
                type="text"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                placeholder="예: 반지하 관리 방법, 쿠팡 파트너스 꿀팁"
                disabled={loading}
                className="w-full px-4 py-3 rounded-xl bg-slate-950/80 border border-slate-800 focus:border-violet-500 focus:outline-none text-slate-200 text-sm transition-all placeholder:text-slate-600"
              />
            </div>

            {/* Configuration Grid */}
            <div className="grid grid-cols-2 gap-3.5">
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-bold text-slate-400">서술 스타일</label>
                <select
                  value={style}
                  onChange={(e) => setStyle(e.target.value)}
                  disabled={loading}
                  className="w-full px-3 py-2.5 rounded-xl bg-slate-950/80 border border-slate-800 focus:border-violet-500 focus:outline-none text-slate-200 text-xs transition-all"
                  style={{ colorScheme: 'dark' }}
                >
                  <option value="friendly">😊 친근한 대화체</option>
                  <option value="professional">🎓 전문적이고 격조있는 체</option>
                  <option value="informative">📋 명료한 정보 요약체</option>
                </select>
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-bold text-slate-400">타겟 분량</label>
                <div className="grid grid-cols-3 gap-1.5">
                  <button
                    type="button"
                    onClick={() => setLength('short')}
                    disabled={loading}
                    className={`py-1.5 px-1 rounded-xl text-[9px] font-bold border transition-all ${length === 'short' ? 'bg-violet-600/20 border-violet-500 text-violet-300' : 'bg-slate-950/40 border-slate-800 text-slate-500'}`}
                  >
                    단문 (1,500자)
                  </button>
                  <button
                    type="button"
                    onClick={() => setLength('long')}
                    disabled={loading}
                    className={`py-1.5 px-1 rounded-xl text-[9px] font-bold border transition-all ${length === 'long' ? 'bg-violet-600/20 border-violet-500 text-violet-300' : 'bg-slate-950/40 border-slate-800 text-slate-500'}`}
                  >
                    장문 (3,000자)
                  </button>
                  <button
                    type="button"
                    onClick={() => setLength('extra-long')}
                    disabled={loading}
                    className={`py-1.5 px-1 rounded-xl text-[9px] font-bold border transition-all ${length === 'extra-long' ? 'bg-violet-600/20 border-violet-500 text-violet-300' : 'bg-slate-950/40 border-slate-800 text-slate-500'}`}
                  >
                    초장문 (5,000자)
                  </button>
                </div>
              </div>
            </div>

            {/* Platform Selector */}
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-bold text-slate-400">발행 대상 플랫폼</label>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { id: 'tistory', name: '티스토리' },
                  { id: 'blogspot', name: '블로그스팟' },
                  { id: 'wordpress', name: '워드프레스' }
                ].map(p => (
                  <button
                    key={p.id}
                    type="button"
                    onClick={() => setPlatform(p.id)}
                    disabled={loading}
                    className={`py-2 rounded-xl text-[11px] font-bold border transition-all ${platform === p.id ? 'bg-indigo-600/20 border-indigo-500 text-indigo-300' : 'bg-slate-950/40 border-slate-800 text-slate-500'}`}
                  >
                    {p.name}
                  </button>
                ))}
              </div>
            </div>

            {/* Error Message Display */}
            {error && (
              <div className="p-3.5 rounded-xl bg-rose-950/20 border border-rose-500/20 flex gap-2 text-rose-300 text-xs items-start">
                <AlertTriangle size={14} className="shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold">발생된 오류: </span>
                  {error}
                </div>
              </div>
            )}

            {/* Generate Trigger Button */}
            <button
              type="submit"
              disabled={loading || !keyword.trim() || credits <= 0}
              className="w-full py-3.5 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-bold text-sm shadow-xl hover:shadow-violet-600/10 transition-all transform hover:scale-[1.01] active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none"
            >
              {loading ? '원고 집필 가동 중...' : '원고 자동 생성 시작'}
            </button>
          </form>
        </section>

        {/* Loading & Progress Display Card */}
        {loading && (
          <section className="glass-card rounded-2xl p-5 border border-slate-800/80 flex flex-col gap-3 shadow-lg">
            <div className="flex justify-between items-center text-xs">
              <span className="font-bold text-violet-400">무인 집필 자동화 가동 중</span>
              <span className="text-[10px] text-slate-500">{progressStep + 1} / {steps.length} 단계</span>
            </div>
            
            {/* Progress Bar Display */}
            <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden border border-slate-800">
              <div 
                className="bg-gradient-to-r from-violet-500 to-indigo-500 h-1.5 rounded-full transition-all duration-500"
                style={{ width: `${((progressStep + 1) / steps.length) * 100}%` }}
              />
            </div>
            
            <div className="text-[11px] text-slate-300 font-medium animate-pulse">
              ⚙️ {steps[progressStep]}
            </div>
          </section>
        )}

        {/* Tags & Summary (Placed below Form) */}
        <section className="glass-card rounded-3xl p-5 border border-slate-800/80 shadow-lg flex flex-col gap-4">
          <h3 className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
            <Hash size={14} className="text-violet-400" />
            추천 태그 & SEO 요약 정보
          </h3>

          {result ? (
            <div className="flex flex-col gap-4">
              <div className="flex flex-col gap-1.5">
                <span className="text-[10px] text-slate-500 font-bold">추천 해시태그</span>
                <div className="flex flex-wrap gap-1.5">
                  {result.tags.map((tag, i) => (
                    <span 
                      key={i} 
                      className="px-2 py-1 bg-slate-900 text-slate-300 border border-slate-800 rounded-lg text-[10px] font-bold"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex flex-col gap-1.5 border-t border-slate-900 pt-3">
                <span className="text-[10px] text-slate-500 font-bold">SEO 요약 정보 (메타 설명)</span>
                <p className="text-slate-400 leading-normal text-[11px]">
                  {result.title}에 대해 비전공자 관점에서 핵심 행동 지침과 실전 전략을 정리한 글입니다. 플랫폼에 맞춰 구조적으로 포맷팅되어 바로 활용할 수 있습니다.
                </p>
              </div>
            </div>
          ) : (
            <div className="text-[11px] text-slate-500 italic py-4 text-center">
              원고가 작성되면 해시태그와 검색엔진용 메타 요약 정보가 여기에 표시됩니다.
            </div>
          )}
        </section>
      </div>

      {/* 2열: HTML 작성 코드 */}
      <section className="glass-card rounded-3xl p-5 border border-slate-800/80 shadow-2xl flex flex-col gap-4 lg:h-[720px]">
        <div className="flex justify-between items-center shrink-0">
          <div>
            <span className="text-[10px] text-violet-400 font-bold uppercase tracking-wider">2열: HTML 코드 출력</span>
            <h3 className="text-xs font-bold text-slate-300 leading-snug">HTML 코드 원본</h3>
          </div>
          
          {result && (
            <button
              onClick={handleCopy}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all shadow-md ${copied ? 'bg-emerald-600 text-white' : 'bg-slate-800 text-slate-200 hover:bg-slate-700 hover:scale-105 active:scale-95'}`}
            >
              {copied ? <Check size={12} /> : <Copy size={12} />}
              {copied ? '복사 완료!' : 'HTML 복사'}
            </button>
          )}
        </div>

        <div className="flex-1 bg-slate-950/80 border border-slate-800 rounded-2xl p-4 overflow-y-auto text-slate-300 text-xs leading-relaxed font-mono select-all cursor-text flex items-stretch min-h-[300px]">
          {result ? (
            <pre className="w-full h-full text-[10px] text-slate-400 whitespace-pre-wrap select-all cursor-text">
              {result.html_content}
            </pre>
          ) : (
            <div className="flex flex-col items-center justify-center w-full text-slate-600 gap-2">
              <PenTool size={32} className="opacity-20" />
              <p className="text-[11px] text-center italic">
                원고 집필 가동 시 이곳에<br />순화 처리된 HTML 코드가 표시됩니다.
              </p>
            </div>
          )}
        </div>
      </section>

      {/* 3열: 글 보기 (실시간 프리뷰) */}
      <section className="glass-card rounded-3xl p-5 border border-slate-800/80 shadow-2xl flex flex-col gap-4 lg:h-[720px]">
        <div className="flex justify-between items-center shrink-0">
          <div>
            <span className="text-[10px] text-emerald-400 font-bold uppercase tracking-wider">3열: 글 보기</span>
            <h3 className="text-xs font-bold text-slate-300 leading-snug">실시간 미리보기</h3>
          </div>
          {result && (
            <span className="text-[9px] bg-emerald-950/40 text-emerald-400 border border-emerald-900/50 px-2 py-0.5 rounded-full font-bold">
              {result.demo ? "데모 생성" : "실시간 생성"}
            </span>
          )}
        </div>

        <div className="flex-1 bg-slate-950/80 border border-slate-800 rounded-2xl p-5 overflow-y-auto text-slate-300 text-xs leading-relaxed flex flex-col min-h-[300px]">
          {result ? (
            <div 
              ref={previewRef}
              className="prose prose-invert prose-xs max-w-none text-slate-300"
              dangerouslySetInnerHTML={{ __html: result.html_content }}
            />
          ) : (
            <div className="flex flex-col items-center justify-center w-full h-full flex-1 text-slate-600 gap-2">
              <ExternalLink size={32} className="opacity-20" />
              <p className="text-[11px] text-center italic">
                원고 집필 가동 시 이곳에<br />실시간 글 미리보기가 렌더링됩니다.
              </p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

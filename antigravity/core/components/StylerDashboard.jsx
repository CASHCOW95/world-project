import React, { useState, useEffect } from 'react';
import { PenTool, Cpu } from 'lucide-react';
import OriginalStylerDashboard from './OriginalStylerDashboard';
import V2AgentDashboard from './V2AgentDashboard';
import './StylerDashboard.css';

export default function StylerDashboard() {
  const [dashboardMode, setDashboardMode] = useState('styler'); // styler or agent

  useEffect(() => {
    document.documentElement.dataset.theme = 'dark';
    localStorage.setItem('styler_theme_mode', 'dark');
  }, []);

  useEffect(() => {
    if (window.__stylerLogLevelNormalizerReady || !window.fetch) return;
    window.__stylerLogLevelNormalizerReady = true;

    const normalizeLogText = (text) => String(text)
      .replaceAll('⚠️ [에러] [ClusterEngine] Gemini 미사용 → fallback 클러스터 생성', 'ℹ️ [정보] [ClusterEngine] Gemini 미사용 → fallback 클러스터 생성')
      .replaceAll('[에러] [ClusterEngine] Gemini 미사용 → fallback 클러스터 생성', '[정보] [ClusterEngine] Gemini 미사용 → fallback 클러스터 생성')
      .replaceAll('⚠️ [에러] [TelegramBot] 토큰 또는 chat_id 미설정. 알림 스킵.', 'ℹ️ [정보] [TelegramBot] 토큰 또는 chat_id 미설정. 알림 스킵.')
      .replaceAll('[에러] [TelegramBot] 토큰 또는 chat_id 미설정. 알림 스킵.', '[정보] [TelegramBot] 토큰 또는 chat_id 미설정. 알림 스킵.')
      .replaceAll('⚠️ [에러] [ResearchEngine] RSS 파싱 실패', 'ℹ️ [정보] [ResearchEngine] 외부 RSS 스킵')
      .replaceAll('[에러] [ResearchEngine] RSS 파싱 실패', '[정보] [ResearchEngine] 외부 RSS 스킵')
      .replaceAll('HTTP Error 404: Not Found', 'RSS 주소 응답 없음')
      .replaceAll('mismatched tag:', 'RSS XML 형식 오류:');

    const originalFetch = window.fetch.bind(window);
    window.fetch = async (input, init) => {
      const response = await originalFetch(input, init);
      const rawUrl = typeof input === 'string' ? input : input?.url || '';
      const isPipelineStream = rawUrl.includes('/api/cluster-publish') || rawUrl.includes('/api/publish-pipeline');
      if (!isPipelineStream || !response.body) return response;

      const decoder = new TextDecoder();
      const encoder = new TextEncoder();
      const stream = response.body.pipeThrough(new TransformStream({
        transform(chunk, controller) {
          controller.enqueue(encoder.encode(normalizeLogText(decoder.decode(chunk, { stream: true }))));
        }
      }));

      return new Response(stream, {
        status: response.status,
        statusText: response.statusText,
        headers: response.headers
      });
    };
  }, []);

  return (
    <div className="flex flex-col gap-4 w-full">
      {/* 모드 세그먼트 스위처 */}
      <div className="flex bg-slate-900/60 p-1.5 rounded-2xl border border-slate-800/80 gap-1.5 max-w-sm w-full mx-auto relative z-30 mb-2 shadow-inner">
        <button
          onClick={() => setDashboardMode('styler')}
          className={`flex-1 py-2.5 rounded-xl text-xs font-black transition-all flex items-center justify-center gap-1.5 ${dashboardMode === 'styler' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20' : 'text-slate-400 hover:text-slate-200'}`}
        >
          <PenTool size={13} /> ✍️ 원고 자동 집필기
        </button>
        <button
          onClick={() => setDashboardMode('agent')}
          className={`flex-1 py-2.5 rounded-xl text-xs font-black transition-all flex items-center justify-center gap-1.5 ${dashboardMode === 'agent' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20' : 'text-slate-400 hover:text-slate-200'}`}
        >
          <Cpu size={13} /> 🤖 에이전트 운영센터 (V2)
        </button>
      </div>

      {/* 대시보드 뷰 전환 */}
      <div className="w-full transition-all duration-300">
        {dashboardMode === 'styler' ? (
          <OriginalStylerDashboard />
        ) : (
          <V2AgentDashboard />
        )}
      </div>
    </div>
  );
}

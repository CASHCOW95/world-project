import React, { useState, useEffect, useRef } from 'react';
import { PenTool, Copy, Check, RotateCcw, AlertTriangle, ExternalLink, Hash, LayoutGrid, Search, Flame, TrendingUp, Cpu, Award, FileText, BadgeHelp, DollarSign, Users, MousePointer, ShieldAlert, Star, RefreshCw, Layers, Sparkles, Clock, Compass, Settings, Link2, StopCircle, CalendarClock } from 'lucide-react';

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
  "금융": 100,
  "정부정책": 90,
  "부동산": 80,
  "건강": 70,
  "생활": 60,
  "비즈니스": 50,
  "디지털": 40,
  "전문직": 30
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

const SUB_TO_JSON_KEY = {
  "정부지원금": "정부지원금",
  "복지": "복지정책",
  "연금": "연금",
  "세금": "세금",
  "환급금": "세금",
  "재테크": "재테크",
  "대출": "대출",
  "보험": "보험",
  "카드": "카드",
  "주식": "주식",
  "ETF": "ETF",
  "코인": "코인",
  "부동산": "부동산",
  "청약": "청약",
  "경매": "경매",
  "재개발": "부동산",
  "전세": "부동산",
  "월세": "부동산",
  "창업": "창업",
  "사업자": "사업자",
  "스마트스토어": "스마트스토어",
  "온라인쇼핑몰": "스마트스토어",
  "IT": "IT",
  "소프트웨어": "IT",
  "전자제품": "IT",
  "모바일": "IT",
  "인터넷서비스": "IT",
  "건강": "건강",
  "질병": "질병",
  "다이어트": "다이어트",
  "병원": "병원",
  "건강검진": "병원",
  "영양제": "건강",
  "자동차": "자동차",
  "전기차": "전기차",
  "여행": "여행",
  "생활정보": "생활꿀팁",
  "반려동물": "반려동물",
  "법률": "법률",
  "이혼/상속": "이혼",
  "취업/이직": "취업",
  "자격증": "자격증",
  "교육/육아": "육아"
};

const formatHistoryPlatform = (platform) => (platform || 'local').toString().toUpperCase();
const formatHistoryDate = (createdAt) => {
  const date = createdAt ? new Date(createdAt) : null;
  return date && !Number.isNaN(date.getTime()) ? date.toLocaleDateString() : '-';
};

const normalizeHistoryItem = (item = {}) => ({
  ...item,
  platform: item.platform || 'local',
  created_at: item.created_at || null,
  title: item.title || '제목 없음',
  seo_score: item.seo_score ?? 0,
  profit_score: item.profit_score ?? 0
});

function ThemeToggleButton({ themeMode, setThemeMode }) {
  return null;

  const isLight = themeMode === 'light';

  return (
    <button
      type="button"
      onClick={() => setThemeMode(isLight ? 'dark' : 'light')}
      className="fixed right-5 top-5 z-50 rounded-xl border border-white/10 bg-slate-950/80 px-3 py-2 text-[11px] font-black text-white shadow-xl backdrop-blur transition-all hover:bg-indigo-600"
      title="화면 테마 변경"
    >
      {isLight ? 'DARK' : 'LIGHT'}
    </button>
  );
}

function ThemeStyle() {
  return (
    <style>{`
      :root {
        --upbit-blue: #0062df;
        --upbit-blue-dark: #003f9e;
        --upbit-blue-soft: #eaf3ff;
        --upbit-red: #e93147;
        --upbit-red-soft: #fff1f3;
        --upbit-text: #071f4a;
        --upbit-muted: #557099;
        --upbit-line: #cfe0f5;
        --upbit-page: #f3f7fc;
        --upbit-card: #ffffff;
      }

      body,
      button,
      input,
      select,
      textarea {
        font-family: 'Pretendard Variable', 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif !important;
        font-size: 14px !important;
        letter-spacing: 0 !important;
      }

      [class*="text-[9px]"] { font-size: 10px !important; }
      [class*="text-[10px]"] { font-size: 11px !important; }
      [class*="text-[11px]"] { font-size: 12px !important; }
      [class*="text-xs"] { font-size: 13px !important; }
      [class*="text-sm"] { font-size: 15px !important; }
      [class*="text-base"] { font-size: 17px !important; }

      html[data-theme="light"] body {
        background: linear-gradient(135deg, #ffffff 0%, var(--upbit-page) 52%, #e7f1ff 100%);
        color: var(--upbit-text);
        font-family: 'Pretendard Variable', 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
        font-size: 14px;
      }

      body,
      button,
      input,
      select,
      textarea,
      p,
      span,
      div,
      label,
      li,
      td,
      th {
        font-family: 'Pretendard Variable', 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif !important;
        letter-spacing: 0 !important;
      }

      body {
        font-size: 14px !important;
      }

      .styler-main-expanded {
        grid-column: 1 / -1 !important;
        width: 100% !important;
        max-width: none !important;
      }

      .styler-assistant-banner-hidden {
        display: none !important;
      }

      html[data-theme="light"] * {
        letter-spacing: 0 !important;
        font-family: 'Pretendard Variable', 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif !important;
      }

      html[data-theme="light"] .min-h-screen {
        background: linear-gradient(135deg, #ffffff 0%, var(--upbit-page) 52%, #e7f1ff 100%) !important;
      }

      html[data-theme="light"] [class*="bg-slate-950"],
      html[data-theme="light"] [class*="bg-slate-900"],
      html[data-theme="light"] [class*="bg-gray-900"],
      html[data-theme="light"] [class*="from-slate"],
      html[data-theme="light"] [class*="to-slate"],
      html[data-theme="light"] [class*="from-gray"],
      html[data-theme="light"] [class*="to-gray"] {
        background: var(--upbit-card) !important;
        background-color: var(--upbit-card) !important;
        color: var(--upbit-text) !important;
      }

      html[data-theme="light"] .bg-slate-950,
      html[data-theme="light"] .bg-slate-950\\/40,
      html[data-theme="light"] .bg-slate-950\\/50,
      html[data-theme="light"] .bg-slate-950\\/60,
      html[data-theme="light"] .bg-slate-950\\/80,
      html[data-theme="light"] .bg-slate-900,
      html[data-theme="light"] .bg-slate-900\\/30,
      html[data-theme="light"] .bg-slate-900\\/40,
      html[data-theme="light"] .bg-slate-900\\/50,
      html[data-theme="light"] .bg-slate-900\\/70,
      html[data-theme="light"] .bg-slate-900\\/80 {
        background-color: #ffffff !important;
      }

      html[data-theme="light"] [class*="bg-indigo-"],
      html[data-theme="light"] [class*="bg-violet-"],
      html[data-theme="light"] [class*="bg-purple-"],
      html[data-theme="light"] [class*="bg-blue-"],
      html[data-theme="light"] [class*="bg-cyan-"],
      html[data-theme="light"] [class*="bg-emerald-"],
      html[data-theme="light"] [class*="bg-teal-"],
      html[data-theme="light"] [class*="bg-rose-"],
      html[data-theme="light"] [class*="bg-red-"],
      html[data-theme="light"] [class*="bg-orange-"],
      html[data-theme="light"] [class*="bg-slate-700"],
      html[data-theme="light"] [class*="bg-slate-800"],
      html[data-theme="light"] [class*="bg-gray-600"],
      html[data-theme="light"] [class*="bg-gray-700"],
      html[data-theme="light"] [class*="bg-gray-800"] {
        background-color: #d0e3fb !important;
        color: #071f4a !important;
      }

      html[data-theme="light"] [class*="bg-indigo-"] *,
      html[data-theme="light"] [class*="bg-violet-"] *,
      html[data-theme="light"] [class*="bg-purple-"] *,
      html[data-theme="light"] [class*="bg-blue-"] *,
      html[data-theme="light"] [class*="bg-cyan-"] *,
      html[data-theme="light"] [class*="bg-emerald-"] *,
      html[data-theme="light"] [class*="bg-teal-"] *,
      html[data-theme="light"] [class*="bg-rose-"] *,
      html[data-theme="light"] [class*="bg-red-"] *,
      html[data-theme="light"] [class*="bg-orange-"] *,
      html[data-theme="light"] [class*="bg-slate-700"] *,
      html[data-theme="light"] [class*="bg-slate-800"] *,
      html[data-theme="light"] [class*="bg-gray-600"] *,
      html[data-theme="light"] [class*="bg-gray-700"] *,
      html[data-theme="light"] [class*="bg-gray-800"] * {
        color: #ffffff !important;
      }

      html[data-theme="light"] .text-white,
      html[data-theme="light"] .text-slate-50,
      html[data-theme="light"] .text-slate-100,
      html[data-theme="light"] .text-slate-200,
      html[data-theme="light"] .text-slate-300,
      html[data-theme="light"] h1,
      html[data-theme="light"] h2,
      html[data-theme="light"] h3,
      html[data-theme="light"] h4 {
        color: #071f4a !important;
        font-weight: 700 !important;
      }

      html[data-theme="light"] .text-slate-400,
      html[data-theme="light"] .text-slate-500,
      html[data-theme="light"] .text-slate-600 {
        color: #5c6f8f !important;
      }

      html[data-theme="light"] [class*="text-indigo-"],
      html[data-theme="light"] [class*="text-violet-"],
      html[data-theme="light"] [class*="text-purple-"],
      html[data-theme="light"] [class*="text-blue-"] {
        color: #0062df !important;
      }

      html[data-theme="light"] [class*="text-emerald-"] {
        color: #00a66a !important;
      }

      html[data-theme="light"] [class*="text-rose-"],
      html[data-theme="light"] [class*="text-red-"] {
        color: #e93147 !important;
      }

      html[data-theme="light"] .border-slate-900,
      html[data-theme="light"] .border-slate-850,
      html[data-theme="light"] .border-slate-800,
      html[data-theme="light"] .border-white\\/5,
      html[data-theme="light"] .border-white\\/10 {
        border-color: #d7dfeb !important;
      }

      html[data-theme="light"] [class*="rounded-3xl"] {
        border-radius: 10px !important;
      }

      html[data-theme="light"] [class*="rounded-2xl"] {
        border-radius: 8px !important;
      }

      html[data-theme="light"] .shadow-2xl,
      html[data-theme="light"] .shadow-xl,
      html[data-theme="light"] .shadow-lg {
        box-shadow: none !important;
      }

      html[data-theme="light"] h1 {
        font-size: 22px !important;
        line-height: 1.25 !important;
      }

      html[data-theme="light"] button,
      html[data-theme="light"] input,
      html[data-theme="light"] select,
      html[data-theme="light"] textarea,
      html[data-theme="light"] p,
      html[data-theme="light"] span,
      html[data-theme="light"] div,
      html[data-theme="light"] label,
      html[data-theme="light"] li,
      html[data-theme="light"] td,
      html[data-theme="light"] th {
        font-family: inherit !important;
      }

      html[data-theme="light"] [class*="text-[9px]"] { font-size: 10px !important; }
      html[data-theme="light"] [class*="text-[10px]"] { font-size: 11px !important; }
      html[data-theme="light"] [class*="text-[11px]"] { font-size: 12px !important; }
      html[data-theme="light"] [class*="text-xs"] { font-size: 13px !important; }
      html[data-theme="light"] [class*="text-sm"] { font-size: 15px !important; }
      html[data-theme="light"] [class*="text-base"] { font-size: 17px !important; }

      html[data-theme="light"] button,
      html[data-theme="light"] input,
      html[data-theme="light"] select,
      html[data-theme="light"] textarea {
        font-family: inherit !important;
        font-size: 13px !important;
      }

      html[data-theme="light"] input,
      html[data-theme="light"] select,
      html[data-theme="light"] textarea {
        background-color: #ffffff !important;
        color: #172b4d !important;
        border-color: #cfd8e6 !important;
      }

      html[data-theme="light"] ::placeholder {
        color: #8a9ab3 !important;
      }

      .history-panel-modalized {
        display: none !important;
        position: fixed !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        z-index: 100001 !important;
        width: min(440px, 92vw) !important;
        max-height: 86vh !important;
        min-height: 0 !important;
        overflow: hidden !important;
        background: #ffffff !important;
        border: 1px solid #d7dfeb !important;
        border-radius: 12px !important;
        box-shadow: 0 24px 70px rgba(15, 23, 42, 0.22) !important;
      }

      body.history-modal-open .history-panel-modalized {
        display: flex !important;
      }

      #history-modal-screen {
        position: fixed;
        inset: 0;
        z-index: 100000;
        display: none;
        background: rgba(15, 23, 42, 0.42);
      }

      body.history-modal-open #history-modal-screen {
        display: block;
      }

      #history-drawer-button {
        position: fixed;
        right: 82px;
        top: 20px;
        z-index: 99999;
        border: 1px solid #cfd8e6;
        border-radius: 12px;
        background: #ffffff;
        color: #071f4a;
        padding: 9px 13px;
        font-size: 13px;
        font-weight: 500 !important;
        box-shadow: 0 8px 26px rgba(15, 23, 42, 0.10);
        cursor: pointer;
      }

      #history-modal-backdrop {
        position: fixed;
        inset: 0;
        z-index: 100000;
        display: none;
        align-items: center;
        justify-content: center;
        background: rgba(15, 23, 42, 0.42);
        padding: 24px;
      }

      #history-modal-backdrop.is-open {
        display: flex;
      }

      #history-modal {
        width: min(440px, 92vw);
        max-height: 86vh;
        overflow: hidden;
        border: 1px solid #d7dfeb;
        border-radius: 12px;
        background: #ffffff;
        color: #071f4a;
        box-shadow: 0 24px 70px rgba(15, 23, 42, 0.22);
      }

      #history-modal-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid #d7dfeb;
        padding: 14px 16px;
        font-size: 15px;
        font-weight: 600 !important;
      }

      #history-modal-close {
        border: 1px solid #d7dfeb;
        border-radius: 8px;
        background: #f8fafc;
        color: #071f4a;
        width: 32px;
        height: 32px;
        cursor: pointer;
      }

      #history-modal-content {
        max-height: calc(86vh - 62px);
        overflow-y: auto;
        padding: 14px;
      }

      #history-modal-content > * {
        width: 100% !important;
        max-width: none !important;
        min-height: 0 !important;
        height: auto !important;
        box-shadow: none !important;
      }

      html[data-theme="light"] [class*="bg-slate-950"],
      html[data-theme="light"] [class*="bg-slate-900"],
      html[data-theme="light"] [class*="bg-slate-800"],
      html[data-theme="light"] [class*="bg-slate-700"],
      html[data-theme="light"] [class*="bg-gray-900"],
      html[data-theme="light"] [class*="bg-gray-800"],
      html[data-theme="light"] [class*="bg-gray-700"],
      html[data-theme="light"] [class*="bg-gray-600"],
      html[data-theme="light"] [class*="from-slate"],
      html[data-theme="light"] [class*="to-slate"],
      html[data-theme="light"] [class*="from-gray"],
      html[data-theme="light"] [class*="to-gray"] {
        background: var(--upbit-card) !important;
        background-color: var(--upbit-card) !important;
        color: var(--upbit-text) !important;
      }

      html[data-theme="light"] [class*="bg-indigo-"],
      html[data-theme="light"] [class*="bg-blue-"],
      html[data-theme="light"] [class*="bg-violet-"],
      html[data-theme="light"] [class*="bg-purple-"] {
        background: var(--upbit-blue) !important;
        background-color: var(--upbit-blue) !important;
        color: #ffffff !important;
      }

      html[data-theme="light"] [class*="bg-indigo-"] *,
      html[data-theme="light"] [class*="bg-blue-"] *,
      html[data-theme="light"] [class*="bg-violet-"] *,
      html[data-theme="light"] [class*="bg-purple-"] * {
        color: #ffffff !important;
      }

      html[data-theme="light"] [class*="bg-rose-"],
      html[data-theme="light"] [class*="bg-red-"] {
        background: var(--upbit-red) !important;
        background-color: var(--upbit-red) !important;
        color: #ffffff !important;
      }

      html[data-theme="light"] [class*="text-indigo-"],
      html[data-theme="light"] [class*="text-blue-"],
      html[data-theme="light"] [class*="text-violet-"],
      html[data-theme="light"] [class*="text-purple-"] {
        color: var(--upbit-blue) !important;
      }

      html[data-theme="light"] [class*="text-rose-"],
      html[data-theme="light"] [class*="text-red-"] {
        color: var(--upbit-red) !important;
      }

      html[data-theme="light"] [class*="text-slate-"],
      html[data-theme="light"] [class*="text-gray-"] {
        color: var(--upbit-muted) !important;
      }

      html[data-theme="light"] h1,
      html[data-theme="light"] h2,
      html[data-theme="light"] h3,
      html[data-theme="light"] h4,
      html[data-theme="light"] .font-black,
      html[data-theme="light"] .font-bold {
        color: var(--upbit-text) !important;
      }

      html[data-theme="light"] [class*="border-slate-"],
      html[data-theme="light"] [class*="border-gray-"],
      html[data-theme="light"] [class*="border-white"] {
        border-color: var(--upbit-line) !important;
      }

      html[data-theme="light"] input,
      html[data-theme="light"] select,
      html[data-theme="light"] textarea {
        background: #ffffff !important;
        color: var(--upbit-text) !important;
        border-color: var(--upbit-line) !important;
      }

      html[data-theme="light"] [class*="shadow-"] {
        box-shadow: 0 8px 24px rgba(0, 98, 223, 0.08) !important;
      }

      html[data-theme="light"] .upbit-force-panel {
        background: #eaf3ff !important;
        background-color: #eaf3ff !important;
        background-image: none !important;
        color: #071f4a !important;
        border-color: #9fc7ff !important;
      }

      html[data-theme="light"] .upbit-force-card {
        background: #ffffff !important;
        background-color: #ffffff !important;
        background-image: none !important;
        color: #071f4a !important;
        border-color: #cfe0f5 !important;
      }

      html[data-theme="light"] .upbit-force-blue {
        background: #d0e3fb !important;
        background-color: #d0e3fb !important;
        background-image: none !important;
        color: #071f4a !important;
      }

      html[data-theme="light"] .upbit-force-blue * {
        color: #071f4a !important;
      }

      html[data-theme="light"] body,
      html[data-theme="light"] .min-h-screen {
        background: #F8FAFC !important;
        color: #0F172A !important;
      }

      .saas-section {
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        background-image: none !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        box-shadow: none !important;
        color: #0F172A !important;
      }

      .saas-keyword-card {
        background: #FFFFFF !important;
        background-image: none !important;
        border: 1px solid #E2E8F0 !important;
        border-left: 4px solid #2563EB !important;
        border-radius: 8px !important;
        color: #0F172A !important;
        min-height: 0 !important;
        padding: 14px 16px !important;
        box-shadow: none !important;
      }

      .saas-keyword-card *,
      .saas-title-card * {
        color: #0F172A !important;
      }

      .saas-title-card {
        background: #FFFFFF !important;
        background-image: none !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        color: #0F172A !important;
        padding: 13px 14px !important;
        box-shadow: none !important;
      }

      .saas-pill-selected {
        background: #2563EB !important;
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        border-color: #2563EB !important;
      }

      .saas-pill-muted {
        background: #FFFFFF !important;
        color: #64748B !important;
        border: 1px solid #E2E8F0 !important;
      }

      .saas-scroll-open {
        max-height: none !important;
        height: auto !important;
        overflow: visible !important;
      }

      .saas-hidden-extra {
        display: revert !important;
      }

      .saas-settings-collapsed {
        max-height: 64px !important;
        overflow: hidden !important;
        cursor: pointer;
      }

      .saas-settings-expanded {
        max-height: none !important;
        overflow: visible !important;
      }

      html[data-theme="light"] [class*="text-[9px]"] { font-size: 9px !important; }
      html[data-theme="light"] [class*="text-[10px]"] { font-size: 10px !important; }
      html[data-theme="light"] [class*="text-[11px]"] { font-size: 11px !important; }
      html[data-theme="light"] [class*="text-xs"] { font-size: 0.75rem !important; }
      html[data-theme="light"] [class*="text-sm"] { font-size: 0.875rem !important; }
      html[data-theme="light"] [class*="text-base"] { font-size: 1rem !important; }
      html[data-theme="light"] [class*="text-lg"] { font-size: 1.125rem !important; }
      html[data-theme="light"] [class*="text-xl"] { font-size: 1.25rem !important; }
      html[data-theme="light"] [class*="text-2xl"] { font-size: 1.5rem !important; }
      html[data-theme="light"] [class*="text-3xl"] { font-size: 1.875rem !important; }

      html[data-theme="light"] .font-normal { font-weight: 400 !important; }
      html[data-theme="light"] .font-medium { font-weight: 500 !important; }
      html[data-theme="light"] .font-semibold { font-weight: 600 !important; }
      html[data-theme="light"] .font-bold { font-weight: 700 !important; }
      html[data-theme="light"] .font-extrabold { font-weight: 800 !important; }
      html[data-theme="light"] .font-black { font-weight: 900 !important; }

      html[data-theme="light"] [class*="bg-slate-950"],
      html[data-theme="light"] [class*="bg-slate-900"],
      html[data-theme="light"] [class*="bg-slate-800"],
      html[data-theme="light"] [class*="bg-slate-700"],
      html[data-theme="light"] [class*="bg-gray-950"],
      html[data-theme="light"] [class*="bg-gray-900"],
      html[data-theme="light"] [class*="bg-gray-800"],
      html[data-theme="light"] [class*="bg-gray-700"],
      html[data-theme="light"] [class*="from-slate"],
      html[data-theme="light"] [class*="to-slate"],
      html[data-theme="light"] [class*="from-gray"],
      html[data-theme="light"] [class*="to-gray"] {
        background: #d0e3fb !important;
        background-color: #d0e3fb !important;
        background-image: none !important;
        color: #0f172a !important;
      }

      html[data-theme="light"] .styler-light-panel-frame {
        background: #d0e3fb !important;
        background-color: #d0e3fb !important;
        background-image: none !important;
        border-color: #9fc4f3 !important;
        color: #0f172a !important;
      }

      .lg\\:col-span-2 {
        display: none !important;
      }

      @media (min-width: 1024px) {
        .lg\\:col-span-10 {
          grid-column: span 12 / span 12 !important;
        }
      }

      html,
      body,
      html[data-theme="light"] body,
      html[data-theme="light"] .min-h-screen {
        background: #ffffff !important;
        background-color: #ffffff !important;
        background-image: none !important;
      }

      html[data-theme="light"] .styler-final-gray-frame {
        background: #d0e3fb !important;
        background-color: #d0e3fb !important;
        background-image: none !important;
        border-color: #9fc4f3 !important;
      }

      html[data-theme="light"] [class*="bg-slate-"],
      html[data-theme="light"] [class*="from-slate"],
      html[data-theme="light"] [class*="to-slate"],
      html[data-theme="light"] [class*="via-slate"],
      html[data-theme="light"] [class*="bg-gray-"],
      html[data-theme="light"] [class*="from-gray"],
      html[data-theme="light"] [class*="to-gray"],
      html[data-theme="light"] [class*="via-gray"] {
        background: #d0e3fb !important;
        background-color: #d0e3fb !important;
        background-image: none !important;
        border-color: #9fc4f3 !important;
      }

      html[data-theme="light"] body,
      html[data-theme="light"] .min-h-screen {
        background: #ffffff !important;
        background-color: #ffffff !important;
        background-image: none !important;
      }

      html[data-theme="light"],
      html[data-theme="light"] body,
      html[data-theme="light"] .min-h-screen {
        background: #ffffff !important;
        background-color: #ffffff !important;
        background-image: none !important;
      }

      [class*="text-[9px]"] { font-size: 9px !important; }
      [class*="text-[10px]"] { font-size: 10px !important; }
      [class*="text-[11px]"] { font-size: 11px !important; }
      [class*="text-xs"] { font-size: 0.75rem !important; }
      [class*="text-sm"] { font-size: 0.875rem !important; }
      [class*="text-base"] { font-size: 1rem !important; }
      [class*="text-lg"] { font-size: 1.125rem !important; }
      [class*="text-xl"] { font-size: 1.25rem !important; }
      [class*="text-2xl"] { font-size: 1.5rem !important; }
      [class*="text-3xl"] { font-size: 1.875rem !important; }

      .font-normal { font-weight: 400 !important; }
      .font-medium { font-weight: 500 !important; }
      .font-semibold { font-weight: 600 !important; }
      .font-bold { font-weight: 700 !important; }
      .font-extrabold { font-weight: 800 !important; }
      .font-black { font-weight: 900 !important; }

      html[data-theme="light"] .force-light-gray-frame,
      html[data-theme="light"] [class*="bg-slate-"],
      html[data-theme="light"] [class*="bg-gray-"],
      html[data-theme="light"] [class*="from-slate"],
      html[data-theme="light"] [class*="to-slate"],
      html[data-theme="light"] [class*="via-slate"],
      html[data-theme="light"] [class*="from-gray"],
      html[data-theme="light"] [class*="to-gray"],
      html[data-theme="light"] [class*="via-gray"] {
        background: #d0e3fb !important;
        background-color: #d0e3fb !important;
        background-image: none !important;
        border-color: #9fc4f3 !important;
      }
    `}</style>
  );
}

function OriginalStylerDashboard() {
  // 40 Categories database state
  const [categories, setCategories] = useState({});
  const [mainCategory, setMainCategory] = useState('정부정책');
  const [subCategory, setSubCategory] = useState('정부지원금');
  const [currentCategory, setCurrentCategory] = useState('정부지원금');
  const [keywordLoading, setKeywordLoading] = useState(false);
  const [keywords, setKeywords] = useState([]);
  const [selectedKeyword, setSelectedKeyword] = useState(null);
  const [keywordSearch, setKeywordSearch] = useState('');
  const [showAllKeywords, setShowAllKeywords] = useState(false);

  const [keywordSortType, setKeywordSortType] = useState('recommend'); // recommend, latest, volume, cpc
  const [customTitle, setCustomTitle] = useState('');
  const [showHistoryDrawer, setShowHistoryDrawer] = useState(false);
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
  const [showAllTitles, setShowAllTitles] = useState(false);
  const [favoriteTitles, setFavoriteTitles] = useState([]);

  // Publisher configurations
  const [style, setStyle] = useState('friendly');
  const [platform, setPlatform] = useState('tistory');
  const [ctaStyle, setCtaStyle] = useState('card');
  const [articleLength, setArticleLength] = useState('5000');
  const [customLength, setCustomLength] = useState('');
  const [faqCount, setFaqCount] = useState('10');
  const [generateImgPrompt, setGenerateImgPrompt] = useState('OFF');
  const [seoStrength, setSeoStrength] = useState('strong'); // normal, strong, extreme
  const [publisherConfig, setPublisherConfig] = useState({ global: { gemini_api_key: '' }, profiles: [] });
  const [selectedProfileId, setSelectedProfileId] = useState(localStorage.getItem('styler_selectedProfileId_v3') || '');
  const [profileForm, setProfileForm] = useState(null);

  // Pipeline execution state
  const [pipelineRunning, setPipelineRunning] = useState(false);
  const [logs, setLogs] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);
  const [terminalStep, setTerminalStep] = useState('');
  const [promptCopied, setPromptCopied] = useState({});

  // History state
  const [history, setHistory] = useState([]);
  const [selectedHistoryItem, setSelectedHistoryItem] = useState(null);

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

  useEffect(() => {
    const loadPublisherProfiles = async () => {
      try {
        const res = await fetch('/api/publisher-profiles');
        const data = await res.json();
        setPublisherConfig(data);
        const profilesForPlatform = (data.profiles || []).filter(p => p.platform === platform && p.enabled !== false);
        const savedProfile = profilesForPlatform.find(p => p.id === selectedProfileId);
        const nextProfile = savedProfile || profilesForPlatform[0] || null;
        if (nextProfile) {
          setSelectedProfileId(nextProfile.id);
          setProfileForm(nextProfile);
        }
      } catch (err) {
        console.error('Failed to load publisher profiles:', err);
      }
    };
    loadPublisherProfiles();
  }, []);

  useEffect(() => {
    const profilesForPlatform = (publisherConfig.profiles || []).filter(p => p.platform === platform && p.enabled !== false);
    if (!profilesForPlatform.length) {
      setSelectedProfileId('');
      setProfileForm(null);
      return;
    }
    const current = profilesForPlatform.find(p => p.id === selectedProfileId) || profilesForPlatform[0];
    setSelectedProfileId(current.id);
    setProfileForm(current);
  }, [platform, publisherConfig.profiles]);

  useEffect(() => {
    if (selectedProfileId) {
      localStorage.setItem('styler_selectedProfileId_v3', selectedProfileId);
    }
  }, [selectedProfileId]);

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
    loadCategories();
    fetchHistory();
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

  // Reload keywords on category changes
  useEffect(() => {
    if (subCategory) {
      setCurrentCategory(subCategory);
      fetchKeywords(subCategory);
      setSelectedKeyword(null);
      setTitles([]);
      setSelectedTitle(null);
      setResult(null);
    }
  }, [subCategory]);

  useEffect(() => {
    if (terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  const fetchKeywords = async (catName) => {
    setKeywordLoading(true);
    try {
      const res = await fetch(`/api/keywords?category=${encodeURIComponent(catName)}`);
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
        const scored = data.map((t, idx) => {
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
  };

  const fetchHistory = async () => {
    try {
      const res = await fetch('/api/history');
      const data = await res.json();
      setHistory(data);
    } catch (err) {
      console.error("Failed to fetch history:", err);
    }
  };

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

  const handleCopyPromptText = (text, type) => {
    if (!text) return;
    navigator.clipboard.writeText(text);
    setPromptCopied(prev => ({ ...prev, [type]: true }));
    setTimeout(() => {
      setPromptCopied(prev => ({ ...prev, [type]: false }));
    }, 2000);
  };

  const handleExportHTML = () => {
    window.open('/api/export-download', '_blank');
  };

  const toggleFavoriteTitle = (tObj, e) => {
    e.stopPropagation();
    if (favoriteTitles.some(item => item.title === tObj.title)) {
      setFavoriteTitles(prev => prev.filter(item => item.title !== tObj.title));
    } else {
      setFavoriteTitles(prev => [...prev, tObj]);
    }
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
                    setMainCategory(e.target.value);
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

function V2AgentDashboard() {
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
  const [terminalExpanded, setTerminalExpanded] = useState(false);

  const terminalEndRef = useRef(null);
  const abortControllerRef = useRef(null);

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
        const res = await fetch('/api/categories');
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
      const res = await fetch(`/api/keywords?category=${encodeURIComponent(catName)}`);
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
      const res = await fetch('/api/dashboard-stats');
      const data = await res.json();
      setDashboardStats(data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchPostsList = async () => {
    try {
      const res = await fetch('/api/published-posts');
      const data = await res.json();
      setPostsList(data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchLinksList = async () => {
    try {
      const res = await fetch('/api/internal-links');
      const data = await res.json();
      setLinksList(data);
    } catch (err) {
      console.error(err);
    }
  };

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



export default function StylerDashboard() {
  const [dashboardMode, setDashboardMode] = useState('styler'); // styler or agent
  const [themeMode, setThemeMode] = useState('dark');

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

  useEffect(() => {
    const hideAssistantBanner = () => {
      if (!document.body) return;
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      const hits = [];
      let textNode = walker.nextNode();
      while (textNode) {
        const text = textNode.nodeValue || '';
        if (text.includes('KODARI AI ASSISTANT') || text.includes('대표님, 키워드만 입력해 주십시오')) {
          hits.push(textNode.parentElement);
        }
        textNode = walker.nextNode();
      }

      hits.forEach((hit) => {
        let target = hit;
        let current = hit;
        for (let i = 0; i < 12 && current && current !== document.body; i += 1) {
          const rect = current.getBoundingClientRect();
          if (rect.top >= 0 && rect.top < 170 && rect.width > window.innerWidth * 0.45 && rect.height > 35 && rect.height < 150) {
            target = current;
          }
          current = current.parentElement;
        }
        target.style.setProperty('display', 'none', 'important');
        target.style.setProperty('height', '0', 'important');
        target.style.setProperty('margin', '0', 'important');
        target.style.setProperty('padding', '0', 'important');
        target.setAttribute('aria-hidden', 'true');
      });

      const seeds = Array.from(document.querySelectorAll('body *')).filter((node) => {
        const text = node.textContent || '';
        return text.includes('KODARI AI ASSISTANT') && text.includes('대표님');
      });

      seeds.forEach((seed) => {
        let target = seed;
        let current = seed;
        for (let i = 0; i < 10 && current && current !== document.body; i += 1) {
          const rect = current.getBoundingClientRect();
          if (rect.top >= 0 && rect.top < 190 && rect.width > 500 && rect.height >= 36 && rect.height < 170) {
            target = current;
          }
          current = current.parentElement;
        }
        target.classList.add('styler-assistant-banner-hidden');
        target.style.setProperty('display', 'none', 'important');
      });
    };

    const forceReadableLightTheme = () => {
      if (document.documentElement.dataset.theme !== 'light') return;

      const parseRgb = (value) => {
        const match = value.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
        return match ? match.slice(1, 4).map(Number) : null;
      };
      const isDarkGray = (rgb) => {
        if (!rgb) return false;
        const max = Math.max(...rgb);
        const min = Math.min(...rgb);
        return max >= 45 && max <= 115 && max - min <= 35;
      };

      document.body.style.setProperty('font-family', 'Arial, "Noto Sans KR", "Malgun Gothic", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif', 'important');
      document.body.style.setProperty('font-size', '14px', 'important');
      document.body.style.setProperty('color', '#071f4a', 'important');

      Array.from(document.querySelectorAll('body *')).forEach((el) => {
        const className = typeof el.className === 'string' ? el.className : '';
        const style = window.getComputedStyle(el);
        const rect = el.getBoundingClientRect();
        const bg = parseRgb(style.backgroundColor);
        const hasDarkClass = /bg-(slate|gray)-(600|700|800|900|950)|from-(slate|gray)|to-(slate|gray)/.test(className);
        const hasBlueClass = /bg-(blue|indigo|violet|purple)-/.test(className);
        const hasRedClass = /bg-(red|rose)-/.test(className);

        el.style.setProperty('font-family', 'Arial, "Noto Sans KR", "Malgun Gothic", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif', 'important');
        el.style.setProperty('letter-spacing', '0', 'important');

        if (hasBlueClass) {
          el.classList.add('upbit-force-blue');
          el.style.setProperty('background', '#d0e3fb', 'important');
          el.style.setProperty('background-color', '#d0e3fb', 'important');
          el.style.setProperty('background-image', 'none', 'important');
          el.style.setProperty('color', '#071f4a', 'important');
          return;
        }

        if (hasRedClass) {
          el.style.setProperty('background', '#e93147', 'important');
          el.style.setProperty('background-color', '#e93147', 'important');
          el.style.setProperty('background-image', 'none', 'important');
          el.style.setProperty('color', '#ffffff', 'important');
          return;
        }

        if (hasDarkClass || isDarkGray(bg)) {
          const isLargePanel = rect.width > 260 && rect.height > 90;
          el.classList.add(isLargePanel ? 'upbit-force-panel' : 'upbit-force-card');
          el.style.setProperty('background', '#d0e3fb', 'important');
          el.style.setProperty('background-color', '#d0e3fb', 'important');
          el.style.setProperty('background-image', 'none', 'important');
          el.style.setProperty('color', '#071f4a', 'important');
          el.style.setProperty('border-color', '#bdd5f1', 'important');
        }
      });
    };

    const applySaasReadability = () => {
      if (document.documentElement.dataset.theme !== 'light') return;

      const smallestPanel = (needle) => {
        const nodes = Array.from(document.querySelectorAll('div')).filter((node) => {
          const text = node.textContent || '';
          const rect = node.getBoundingClientRect();
          return text.includes(needle) && rect.width > 260 && rect.height > 80;
        });
        return nodes.sort((a, b) => {
          const ar = a.getBoundingClientRect();
          const br = b.getBoundingClientRect();
          return (ar.width * ar.height) - (br.width * br.height);
        })[0];
      };

      const styleSection = (panel) => {
        if (!panel) return;
        panel.classList.add('saas-section');
        panel.style.setProperty('background', '#FFFFFF', 'important');
        panel.style.setProperty('background-color', '#FFFFFF', 'important');
        panel.style.setProperty('background-image', 'none', 'important');
        panel.style.setProperty('border', '1px solid #E2E8F0', 'important');
        panel.style.setProperty('border-radius', '8px', 'important');
        panel.style.setProperty('box-shadow', 'none', 'important');
        panel.style.setProperty('color', '#0F172A', 'important');
      };

      const removeInternalScroll = (panel) => {
        if (!panel) return;
        panel.querySelectorAll('div').forEach((node) => {
          const style = window.getComputedStyle(node);
          if (style.overflowY === 'auto' || style.overflowY === 'scroll') {
            node.classList.add('saas-scroll-open');
          }
        });
      };

      const stylePills = (root) => {
        if (!root) return;
        Array.from(root.querySelectorAll('button, div, span')).forEach((node) => {
          const text = (node.textContent || '').trim();
          const rect = node.getBoundingClientRect();
          if (rect.width < 24 || rect.width > 160 || rect.height < 16 || rect.height > 42) return;
          if (!/^(전체|정보형|비교형|리스트형|후기형|충격형|실수방지형|전문가형|최신뉴스형|추천순|최신순|검색량순|CPC순)$/.test(text)) return;
          const selected = text === '전체' || text === '추천순';
          node.classList.add(selected ? 'saas-pill-selected' : 'saas-pill-muted');
          node.style.setProperty('border-radius', '999px', 'important');
          node.style.setProperty('padding', '6px 12px', 'important');
          node.style.setProperty('font-size', '12px', 'important');
          node.style.setProperty('font-weight', selected ? '800' : '700', 'important');
        });
      };

      const keywordPanel = smallestPanel('황금 키워드 분석');
      const titlePanel = smallestPanel('유입 극대화 제목');
      const analysisPanel = smallestPanel('AI 키워드 추천 이유 분석');
      const settingsPanel = smallestPanel('월드 개발 페이지 제어 설정');

      [keywordPanel, titlePanel].forEach((panel) => {
        styleSection(panel);
        removeInternalScroll(panel);
        stylePills(panel);
      });

      Array.from(keywordPanel?.querySelectorAll('div') || []).filter((node) => {
        const text = node.textContent || '';
        const rect = node.getBoundingClientRect();
        return /추천\s*\d+/.test(text) && text.includes('검색량') && text.includes('CPC') && rect.width > 260 && rect.height > 60;
      }).sort((a, b) => a.getBoundingClientRect().top - b.getBoundingClientRect().top).forEach((card, index) => {
        card.classList.add('saas-keyword-card');
        if (index >= 5) card.classList.add('saas-hidden-extra');
      });

      Array.from(titlePanel?.querySelectorAll('div') || []).filter((node) => {
        const text = node.textContent || '';
        const rect = node.getBoundingClientRect();
        return text.includes('CTR 예상') && text.includes('SEO') && rect.width > 260 && rect.height > 45;
      }).sort((a, b) => a.getBoundingClientRect().top - b.getBoundingClientRect().top).forEach((card, index) => {
        card.classList.add('saas-title-card');
        if (index >= 5) card.classList.add('saas-hidden-extra');
      });

      styleSection(analysisPanel);
      if (analysisPanel) analysisPanel.style.setProperty('border-left', '4px solid #2563EB', 'important');

      if (settingsPanel && settingsPanel.dataset.saasCollapseReady !== '1') {
        settingsPanel.dataset.saasCollapseReady = '1';
        settingsPanel.classList.add('saas-section', 'saas-settings-collapsed');
        settingsPanel.addEventListener('click', () => {
          settingsPanel.classList.toggle('saas-settings-collapsed');
          settingsPanel.classList.toggle('saas-settings-expanded');
        });
      }
    };

    const markLightPanelFrames = () => {
      if (document.documentElement.dataset.theme !== 'light') return;
      const parseRgb = (value) => {
        const match = value.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
        return match ? match.slice(1, 4).map(Number) : null;
      };
      const isDarkFrame = (element) => {
        if (!element || element === document.body) return false;
        const rect = element.getBoundingClientRect();
        const rgb = parseRgb(window.getComputedStyle(element).backgroundColor);
        if (!rgb) return false;
        const max = Math.max(...rgb);
        const min = Math.min(...rgb);
        return rect.width > 360 && rect.height > 180 && max >= 35 && max <= 105 && max - min <= 45;
      };
      const labels = [
        '황금 키워드 분석',
        '유입 극대화 제목',
        '월드 개발 페이지 제어 설정'
      ];

      labels.forEach((label) => {
        const seed = Array.from(document.querySelectorAll('body *')).find((node) => {
          const text = node.textContent || '';
          const rect = node.getBoundingClientRect();
          return text.includes(label) && rect.width > 80 && rect.height > 12;
        });
        if (!seed) return;

        let target = null;
        let current = seed;
        for (let i = 0; i < 12 && current && current !== document.body; i += 1) {
          if (isDarkFrame(current)) target = current;
          current = current.parentElement;
        }
        if (!target) return;

        target.classList.add('styler-light-panel-frame');
        target.style.setProperty('background', '#d0e3fb', 'important');
        target.style.setProperty('background-color', '#d0e3fb', 'important');
        target.style.setProperty('background-image', 'none', 'important');
        target.style.setProperty('border-color', '#9fc4f3', 'important');
      });

      Array.from(document.querySelectorAll('div')).forEach((element) => {
        const rect = element.getBoundingClientRect();
        if (rect.width < 520 || rect.height < 220 || rect.top < 80) return;

        const rgb = parseRgb(window.getComputedStyle(element).backgroundColor);
        if (!rgb) return;

        const [r, g, b] = rgb;
        const isDarkFrame = r >= 45 && r <= 95 && g >= 55 && g <= 105 && b >= 70 && b <= 125;
        if (!isDarkFrame) return;

        element.style.setProperty('background', '#d0e3fb', 'important');
        element.style.setProperty('background-color', '#d0e3fb', 'important');
        element.style.setProperty('background-image', 'none', 'important');
        element.style.setProperty('border-color', '#9fc4f3', 'important');
      });

      Array.from(document.querySelectorAll('div')).forEach((element) => {
        const rect = element.getBoundingClientRect();
        if (rect.width < 560 || rect.height < 260) return;

        const rgb = parseRgb(window.getComputedStyle(element).backgroundColor);
        if (!rgb) return;
        const [r, g, b] = rgb;
        const isCurrentDarkFrame =
          r >= 40 && r <= 95 &&
          g >= 45 && g <= 105 &&
          b >= 55 && b <= 125;
        if (!isCurrentDarkFrame) return;

        const text = element.textContent || '';
        const hasPanelWords =
          text.includes('황금 키워드') ||
          text.includes('유입 극대화') ||
          text.includes('전체 100개') ||
          text.includes('키워드 보기') ||
          text.includes('제목 보기') ||
          text.includes('월드 개발 페이지 제어 설정');

        const hasLargeLightInnerBox = Array.from(element.children).some((child) => {
          const childRect = child.getBoundingClientRect();
          const childRgb = parseRgb(window.getComputedStyle(child).backgroundColor);
          if (!childRgb) return false;
          const [cr, cg, cb] = childRgb;
          return childRect.width > rect.width * 0.75 &&
            childRect.height > rect.height * 0.45 &&
            cr > 180 && cg > 200 && cb > 220;
        });

        if (!hasPanelWords && !hasLargeLightInnerBox) return;

        element.style.setProperty('background', '#d0e3fb', 'important');
        element.style.setProperty('background-color', '#d0e3fb', 'important');
        element.style.setProperty('background-image', 'none', 'important');
        element.style.setProperty('border-color', '#9fc4f3', 'important');
      });

      document.documentElement.style.setProperty('background', '#ffffff', 'important');
      document.documentElement.style.setProperty('background-color', '#ffffff', 'important');
      document.documentElement.style.setProperty('background-image', 'none', 'important');
      document.body.style.setProperty('background', '#ffffff', 'important');
      document.body.style.setProperty('background-color', '#ffffff', 'important');
      document.body.style.setProperty('background-image', 'none', 'important');

      document.querySelectorAll('.min-h-screen').forEach((node) => {
        node.style.setProperty('background', '#ffffff', 'important');
        node.style.setProperty('background-color', '#ffffff', 'important');
        node.style.setProperty('background-image', 'none', 'important');
      });

      Array.from(document.querySelectorAll('div')).forEach((element) => {
        const rect = element.getBoundingClientRect();
        if (rect.width < 480 || rect.height < 140) return;

        const rgb = parseRgb(window.getComputedStyle(element).backgroundColor);
        if (!rgb) return;
        const [r, g, b] = rgb;
        const isLargeGrayFrame = r >= 35 && r <= 110 &&
          g >= 40 && g <= 120 &&
          b >= 50 && b <= 135;
        if (!isLargeGrayFrame) return;

        element.classList.add('styler-final-gray-frame');
        element.style.setProperty('background', '#d0e3fb', 'important');
        element.style.setProperty('background-color', '#d0e3fb', 'important');
        element.style.setProperty('background-image', 'none', 'important');
        element.style.setProperty('border-color', '#9fc4f3', 'important');
      });

      Array.from(document.querySelectorAll('*')).forEach((element) => {
        if (document.documentElement.dataset.theme !== 'light') return;
        const rect = element.getBoundingClientRect();
        if (rect.width < 420 || rect.height < 90) return;

        const rgb = parseRgb(window.getComputedStyle(element).backgroundColor);
        if (!rgb) return;
        const grayish = Math.max(...rgb) - Math.min(...rgb) <= 65;
        const darkEnough = rgb[0] < 140 && rgb[1] < 150 && rgb[2] < 165;
        if (!grayish || !darkEnough) return;

        element.classList.add('force-light-gray-frame');
        element.style.setProperty('background', '#d0e3fb', 'important');
        element.style.setProperty('background-color', '#d0e3fb', 'important');
        element.style.setProperty('background-image', 'none', 'important');
        element.style.setProperty('border-color', '#9fc4f3', 'important');
      });
    };

    const restoreGeneratedLists = () => {
      document.querySelectorAll('.saas-hidden-extra').forEach((node) => node.classList.remove('saas-hidden-extra'));
      document.querySelectorAll('[style]').forEach((node) => {
        const style = node.getAttribute('style') || '';
        if (style.includes('display: none') || style.includes('max-height: 64px')) {
          node.style.removeProperty('display');
          node.style.removeProperty('max-height');
          node.style.removeProperty('overflow');
        }
      });
    };

    const removeAssistantAndHistory = () => {
      const kodariSeed = Array.from(document.querySelectorAll('body *')).find((node) => {
        const text = node.textContent || '';
        const rect = node.getBoundingClientRect();
        return text.includes('KODARI AI ASSISTANT') &&
          rect.top >= 0 &&
          rect.top < 90 &&
          rect.width > 500 &&
          rect.height < 80;
      });
      if (kodariSeed) {
        let target = kodariSeed;
        let current = kodariSeed;
        for (let i = 0; i < 6 && current && current !== document.body; i += 1) {
          const rect = current.getBoundingClientRect();
          if (rect.top >= 0 && rect.top < 90 && rect.width > 700 && rect.height >= 24 && rect.height <= 90) {
            target = current;
          }
          current = current.parentElement;
        }
        target.style.setProperty('display', 'none', 'important');
      }

      const historySeed = Array.from(document.querySelectorAll('body *')).find((node) => {
        const text = node.textContent || '';
        const rect = node.getBoundingClientRect();
        return text.includes('로컬 DB 백업 발행 이력') &&
          rect.width >= 160 &&
          rect.width <= 420 &&
          rect.height >= 24;
      });
      if (historySeed) {
        let target = historySeed;
        let current = historySeed;
        for (let i = 0; i < 8 && current && current !== document.body; i += 1) {
          const rect = current.getBoundingClientRect();
          if (
            rect.width >= 180 &&
            rect.width <= 460 &&
            rect.height >= 260 &&
            rect.left > window.innerWidth * 0.45
          ) {
            target = current;
          }
          current = current.parentElement;
        }
        target.style.setProperty('display', 'none', 'important');
      }

      /*
      ['KODARI AI ASSISTANT', '로컬 DB 백업 발행 이력'].forEach((targetText) => {
        Array.from(document.querySelectorAll('body *')).forEach((node) => {
          const text = node.textContent || '';
          const rect = node.getBoundingClientRect();
          if (!text.includes(targetText)) return;

          let target = node;
          let current = node;
          for (let i = 0; i < 8 && current && current !== document.body; i += 1) {
            const currentRect = current.getBoundingClientRect();
            if (
              currentRect.width >= Math.max(180, rect.width) &&
              currentRect.height >= Math.max(24, rect.height) &&
              currentRect.height < window.innerHeight * 0.95
            ) {
              target = current;
            }
            current = current.parentElement;
          }

          target.style.setProperty('display', 'none', 'important');
        });
      });
      */

      document.getElementById('history-drawer-button')?.remove();
      document.getElementById('history-modal-screen')?.remove();
      document.getElementById('history-modal-backdrop')?.remove();
    };

    const findHistoryPanel = () => Array.from(document.querySelectorAll('div')).find((node) => {
      if (node.closest('#history-modal-backdrop')) return false;
      if (node.id === 'history-modal-backdrop' || node.id === 'history-modal' || node.id === 'history-modal-content') return false;
      const text = node.textContent || '';
      const rect = node.getBoundingClientRect();
      return text.includes('로컬 DB 백업 발행 이력') && rect.width > 160 && rect.height > 240;
    });

    const setupHistoryPopup = () => {
      const panel = findHistoryPanel();
      if (!panel || panel.dataset.historyPopupReady === '1') return;
      panel.dataset.historyPopupReady = '1';

      let button = document.getElementById('history-drawer-button');
      if (!button) {
        button = document.createElement('button');
        button.id = 'history-drawer-button';
        button.type = 'button';
        button.textContent = '발행 이력';
        document.body.appendChild(button);
      }

      let backdrop = document.getElementById('history-modal-backdrop');
      if (!backdrop) {
        backdrop = document.createElement('div');
        backdrop.id = 'history-modal-backdrop';
        backdrop.innerHTML = `
          <div id="history-modal" role="dialog" aria-modal="true">
            <div id="history-modal-header">
              <span>로컬 DB 백업 발행 이력</span>
              <button id="history-modal-close" type="button">×</button>
            </div>
            <div id="history-modal-content"></div>
          </div>
        `;
        document.body.appendChild(backdrop);
        backdrop.addEventListener('click', (event) => {
          if (event.target === backdrop) backdrop.classList.remove('is-open');
        });
        backdrop.querySelector('#history-modal-close')?.addEventListener('click', () => {
          backdrop.classList.remove('is-open');
        });
      }

      const content = backdrop.querySelector('#history-modal-content');
      if (content) {
        content.innerHTML = '';
        content.appendChild(panel.cloneNode(true));
      }
      const mainContent = panel.previousElementSibling;
      if (mainContent) mainContent.style.setProperty('grid-column', '1 / -1', 'important');
      panel.style.setProperty('display', 'none', 'important');
      button.onclick = () => backdrop.classList.add('is-open');
    };

    const setupHistoryPanelModal = () => {
      const candidates = Array.from(document.querySelectorAll('div')).filter((node) => {
        if (node.closest('#history-modal-screen')) return false;
        const text = node.textContent || '';
        const rect = node.getBoundingClientRect();
        return text.includes('로컬 DB 백업 발행 이력') &&
          rect.width >= 160 &&
          rect.width <= 460 &&
          rect.height > 220;
      });
      const panel = candidates.sort((a, b) => {
        const ar = a.getBoundingClientRect();
        const br = b.getBoundingClientRect();
        return (ar.width * ar.height) - (br.width * br.height);
      })[0];
      if (!panel) return;

      panel.classList.add('history-panel-modalized');
      panel.previousElementSibling?.classList.add('styler-main-expanded');

      if (!document.getElementById('history-modal-screen')) {
        const backdrop = document.createElement('div');
        backdrop.id = 'history-modal-screen';
        backdrop.addEventListener('click', () => document.body.classList.remove('history-modal-open'));
        document.body.appendChild(backdrop);
      }

      if (!document.getElementById('history-drawer-button')) {
        const button = document.createElement('button');
        button.id = 'history-drawer-button';
        button.type = 'button';
        button.textContent = '발행 이력';
        button.addEventListener('click', () => document.body.classList.add('history-modal-open'));
        document.body.appendChild(button);
      }
    };

    const runLayoutFixes = () => {
      markLightPanelFrames();
      restoreGeneratedLists();
    };

    runLayoutFixes();
    const firstTimer = window.setTimeout(runLayoutFixes, 300);
    const secondTimer = window.setTimeout(runLayoutFixes, 1000);
    let layoutFixTimer = null;
    const observer = new MutationObserver(() => {
      window.clearTimeout(layoutFixTimer);
      layoutFixTimer = window.setTimeout(runLayoutFixes, 150);
    });
    observer.observe(document.body, { childList: true, subtree: true });
    return () => {
      window.clearTimeout(firstTimer);
      window.clearTimeout(secondTimer);
      window.clearTimeout(layoutFixTimer);
      observer.disconnect();
    };
  }, [dashboardMode]);

  return (
    <>
      <ThemeStyle />
      <ThemeToggleButton themeMode={themeMode} setThemeMode={setThemeMode} />
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
    </>
  );
}

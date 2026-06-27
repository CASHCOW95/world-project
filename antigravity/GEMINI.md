# GEMINI.md - AI 블로그 자동 발행 에이전트 프로젝트 컨텍스트

이 문서는 프로젝트의 설계, 아키텍처, 디렉토리 구조, API 사양 및 개발 규칙을 정의하여 다른 AI 에이전트가 즉시 프로젝트를 파악하고 이어서 작업할 수 있도록 안내하는 마스터 가이드입니다.

---

## 1. 프로젝트 개요 (Project Overview)
- **프로젝트명**: Styler Pro X v3.0 Premium 대시보드 & V2 에이전트
- **목적**: 키워드 발굴, 제목 선정, RAG 기반 글 생성, 토픽 클러스터링(메인-서브 링크 자동 연결) 및 블로그 플랫폼(Tistory 등) 자동 발행을 일괄 수행하는 에이전트 시스템.
- **주요 모드**:
  1. **✍️ 원고 자동 집필기 (Single Mode)**: 단일 키워드 기반으로 키워드 지수 분석, 제목 매칭, 단일 글 작성 및 발행.
  2. **🤖 에이전트 운영센터 (Cluster Mode)**: 3~5개의 연관 키워드를 묶어 RAG 기반 사실 수집, 회피 생성, 본문 내 내부링크 그래프 자동 구성 및 텔레그램 연동 리포트 발행.

---

## 2. 기술 스택 (Tech Stack)
- **Frontend**: React, Vite, Lucide-React, CSS (Vanilla + Tailwind)
- **Backend**: Node.js, Express (API 및 SSE 스트리밍 게이트웨이), Python (사실 수집 및 자동 발행 핵심 엔진)
- **Database**: 로컬 파일 시스템 데이터베이스 (`categories.json`, `published_posts` 등 임시 목업 상태)

---

## 3. 디렉토리 구조 (Directory Structure)
```text
/
├── core/                       # React 프론트엔드 핵심 소스
│   ├── components/             # 대시보드 뷰 컴포넌트
│   │   ├── shared/             # [NEW] 추출된 공통 재사용 UI 컴포넌트
│   │   │   ├── CategoryHeader.jsx   # 카테고리 선택 헤더 UI
│   │   │   ├── KeywordList.jsx      # 키워드 카드 검색/정렬 리스트 UI
│   │   │   ├── TitleList.jsx        # 제목 100선 필터/목록 UI
│   │   │   ├── SettingsPanel.jsx    # 8개 발행 옵션 설정 카드
│   │   │   ├── TerminalLog.jsx      # 실시간 터미널 콘솔 로그 UI
│   │   │   ├── ProfitAnalysis.jsx   # 수익성 & 경쟁도 분석 센터 UI
│   │   │   └── Tooltip.jsx          # 마우스 오버 안내 툴팁
│   │   ├── OriginalStylerDashboard.jsx # 원고 자동 집필기 대시보드 (~300줄로 최적화)
│   │   ├── V2AgentDashboard.jsx        # 에이전트 운영센터 대시보드 (~560줄로 최적화)
│   │   └── StylerDashboard.jsx         # 두 대시보드 모드를 전환하는 래퍼 컴포넌트
│   ├── hooks/                  # [NEW] 프론트엔드 비즈니스 로직 Custom Hooks
│   │   ├── useSettings.js      # 8개 발행 옵션의 localStorage 저장/동기화 관리
│   │   ├── useCategories.js    # 카테고리 로드 및 대/소분류 연동
│   │   ├── useKeywords.js      # 키워드 Fetch, 검색, useMemo 기반 4개 기준 정렬 캐싱
│   │   ├── useTitles.js        # AI 추천 제목 생성 및 필터 상태 관리
│   │   ├── usePipeline.js      # Single/Cluster SSE 스트리밍 파서, AbortController 중단
│   │   └── useApi.js           # 이력(history), 발행 관리, 링크 목록 Fetch
│   ├── index.css               # 글로벌 CSS 테마 스타일
│   ├── main.jsx                # React 마운트 진입점
│   └── App.jsx                 # 세션 유효성 검사 및 대시보드 마운트
├── web_dashboard/              # 빌드된 정적 HTML/Asset 배포 폴더
├── server.js                   # Express 백엔드 서버 (포트 5000)
├── package.json                # 의존성 및 스크립트 정의
└── vite.config.js              # Vite 프론트엔드 번들러 설정
```

---

## 4. 핵심 아키텍처 및 리팩토링 설계 (Refactoring Design)
기존의 스파게티 코드(~2,500줄)를 리팩토링하여 비즈니스 로직과 UI 컴포넌트를 완전히 분리했습니다.
1. **상태 관리의 Hook 위임**: UI 컴포넌트 내의 수많은 `useState`를 개별 훅으로 위임하여 가독성과 리렌더링 최적화를 달성했습니다.
2. **localStorage 공유**: `useSettings` 훅을 통해 두 대시보드 뷰가 동일한 localStorage 설정을 완벽하게 동기화하며 작동합니다.
3. **SSE 파이프라인 단일화**: `usePipeline` 훅이 단일 스트리밍과 클러스터 스트리밍을 모두 파싱하며, 메모리 누수를 방지하기 위해 로그 최대치를 500줄로 강제 제어합니다.
4. **공통 컴포넌트 memo 적용**: `shared/` 하위 컴포넌트들은 `React.memo`로 감싸 부모의 불필요한 리렌더링 시 자식 컴포넌트의 계산을 방지합니다.

---

## 5. 주요 API 사양 (API Specifications)
백엔드(`server.js`)와 통신하는 모든 API 경로는 상대 경로(`/api/...`)로 일관화되어 있습니다.

| 엔드포인트 | 메소드 | 설명 |
|---|---|---|
| `/api/categories` | GET | 카테고리 맵 트리 반환 |
| `/api/keywords` | GET | 소분류에 따른 황금 키워드 목록 조회 |
| `/api/generate-titles` | POST | 키워드 기반 추천 제목 목록 생성 |
| `/api/publish-pipeline` | POST | [SSE] 단일 글 발행 스트리밍 시작 |
| `/api/cluster-generate` | POST | 키워드 기반 토픽 클러스터(메인/서브글 구조) 생성 |
| `/api/cluster-publish` | POST | [SSE] 클러스터 글 일괄 생성, 발행 및 링크 연결 시작 |
| `/api/dashboard-stats` | GET | 대시보드 통계(발행 완료, 보류, 실패 등) 조회 |
| `/api/published-posts` | GET | 플랫폼 발행 완료 포스트 목록 조회 |
| `/api/internal-links` | GET | 클러스터간 내부링크 매핑 히스토리 조회 |
| `/api/telegram-test` | POST | 텔레그램 알림 수신 연결 테스트 |

---

## 6. 개발 가이드라인 (Guidelines for AI)
1. **외과적 수정 원칙**: 기능 추가 또는 수정 시, 기존의 훅(`hooks/`) 또는 공유 컴포넌트(`components/shared/`) 구조를 무너뜨리지 않고 필요한 부분만 정밀하게 타격하여 변경하십시오.
2. **비즈니스 로직과 UI 분리**: 새로운 기능 추가 시 상태나 API 통신은 가급적 커스텀 훅에 작성하고, 컴포넌트는 UI 렌더링에만 집중하도록 유지하십시오.
3. **빌드 안정성 확인**: 수정을 거친 후에는 반드시 `npm run build`를 실행하여 컴파일 에러가 없는지 체크하십시오.

---

## 7. 로컬 기동 및 빌드 명령어 (Commands)
- **개발 서버 기동**: `npm run dev` (프론트엔드 Vite HMR 서버 기동)
- **백엔드 서버 기동**: `npm run server` (포트 5000에서 Express 서버 실행)
- **프론트엔드 빌드**: `npm run build` (코드 수정 후 번들 생성 및 배포 폴더 복사 자동 수행)

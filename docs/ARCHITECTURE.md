# Architecture

## 실제 구조

요청에 포함된 `run.py`, `src`, `dashboard/static/app.js`, `dashboard/server.py` 구조는 현재 `C:\dev\python` 루트에 존재하지 않습니다. 1차 리빌드는 실제 실행 프로젝트인 `03_월드개발페이지`를 기준으로 정리했습니다.

```text
C:\dev\python
├─ 03_월드개발페이지
│  ├─ frontend
│  │  ├─ index.html
│  │  ├─ js/main.js
│  │  ├─ css/style.css
│  │  ├─ build.js
│  │  └─ dist/                  # 빌드 산출물
│  └─ backend
│     ├─ server.js              # Express API/정적 호스팅
│     ├─ core
│     │  ├─ App.jsx
│     │  ├─ components
│     │  ├─ hooks
│     │  ├─ utils
│     │  └─ styler_pro_engine   # Python 콘텐츠 엔진
│     └─ web_dashboard/output   # 생성 산출물
├─ docs
├─ scripts
├─ requirements.txt
└─ _archive/before_full_rebuild
```

## 실행 흐름

1. `frontend/index.html`이 포털 첫 화면을 제공합니다.
2. `frontend/js/main.js`가 로그인 상태, 기능 잠금, ROI 계산기, 피드백 모달, 서버 운영센터를 초기화합니다.
3. `frontend/build.js`가 `backend`의 React 앱을 빌드하고 결과물을 `frontend/dist/workspace`로 합칩니다.
4. `backend/server.js`가 `frontend/dist`와 `/workspace`를 정적으로 제공하고 `/api/*`를 처리합니다.
5. React 워크스페이스는 `backend/core/App.jsx`에서 시작해 `components/StylerDashboard.jsx`로 진입합니다.
6. `StylerDashboard.jsx`는 `OriginalStylerDashboard`와 `V2AgentDashboard`를 모드별로 전환합니다.
7. React hooks가 `/api/*`를 호출하고, Express 서버는 필요한 경우 Python 스크립트를 `spawn`으로 실행합니다.

## 주요 API/엔진 경계

- UI 상태와 fetch 공통 처리: `backend/core/hooks`, `backend/core/utils/apiClient.js`
- 파이프라인 스트리밍 처리: `backend/core/hooks/usePipeline.js`
- 콘텐츠 생성/발행 엔진: `backend/core/styler_pro_engine/main.py`
- 이미지 생성 fallback: `image_generator.py`, `image_factory.py`
- 발행 연동: `publisher.py`

## 데이터와 산출물

- SQLite DB: `backend/core/styler_pro_engine/*.db`
- 발행 프로필 설정: `backend/core/styler_pro_engine/publisher_profiles.json`
- 생성 HTML/이미지: `backend/web_dashboard/output`

민감 정보와 런타임 데이터는 구조 정리 대상이지만 삭제 대상은 아닙니다.

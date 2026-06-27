# World Project

World Project는 정적 포털, React/Vite 기반 AI 블로그 워크스페이스, Node/Express API, Python 콘텐츠 엔진을 함께 사용하는 대시보드 시스템입니다.

## 핵심 경로

| 경로 | 역할 |
| --- | --- |
| `03_월드개발페이지/frontend` | 정적 포털 HTML/CSS/JS와 통합 빌드 엔트리 |
| `03_월드개발페이지/frontend/js/main.js` | 포털 공통 UI, 로그인 가드, 피드백 모달, 서버 운영센터 |
| `03_월드개발페이지/backend` | React/Vite 워크스페이스 소스와 Express API 서버 |
| `03_월드개발페이지/backend/core` | React 컴포넌트, hooks, API 유틸 |
| `03_월드개발페이지/backend/core/styler_pro_engine` | Python 블로그 생성/발행 엔진 |
| `03_월드개발페이지/backend/web_dashboard/output` | 생성된 HTML/이미지 산출물 |
| `docs` | 실행, 구조, API, 리빌드 보고서 |
| `_archive/before_full_rebuild` | 1차 리빌드 전 보존 파일 |

## 설치

```powershell
cd C:\dev\python
python -m pip install -r requirements.txt

cd C:\dev\python\03_월드개발페이지\backend
npm ci
```

## 개발 실행

API 서버와 React 개발 서버를 함께 실행하려면:

```powershell
cd C:\dev\python\03_월드개발페이지\backend
npm run dev:all
```

정적 포털과 빌드된 워크스페이스를 Express로 확인하려면:

```powershell
cd C:\dev\python\03_월드개발페이지\frontend
npm run build

cd C:\dev\python\03_월드개발페이지\backend
npm run server
```

브라우저에서 `http://localhost:5000`을 엽니다.

Codex 인앱 브라우저에서 기존처럼 8000 포트로 확인하려면:

```powershell
cd C:\dev\python\03_월드개발페이지\backend
$env:PORT = "8000"
node server.js
```

브라우저에서 `http://localhost:8000`을 엽니다.

## 검증

```powershell
cd C:\dev\python
.\scripts\validate-world.ps1
```

개별 검증:

```powershell
python -m pip install -r requirements.txt
python -m compileall -q 03_월드개발페이지\backend\core\styler_pro_engine
node --check 03_월드개발페이지\frontend\js\main.js
node --check 03_월드개발페이지\frontend\build.js
node --check 03_월드개발페이지\backend\server.js
```

## 주의

- `C:\dev\python_backup`은 백업 폴더이며 작업 대상이 아닙니다.
- `.env`, 토큰, 인증 정보는 문서화 대상이 아니며 커밋/공유하지 않습니다.
- 실제 발행, 외부 기기 제어, 배포 명령은 수동 확인 후 별도 절차로 수행합니다.

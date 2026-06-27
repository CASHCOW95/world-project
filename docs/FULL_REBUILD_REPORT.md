# Full Rebuild Report

## 1. 작업 전 문제점

- 루트에는 요청된 `run.py`, `src`, `dashboard/static/app.js`, `dashboard/server.py` 구조가 없었습니다.
- 실제 실행 프로젝트는 `03_월드개발페이지`였고, README의 기존 설명도 해당 구조를 가리키고 있었습니다.
- `backend/core/components/StylerDashboard.jsx`가 약 20만 자 규모로 비대해져 기존 대시보드, 신규 대시보드, DOM 후처리 해킹 코드가 한 파일에 공존했습니다.
- 정적 포털 JS(`frontend/js/main.js`)가 인증, 서버 운영센터, ROI 계산기, 모달, 스크롤 애니메이션을 하나의 긴 `DOMContentLoaded` 블록에서 처리했습니다.
- 서버 운영센터는 요청 실패 사유를 화면에 충분히 남기지 않아 사용자가 현재 상태를 알기 어려웠습니다.
- React 리스트 UI는 키워드/제목이 비어 있을 때 명확한 빈 상태가 부족했습니다.
- Python 이미지 엔진은 런타임 중 `pip install Pillow`를 시도했습니다.
- `image_factory.py`에는 `compileall`에서 실패할 수 있는 f-string 문법 오류가 있었습니다.
- 루트 `requirements.txt`가 없어 요청된 Python 의존성 검증 명령을 실행할 수 없었습니다.

## 2. 변경한 전체 구조

```text
C:\dev\python
├─ 03_월드개발페이지
│  ├─ frontend
│  │  ├─ js/main.js
│  │  └─ css/style.css
│  └─ backend
│     ├─ server.js
│     └─ core
│        ├─ components/StylerDashboard.jsx
│        ├─ components/shared
│        ├─ hooks
│        ├─ utils/apiClient.js
│        └─ styler_pro_engine
├─ _archive/before_full_rebuild
├─ docs
├─ scripts/validate-world.ps1
└─ requirements.txt
```

## 3. 주요 변경 파일

- `README.md`
- `requirements.txt`
- `scripts/validate-world.ps1`
- `03_월드개발페이지/frontend/js/main.js`
- `03_월드개발페이지/frontend/css/style.css`
- `03_월드개발페이지/backend/core/components/StylerDashboard.jsx`
- `03_월드개발페이지/backend/core/components/OriginalStylerDashboard.jsx`
- `03_월드개발페이지/backend/core/components/V2AgentDashboard.jsx`
- `03_월드개발페이지/backend/core/components/shared/ErrorBanner.jsx`
- `03_월드개발페이지/backend/core/components/shared/KeywordList.jsx`
- `03_월드개발페이지/backend/core/components/shared/TitleList.jsx`
- `03_월드개발페이지/backend/core/components/shared/TerminalLog.jsx`
- `03_월드개발페이지/backend/core/hooks/useApi.js`
- `03_월드개발페이지/backend/core/hooks/useCategories.js`
- `03_월드개발페이지/backend/core/hooks/useKeywords.js`
- `03_월드개발페이지/backend/core/hooks/useTitles.js`
- `03_월드개발페이지/backend/core/utils/apiClient.js`
- `03_월드개발페이지/backend/core/styler_pro_engine/image_generator.py`
- `03_월드개발페이지/backend/core/styler_pro_engine/image_factory.py`
- `docs/SETUP.md`
- `docs/ARCHITECTURE.md`
- `docs/API.md`
- `docs/FULL_REBUILD_REPORT.md`

## 4. archive로 이동한 파일

- 삭제하지 않고 보존한 파일:
  - `_archive/before_full_rebuild/03_월드개발페이지/backend/core/components/StylerDashboard.legacy.jsx`

## 5. 삭제 후보 파일

- `03_월드개발페이지/backend/core/components/OriginalStylerDashboard.jsx`: 기능은 유지 중이지만 장기적으로 V2와 UI/상태 흐름을 통합할 후보입니다.
- `03_월드개발페이지/backend/core/components/V2AgentDashboard.jsx`: 현재 유지. 다음 단계에서 더 작은 섹션 컴포넌트로 분해할 후보입니다.
- `03_월드개발페이지/backend/scratch/*`: 분석/일회성 스크립트로 보이며 실행 경로와 분리 검토가 필요합니다.
- `03_월드개발페이지/backend/deploy/*`, `03_월드개발페이지/backend/dist/*`, `03_월드개발페이지/frontend/workspace/*`: 빌드 산출물 또는 배포 사본으로 보이며, 삭제 전 배포 흐름 확인이 필요합니다.
- `03_월드개발페이지/backend/*.json`, `*.txt`, `*.srt`, `*.webp`: 데이터/산출물 성격이 섞여 있어 삭제하지 않았습니다.

## 6. 유지한 기존 기능

- 포털 첫 화면
- 관리자 로그인 가드
- 기능 카드 잠금
- ROI 계산기
- 피드백 메일 모달
- 서버 운영센터 상태 확인
- React 워크스페이스 모드 전환
- 원고 자동 집필기
- AI 블로그 에이전트 운영센터
- 키워드/제목 생성
- 단일 글 생성/발행 파이프라인
- 클러스터 생성/발행 파이프라인
- 발행 이력/링크/통계 조회
- Python 엔진 기반 콘텐츠 생성, 이미지 fallback, 발행 연동

## 7. 변경한 기능

- `StylerDashboard.jsx`를 대형 중복 구현에서 얇은 모드 전환 wrapper로 변경했습니다.
- 기존 대형 구현은 archive에 보존했습니다.
- 정적 포털 JS를 기능별 초기화 함수로 재구성했습니다.
- 서버 운영센터 fetch에 timeout, 버튼 busy 상태, 화면 오류 메시지를 추가했습니다.
- React fetch hook에 HTTP 오류 처리 유틸을 적용했습니다.
- Python 이미지 엔진의 런타임 자동 패키지 설치를 제거했습니다.
- `image_factory.py` 문법 오류를 수정했습니다.

## 8. UI/UX 개선 내용

- 서버 상태를 `CHECKING`, `ONLINE`, `OFFLINE`으로 명확히 표시합니다.
- 서버 상태 확인 실패 사유를 운영센터 패널 안에 표시합니다.
- 상태 확인/워커 새로고침 버튼의 로딩/비활성 상태를 통일했습니다.
- 피드백 폼 입력 누락은 alert 대신 toast로 표시합니다.
- 키워드, 제목, 터미널 로그에 빈 상태를 추가했습니다.
- 모바일에서 헤더, 운영센터 버튼, 모달 여백이 깨지지 않도록 CSS를 보완했습니다.

## 9. 성능/구조 개선 내용

- 활성 React 대시보드 엔트리 파일을 20만 자 규모에서 작은 wrapper로 축소했습니다.
- 이미 존재하던 hooks/shared components 구조를 실제 엔트리로 연결했습니다.
- API JSON 처리 공통 유틸을 추가해 반복 오류 처리를 줄였습니다.
- 정적 JS에서 DOM 선택, 이벤트 등록, fetch timeout, 버튼 상태 관리를 분리했습니다.
- 런타임 `pip install` 제거로 실행 예측 가능성을 높였습니다.

## 10. 검증 결과

실행한 검증:

| 명령 | 결과 |
| --- | --- |
| `python -m pip install -r requirements.txt` | 통과 |
| `python -m compileall -q 03_월드개발페이지\backend\core\styler_pro_engine` | 통과 |
| `node --check 03_월드개발페이지\frontend\js\main.js` | 통과 |
| `node --check 03_월드개발페이지\frontend\build.js` | 통과 |
| `node --check 03_월드개발페이지\backend\server.js` | 통과 |
| `cd 03_월드개발페이지\frontend; npm run build` | 통과 |
| `python -m compileall -q run.py src dashboard` | 현재 루트에 `run.py`, `src`, `dashboard`가 없어 적용 불가. 명령 출력: `Can't list 'run.py'`, `Can't list 'src'`, `Can't list 'dashboard'` |
| `python -c "import dashboard.server"` | 현재 `dashboard` Python 패키지가 없어 적용 불가. 결과: `ModuleNotFoundError: No module named 'dashboard'` |
| 루트 `npm run build` | 루트 `package.json`이 없어 생략. 실제 빌드는 `03_월드개발페이지/frontend`에서 통과 |

검증 중 생성된 `__pycache__` 캐시는 프로젝트 내부 경로 확인 후 정리했습니다.

브라우저 확인:

- 기존 `localhost:8000`은 이전 Android Agent Dashboard 프로세스가 사용 중이어서 종료했습니다.
- 원본 프로젝트 Express 서버를 `PORT=8000 node server.js`로 실행했습니다.
- `http://localhost:8000/` 포털 로딩 확인: title `WORLD - 나만의 월드 파트너`, feature card 9개, console error 0건.
- `http://localhost:8000/workspace/index.html?view=styler` 워크스페이스 로딩 확인: 모드 버튼, 터미널 빈 상태, console error 0건.
- `에이전트 운영센터` 모드 전환 버튼 클릭 확인: V2 탭(`키워드 & 클러스터`, `발행 관리`, `설정`) 표시, console error 0건.

## 11. 아직 남은 문제

- `backend/server.js`는 아직 단일 파일에 API 라우트가 많이 몰려 있습니다.
- `V2AgentDashboard.jsx` 내부도 다음 단계에서 탭/설정/파이프라인 섹션으로 더 분리하는 것이 좋습니다.
- `frontend/build.js`는 빌드 중 `backend/dist`, `frontend/dist`를 갱신하므로 산출물 추적 정책을 별도로 정해야 합니다.
- 실제 배포, 실제 발행, 외부 기기 제어는 이번 작업에서 실행하지 않았습니다.

## 12. 다음 추천 작업

- `backend/server.js`를 routes/services 단위로 분리합니다.
- React 대시보드의 V2 탭을 파일 단위로 분리합니다.
- 산출물/데이터/소스 파일의 Git 추적 정책을 확정합니다.
- Playwright 또는 Vitest 기반 UI/흐름 테스트를 추가합니다.
- 로컬 서버 헬스체크 API와 Mac mini 외부 헬스체크 UI를 분리합니다.

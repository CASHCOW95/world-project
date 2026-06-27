# 작업 프로젝트 기록부 (Project Log)

앞으로 진행되는 모든 작업은 이 파일에 프로젝트별로 넘버링하여 기록되며, 최신 작업이 가장 위에 노출됩니다.
## [Project #2] 토픽 클러스터 스마트 발행 및 UI/UX 개선 - 4차 업데이트 (품질/검증 엔진 구축 및 백엔드 파이프라인 고도화)
* **최종 업데이트 시간:** 2026-06-21 23:45:00 (KST)
* **상태:** ✅ 완료 (품질/검증 QA 엔진 구축 및 백엔드 파이프라인 무결성 확보)

### 📌 이번 추가 진행 내역
1. **ResearchEngine RSS 예외 처리 및 대체 수집 구현**
   - 정부기관 RSS(`gov.kr`, `nts.go.kr`) 수집 시 발생하는 XML 태그 mismatched 오류나 404 에러 시 전체 파이프라인이 중단되지 않고 graceful하게 skip 되도록 예외 처리를 구성했습니다.
   - SQLite 내 `rss_feeds` 테이블을 통해 연속 실패 횟수 및 기간을 저장하고, 7일 이상 연속 실패가 감지되면 해당 피드를 비활성화하여 자동 Skip하도록 조치했습니다.
   - 실패 발생 시 즉시 `[RSS] Fallback Source Activated`와 함께 Google News 등을 통해 대체 자료를 자동 수집하고, 수집된 참고 자료 중 Keyword Relevance Score 70점 미만인 출처는 필터링하여 출처 품질을 보장했습니다.
2. **키워드 중복 제거 (Normalizer Engine)**
   - 입력 키워드 내 인접 단어가 연속으로 반복되는 오류(예: `"소상공인 지원금 신청 신청 자격 요건"`)를 정규화하여 중복 없는 형태(`"소상공인 지원금 신청 자격 요건"`)로 전처리 후 파이프라인을 작동시켰습니다.
3. **주제 오염 방지 및 Mock DB 구축**
   - 청년 정책 관련 데이터가 무분별하게 재사용되는 문제를 막기 위해 `content_builder.py` 내의 Fallback Mock DB에 `SO_SANG_GONG_IN_MOCK`(소상공인 지원금 전용 목업 데이터) 및 일반 카테고리를 독립적으로 추가하여 의도치 않은 정보 오염을 원천 차단했습니다.
   - LLM 집필 프롬프트에 `Keyword → Intent → Program Detection → Fact Collection → Content Generation`의 sequential reasoning 체인을 강화하여 다른 지원 정책명이 혼입되는 것을 강력하게 막았습니다.
4. **12-Criteria SEO 및 FAQ Context Summary 제약**
   - **SEO 평가지표 현실화**: Keyword Naturalness, Topic Consistency, Fact Accuracy, Duplicate Sentence Ratio 등 4개 핵심 지표를 추가로 구현하여 총 12개의 점수 산정 항목 매트릭스를 구성했습니다.
   - **FAQ 품질 보장**: 본문의 실시간 맥락을 선추출한 `<CONTEXT_SUMMARY>` 제약 조건 내에서만 FAQ가 생성되도록 하여, 본문과 어긋난 청년 일자리 질문이 소상공인 관련 글에 유입되지 않도록 막았습니다.
5. **수익성 엔진 모델 및 AI 뱃지 현실화**
   - Estimated Revenue의 클릭률(1~3%), 유입률(검색량의 1~5%), CPC 환산 부스트 계수를 실제 광고 전환 지표에 맞게 보정하여 현실적인 스코어가 노출되도록 개선했습니다.
6. **Content QA Engine 설계 및 통합 검증**
   - 최종 발행 직전 문맥 자연스러움(중복 문장 비율 5% 미만), 제목 중복어, 정책명 일치 여부, 표 데이터 및 FAQ 정합성을 교차 검증하는 `Content QA Engine`을 `content_qa.py`로 분리 탑재하여, 불합격 시 피드백 기반 3~5회 자동 재생성(Refine) 루프를 돌도록 구성했습니다.

---

## [Project #2] 토픽 클러스터 스마트 발행 및 UI/UX 개선 - 3차 업데이트 (화면 크래시 복구 및 문법 오류 해결)
* **최종 업데이트 시간:** 2026-06-21 18:45:00 (KST)
* **상태:** ✅ 완료 (화면 크래시 복구 및 빌드 무결성 확보)

### 📌 이번 추가 진행 내역
1. **React JSX Fragment 문법 오류 해결**
   - `{activeTab === 'cluster' && ( ... )}` 내부에 여러 최상위 엘리먼트(`div`, `section`)가 감싸지지 않고 병렬 배치되어 Vite 빌드를 가로막던 문법 오류를 `<React.Fragment>` (`<> ... </>`)로 묶어 해결했습니다.
2. **Settings, Link 아이콘 임포트 누락 런타임 오류 해결**
   - 오리지널 대시보드를 reflog에서 가져올 때 `Settings`와 `Link` 아이콘이 `lucide-react` 임포트 리스트에서 누락되어 발생하던 `ReferenceError: Settings is not defined` 크래시를 `merge_dashboards.cjs` 에서 병합 시점에 임포트를 자동으로 주입하도록 수정하여 해결했습니다.
3. **`item.platform` Null Pointer 런타임 오류 예외 처리**
   - 발행 이력 목록에서 `item.platform`이 없는 데이터가 들어올 경우 `item.platform.toUpperCase()`에서 `TypeError: Cannot read properties of undefined` 크래시가 나며 화면이 하얗게 굳던 문제를 `(item.platform || 'tistory').toUpperCase()`로 기본값을 제공하도록 `merge_dashboards.cjs` 에 최종 치환 규칙을 삽입하여 예방했습니다.
4. **Vite 빌드 복구 및 정상 작동 검증**
   - `npm run build`가 에러 없이 성공적으로 수행되는 것을 확인했습니다.
   - 브라우저 서브에이전트 접속 검증을 통해 크래시 없이 원고 집필기 및 에이전트 모드가 안정적으로 로딩되는 것을 최종 확인했습니다.

---

## [Project #2] 토픽 클러스터 스마트 발행 및 UI/UX 개선 - 2차 업데이트
* **최종 업데이트 시간:** 2026-06-19 11:23:00 (KST)
* **상태:** 🔄 작업 진행 중

### 📌 이번 추가 진행 내역
1. **코다리 배너 완전 제거**
   - `App.jsx`에서 Kodari AI Assistant 상단 배너 JSX 및 변수 정의 완전 삭제.
   - `StylerDashboard.jsx`의 `runLayoutFixes`에서 `hideAssistantBanner()` 및 `removeAssistantAndHistory()` DOM 스캔 호출 제거.
   - DOM을 반복 스캔하여 강제 숨기는 불안정한 로직 대신 JSX 레벨에서 근본 제거.

2. **터미널 로그 접기/펼치기 기능 구현**
   - `terminalExpanded` 상태를 `V2AgentDashboard`에 추가.
   - 기본 상태: **접힘** (높이 auto, 로그 카운트 배지만 노출).
   - 파이프라인 실행 시 자동으로 펼침 (`handleStartPipeline`에서 `setTerminalExpanded(true)`).
   - 접힌 상태에서는 콘텐츠 영역(황금틈새 리포트, 클러스터 프리뷰, 키워드 목록)이 화면 상단에 바로 노출.

3. **키워드 카드 디자인 개선**
   - 파란 좌측 보더(`border-l-4 border-l-indigo-600/60`) 적용으로 카드 시각적 구분 강화.
   - 검색량/CPC에 이모지 아이콘(🔍/💰) 추가.
   - 선택 상태 시 배지 색상이 분리되어 활성 카드가 더 뚜렷하게 구분.

4. **키워드 목록 기본 5개 + 더보기 방식**
   - 기존 10개 → 5개로 초기 노출 수 축소.
   - "더보기" 버튼 텍스트 및 패딩 개선.

### 📌 현재 상태
- `npm run build` 성공 (574ms, JS 번들 319KB).
- 터미널이 접힌 상태에서 핵심 콘텐츠가 화면 상단으로 올라옴.
- 서버 재시작 후 `http://localhost:5000/workspace/index.html?view=styler`에서 확인 가능.

---

## [Project #2] 토픽 클러스터 스마트 발행 및 UI/UX 스크린샷 싱크 구현 - 중간 저장
* **최종 업데이트 시간:** 2026-06-17 22:55:00 (KST)
* **상태:** ⚠️ 작업 진행 중 (화면 크래시 복구 및 UI 안정화 중간 저장)

### 📌 이번 추가 진행 내역
1. **화면 크래시 복구**
   - 발행 이력 렌더링에서 `platform` 값이 없는 데이터로 인해 `toUpperCase()` 호출 크래시가 발생하던 문제를 방어 처리했습니다.
   - `formatHistoryPlatform`, `formatHistoryDate`, `normalizeHistoryItem`를 추가하여 누락 데이터가 있어도 화면이 죽지 않도록 했습니다.
   - `/api/history` 응답 보정용 안전 처리도 `web_dashboard/workspace/index.html`에 추가했습니다.

2. **다크/라이트 모드 및 색상 정리**
   - 우상단 `LIGHT / DARK` 테마 토글을 추가했습니다.
   - 라이트모드 기준 폰트 계열을 `Arial`, `Noto Sans KR`, `Malgun Gothic`, system UI 계열로 통일했습니다.
   - 라이트모드 색상 기준을 아래처럼 정리했습니다.
     - Primary: `#2563EB`
     - Secondary: `#64748B`
     - Background: `#F8FAFC`
     - Success: `#22C55E`
   - 라이트모드에서 다크모드용 `slate/gray` 배경이 남는 경우 흰 카드 톤으로 보정하는 안전 CSS를 추가했습니다.
   - 파란 배경 위 텍스트는 흰색으로 보이도록 보정했습니다.

3. **상단 배너 및 발행 이력 영역 조정**
   - `KODARI AI ASSISTANT` 상단 안내 배너 숨김 처리를 추가했습니다.
   - 로컬 DB 발행 이력 패널이 빠진 오른쪽 공간만큼 메인 콘텐츠가 넓게 보이도록 `lg:col-span-10`을 12칸 폭으로 보정했습니다.
   - 발행 이력 팝업화는 시도했으나 DOM 이동/복사 방식이 React 렌더와 충돌해 크래시 가능성이 있어 위험 로직은 비활성화했습니다.

4. **안정화를 위해 비활성화한 내용**
   - 화면 렌더 후 전체 DOM을 반복 스캔하며 스타일을 인라인으로 강제 적용하던 스크립트는 크래시 가능성 때문에 껐습니다.
   - `MutationObserver` 기반 자동 레이아웃 변경도 크래시 가능성 때문에 사용하지 않는 방향으로 정리했습니다.

### 📌 현재 상태
- 서버가 켜져 있으면 `http://localhost:5000/workspace/index.html?view=styler` 화면은 정상 복구됩니다.
- 현재 UI 개선은 주로 `web_dashboard/workspace/index.html`의 안전 CSS 보정과 `StylerDashboard.jsx`의 일부 소스 보정으로 반영되어 있습니다.
- 브라우저 반영 시 `Ctrl + F5` 강력 새로고침이 필요합니다.

### 📌 다음 작업 권장 방향
1. **임시 HTML 보정 대신 React 구조 직접 수정**
   - 상단 배너는 JSX에서 직접 제거.
   - 발행 이력은 `useState` 기반 모달 컴포넌트로 구현.
   - 추천 키워드, 제목 카드, AI 분석, 설정 영역은 JSX 구조와 Tailwind 클래스 기준으로 정리.
2. **UI 가독성 개선안 반영**
   - 추천 키워드 카드: 흰 카드 + 파란 좌측 보더.
   - 제목 카드: 제목 우선, CTR/SEO는 작은 보조 정보.
   - 설정 영역: 기본 접힘 상태.
   - 내부 스크롤 제거, 상위 5개 우선 노출 + 더보기 방식.
3. **검증**
   - `npm run build`로 빌드 검증.
   - 서버 재시작 후 라이트/다크 모드 각각 화면 확인.

---

## [Project #2] 토픽 클러스터 스마트 발행 및 UI/UX 스크린샷 싱크 구현
* **최종 업데이트 시간:** 2026-06-17 21:31:00 (KST)
* **상태:** ✅ 완료

### 📌 주요 수행 내역
1. **백엔드 Python 엔진 (`main.py`)**: ✅
   - `--contextual_links` (ON/OFF) 인자 추가 완료.
   - `run_cluster_pipeline` 함수 내 `[CLUSTER-4]` 단계 분기 조건 처리 완료.
2. **백엔드 Node Express (`server.js`)**: ✅
   - `/api/cluster-publish` 라우트에서 `scheduled_at`, `contextual_links` 수신·전달 완료.
3. **프론트엔드 React UI (`StylerDashboard.jsx`)**: ✅
   - `useCodexImages`, `useContextualLinks`, `publishType`, `firstPublishTime`, `clusterInterval`, `clusterTotal`, `clusterCurrent`, `clusterStatusLabel` 상태 정의 완료.
   - 우측 사이드바 패널 리디자인 완료 (Codex AI 이미지 토글, 문맥형 내부링크 토글, 발행 모드 4버튼, 예약 발행 datetime picker, 글 간격 슬라이더).
   - **"황금틈새 판단 이유"** 카드 (AI 블루오션 전략 분석 리포트) 구현 완료.
   - **주황색 프로그레스 바** + **"강제 중지"** 버튼 탑재 진행률 모니터링 카드 구현 완료.
   - 포트 5001→5000 API 일원화 완료.
   - `Link`→`Link2`, `Settings` 아이콘 import 누락 수정 완료.
   - `AbortController` 기반 파이프라인 강제 중지 핸들러 구현 완료.
4. **빌드 검증**: ✅
   - `npm run build` 성공 (✓ built in 586ms). 구문 오류 5건 수정 후 무결성 확인.


---

## [Project #1] Styler Pro X v3.0 Premium 대시보드 & V2 에이전트 병합 통합
* **완료 시간:** 2026-06-17 16:30:00 (KST)
* **상태:** ✅ 완료

### 📌 주요 수행 내역
1. **오리지널과 V2의 대시보드 병합**:
   - `StylerDashboard.jsx`에 상단 모드 스위처(`dashboardMode` 상태)를 마운트하여 **[✍️ 원고 자동 집필기]**(3단 그리드)와 **[🤖 에이전트 운영센터]**(5개 탭) 간 전환 흐름을 구축했습니다.
2. **포트 5000 기반 API 일원화**:
   - 서로 달랐던 프론트엔드 빌드 환경 및 API 호출 주소를 상대 경로(`/api/...`)로 통합하여, 5000 포트 단일 노드 서버 환경에서 전체 기능이 통합 기동하도록 조치했습니다.
3. **빌드 검증**:
   - `npm run build`를 성공하여 문법 검증 및 React 빌드 무결성을 최종 확인했습니다.

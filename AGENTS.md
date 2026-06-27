# AGENTS.md

이 파일은 현재 워크스페이스의 루트 AI 에이전트 진입점이다.
새 세션에서는 이 파일을 먼저 읽고, 작업 대상에 맞는 하위 문서만 추가로 읽는다.
기본 개발 철학과 작업 원칙은 `00_MD/BASE_INSTRUCTIONS.md`를 최상위 기준으로 삼는다.

## 기본 원칙

- 현재 저장소는 여러 프로젝트가 섞인 모노레포에 가깝다. 작업 대상 폴더를 먼저 확정한 뒤 움직인다.
- 대규모 리팩토링, 파일 이동, 폴더 구조 변경, 의존성 교체는 사용자 승인 없이 하지 않는다.
- 빌드 산출물, 실행파일 번들, vendor 파일은 작업 대상이 명시된 경우가 아니면 건드리지 않는다.
- 빠른 실행과 검증을 우선하되, 기존 동작을 깨지 않도록 작은 단위로 수정한다.
- Python 코드는 `pathlib.Path`, `sys.executable`, `subprocess`를 우선한다. `os.system`, 절대 경로, OS 고정 경로는 피한다.

## 첫 5분 루틴

1. 루트 `AGENTS.md`를 읽는다.
2. `00_MD/BASE_INSTRUCTIONS.md`를 기본 개발 원칙으로 숙지한다.
3. `00_MD/MD_INVENTORY.md`에서 관련 문서 그룹만 확인한다.
4. 공통 운영 원칙이 필요하면 `core/GEMINI.md`, `core/PROJECT.md`, `core/TASKS.md`, `core/DEV_RULES.md`를 읽는다.
5. 작업 대상 폴더의 전용 `AGENTS.md`가 있으면 그것을 우선한다. 예: `06_유튜브플리/AGENTS.md`, `101_블로그글쓰기/AGENTS.md`.
6. `node_modules`, `exe`, `_internal`, `dist`, `pdf_pages`, `pdf_jpg`, `legacy/deploy`는 기본 검색/수정 범위에서 제외한다.

`CLAUDE.md`와 `GEMINI.md`는 호환용 부트스트랩이다. 실제 공통 지침의 원본은 이 `AGENTS.md`다.
`000_월드개발페이지`가 현재 월드 개발 페이지의 활성 경로다. `03_월드개발페이지`는 Windows 잠금 때문에 남아 있는 레거시 복사본이므로, 별도 정리 요청이 없으면 읽기/수정 대상에서 제외한다.
예외적으로 `03_월드개발페이지/frontend`는 Cloudflare Pages가 아직 예전 Root Directory를 볼 때 최신 `000_월드개발페이지`를 빌드하게 하는 호환 shim이며, 실제 소스 기준은 아니다.

## 프로젝트 라우팅

| 작업 대상 | 먼저 읽을 문서 | 주 작업 경로 | 기본 검증 |
|---|---|---|---|
| 루트/배포 구조 | `README.md`, `00_MD/MD_INVENTORY.md` | 루트, `000_월드개발페이지/frontend` | `npm run build` from `000_월드개발페이지/frontend` |
| 월드 개발 페이지 | `000_월드개발페이지/AGENTS.md`, `README.md` | `000_월드개발페이지/backend`, `000_월드개발페이지/frontend` | backend build 또는 frontend 통합 build |
| Styler Pro X / AI 블로그 | `101_블로그글쓰기/AGENTS.md`, `101_블로그글쓰기/GEMINI.md`, `101_블로그글쓰기/project.md` | `101_블로그글쓰기` | `npm run build`, 필요 시 `npm run server` |
| Core 공통 자동화 | `core/AGENTS.md`, `core/PROJECT.md`, `core/TASKS.md` | `core` | 변경 파일별 syntax/type check |
| AUTOmaple | `core/game_auto/AGENTS.md`, `01_오토메이플/AGENTS.md` | `core/game_auto`, `01_오토메이플/src` | Python AST parse, 수동 GUI 확인 계획 |
| 오픈폼 자동화 | `02_오픈폼/AGENTS.md`, `core/DEV_RULES.md` | `core/form_auto`, `02_오픈폼/src` | GUI 실행 전 설정 파일 확인 |
| 텔레그램봇 | `04_텔레그램봇/AGENTS.md` | `04_텔레그램봇`, `core/orchestrator` | Python AST parse, live send는 요청 시만 |
| 추첨 도구 | `05_추첨도구/AGENTS.md`, `core/DEV_RULES.md` | `core/winner_finder`, `05_추첨도구` | 샘플 xlsx 기준 dry run |
| 유튜브 플레이리스트 | `06_유튜브플리/README.md`, `06_유튜브플리/PROGRESS.md`, `06_유튜브플리/AGENTS.md` | `06_유튜브플리/apps`, `06_유튜브플리/agent` | server/web typecheck, Agent heartbeat |
| Mac Mini 서버 | `98_맥미니서버/AGENTS.md`, `98_맥미니서버/README.md` | `98_맥미니서버` | `docker compose config`, 수동 운영 확인 |
| TikTok 자동화 | `99_틱톡자동화/AGENTS.md` | `99_틱톡자동화` | Python AST parse, live ADB는 요청 시만 |
| 하네스 템플릿 | `00_MD/START.md`, `00_MD/CLAUDE.md` | `00_MD` | `SPEC.md`, `SELF_CHECK.md`, `QA_REPORT.md` 생성 확인 |
| 지식베이스 | `brain/wiki/index.md`, `brain/aaa.md` | `brain` | 링크/문서 구조 확인 |

## 하네스 구조

`00_MD`는 단일 산출물 생성을 위한 3-Agent 하네스 템플릿이다.

```text
00_MD/
  CLAUDE.md
    -> 오케스트레이터. Planner, Generator, Evaluator 호출 순서를 정의한다.
  START.md
    -> 실행 방법과 비교 실험 방법.
  agents/
    planner.md
      -> 사용자 요청을 SPEC.md로 확장한다.
    generator.md
      -> SPEC.md를 구현하고 SELF_CHECK.md를 작성한다.
    evaluator.md
      -> 결과물을 평가하고 QA_REPORT.md를 작성한다.
    evaluation_criteria.md
      -> 공통 채점 기준.
```

이 하네스는 `output/index.html` 같은 단일 웹 결과물에 맞춰져 있다.
현재 루트 모노레포 작업에는 아래의 Repo Agent Loop를 적용한다.

```text
요청 수신
  -> 작업 대상 폴더 확정
  -> 관련 MD만 읽기
  -> 영향 범위 확인
  -> 작은 수정
  -> 해당 프로젝트 검증
  -> 변경 요약과 남은 리스크 보고
```

## Markdown 운용 규칙

- 전체 Markdown 지도는 `00_MD/MD_INVENTORY.md`에 있다.
- 모든 Markdown을 매 세션 전부 읽지 않는다. 인벤토리로 범위를 좁힌 뒤 관련 문서만 읽는다.
- `docs/`와 `01_오토메이플/docs/`에는 동일한 AUTOmaple 문서가 많다. 일반 기준 문서는 `docs/`를 우선하고, 패키지 산출물 문서가 필요한 경우에만 `01_오토메이플/docs/`를 함께 본다.
- `101_블로그글쓰기/docs/benchmarking_analysis.md`와 `docs/benchmarking_analysis.md`는 동일하다. Styler Pro X / AI 블로그 작업이면 `101_블로그글쓰기` 쪽 경로를 우선한다.
- `brain/raw`는 긴 원문 자료다. 요약/지식화 작업이 아니면 기본 컨텍스트에 넣지 않는다.
- `03_월드개발페이지`는 레거시 잠금 복사본이다. 월드 개발 페이지 작업은 `000_월드개발페이지`만 기준으로 한다.

## 지침 문서 유지보수 규칙

루트 `AGENTS.md`는 모든 내용을 담는 문서가 아니라 라우터다. 무겁게 만들지 않는다.

- 루트 `AGENTS.md`: 공통 원칙, 부트 순서, 프로젝트 라우팅, 전역 금지 범위만 관리한다.
- `00_MD/BASE_INSTRUCTIONS.md`: 모든 프로젝트에 공통 적용되는 기본 개발 철학과 작업 원칙을 관리한다.
- 프로젝트 `AGENTS.md`: 해당 프로젝트의 읽기 순서, 주요 경로, 검증 방법만 관리한다.
- `00_MD/MD_INVENTORY.md`: 전체 Markdown 목록, 중복 문서, 상세 문서 위치를 관리한다.
- 상세 스펙, 기획서, 운영 매뉴얼, 긴 참고자료는 각 프로젝트 `docs/`나 전용 문서에 둔다.

새 프로젝트나 새 핵심 지침 문서가 생기면 아래 순서로 갱신한다.

```text
새 프로젝트 발견 또는 생성
  -> 프로젝트/AGENTS.md 생성
  -> 루트 AGENTS.md의 프로젝트 라우팅 표에 한 줄 추가
  -> 00_MD/MD_INVENTORY.md에 문서 그룹 추가
```

```text
새 핵심 Markdown 생성
  -> 해당 프로젝트/AGENTS.md의 Read Order 또는 Scope에 추가
  -> 필요할 때만 루트 AGENTS.md 라우팅 표 갱신
  -> 00_MD/MD_INVENTORY.md 갱신
```

에이전트는 새 프로젝트 폴더나 새 핵심 지침 문서를 발견하면, 작업 전에 위 문서 유지보수 갱신이 필요한지 확인한다.

## 수정 금지 기본 범위

명시 요청이 없으면 아래 경로는 읽기 또는 검색 참고까지만 한다.

- `**/node_modules/**`
- `**/exe/**`
- `**/_internal/**`
- `**/dist/**`
- `03_월드개발페이지/**`
- 단, `03_월드개발페이지/frontend/{README.md,package.json,build.js}`는 Cloudflare 호환 shim 유지 목적에 한해 수정 가능
- `legacy/deploy/**`
- `pdf_pages/**`
- `pdf_jpg/**`
- 대용량 이미지, xlsx, db, 로그 산출물

## 보고 형식

작업 완료 보고에는 다음만 간결하게 남긴다.

- 무엇을 바꿨는지
- 어떤 검증을 했는지
- 검증하지 못한 부분 또는 수동 확인이 필요한 부분
- 다음 작업이 있다면 바로 이어갈 수 있는 파일/명령

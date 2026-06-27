# World Project

이 프로젝트는 키워드 발굴, 블로그 자동 발행, 수익성 분석 및 서버 운영 현황을 관리하는 대시보드 시스템입니다.

## 🚀 배포 단일화 및 개발 가이드

배포 및 개발 구조를 다음과 같이 `000_월드개발페이지/frontend` 경로로 단일화했습니다.

### 1. 주요 경로 (Directories)

*   **실제 개발 및 배포 루트 경로**: `000_월드개발페이지/frontend`
*   **React/Vite 프론트엔드 소스 경로**: `000_월드개발페이지/backend` (빌드 과정에서 자동으로 컴파일되어 `frontend/dist/workspace`로 주입됨)
*   **레거시 정적 파일 보관소**: `legacy/` (이전 루트 수준의 정적 HTML/CSS/JS 파일 및 구버전 `web_dashboard` 등이 백업되어 배포 대상에서 완전히 제외되었습니다.)

### 2. 빌드 명령어 (Build Command)

로컬 빌드 및 배포 환경에서 최신 수정본을 반영하기 위해 다음 명령어를 배포 루트(`000_월드개발페이지/frontend`)에서 실행합니다:

```bash
cd 000_월드개발페이지/frontend
npm run build
```

이 명령어는 내부적으로 `build.js` 스크립트를 작동시켜:
1. `000_월드개발페이지/backend` 폴더에서 `npm run build`를 실행하여 React 앱을 컴파일합니다 (`dist` 생성).
2. `000_월드개발페이지/frontend/dist` 디렉토리를 초기화하고 정적 HTML, CSS, JS, Assets 파일을 복사합니다.
3. React 빌드 결과물(`backend/dist`)을 `frontend/dist/workspace`로 이동 및 결합합니다.

### 3. Cloudflare Pages 설정값 (Cloudflare Pages Config)

Cloudflare Pages에 프로젝트를 배포할 때 아래와 같이 빌드 설정을 반드시 일치시켜 주십시오:

| 설정 항목 (Configuration Item) | 설정 값 (Configuration Value) |
| :--- | :--- |
| **Root Directory** | `000_월드개발페이지/frontend` |
| **Build Command** | `npm run build` |
| **Build Output Directory** | `dist` |

이 구성을 통해 GitHub 커밋 및 푸시가 발생할 때마다 자동으로 `npm ci` ➔ `npm run build` ➔ `dist` 배포 파이프라인이 작동하며, 지구 배경화면(`space-bg.png`) 등 모든 자산이 유실 없이 정상 배포됩니다.

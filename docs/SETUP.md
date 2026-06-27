# Setup

## 요구 환경

- Windows PowerShell
- Python 3.10 이상
- Node.js 20 이상 권장
- npm

## Python 의존성

```powershell
cd C:\dev\python
python -m pip install -r requirements.txt
```

`requirements.txt`는 Python 엔진에서 실제로 참조하는 외부 패키지만 포함합니다.

- `google-generativeai`: Python Gemini fallback/생성 엔진
- `Pillow`: 로컬 WebP 이미지 생성
- `requests`: Tistory API 호출

## Node 의존성

```powershell
cd C:\dev\python\03_월드개발페이지\backend
npm ci
```

## 로컬 실행

개발 모드:

```powershell
cd C:\dev\python\03_월드개발페이지\backend
npm run dev:all
```

빌드 결과 확인:

```powershell
cd C:\dev\python\03_월드개발페이지\frontend
npm run build

cd C:\dev\python\03_월드개발페이지\backend
npm run server
```

확인 URL:

- 포털: `http://localhost:5000`
- 워크스페이스: `http://localhost:5000/workspace/index.html?view=styler`
- API 상태: `http://localhost:5000/api/`

인앱 브라우저에서 `localhost:8000`을 계속 사용하려면:

```powershell
cd C:\dev\python\03_월드개발페이지\backend
$env:PORT = "8000"
node server.js
```

확인 URL:

- 포털: `http://localhost:8000`
- 워크스페이스: `http://localhost:8000/workspace/index.html?view=styler`
- API 상태: `http://localhost:8000/api/`

## 검증

```powershell
cd C:\dev\python
.\scripts\validate-world.ps1
```

## 민감 정보

`.env`, 발행 토큰, Telegram 토큰, Tistory/WordPress 인증 값은 문서나 테스트 명령에 포함하지 않습니다.

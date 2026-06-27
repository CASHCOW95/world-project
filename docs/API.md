# API

Base URL: `http://localhost:5000`

## Health

### `GET /api/`

서버 동작 여부를 확인합니다.

응답:

```json
{
  "ok": true,
  "message": "API server is running. Open /workspace/index.html?view=styler for the dashboard."
}
```

## Credits

### `GET /api/credits`

데모 크레딧 수를 반환합니다.

### `POST /api/credits/reset`

데모 크레딧을 초기화합니다.

## Publisher Profiles

### `GET /api/publisher-profiles`

발행 프로필 설정을 반환합니다.

### `PUT /api/publisher-profiles`

발행 프로필 설정을 저장합니다.

### `POST /api/publisher-profiles/test`

선택한 프로필의 필수 입력값을 검사합니다.

요청 예:

```json
{
  "platform": "tistory",
  "profile_id": "tistory-default"
}
```

## Generation

### `POST /api/generate`

Gemini 기반 단일 글 생성을 수행합니다. API 키가 없으면 데모 템플릿을 반환합니다.

### `GET /api/categories`

카테고리 JSON을 반환합니다.

### `GET /api/keywords?category=정부지원금`

카테고리별 키워드 후보를 반환합니다.

### `POST /api/generate-titles`

선택 키워드의 제목 후보를 생성합니다.

요청 예:

```json
{
  "keyword": "정부지원금",
  "category": "정부지원금"
}
```

## Pipeline

### `POST /api/publish-pipeline`

단일 글 생성/발행 파이프라인을 SSE 형식으로 스트리밍합니다.

주요 필드:

- `keyword`
- `platform`
- `profile_id`
- `style`
- `category`
- `length`
- `faq_count`
- `img_prompt`
- `seo_strength`
- `publish`

### `POST /api/cluster-generate`

토픽 클러스터 구조 미리보기를 생성합니다.

### `POST /api/cluster-publish`

클러스터 글 생성/발행 파이프라인을 SSE 형식으로 스트리밍합니다.

## History and Output

### `GET /api/history`

로컬 생성/발행 이력을 반환합니다.

### `GET /api/post-preview/:postId`

로컬 원고 검수용 HTML을 반환합니다.

### `GET /api/export-download`

`web_dashboard/output` 산출물을 ZIP으로 내려받습니다.

### `GET /api/published-posts`

발행된 글 목록을 반환합니다.

### `GET /api/internal-links`

내부 링크 그래프 데이터를 반환합니다.

### `GET /api/dashboard-stats`

발행 대시보드 통계를 반환합니다.

## Integrations

### `POST /api/telegram-test`

Telegram 연결 값을 테스트합니다.

### `POST /api/research`

키워드 기반 자료 수집 결과를 반환합니다.

# 혁신AI 랜딩페이지 벤치마킹 분석 및 디자인 가이드

## 목적

혁신AI 랜딩페이지의 디자인 철학, 레이아웃 구조, 색상 체계, UX 패턴을 분석하여 향후 모든 웹페이지 및 랜딩페이지 제작 시 일관된 디자인 시스템으로 활용한다.

---

# 핵심 결론

혁신AI의 강점은 화려한 디자인이 아니다.

강점은 다음 3가지다.

1. 정보 밀도가 낮다.
2. CTA가 명확하다.
3. 시선 흐름이 자연스럽다.

디자인보다 "전환율 중심 구조"를 벤치마킹해야 한다.

---

# 디자인 철학

## 원칙

화려함 금지

심플함 우선

검정 기반

보라색 포인트

넓은 여백

큰 카드

짧은 문장

많은 설명 금지

---

# 컬러 시스템

## Background

```css
#09090B
```

Tailwind

```css
bg-zinc-950
```

---

## Section Background

```css
#18181B
```

Tailwind

```css
bg-zinc-900
```

---

## Border

```css
#27272A
```

Tailwind

```css
border-zinc-800
```

---

## Primary Text

```css
#FAFAFA
```

Tailwind

```css
text-zinc-50
```

---

## Secondary Text

```css
#A1A1AA
```

Tailwind

```css
text-zinc-400
```

---

## Primary CTA

```css
#6366F1
```

Tailwind

```css
bg-indigo-500
```

Hover

```css
#4F46E5
```

Tailwind

```css
hover:bg-indigo-600
```

---

## Success

```css
#10B981
```

Tailwind

```css
bg-emerald-500
```

---

# 폰트

## 기본

Pretendard Variable

```css
font-family:
Pretendard Variable,
Pretendard,
sans-serif;
```

---

# 레이아웃 규칙

## 최대 너비

```css
max-width: 1280px;
```

Tailwind

```css
max-w-7xl
```

---

## Section Padding

```css
padding-top: 96px;
padding-bottom: 96px;
```

Tailwind

```css
py-24
```

---

## Container

```css
px-6
lg:px-8
```

---

# Radius 규칙

절대 작은 Radius 사용 금지

사용

```css
12px
16px
24px
```

Tailwind

```css
rounded-xl
rounded-2xl
rounded-3xl
```

금지

```css
rounded-sm
rounded-md
```

---

# Shadow 규칙

강한 그림자 금지

사용

```css
shadow-lg
```

또는

```css
border
```

위주

---

# 간격 시스템

8pt Grid 사용

허용

```css
8
16
24
32
48
64
96
```

비허용

```css
13
17
21
29
```

---

# Hero 영역 구조

## 구성

1. Badge
2. 메인 헤드라인
3. 서브 헤드라인
4. CTA 버튼
5. 제품 미리보기

---

## 헤드라인 규칙

최대 2줄

최대 12단어

설명 금지

가치만 전달

예시

"24시간 자동사냥"

"5분 설정으로 끝"

"수동사냥을 끝내세요"

---

# 카드 디자인 규칙

## 구조

아이콘

제목

설명

---

설명은 최대 2줄

카드 높이는 동일하게 유지

---

# 랜딩페이지 구조

## Section 1

Hero

---

## Section 2

문제 제기

현재 사용자가 겪는 불편

---

## Section 3

해결 방법

프로그램 소개

---

## Section 4

주요 기능

3~6개

---

## Section 5

전후 비교

Before / After

---

## Section 6

실제 사용 화면

스크린샷

GIF

영상

---

## Section 7

FAQ

---

## Section 8

최종 CTA

구매 버튼

---

# 전환율 규칙

기능 설명 금지

결과 설명 우선

나쁜 예

"자동 포션 사용"

좋은 예

"24시간 사냥 유지"

---

나쁜 예

"자동 이동"

좋은 예

"자리 이탈 없이 사냥"

---

나쁜 예

"매크로 엔진"

좋은 예

"5분 설정 후 자동 운영"

---

# 버튼 규칙

Primary 버튼은 페이지당 1개

Secondary 버튼은 보조

CTA 문구는 행동형

사용

"지금 시작하기"

"구매하기"

"체험하기"

금지

"더 알아보기"

"확인"

"클릭"

---

# 개발 규칙

Tailwind 우선

Pretendard 사용

다크모드 기본

모바일 우선

Desktop 확장

컴포넌트 재사용

색상 하드코딩 금지

Theme 변수 사용

---

# 최종 원칙

우리는 디자인을 만드는 것이 아니라 판매 페이지를 만든다.

모든 UI 요소는 아래 질문을 통과해야 한다.

"이 요소가 구매 전환율을 높이는가?"

YES → 유지

NO → 삭제

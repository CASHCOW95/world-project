# AUTOmaple 통합 기술 명세서 (Master Technical Specification)

## 1. 프로젝트 개요
- **최종 정식 버전**: v1.0.0 (Master Original)
- **현재 진행 버전**: v1.0.1 (Development)
- **핵심 목표**: 인간의 행동 패턴을 완벽히 모방하는 투명 도형 자동 추적 솔루션 구현.

## 2. v1.0.0 핵심 구현 기술 (Original Specs)

### 2.1 Human-Engine (지능형 마우스 제어)
- **알고리즘**: 베지에 곡선(Bézier Curve) 기반 궤적 생성 및 가속도 감쇠(Damping) 적용.
- **특징**:
  - 타겟 거리에 따른 동적 LERP(Linear Interpolation) 팩터 조절.
  - 목표 지점 근접 시 의도적인 오버슈트(Overshoot) 및 미세 손떨림(Micro-shaking) 시뮬레이션.
  - 탐지 시스템 우회를 위한 비선형 이동 경로 확보.

### 2.2 도형 탐지 및 추적 (Computer Vision)
- **색상 분석**: `anti1.png`를 기반으로 한 동적 HSV 색 공간 추출 및 필터링.
- **배경 제거**: `game_background_pattern.png`와의 배경 차분(`absdiff`)을 통한 움직이는 객체 분리.
- **최적화**: 모폴로지 연산(Opening/Closing)을 통한 노이즈 제거 및 50FPS급 실시간 루프 성능.

### 2.3 시스템 아키텍처
- **UI Framework**: PySide6 기반 대시보드 (CPU, RAM, 가동 시간 실시간 모니터링).
- **시그널 시스템**: 백그라운드 연산 스레드와 UI 간의 비동기 통신(`Signal/Slot`).
- **리소스 관리**: `sys._MEIPASS`를 활용한 빌드 환경 내 리소스 접근 최적화.

## 3. v1.0.1 업데이트 로드맵: Lucas-Kanade 알고리즘

### 3.1 기술 도입 배경
현재의 배경 차분 방식은 고속 이동 물체에 대한 특징 보존이 어려울 수 있음. 이를 해결하기 위해 픽셀의 광학적 흐름을 분석하는 기술 도입 필요.

### 3.2 Lucas-Kanade 광학 흐름 (Optical Flow) 상세 계획
- **핵심 함수**: OpenCV `cv2.calcOpticalFlowPyrLK` 활용.
- **작동 원리**:
  - 도형 내의 강한 특징점(Corner)을 추출하여 프레임 간 이동 벡터 계산.
  - 투명도가 높은 객체가 배경과 겹칠 때도 특징점 기반의 정밀 추적 유지.
  - 비선형/불규칙 경로(당구공 튀김 현상 등)에 대한 예측 보간력 강화.
- **기대 효과**: 추적 탈조 현상 0% 지향 및 초고속 트래킹 안정성 확보.

## 4. 버전 관리 및 운영 원칙
1. **0.0.1 증분 원칙**: 모든 기능 수정 및 추가 시 버전을 0.0.1 상향한다.
2. **원본 백업**: v1.0.0 마스터 데이터는 `deploy/backup/v1.0.0`에 영구 보존한다.
3. **기록 의무**: 모든 기술적 변경 사항은 본 명세서에 즉시 업데이트하여 누락을 방지한다.

---
*Last Updated: 2026.06.03*
*Status: v1.0.1 Developing (Lucas-Kanade Integration)*

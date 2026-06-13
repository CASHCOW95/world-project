# AUTOmaple v1.0.0 통합 기술 명세서 (Master Original)

## 1. 프로젝트 개요
- **공식 버전**: v1.0.0
- **상태**: 정식 원본 (Master Original)
- **개발 환경**: Python 3.14, PySide6, OpenCV, PyAutoGUI, mss

## 2. 핵심 기술 사양 (Core Technologies)

### 2.1 Human-Engine (인간미 트래킹)
- **알고리즘**: 베지에 곡선(Bézier Curve) 및 동적 선형 보간(Lerp) 결합.
- **가속도 제어**: 타겟과의 거리에 따른 가변 Lerp Factor 적용 (원거리 고속, 근거리 저속 정밀 추적).
- **인간 행동 시뮬레이션**: 
  - **오버슈트(Overshoot)**: 목표 지점 도달 시 관성에 의한 미세 지나침 구현.
  - **마이크로 쉐이킹(Micro-shaking)**: random noise를 이용한 손떨림 및 미세 진동 재현.

### 2.2 도형 추적 엔진 (Shape Tracking)
- **현재 구현 (v1.0.0)**:
  - `game_background_pattern.png`를 이용한 배경 차분(Background Subtraction - `absdiff`).
  - `anti1.png`에서 타겟 색상(HSV)을 동적으로 추출하여 마스킹 처리.
  - 모폴로지 연산(Morphology Opening)을 통한 노이즈 제거 및 50FPS급 실시간 루프 성능 확보.
- **차세대 기술 (v1.0.1 목표)**: **Lucas-Kanade 광학 흐름(Optical Flow)**
  - OpenCV의 `calcOpticalFlowPyrLK`를 활용하여 프레임 간 픽셀의 이동 벡터 계산.
  - 형상이 뚜렷하지 않은 반투명 객체의 움직임을 수학적으로 추론하여 트래킹 안정성 극대화.

### 2.3 UI & 시스템 대시보드
- **시그널 아키텍처**: `PySide6.QtCore.Signal`을 통한 백그라운드 스레드와 UI 간의 비동기 통신.
- **동적 레이아웃**: `create_data_row` 메서드를 통한 실시간 지표(가동 시간, 명령 횟수, 탐지 기록) QLabel 생성 및 렌더링.

## 3. 운영 및 버전 관리 원칙 (0.0.1 Rule)
1. **버전 증분**: 모든 수정 및 업그레이드 시 버전 번호를 **0.0.1** 단위로 상향한다.
2. **원본 백업**: v1.0.0은 정식 원본으로 정의하며, `deploy/backup/v1.0.0`에 영구 보존한다.
3. **업데이트 기록**: 모든 변경 사항은 본 문서의 '업데이트 히스토리' 섹션에 누락 없이 기록한다.

## 4. 업데이트 히스토리
- **v1.0.0 (2026.06.03)**:
  - 최초 정식 원본 릴리즈.
  - `AttributeError: create_data_row` 런타임 오류 완벽 해결.
  - Human-Engine 및 투명 도형 추적 로직 통합.

---
*본 문서는 AUTOmaple 프로젝트의 공식 기술 명세서이며, Lucas-Kanade 등 핵심 알고리즘의 발전 과정을 기록합니다.*

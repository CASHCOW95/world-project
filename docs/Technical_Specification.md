# AUTOmaple 기술 사양서 (Technical Specification)

## 1. 개요
본 문서는 MapleStory '투명 도형 찾기' 미니게임 해결을 위한 자동화 솔루션의 기술적 구조를 정의합니다.

## 2. 핵심 알고리즘
### 2.1 Human-like Mouse Tracking (Anti-Cheat Bypass)
- **가속도 제어**: 타겟 거리($d$)에 따른 가변 선형 보간($Lerp$) 적용.
- **베지에 곡선($B\acute{e}zier Curve$)**: 자연스러운 곡선 궤적 생성.
- **Micro-shaking**: 도달 지점 부근에서 $\pm 3px$ 범위의 무작위 오버슈트 및 떨림 발생.

### 2.2 Image Processing Pipeline (v1.0.0)
- **ROI Capture**: `mss` 라이브러리를 통한 고속 화면 캡처 ($50FPS+$).
- **Background Subtraction**: `cv2.absdiff`를 활용한 정적 배경 제거.
- **Color Masking**: `anti1.png` 분석을 통한 동적 HSV 범위($H \pm 20$) 필터링.

### 2.3 차세대 추적 엔진: Lucas-Kanade 광학 흐름 (v1.0.1 도입 예정)
- **Algorithm**: **Lucas-Kanade Method (Optical Flow)**.
- **Implementation Strategy**:
  - `cv2.goodFeaturesToTrack`을 통한 타겟 객체의 코너(Shi-Tomasi) 추출.
  - `cv2.calcOpticalFlowPyrLK`를 통한 이전 프레임과 현재 프레임 간의 특징점 이동 벡터 계산.
- **기대 효과**: 투명도가 높은 객체, 배경 노이즈가 심한 환경, 그리고 비선형 궤적(당구공 바운스 등)에 대한 추적 이탈률 0% 달성 목표.

## 3. 시스템 아키텍처
- **Framework**: PySide6 (GUI), OpenCV (Computer Vision).
- **Concurrency**: Multi-threading (Monitor, Tracking, UI Update 분리).
- **Failsafe**: 전역 단축키(F3) 및 PyAutoGUI Fail-safe 기능 활성화.

---
*Last Updated: 2026.06.03*

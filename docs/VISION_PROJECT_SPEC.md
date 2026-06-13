# AUTOmaple Vision Project Specification (v1.0.1)

## 1. 프로젝트 목표 (Project Objective)
본 명세서는 AUTOmaple의 차세대 비전 트래킹 엔진인 **v1.0.1** 개발을 위한 구체적이고 섬세한 기술 청사진입니다. 핵심 목표는 기존의 '색상 기반 배경 차분' 방식을 뛰어넘어, **Lucas-Kanade 광학 흐름 (Optical Flow)** 알고리즘을 도입하여 메이플스토리의 '투명 도형 찾기' 거탐을 완벽히, 그리고 인간처럼 부드럽게 추적하는 것입니다.

## 2. 핵심 기술 스택 및 알고리즘
### 2.1 Shi-Tomasi Corner Detection (`cv2.goodFeaturesToTrack`)
- **목적**: 투명 도형 내에서 추적하기 가장 좋은 강한 특징점(코너)을 최초 포착합니다.
- **작동 방식**:
  - `anti1.png`를 기반으로 필터링된 도형의 대략적인 ROI(Region of Interest) 내부에서 가장 뚜렷한 픽셀 패턴을 찾습니다.
  - 투명도가 높아 경계가 모호하더라도 내부 텍스처의 미세한 변화를 특징점으로 삼아 추적의 기준점으로 설정합니다.

### 2.2 Lucas-Kanade Optical Flow (`cv2.calcOpticalFlowPyrLK`)
- **목적**: 이전 프레임에서 찾은 특징점이 현재 프레임에서 어디로 이동했는지 픽셀 단위의 벡터로 계산합니다.
- **작동 방식**:
  - **Pyramid (피라미드)** 접근법을 사용하여 도형이 순간적으로 크게 튀거나 빠르게 이동하더라도 모션 벡터를 놓치지 않도록 다해상도로 분석합니다.
  - 프레임 간의 밝기(Intensity) 불변성을 가정하여, 투명 도형의 배경이 바뀌더라도 도형 자체의 미세한 픽셀 흐름을 끈질기게 추적합니다.
  - 추적된 포인트들의 평균 이동 벡터를 계산하여 타겟의 최종 중심 좌표(cx, cy)를 도출합니다.

### 2.3 Human-Engine 2.0 (추적 데이터 연동)
- Lucas-Kanade 엔진이 산출한 50FPS급의 고정밀 목표 좌표(tx, ty)를 기존의 **Human-Engine**에 전달합니다.
- **동적 가속도 (Dynamic Lerp)**: 목표물이 멀어지는 속도(Optical Flow 벡터의 크기)에 비례하여 마우스의 추적 속도를 탄력적으로 조절합니다.
- **예측 보간 (Predictive Tracking)**: 도형이 너무 빨라 잠시 시야에서 사라지더라도, 마지막으로 계산된 이동 벡터 방향으로 마우스를 살짝 관성 이동시켜 인간의 '예측 추적' 본능을 모방합니다.

## 3. 구체적 작동 파이프라인 (Execution Flow)
1. **초기화 및 특징점 탐색 (Initialization & Feature Extraction)**
   - 도형 엔진 활성화 시, 기존 방식(배경 차분 + 색상 필터링)을 사용하여 도형이 최초로 나타나는 프레임을 포착.
   - 도형의 Bounding Box 내부에서 `cv2.goodFeaturesToTrack`을 호출하여 추적할 포인트 배열(Points) 획득.
2. **광학 흐름 추적 루프 (Optical Flow Tracking Loop)**
   - 매 프레임(0.02초 간격)마다 `cv2.calcOpticalFlowPyrLK`를 호출.
   - 이전 프레임(prev_gray)과 현재 프레임(gray) 이미지를 비교하여 포인트 배열의 새로운 위치 계산.
   - 추적에 성공한 포인트(status == 1)들의 무게중심을 구하여 목표 타겟 좌표 갱신.
3. **포인트 소실 대응 (Feature Recovery)**
   - 궤적 변화나 투명도 간섭으로 추적 포인트가 일정 수 이하로 떨어지면, 즉시 1번 단계로 돌아가 특징점을 재추출(Re-initialization).
4. **마우스 제어 (Mouse Control)**
   - 산출된 목표 좌표를 `human_mouse_move`에 전달하여 드래그 상태(`pyautogui.mouseDown()`)를 유지하며 부드럽게 추적.

## 4. 장애 조치 및 예외 처리 (Failsafe)
- **추적 실패 (Tracking Failure)**: 5프레임 이상 Optical Flow가 유효한 벡터를 찾지 못하면 드래그를 즉시 해제(mouseUp)하고 대기 모드로 전환.
- **안전성 (Safety)**: F3 단축키 입력 시 어떠한 상태에 있더라도 CV 연산을 중단하고 마우스 제어권을 사용자에게 즉시 반환.

## 5. 이미지 리소스 규격 (Image Resource Specifications)
- **사진파일 크기 고정**: 프로그램에서 템플릿 매칭 및 감지에 사용하는 모든 탐색 대상 사진파일(예: `anti1.png` ~ `anti4.png` 등)의 픽셀 크기는 가로/세로 **300픽셀(300px)**로 고정하여 일관성 있게 관리합니다.

---
*본 명세서는 AUTOmaple v1.0.1 (Lucas-Kanade Update) 개발을 위한 최상위 지침서로 작용하며, 단 하나의 세부 로직도 누락 없이 구현될 것입니다.*

VISION_PROJECT_SPEC.md
Computer Vision Learning Project
Transparent Shape Detection & Tracking System
1. Project Goal

본 프로젝트의 목적은 게임 화면에 표시되는 투명 도형을 실시간으로 탐지하고 추적하는 컴퓨터 비전 시스템을 구축하는 것이다.

본 프로젝트는 학습 목적의 화면 분석 프로젝트이며 다음 기능만 구현한다.

포함 기능
실시간 화면 캡처
ROI 추출
HSV 색상 분석
윤곽선 검출
객체 후보 탐색
중심 좌표 계산
객체 추적
Optical Flow 분석
Kalman Filter 예측
디버그 시각화
FPS 성능 측정
제외 기능
자동 클릭
자동 마우스 이동
자동 키 입력
게임 조작 기능
매크로 기능
2. Technology Stack
Required
Python 3.12+
OpenCV
NumPy
MSS
SciPy
Optional
opencv-contrib-python
PyQt5
Tkinter
3. System Architecture
Screen Capture
        ↓
ROI Detection
        ↓
Preprocessing
        ↓
HSV Analysis
        ↓
Contour Detection
        ↓
Candidate Filtering
        ↓
Center Extraction
        ↓
Tracking
        ↓
Visualization
        ↓
Performance Metrics
4. Project Structure
project/

capture/
│
├── screen_capture.py

vision/
│
├── preprocess.py
├── hsv_filter.py
├── contour_detector.py
├── candidate_filter.py

tracking/
│
├── tracker.py
├── optical_flow.py
├── kalman_tracker.py

ui/
│
├── debug_window.py

utils/
│
├── fps_counter.py
├── config.py

main.py
5. Screen Capture Module
Objective

실시간으로 화면을 캡처한다.

Requirements
MSS 사용
30FPS 이상
특정 영역 캡처 가능
전체 화면 캡처 가능
NumPy 배열 반환
Interface
class ScreenCapture:

    def grab_frame(self):
        pass
6. ROI Manager
Objective

관심 영역(ROI)을 설정한다.

Features
ROI 생성
ROI 저장
ROI 수정
ROI Crop
Interface
class ROIManager:

    def set_roi(self):
        pass

    def crop(self):
        pass
7. Preprocessing Module
Objective

노이즈 제거 및 대비 향상

Pipeline
Gaussian Blur
Histogram Equalization
Contrast Enhancement
Noise Reduction
Example
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

blur = cv2.GaussianBlur(
    gray,
    (5,5),
    0
)

equalized = cv2.equalizeHist(blur)
8. HSV Analysis
Objective

HSV 색공간에서 흰색 객체 검출

RGB 사용 금지

HSV 사용

White Range
lower_white = np.array([
    0,
    0,
    180
])

upper_white = np.array([
    180,
    70,
    255
])
Mask Generation
mask = cv2.inRange(
    hsv,
    lower_white,
    upper_white
)
9. HSV Tuning Tool

실시간 HSV 조절 기능 구현

Trackbars
H Min
H Max
S Min
S Max
V Min
V Max

실시간 반영

10. Contour Detection
Objective

객체 후보 검출

API
contours, hierarchy = cv2.findContours(
    mask,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
)
11. Candidate Filtering
Objective

노이즈 제거

Metrics
Area
cv2.contourArea()
Perimeter
cv2.arcLength()
Circularity
4πA / P²
Aspect Ratio
width / height
Solidity
area / hull_area
12. Center Coordinate Extraction
Objective

객체 중심 계산

Example
moments = cv2.moments(cnt)

cx = int(
    moments["m10"] /
    moments["m00"]
)

cy = int(
    moments["m01"] /
    moments["m00"]
)
Output
Center X
Center Y
Area
Confidence
13. Object Tracking
Objective

탐지된 객체 지속 추적

Tracker
Primary
cv2.TrackerCSRT_create()
Alternative
KCF
MOSSE
14. Optical Flow
Objective

프레임 간 움직임 분석

Algorithm

Lucas-Kanade

API
cv2.calcOpticalFlowPyrLK()
Output
Motion Vector
Direction
Velocity
15. Kalman Filter
Objective

객체 위치 예측

State
X
Y
Velocity X
Velocity Y
API
cv2.KalmanFilter()
Output
Current Position
Predicted Position
Estimated Velocity
16. Visualization
Draw Elements
ROI
cv2.rectangle()
Bounding Box
cv2.rectangle()
Center Point
cv2.circle()
Tracking Path
cv2.line()
Labels
cv2.putText()
17. Debug Overlay

표시 정보

System
FPS
Frame Time
CPU Usage
Detection
Contour Count
Candidate Count
Detection Confidence
Tracking
Tracking Status
Position
Velocity
18. Performance Targets
Resolution

1920 × 1080

Requirements
30 FPS 이상
탐지 지연 100ms 이하
CPU 사용률 20% 이하
안정적 추적 유지
19. Future Expansion
Medium
Shape Classification
Multi Object Tracking
Adaptive Threshold
Advanced
YOLO Integration
Deep Learning Detector
Segmentation Model
ONNX Runtime Optimization
20. Final Deliverable

프로그램 실행 시 다음 기능이 동작해야 한다.

실시간 화면 캡처
ROI 표시
HSV 마스크 생성
윤곽선 탐지
후보 객체 표시
중심 좌표 계산
객체 추적
Optical Flow 분석
Kalman Filter 예측
디버그 정보 출력
FPS 출력

프로젝트는 학습용 컴퓨터 비전 분석 시스템으로 구현한다.
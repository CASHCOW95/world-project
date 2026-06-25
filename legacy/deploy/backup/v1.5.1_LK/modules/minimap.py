import os
import time
import random
import ctypes
import ctypes.wintypes
import numpy as np
import cv2
import mss
import winsound
import pyautogui
from PySide6.QtWidgets import QApplication

class MinimapDetector:
    def __init__(self, main_win):
        self.main_win = main_win
        
    def get_player_coords(self, sct):
        reg = {"top": self.main_win.reg_t, "left": self.main_win.reg_l, "width": self.main_win.reg_w, "height": self.main_win.reg_h}
        try:
            shot = np.array(sct.grab(reg))
            img = cv2.cvtColor(shot, cv2.COLOR_BGRA2BGR)
            m = self.main_win.color_margin
            low = np.array([
                max(0, self.main_win.base_lower[2]-m), 
                max(0, self.main_win.base_lower[1]-m), 
                max(0, self.main_win.base_lower[0]-m)
            ])
            high = np.array([
                min(255, self.main_win.base_upper[2]+m), 
                min(255, self.main_win.base_upper[1]+m), 
                min(255, self.main_win.base_upper[0]+m)
            ])
            mask = cv2.inRange(img, low, high)
            
            cx, cy = -1, -1
            if np.any(mask):
                M = cv2.moments(mask)
                if M["m00"] > 0:
                    cx, cy = int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"])
            return cx, cy, img, mask
        except:
            return -1, -1, None, None

    def detect_floor_layers(self):
        reg = {"top": self.main_win.reg_t, "left": self.main_win.reg_l, "width": self.main_win.reg_w, "height": self.main_win.reg_h}
        try:
            with mss.mss() as sct:
                shot = np.array(sct.grab(reg))
                img = cv2.cvtColor(shot, cv2.COLOR_BGRA2BGR)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                
                # 각 y 행마다 밝기가 100 이상인 픽셀 수 계산
                threshold = 100
                row_counts = np.sum(gray > threshold, axis=1)
                
                # 너비의 15% 이상이 밝은 픽셀인 행 찾기
                min_pixels = int(self.main_win.reg_w * 0.15)
                candidate_ys = np.where(row_counts >= min_pixels)[0]
                
                # 인접한 Y값들을 그룹화
                layers = []
                if len(candidate_ys) > 0:
                    current_group = [candidate_ys[0]]
                    for y in candidate_ys[1:]:
                        if y - current_group[-1] <= 4:  # 인접 오차 4px
                            current_group.append(y)
                        else:
                            layers.append(int(np.mean(current_group)))
                            current_group = [y]
                    layers.append(int(np.mean(current_group)))
                
                # Y값 오름차순 정렬 (위에서 아래로)
                layers = sorted(layers)
                return layers
        except Exception as e:
            return []

    def find_maplestory_window_rect(self):
        hwnd_list = [None]
        
        def enum_windows_callback(hwnd, extra):
            if ctypes.windll.user32.IsWindowVisible(hwnd):
                length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
                    title = buff.value.lower()
                    if "maplestory" in title:
                        hwnd_list[0] = hwnd
                        return False  # 중단
            return True
            
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        ctypes.windll.user32.EnumWindows(WNDENUMPROC(enum_windows_callback), 0)
        
        hwnd = hwnd_list[0]
        if hwnd:
            rect = ctypes.wintypes.RECT()
            ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
            return rect.left, rect.top, rect.right, rect.bottom
        return None

    def auto_detect_minimap(self):
        if self.main_win.is_running:
            self.main_win.logger.log("[미니맵] 사냥 진행 중에는 미니맵 재탐색이 금지됩니다.", "MINIMAP")
            return False

        # 1. 메이플 게임창 탐색 시도
        win_coords = self.find_maplestory_window_rect()
        if not win_coords:
            self.main_win.logger.log("자동 인식 실패: 메이플스토리 게임창을 찾을 수 없습니다. (창모드 활성화 필수)", "MINIMAP")
            winsound.Beep(800, 300)
            return False
            
        win_l, win_t, win_r, win_b = win_coords
        self.main_win.logger.log(f"메이플스토리 게임창 감지 완료! -> 위치: ({win_l}, {win_t}), 크기: {win_r-win_l}x{win_b-win_t}", "MINIMAP")
        self.main_win.logger.log("게임창 좌상단 (400x300) 영역으로 미니맵 복합 정밀 자동 탐색을 실행합니다.", "MINIMAP")
        
        try:
            reg = {
                "top": win_t,
                "left": win_l,
                "width": min(400, win_r - win_l),
                "height": min(300, win_b - win_t)
            }
            with mss.mss() as sct:
                shot = np.array(sct.grab(reg))
                img = cv2.cvtColor(shot, cv2.COLOR_BGRA2BGR)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                
                # --- 캐릭터 좌표 색상 (#FEFD7D) BGR (125, 253, 254) ---
                target_bgr = (125, 253, 254)
                m = 5
                low = np.array([target_bgr[0]-m, target_bgr[1]-m, target_bgr[2]-m])
                high = np.array([target_bgr[0]+m, target_bgr[1]+m, target_bgr[2]+m])
                mask = cv2.inRange(img, low, high)
                
                # 에지 분석용
                edges = cv2.Canny(gray, 30, 150)
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
                dilated = cv2.dilate(edges, kernel, iterations=1)
                contours, _ = cv2.findContours(dilated, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                
                # 노란색 후보 도트 검출
                yellow_contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                candidates = []
                for yc in yellow_contours:
                    area = cv2.contourArea(yc)
                    if 1 <= area <= 60:
                        M = cv2.moments(yc)
                        if M["m00"] > 0:
                            cx = int(M["m10"]/M["m00"])
                            cy = int(M["m01"]/M["m00"])
                            candidates.append((cx, cy))
                
                best_rect = None
                best_score = -1
                
                # 모든 윤곽선 검증 및 복합 스코어 계산
                for c in contours:
                    x, y, w, h = cv2.boundingRect(c)
                    if 120 < w < 280 and 60 < h < 180:
                        score = 5 # 외곽 프레임 기본 점수
                        
                        # 1) 캐릭터 노란색 도트 (#FEFD7D) 포함 여부
                        has_yellow = False
                        for cx, cy in candidates:
                            if x <= cx <= x+w and y <= cy <= y+h:
                                has_yellow = True
                                break
                        if has_yellow:
                            score += 10
                            
                        # 2) 상단 타이틀바 영역 내 MINI MAP 텍스트 & WORLD 버튼 존재 여부
                        y_start = max(0, y-28)
                        y_end = y
                        if y_end > y_start and x+w > x:
                            header_edges = edges[y_start:y_end, x:x+w]
                            header_dilated = dilated[y_start:y_end, x:x+w]
                            
                            # MINI MAP 텍스트 검증: 에지 밀도 검사
                            if header_edges.size > 0:
                                edge_density = np.mean(header_edges > 0)
                                if edge_density > 0.04: # 에지 밀도 4% 초과 시 텍스트 존재로 판정
                                    score += 5
                                    
                            # WORLD 버튼 검증: 타이틀바 내부의 버튼 크기 컨투어 탐색
                            if header_dilated.size > 0:
                                sub_contours, _ = cv2.findContours(header_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                                for sc in sub_contours:
                                    _, _, sw, sh = cv2.boundingRect(sc)
                                    if 10 <= sw <= 45 and 8 <= sh <= 25:
                                        score += 5
                                        break
                                        
                        if score > best_score:
                            best_score = score
                            best_rect = (x, y, w, h)
                            
                # 복합 점수 기준 (최소 15점 이상 확보한 후보 중 최고점 선택)
                if best_rect and best_score >= 15:
                    x, y, w, h = best_rect
                    self.main_win.logger.log(f"[미니맵] 복합 검증 매칭 성공 (스코어: {best_score}/25)", "MINIMAP")
                else:
                    # 복합 검증 실패 시 폴백 기하 에지 매칭 시도
                    self.main_win.logger.log("[미니맵] 복합 검증 실패 -> 폴백 기하학 테두리 매칭 실행", "MINIMAP")
                    candidate_rects = []
                    for c in contours:
                        x, y, w, h = cv2.boundingRect(c)
                        if 120 < w < 280 and 60 < h < 180:
                            if x < 150 and y < 120:
                                candidate_rects.append((x, y, w, h))
                    if candidate_rects:
                        best_rect = max(candidate_rects, key=lambda r: r[2] * r[3])
                    else:
                        best_rect = None
                        
                if best_rect:
                    x, y, w, h = best_rect
                    new_l = win_l + x + 3
                    new_t = win_t + y + 3
                    new_w = w - 6
                    new_h = h - 6
                    
                    self.main_win.reg_l = new_l
                    self.main_win.reg_t = new_t
                    self.main_win.reg_w = new_w
                    self.main_win.reg_h = new_h
                    
                    margin_px = int(self.main_win.reg_w * 0.15)
                    self.main_win.x_min = margin_px
                    self.main_win.x_max = self.main_win.reg_w - margin_px
                    self.main_win.x_min_slider.setValue(self.main_win.x_min)
                    self.main_win.x_max_slider.setValue(self.main_win.x_max)
                    
                    self.main_win.logger.log(f"[미니맵] 미니맵 영역 확정 (L:{new_l}, T:{new_t}, W:{new_w}, H:{new_h})", "MINIMAP")
                    winsound.Beep(1200, 200)
                    self.main_win.settings_manager.save_settings_silently()
                    return True
                else:
                    # 최종 폴백 기본 영역
                    new_l = win_l + 10
                    new_t = win_t + 10
                    new_w = 200
                    new_h = 150
                    self.main_win.reg_l = new_l
                    self.main_win.reg_t = new_t
                    self.main_win.reg_w = new_w
                    self.main_win.reg_h = new_h
                    self.main_win.x_min = 20
                    self.main_win.x_max = 180
                    self.main_win.x_min_slider.setValue(self.main_win.x_min)
                    self.main_win.x_max_slider.setValue(self.main_win.x_max)
                    self.main_win.logger.log("미니맵 검출 실패로 게임창 기준 200x150 기본 영역으로 강제 설정했습니다.", "MINIMAP")
                    winsound.Beep(1000, 300)
                    self.main_win.settings_manager.save_settings_silently()
                    return True
        except Exception as e:
            self.main_win.logger.log(f"자동 인식 스캔 예외 발생: {str(e)}", "MINIMAP")
            return False


    def anti_macro_loop(self):
        while not self.main_win.stop_threads:
            if self.main_win.use_anti_macro and self.main_win.is_running:
                try:
                    with mss.mss() as sct:
                        img = np.array(sct.grab(sct.monitors[0]))
                        gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
                        for i in range(1, 4):
                            p = os.path.join(self.main_win.base_dir, f"anti{i}.png")
                            if os.path.exists(p):
                                tm = cv2.imread(p, 0)
                                if tm is not None and np.max(cv2.matchTemplate(gray, tm, cv2.TM_CCOEFF_NORMED)) > 0.8:
                                    self.main_win.err_cnt += 1
                                    self.main_win.signals.alert_signal.emit()
                                    self.main_win.signals.shape_start_signal.emit()
                                    self.main_win.logger.log("거짓 탐지기 매칭 경보 감지됨!", "SYSTEM")
                                    break
                except:
                    pass
                time.sleep(2)
            else:
                time.sleep(1)

    def shape_tracking_loop(self):
        lk_params = dict(winSize=(21, 21), maxLevel=3, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))
        feature_params = dict(maxCorners=20, qualityLevel=0.1, minDistance=5, blockSize=5)
        old_gray, p0, popup_roi = None, None, None
        is_tracking, last_x, last_y, vx, vy, inertia_cnt = False, None, None, 0.0, 0.0, 0
        MAX_INERTIA_FRAMES = 20
        lost_cnt = 0
        lockon_start_time = None
        bg_cache = {}
        dynamic_bg = None

        while not self.main_win.stop_threads:
            if self.main_win.use_shape_anti:
                try:
                    with mss.mss() as sct:
                        monitor = sct.monitors[1]
                        scr = np.array(sct.grab(monitor))
                        scr_bgr = cv2.cvtColor(scr, cv2.COLOR_BGRA2BGR)
                        frame_gray = cv2.cvtColor(scr_bgr, cv2.COLOR_BGR2GRAY)
                        if popup_roi is None:
                            for bg_name in ["anti0.png", "anti0.1.png"]:
                                bg_path = os.path.join(self.main_win.base_dir, bg_name)
                                if os.path.exists(bg_path):
                                    bg_img = cv2.imread(bg_path, 0)
                                    if bg_img is not None:
                                        res = cv2.matchTemplate(frame_gray, bg_img, cv2.TM_CCOEFF_NORMED)
                                        _, max_val, _, max_loc = cv2.minMaxLoc(res)
                                        if max_val > 0.5: 
                                            popup_roi = (max_loc[0], max_loc[1], bg_img.shape[1], bg_img.shape[0])
                                            break
                            if popup_roi is None:
                                scr_h, scr_w = frame_gray.shape
                                popup_roi = (max(0, (scr_w - 1024) // 2), max(0, (scr_h - 679) // 2 - 20), 1024, 679)
                        
                        rx, ry, rw, rh = popup_roi
                        cropped_gray, cropped_bgr = frame_gray[ry:ry+rh, rx:rx+rw], scr_bgr[ry:ry+rh, rx:rx+rw]
                        log_msg, found_valid, target_pos, is_initial_lockon = "", False, None, False

                        if not is_tracking:
                            if lockon_start_time is None:
                                lockon_start_time = time.time()
                                dynamic_bg = None
                                self.main_win.logger.log("초기 정가운데 락온 탐색 시작 (무제한 탐색)", "MINIMAP")
                            
                            cx_center, cy_center = rw // 2, rh // 2
                            cw_half = 80
                            cx_min, cx_max = cx_center - cw_half, cx_center + cw_half
                            cy_min, cy_max = cy_center - cw_half, cy_center + cw_half
                            
                            if dynamic_bg is None:
                                dynamic_bg = cropped_gray.copy()
                                time.sleep(0.04)
                                continue
                            
                            diff = cv2.absdiff(cropped_gray, dynamic_bg)
                            _, diff_mask = cv2.threshold(diff, 15, 255, cv2.THRESH_BINARY)
                            _, white_mask = cv2.threshold(cropped_gray, 180, 255, cv2.THRESH_BINARY)
                            initial_mask = cv2.bitwise_or(diff_mask, white_mask)
                            contours, _ = cv2.findContours(initial_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                            valid_targets = []
                            for c in contours:
                                area = cv2.contourArea(c)
                                if 300 < area < 30000:
                                    x_b, y_b, w_b, h_b = cv2.boundingRect(c)
                                    if 0.5 < float(w_b)/h_b < 2.0:
                                        hull = cv2.convexHull(c)
                                        hull_area = cv2.contourArea(hull)
                                        if (float(area)/hull_area if hull_area > 0 else 0) > 0.4:
                                            M = cv2.moments(c)
                                            if M["m00"] > 0:
                                                cx_mom, cy_mom = int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"])
                                                if cx_min <= cx_mom <= cx_max and cy_min <= cy_mom <= cy_max:
                                                     valid_targets.append((c, area, (cx_mom, cy_mom)))
                            if valid_targets:
                                best_contour, _, (cx_mom, cy_mom) = max(valid_targets, key=lambda x: x[1])
                                target_pos = (cx_mom, cy_mom)
                                found_valid, is_tracking, is_initial_lockon = True, True, True
                                last_x, last_y, vx, vy, inertia_cnt = cx_mom, cy_mom, 0.0, 0.0, 0
                                lockon_start_time = None
                                lost_cnt = 0
                                
                                x_b, y_b, w_b, h_b = cv2.boundingRect(best_contour)
                                grid_points = []
                                for gy in range(y_b, y_b + h_b, 5):
                                    for gx in range(x_b, x_b + w_b, 5):
                                        if cv2.pointPolygonTest(best_contour, (float(gx), float(gy)), False) >= 0:
                                            grid_points.append([[float(gx), float(gy)]])
                                if len(grid_points) >= 5:
                                    p0 = np.array(grid_points, dtype=np.float32)
                                else:
                                    roi_mask = np.zeros_like(cropped_gray)
                                    cv2.drawContours(roi_mask, [best_contour], -1, 255, -1)
                                    p0 = cv2.goodFeaturesToTrack(cropped_gray, mask=roi_mask, **feature_params)
                                
                                self.main_win.logger.log(f"[{self.main_win.frame_num:05d}] 실시간 동적 배경차분 정가운데 락온 성공! ({cx_mom},{cy_mom})", "MINIMAP")
                        else:
                            if p0 is not None and old_gray is not None and len(p0) > 0:
                                p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, cropped_gray, p0, None, **lk_params)
                                if p1 is not None and st is not None:
                                    good_new = p1[st == 1]
                                    if len(good_new) >= 3:
                                        mean_x, mean_y = int(np.mean(good_new[:, 0])), int(np.mean(good_new[:, 1]))
                                        dx, dy = mean_x - last_x, mean_y - last_y
                                        dist = np.hypot(dx, dy)
                                        
                                        is_valid_trajectory = True
                                        if dist > 40:
                                            is_valid_trajectory = False
                                        
                                        prev_speed = np.hypot(vx, vy)
                                        if is_valid_trajectory and prev_speed > 2.0 and dist > 5.0:
                                            cos_sim = (vx * dx + vy * dy) / (prev_speed * dist)
                                            if cos_sim < 0.17:
                                                is_valid_trajectory = False
                                                log_msg = f"⚠️ 방향 급변 검출 (cos: {cos_sim:.2f}) - 관성 궤적 대체"
                                        
                                        if is_valid_trajectory:
                                            found_valid = True
                                            target_pos = (mean_x, mean_y)
                                            p0 = good_new.reshape(-1, 1, 2)
                                            vx, vy = 0.8*vx + 0.2*dx, 0.8*vy + 0.2*dy
                                            last_x, last_y, inertia_cnt = mean_x, mean_y, 0
                                        else:
                                            p0 = None
                                    else: 
                                        p0 = None
                            if not found_valid and last_x is not None and last_y is not None:
                                lw = 80
                                lx_min, ly_min = max(0, last_x - lw), max(0, last_y - lw)
                                lx_max, ly_max = min(rw, last_x + lw), min(rh, last_y + lw)
                                local_gray = cropped_gray[ly_min:ly_max, lx_min:lx_max]
                                
                                bg_name = "anti0.png" if rw == 1024 else "anti0.1.png"
                                if bg_name not in bg_cache:
                                    bg_path = os.path.join(self.main_win.base_dir, bg_name)
                                    if os.path.exists(bg_path):
                                        bg_cache[bg_name] = cv2.imread(bg_path, cv2.IMREAD_GRAYSCALE)
                                    else:
                                        bg_cache[bg_name] = None
                                
                                bg_ref = bg_cache.get(bg_name)
                                if bg_ref is not None:
                                    diff = cv2.absdiff(local_gray, bg_ref[ly_min:ly_max, lx_min:lx_max])
                                    _, thresh = cv2.threshold(cv2.GaussianBlur(diff, (5, 5), 0), 5, 255, cv2.THRESH_BINARY)
                                else: 
                                    _, thresh = cv2.threshold(local_gray, 150, 255, cv2.THRESH_BINARY)
                                contours, _ = cv2.findContours(cv2.dilate(thresh, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), iterations=1), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                                valid_local = []
                                for c in contours:
                                    area = cv2.contourArea(c)
                                    if 300 < area < 25000:
                                        x, y, w, h = cv2.boundingRect(c)
                                        if 0.5 < float(w)/h < 2.0:
                                            hull = cv2.convexHull(c)
                                            hull_area = cv2.contourArea(hull)
                                            if (float(area)/hull_area if hull_area > 0 else 0) > 0.3: 
                                                valid_local.append((c, area))
                                if valid_local:
                                    best_contour, _ = max(valid_local, key=lambda x: x[1])
                                    M = cv2.moments(best_contour)
                                    if M["m00"] > 0:
                                        local_cx, local_cy = int(M["m10"]/M["m00"]) + lx_min, int(M["m01"]/M["m00"]) + ly_min
                                        if np.hypot(local_cx - last_x, local_cy - last_y) <= 40:
                                            found_valid = True
                                            target_pos = (local_cx, local_cy)
                                            
                                            global_contour = best_contour + np.array([lx_min, ly_min])
                                            x_b, y_b, w_b, h_b = cv2.boundingRect(global_contour)
                                            grid_points = []
                                            for gy in range(y_b, y_b + h_b, 5):
                                                for gx in range(x_b, x_b + w_b, 5):
                                                    if cv2.pointPolygonTest(global_contour, (float(gx), float(gy)), False) >= 0:
                                                        grid_points.append([[float(gx), float(gy)]])
                                            if len(grid_points) >= 5:
                                                p0 = np.array(grid_points, dtype=np.float32)
                                            else:
                                                roi_mask = np.zeros_like(cropped_gray)
                                                cv2.drawContours(roi_mask, [global_contour], -1, 255, -1)
                                                p0 = cv2.goodFeaturesToTrack(cropped_gray, mask=roi_mask, **feature_params)
                                                
                                            vx, vy = 0.8*vx + 0.2*(local_cx-last_x), 0.8*vy + 0.2*(local_cy-last_y)
                                            last_x, last_y, inertia_cnt = local_cx, local_cy, 0
                            if not found_valid and last_x is not None and last_y is not None and (abs(vx) > 0.1 or abs(vy) > 0.1):
                                inertia_cnt += 1
                                if inertia_cnt <= MAX_INERTIA_FRAMES:
                                    speed = np.hypot(vx, vy)
                                    use_vx, use_vy = (vx/speed)*15.0 if speed > 15 else vx, (vy/speed)*15.0 if speed > 15 else vy
                                    target_pos = (max(10, min(rw-10, int(last_x + use_vx))), max(10, min(rh-10, int(last_y + use_vy))))
                                    found_valid, last_x, last_y = True, target_pos[0], target_pos[1]
                        
                        debug_feed = cv2.addWeighted(cropped_bgr, 0.5, np.zeros(cropped_bgr.shape, cropped_bgr.dtype), 0, 0)
                        
                        if p0 is not None:
                            for pt in p0:
                                cv2.circle(debug_feed, (int(pt[0][0]), int(pt[0][1])), 2, (0, 255, 0), -1)
                        
                        if is_tracking and last_x is not None and last_y is not None:
                            cv2.rectangle(debug_feed, (max(0, last_x-80), max(0, last_y-80)), (min(rw, last_x+80), min(rh, last_y+80)), (255, 100, 0), 1)
                        else:
                            cx_center, cy_center = rw // 2, rh // 2
                            cv2.rectangle(debug_feed, (cx_center-80, cy_center-80), (cx_center+80, cy_center+80), (128, 128, 128), 1)
                        self.main_win.frame_num += 1
                        if found_valid and target_pos is not None:
                            lost_cnt = 0
                            lx, ly = target_pos
                            cv2.circle(debug_feed, (lx, ly), 10, (0, 255, 255) if inertia_cnt > 0 else (0, 0, 255), 2)
                            tx, ty = rx + lx + monitor["left"], ry + ly + monitor["top"]
                            if not self.main_win.is_dragging_anti: 
                                if is_initial_lockon:
                                    if self.main_win.input_mode == 1:
                                        ctypes.windll.user32.SetCursorPos(int(tx), int(ty))
                                    elif self.main_win.input_mode == 2 and self.main_win.logitech_input.dll:
                                        cx, cy = pyautogui.position()
                                        self.main_win.logitech_input.move(tx - cx, ty - cy)
                                    else:
                                        pyautogui.moveTo(tx, ty)
                                self.main_win.drag_mouse_down()
                                self.main_win.is_dragging_anti = True
                            self.main_win.human_mouse_move(tx, ty)
                        else:
                            lost_cnt += 1
                            if lost_cnt > 8 and self.main_win.is_dragging_anti:
                                self.main_win.drag_mouse_up()
                                self.main_win.is_dragging_anti = False
                            if lost_cnt > 20:
                                is_tracking, p0, last_x, last_y, vx, vy, inertia_cnt, popup_roi = False, None, None, None, 0.0, 0.0, 0, None
                                lockon_start_time = None
                                dynamic_bg = None
                                self.main_win.signals.shape_stop_signal.emit()
                        old_gray = cropped_gray.copy()
                        self.main_win.signals.shape_monitor_signal.emit((debug_feed, log_msg))
                except Exception as e:
                    pass
                time.sleep(0.02)
            else:
                if self.main_win.is_dragging_anti: 
                    self.main_win.drag_mouse_up()
                    self.main_win.is_dragging_anti = False
                p0, old_gray = None, None
                is_tracking = False
                last_x, last_y = None, None
                vx, vy = 0.0, 0.0
                inertia_cnt = 0
                popup_roi = None
                lost_cnt = 0
                lockon_start_time = None
                dynamic_bg = None
                time.sleep(0.5)

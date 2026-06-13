import os
import time
import random
import ctypes
import ctypes.wintypes
import numpy as np
import cv2
import mss
import winsound
from PySide6.QtWidgets import QApplication

class MinimapDetectorV2:
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
                
                threshold = 100
                row_counts = np.sum(gray > threshold, axis=1)
                
                min_pixels = int(self.main_win.reg_w * 0.15)
                candidate_ys = np.where(row_counts >= min_pixels)[0]
                
                layers = []
                if len(candidate_ys) > 0:
                    current_group = [candidate_ys[0]]
                    for y in candidate_ys[1:]:
                        if y - current_group[-1] <= 4:
                            current_group.append(y)
                        else:
                            layers.append(int(np.mean(current_group)))
                            current_group = [y]
                    layers.append(int(np.mean(current_group)))
                
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
                        return False
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

        win_coords = self.find_maplestory_window_rect()
        if not win_coords:
            self.main_win.logger.log("자동 인식 실패: 메이플스토리 게임창을 찾을 수 없습니다.", "MINIMAP")
            winsound.Beep(800, 300)
            return False
            
        win_l, win_t, win_r, win_b = win_coords
        self.main_win.logger.log(f"게임창 감지: ({win_l}, {win_t}) {win_r-win_l}x{win_b-win_t}", "MINIMAP")
        
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
                
                target_bgr = (125, 253, 254)
                m = 5
                low = np.array([target_bgr[0]-m, target_bgr[1]-m, target_bgr[2]-m])
                high = np.array([target_bgr[0]+m, target_bgr[1]+m, target_bgr[2]+m])
                mask = cv2.inRange(img, low, high)
                
                edges = cv2.Canny(gray, 30, 150)
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
                dilated = cv2.dilate(edges, kernel, iterations=1)
                contours, _ = cv2.findContours(dilated, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                
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
                
                for c in contours:
                    x, y, w, h = cv2.boundingRect(c)
                    if 120 < w < 280 and 60 < h < 180:
                        score = 5
                        has_yellow = False
                        for cx, cy in candidates:
                            if x <= cx <= x+w and y <= cy <= y+h:
                                has_yellow = True
                                break
                        if has_yellow:
                            score += 10
                            
                        y_start = max(0, y-28)
                        y_end = y
                        if y_end > y_start and x+w > x:
                            header_edges = edges[y_start:y_end, x:x+w]
                            header_dilated = dilated[y_start:y_end, x:x+w]
                            if header_edges.size > 0:
                                edge_density = np.mean(header_edges > 0)
                                if edge_density > 0.04:
                                    score += 5
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
                            
                if best_rect and best_score >= 15:
                    x, y, w, h = best_rect
                else:
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
                    
                    self.main_win.logger.log(f"[미니맵] 영역 확정 (L:{new_l}, T:{new_t}, W:{new_w}, H:{new_h})", "MINIMAP")
                    winsound.Beep(1200, 200)
                    self.main_win.settings_manager.save_settings_silently()
                    return True
                else:
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
                    self.main_win.logger.log("기본 영역으로 강제 설정했습니다.", "MINIMAP")
                    winsound.Beep(1000, 300)
                    self.main_win.settings_manager.save_settings_silently()
                    return True
        except Exception as e:
            self.main_win.logger.log(f"자동 인식 스캔 예외 발생: {str(e)}", "MINIMAP")
            return False

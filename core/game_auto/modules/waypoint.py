import os
import time
import csv
import random
import winsound
import threading
import keyboard
import numpy as np
from datetime import datetime

class WaypointManager:
    def __init__(self, main_win):
        self.main_win = main_win
        
    def update_waypoint_ui(self, idx):
        self.main_win.txt_waypoints_x_min[idx].blockSignals(True)
        self.main_win.txt_waypoints_x_max[idx].blockSignals(True)
        self.main_win.txt_waypoints_y[idx].blockSignals(True)
        self.main_win.cb_waypoints_move[idx].blockSignals(True)
        self.main_win.txt_waypoints_stay[idx].blockSignals(True)
        
        data = self.main_win.waypoints[idx]
        x_min = data.get("x_min", -1)
        x_max = data.get("x_max", -1)
        y = data.get("y", -1)
        m_type = data.get("move_type", "TELE_LEFT")
        if m_type == "TELEPORT":
            m_type = "TELE_LEFT"
        s_time = data.get("stay_time", 2.0)
        
        self.main_win.txt_waypoints_x_min[idx].setText(str(x_min) if x_min != -1 else "")
        self.main_win.txt_waypoints_x_max[idx].setText(str(x_max) if x_max != -1 else "")
        self.main_win.txt_waypoints_y[idx].setText(str(y) if y != -1 else "")
        
        self.main_win.cb_waypoints_move[idx].setCurrentText(m_type)
        self.main_win.txt_waypoints_stay[idx].setText(f"{s_time:.1f}" if s_time > 0 else "")
        
        self.main_win.txt_waypoints_x_min[idx].blockSignals(False)
        self.main_win.txt_waypoints_x_max[idx].blockSignals(False)
        self.main_win.txt_waypoints_y[idx].blockSignals(False)
        self.main_win.cb_waypoints_move[idx].blockSignals(False)
        self.main_win.txt_waypoints_stay[idx].blockSignals(False)

    def on_waypoint_move_changed(self, idx, cb_idx):
        types = [
            "TELE_LEFT", "TELE_RIGHT", "TELE_UP", 
            "JUMP_LEFT", "JUMP_RIGHT", "JUMP_UP",
            "WALK_LEFT", "WALK_RIGHT", "DROP"
        ]
        m_type = types[cb_idx] if 0 <= cb_idx < len(types) else "TELE_LEFT"
        self.main_win.waypoints[idx]["move_type"] = m_type
        next_idx = (idx + 2) if idx < self.main_win.waypoint_count - 1 else 1
        self.main_win.logger.log(f"[순환 이동 방식 변경] 슬롯 {idx+1:02d} → {next_idx:02d} 이동방식: {m_type}", "WAYPOINT")

    def on_waypoint_stay_editing_finished(self, idx):
        text = self.main_win.txt_waypoints_stay[idx].text().strip()
        try:
            val = float(text) if text != "" else 2.0
        except:
            val = 2.0
        self.main_win.waypoints[idx]["stay_time"] = val
        self.main_win.logger.log(f"[순환 체류 시간 변경] 슬롯 {idx+1} -> {val}초", "WAYPOINT")

    def on_waypoint_editing_finished(self, idx, axis):
        if axis == 'x_min':
            txt_widget = self.main_win.txt_waypoints_x_min[idx]
        elif axis == 'x_max':
            txt_widget = self.main_win.txt_waypoints_x_max[idx]
        elif axis == 'y':
            txt_widget = self.main_win.txt_waypoints_y[idx]
        else:
            return
            
        text = txt_widget.text().strip()
        try:
            val = int(text) if text != "" else -1
        except:
            val = -1
            
        self.main_win.waypoints[idx][axis] = val
        self.main_win.logger.log(f"[수동 입력 좌표 반영] 슬롯 {idx+1} -> 축: {axis.upper()}, 값: {val}, 반영 후 전체: {self.main_win.waypoints[idx]}", "WAYPOINT")

    def delete_waypoint(self, idx):
        self.main_win.waypoints[idx] = {"x_min": -1, "x_max": -1, "y": -1, "move_type": "TELE_LEFT", "stay_time": 2.0}
        self.update_waypoint_ui(idx)
        self.main_win.logger.log(f"순환 좌표 슬롯 {idx+1} 초기화 완료", "WAYPOINT")
        winsound.Beep(1000, 150)

    def shift_waypoint(self, idx, direction):
        target = idx + direction
        if 0 <= target < self.main_win.waypoint_count:
            self.main_win.waypoints[idx], self.main_win.waypoints[target] = self.main_win.waypoints[target], self.main_win.waypoints[idx]
            self.update_waypoint_ui(idx)
            self.update_waypoint_ui(target)
            self.main_win.logger.log(f"순환 좌표 슬롯 {idx+1} <=> 슬롯 {target+1} 위치 교환 완료", "WAYPOINT")
            winsound.Beep(1100, 150)

    def hotkey_record_waypoint(self):
        if self.main_win.char_x != -1 and self.main_win.char_y != -1:
            idx = self.main_win.waypoint_record_idx
            self.main_win.waypoints[idx]["x_min"] = max(0, self.main_win.char_x - 1)
            self.main_win.waypoints[idx]["x_max"] = self.main_win.char_x + 1
            self.main_win.waypoints[idx]["y"] = self.main_win.char_y
            self.update_waypoint_ui(idx)
            self.main_win.logger.log(f"[순환 좌표 기록] 슬롯 {idx+1} -> X범위: {self.main_win.char_x-1}~{self.main_win.char_x+1}, Y: {self.main_win.char_y}", "WAYPOINT")
            self.main_win.logger.log(f"[F2 좌표 등록 완료] 내부 배열 반영 -> waypoints[{idx}] = {self.main_win.waypoints[idx]}", "WAYPOINT")
            self.main_win.waypoint_record_idx = (idx + 1) % self.main_win.waypoint_count
            winsound.Beep(1400, 200)
        else:
            self.main_win.logger.log("[좌표 기록 실패] 현재 캐릭터 위치 인식이 불가능합니다.", "WAYPOINT")
            winsound.Beep(800, 300)

    def reset_waypoints(self):
        self.main_win.waypoints = [{"x_min": -1, "x_max": -1, "y": -1, "move_type": "TELE_LEFT", "stay_time": 2.0} for _ in range(self.main_win.waypoint_count)]
        self.main_win.waypoint_record_idx = 0
        self.main_win.current_waypoint_idx = 0
        self.main_win.visited_waypoints = [False] * self.main_win.waypoint_count
        for idx in range(self.main_win.waypoint_count):
            self.update_waypoint_ui(idx)
        self.main_win.logger.log("순환 좌표 전체 초기화 완료", "WAYPOINT")
        winsound.Beep(1000, 150)
        
    def toggle_route_recording(self):
        if self.main_win.is_recording:
            self.stop_route_recording()
        else:
            self.start_route_recording()

    def start_route_recording(self):
        if self.main_win.is_recording:
            return
        # 사냥 중이라면 중지 (녹화와 사냥의 완전 분리)
        if self.main_win.is_running:
            self.main_win.stop_hunting()
            
        self.main_win.is_recording = True
        self.main_win.recording_data = []
        self.main_win.recording_start_time = time.time()
        self.main_win.btn_record_start.setEnabled(True) # 토글 버튼으로 활용될 수 있음
        self.main_win.btn_record_start.setText("⏹️ 녹화 종료 (F4)")
        self.main_win.btn_record_start.setStyleSheet("background-color: #238636; color: white; font-size: 15px; font-weight: bold; border-radius: 10px;")
        self.main_win.btn_record_stop.setEnabled(False) 
        
        self.main_win.lbl_record_status.setText("현재 상태: 🔴 경로 녹화 중 (F4로 종료)")
        self.main_win.logger.log("사냥 경로 녹화 시작 (사냥 기능과 분리됨)", "RECORD")
        
        try:
            with open(self.main_win.logger.record_file_path, "a", encoding="utf-8") as f:
                f.write(f"\n--- 녹화 세션 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        except:
            pass
            
        threading.Thread(target=self.route_recording_loop, daemon=True).start()

    def route_recording_loop(self):
        import mss
        with mss.mss() as sct:
            while self.main_win.is_recording:
                cx, cy, _, _ = self.main_win.minimap_detector.get_player_coords(sct)
                
                # 키 입력 상태 감지
                dir_str = "none"
                if keyboard.is_pressed('left'):
                    dir_str = "left"
                elif keyboard.is_pressed('right'):
                    dir_str = "right"
                    
                is_down = keyboard.is_pressed('down')
                
                tele_key = self.main_win.key_teleport_cb.currentText()
                is_teleport = keyboard.is_pressed(tele_key) if tele_key else False
                
                jump_key = self.main_win.key_jump_cb.currentText()
                is_jump = keyboard.is_pressed(jump_key) if jump_key else False
                
                att_key = self.main_win.key_att_cb.currentText()
                is_combat = keyboard.is_pressed(att_key) if att_key else False
                
                t_offset = round(time.time() - self.main_win.recording_start_time, 3)
                
                # 데이터 추가
                self.main_win.recording_data.append({
                    "time": t_offset,
                    "x": cx,
                    "y": cy,
                    "dir": dir_str,
                    "down": is_down,
                    "teleport": is_teleport,
                    "jump": is_jump,
                    "combat": is_combat
                })
                
                # 실시간 파일 기록
                self.main_win.logger.write_movement_record(
                    t_offset, cx, cy, dir_str, is_teleport, is_jump, is_combat
                )
                
                time.sleep(0.15)

    def stop_route_recording(self):
        if not self.main_win.is_recording:
            return
        self.main_win.is_recording = False
        self.main_win.btn_record_start.setText("🔴 사냥 경로 녹화 시작 (F4)")
        self.main_win.btn_record_start.setStyleSheet("background-color: #9e1c1c; color: white; font-size: 15px; font-weight: bold; border-radius: 10px;")
        
        if not self.main_win.recording_data:
            self.main_win.lbl_record_status.setText("현재 상태: 데이터 없음")
            self.main_win.logger.log("녹화 종료: 데이터가 기록되지 않았습니다.", "RECORD")
            return
            
        self.main_win.logger.log(f"사냥 경로 녹화 종료. 총 {len(self.main_win.recording_data)}개 데이터 수집.", "RECORD")
        
        # CSV 파일 저장
        try:
            now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"route_record_{now_str}.csv"
            filepath = os.path.join(self.main_win.config_dir, filename)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Time", "X", "Y", "Direction", "Down", "Teleport", "Jump", "Combat"])
                for row in self.main_win.recording_data:
                    writer.writerow([row["time"], row["x"], row["y"], row["dir"], row["down"], row["teleport"], row["jump"], row["combat"]])
                    
            self.main_win.logger.log(f"녹화 원본 CSV 저장 완료 -> {filename}", "RECORD")
            self.main_win.lbl_record_status.setText(f"녹화 완료: {filename} 저장됨")
        except Exception as e:
            self.main_win.logger.log(f"녹화 CSV 저장 실패: {str(e)}", "RECORD")
            
        # 웨이포인트 자동 생성 및 분석 실행
        self.analyze_recorded_route()

    def analyze_recorded_route(self):
        data = [r for r in self.main_win.recording_data if r["x"] != -1 and r["y"] != -1]
        if len(data) < 10:
            self.main_win.logger.log("유효 데이터가 너무 부족하여 분석을 건너뜁니다.", "RECORD")
            return
            
        # 1. 정차 구간 검출 (V4 컨셉: 체류 시간 1.0초 이상인 곳만 슬롯으로 인정)
        stay_regions = []
        current_region = []
        
        # 샘플링 주기(0.15초) 기준 1.0초는 약 7프레임 이상
        MIN_STAY_FRAMES = 7 
        
        for i in range(len(data)):
            if not current_region:
                current_region.append(data[i])
            else:
                ref_x = current_region[0]["x"]
                ref_y = current_region[0]["y"]
                # 미세 움직임 허용 오차 (3px)
                if abs(data[i]["x"] - ref_x) <= 3 and abs(data[i]["y"] - ref_y) <= 3:
                    current_region.append(data[i])
                else:
                    if len(current_region) >= MIN_STAY_FRAMES:
                        stay_regions.append(current_region)
                    current_region = [data[i]]
                    
        if len(current_region) >= MIN_STAY_FRAMES:
            stay_regions.append(current_region)
            
        if not stay_regions:
            self.main_win.logger.log("사냥 정차 구간(1초 이상 체류)이 감지되지 않았습니다. 분석을 종료합니다.", "RECORD")
            self.main_win.lbl_record_status.setText("분석 결과: 사냥(정차) 지점 없음")
            return
            
        # 2. 정차 구간별 웨이포인트 산출 및 이동 방식 분석
        new_wps = []
        for idx_reg, reg in enumerate(stay_regions):
            xs = [r["x"] for r in reg]
            ys = [r["y"] for r in reg]
            
            x_min_val = max(0, min(xs) - 6)
            x_max_val = max(0, max(xs) + 6)
            y_val = int(np.mean(ys))
            
            stay_sec = round(len(reg) * 0.15, 1)
            move_type = "TELE_LEFT" # 초기값
            
            # 다음 정차 지점까지의 행동 분석
            last_frame = reg[-1]
            try:
                start_idx = data.index(last_frame)
                if idx_reg < len(stay_regions) - 1:
                    next_first_frame = stay_regions[idx_reg + 1][0]
                    end_idx = data.index(next_first_frame)
                    between_frames = data[start_idx:end_idx]
                else:
                    # 마지막 슬롯에서 첫 번째 슬롯으로 순환하는 구간 분석
                    next_first_frame = stay_regions[0][0]
                    end_idx = data.index(next_first_frame)
                    if start_idx < end_idx:
                        between_frames = data[start_idx:end_idx]
                    else:
                        between_frames = data[start_idx:] + data[:end_idx]
                
                # 행동 분석 (V3/V4 명시적 모드 추출)
                has_tele = any(r.get("teleport", False) for r in between_frames)
                has_jump = any(r.get("jump", False) for r in between_frames)
                has_drop = any(r.get("down", False) and r.get("jump", False) for r in between_frames)
                
                # 방향 판단
                target_x_avg = (stay_regions[(idx_reg+1)%len(stay_regions)][0]["x"])
                start_x_avg = reg[-1]["x"]
                is_right = target_x_avg > start_x_avg
                
                target_y_avg = stay_regions[(idx_reg+1)%len(stay_regions)][0]["y"]
                is_up = target_y_avg < (y_val - 5) # Y는 작을수록 위쪽
                
                if has_drop:
                    move_type = "DROP"
                elif has_tele:
                    if is_up: move_type = "TELE_UP"
                    else: move_type = "TELE_RIGHT" if is_right else "TELE_LEFT"
                elif has_jump:
                    if is_up: move_type = "JUMP_UP"
                    else: move_type = "JUMP_RIGHT" if is_right else "JUMP_LEFT"
                else:
                    move_type = "WALK_RIGHT" if is_right else "WALK_LEFT"
            except:
                pass
                
            new_wps.append({
                "x_min": x_min_val,
                "x_max": x_max_val,
                "y": y_val,
                "move_type": move_type,
                "stay_time": stay_sec
            })
            
        # 3. 30개 웨이포인트 슬롯에 적용
        for idx in range(self.main_win.waypoint_count):
            if idx < len(new_wps):
                self.main_win.waypoints[idx] = new_wps[idx]
            else:
                self.main_win.waypoints[idx] = {"x_min": -1, "x_max": -1, "y": -1, "move_type": "TELE_LEFT", "stay_time": 2.0}
            self.update_waypoint_ui(idx)
            
        self.main_win.logger.log(f"분석 완료: 총 {len(new_wps)}개의 핵심 사냥 지점을 순환 슬롯에 등록했습니다.", "RECORD")
        self.main_win.lbl_record_status.setText(f"자동 생성 완료: {len(new_wps)}개 슬롯 반영됨")

import time
import random

class CombatController:
    def __init__(self, main_win):
        self.main_win = main_win
        
    def execute_stay_combat(self, stay_sec, last_att_time):
        self.main_win.is_attacking = True
        att_start = time.time()
        l_att = last_att_time
        
        while time.time() - att_start < stay_sec and self.main_win.is_running:
            if self.main_win.is_selling or self.main_win.is_dragging_anti:
                time.sleep(0.05)
                continue
                
            now = time.time() * 1000
            if now - l_att >= self.main_win.attack_delay_ms:
                if getattr(self.main_win, 'use_debug_mode', False):
                    self.main_win.logger.log(f"[V3 체류 사냥 공격] 설정: {self.main_win.attack_delay_ms}ms, 실제 지연: {int(now - l_att)}ms", "COMBAT")
                
                # 녹화 활성화 시 movement_record.log 기록
                if self.main_win.is_recording:
                    t_offset = time.time() - self.main_win.recording_start_time
                    self.main_win.logger.write_movement_record(
                        t_offset, self.main_win.char_x, self.main_win.char_y, 
                        "none", False, False, True
                    )
                    
                att_key = self.main_win.key_att_cb.currentText()
                self.main_win.press_key(att_key)
                l_att = now
            time.sleep(0.05)
            
        self.main_win.is_attacking = False
        return l_att

    def execute_normal_combat(self, now_ms, last_att_time, last_dash_time):
        l_att = last_att_time
        l_dash = last_dash_time
        
        # 1초 주기 공격 루프 진입 로깅
        now_sec = time.time()
        if now_sec - getattr(self.main_win, 'last_combat_loop_log_time', 0.0) >= 1.0:
            self.main_win.last_combat_loop_log_time = now_sec
            self.main_win.logger.log("공격 루프 진입", "COMBAT")
        
        # 제자리 고정 모드 및 공격 금지 상태 확인
        is_fixed_mode = getattr(self.main_win, 'chk_pingpong_fixed', None) and self.main_win.chk_pingpong_fixed.isChecked()
        prevent_attack = getattr(self.main_win, 'is_pingpong_fixed_prevent_attack', False)
        
        # 회수 모드나 복귀 모드인 경우에도 공격을 차단
        is_recovering = getattr(self.main_win, 'is_recovering', False)
        is_falling_recovering = getattr(self.main_win, 'is_falling_recovering', False)
        
        # 회수 중이거나 복귀 중이거나 공격 금지층(회수층 등)인 경우 공격 중단
        if is_recovering or is_falling_recovering or prevent_attack:
            return l_att, l_dash
        
        if self.main_win.hunt_mode == 0 or self.main_win.hunt_mode == 1:
            att_key = self.main_win.key_att_cb.currentText()
            # 핑퐁 사냥 시 공격 키 홀드 처리
            if not getattr(self.main_win, 'is_pingpong_fixed_attacking', False):
                self.main_win.logger.log("핑퐁 사냥 공격 키 홀드 활성화", "COMBAT")
                if self.main_win.is_recording:
                    t_offset = time.time() - self.main_win.recording_start_time
                    self.main_win.logger.write_movement_record(
                        t_offset, self.main_win.char_x, self.main_win.char_y, 
                        "none", False, False, True
                    )
                self.main_win.set_key_state(att_key, True)
                self.main_win.is_pingpong_fixed_attacking = True
                
            # 제자리 고정 사냥 모드일 때는 텔레포트(이동) 입력 생략
            if not is_fixed_mode and self.main_win.hunt_mode == 0 and now_ms - l_dash >= self.main_win.dash_delay_ms:
                if getattr(self.main_win, 'use_debug_mode', False):
                    self.main_win.logger.log(f"[텔레포트 실행] 설정: {self.main_win.dash_delay_ms}ms, 실제 지연: {int(now_ms - l_dash)}ms", "COMBAT")
                
                if self.main_win.is_recording:
                    t_offset = time.time() - self.main_win.recording_start_time
                    self.main_win.logger.write_movement_record(
                        t_offset, self.main_win.char_x, self.main_win.char_y, 
                        "none", True, False, False
                    )
                    
                self.main_win.logger.log("텔레포트 입력 실행 직전", "COMBAT")
                dash_key = self.main_win.key_teleport_cb.currentText()
                self.main_win.press_key(dash_key)
                l_dash = now_ms
                
        return l_att, l_dash
        
    def execute_pet_buff(self, last_buff_time):
        l_del = last_buff_time
        if time.time() - l_del >= self.main_win.periodic_interval_min * 60:
            self.main_win.logger.log("주기적 펫 소모품 버프 실행 (del)", "SYSTEM")
            self.main_win.press_key("del")
            l_del = time.time()
        return l_del

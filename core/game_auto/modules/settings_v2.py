import os
import json
from PySide6.QtWidgets import QMessageBox

class SettingsManagerV2:
    def __init__(self, main_win):
        self.main_win = main_win
        self.config_file = main_win.config_file
        
    def save_settings_silently(self):
        # 프로필 로딩 중에는 자동 저장을 수행하지 않음 (설정 덮어쓰기/오염 방지)
        if getattr(self.main_win, 'is_loading_profile', False):
            return

        n = self.main_win.profile_combo.currentText().strip()
        if not n:
            return
            
        self.main_win.profiles_data[n] = {
            "reg": {
                "t": self.main_win.reg_t,
                "l": self.main_win.reg_l,
                "w": self.main_win.reg_w,
                "h": self.main_win.reg_h
            },
            "minimap_x": self.main_win.reg_l,
            "minimap_y": self.main_win.reg_t,
            "minimap_width": self.main_win.reg_w,
            "minimap_height": self.main_win.reg_h,
            "use_saved_minimap": self.main_win.chk_use_saved_minimap.isChecked(),
            "range": {
                "min": self.main_win.x_min_slider.value(),
                "max": self.main_win.x_max_slider.value(),
                "stat": self.main_win.stat_range_slider.value()
            },
            "keys": {
                "att": self.main_win.key_att_cb.currentText(),
                "jump": self.main_win.key_jump_cb.currentText(),
                "teleport": self.main_win.key_teleport_cb.currentText(),
                "pet": self.main_win.key_pet_cb.currentText()
            },
            "params": {
                "margin": 0,
                "precision": 0.0,
                "ad": self.main_win.attack_delay_ms,
                "dd": self.main_win.dash_delay_ms,
                "mode": self.main_win.hunt_mode,
                "per_int": self.main_win.periodic_interval_min,
                "sell_int": self.main_win.sell_interval_min,
                "sound": self.main_win.use_sound_alert,
                "input_mode": self.main_win.input_mode,
                "top": self.main_win.chk_top.isChecked()
            },
            "coord": {
                "use_bottom": self.main_win.use_bottom_hunt,
                "bottom_y": self.main_win.bottom_y_threshold,
                "bottom_time": self.main_win.bottom_hunt_time_sec,
                "use_fall": self.main_win.use_fall_recovery,
                "fall_y": self.main_win.fall_y_threshold,
                "use_escape": self.main_win.use_escape_lost,
                "lost_time": self.main_win.lost_timeout_sec,
                "use_fishing": self.main_win.use_fishing_mode,
                "fish_x": self.main_win.fish_x,
                "fish_y": self.main_win.fish_y
            },
            "pingpong_recovery": {
                "use": self.main_win.chk_pingpong_recovery.isChecked(),
                "interval": int(self.main_win.txt_pingpong_recovery_interval.text().strip() or "60"),
                "duration": int(self.main_win.txt_pingpong_recovery_duration.text().strip() or "10"),
                "hunt_y": self.main_win.hunt_y,
                "recovery_y": self.main_win.recovery_y,
                "hunt_layer_idx": self.main_win.hunt_layer_idx,
                "recovery_layer_idx": self.main_win.recovery_layer_idx,
                "return_x_min": int(self.main_win.txt_pingpong_return_x_min.text().strip() or "45"),
                "return_x_max": int(self.main_win.txt_pingpong_return_x_max.text().strip() or "50"),
                "rope_climb_time": float(self.main_win.txt_pingpong_rope_climb_time.text().strip() or "1.5"),
                "return_seq": self.main_win.txt_pingpong_return_seq.text().strip(),
                "recovery_seq": self.main_win.txt_pingpong_recovery_seq.text().strip(),
                "teleport_x": int(self.main_win.txt_pingpong_teleport_x.text().strip() or "-1"),
                "teleport_y": int(self.main_win.txt_pingpong_teleport_y.text().strip() or "-1"),
                "recovery_start_x": int(self.main_win.txt_pingpong_recovery_start_x.text().strip() or "-1"),
                "recovery_start_y": int(self.main_win.txt_pingpong_recovery_start_y.text().strip() or "-1"),
                "fixed_mode": self.main_win.chk_pingpong_fixed.isChecked(),
                "seq_delay": float(self.main_win.txt_pingpong_seq_delay.text().strip() or "1.0"),
                "recovery_teleport": self.main_win.chk_pingpong_recovery_teleport.isChecked(),
                "att_reset_sec": int(self.main_win.txt_att_reset_sec.text().strip() or "59")
            },
            "inventory_sell": {
                "sell_pos1": self.main_win.txt_sell_pos1.text().strip() or "0, 0",
                "sell_pos2": self.main_win.txt_sell_pos2.text().strip() or "0, 0",
                "sell_pos3": self.main_win.txt_sell_pos3.text().strip() or "0, 0",
                "sell_pos4": self.main_win.txt_sell_pos4.text().strip() or "0, 0",
                "sell_pos5": self.main_win.txt_sell_pos5.text().strip() or "0, 0",
                "sell_rows": int(self.main_win.txt_sell_rows.text().strip() or "8"),
                "sell_start_row": int(self.main_win.txt_sell_start_row.text().strip() or "2"),
                "sell_delay": float(self.main_win.txt_sell_delay.text().strip() or "0.05"),
                "use_auto_sell": self.main_win.chk_auto_sell.isChecked(),
                "auto_sell_interval": int(self.main_win.txt_auto_sell_interval.text().strip() or "5"),
                "sell_delay1": float(self.main_win.txt_sell_delay1.text().strip() or "1.5"),
                "sell_delay2": float(self.main_win.txt_sell_delay2.text().strip() or "1.0"),
                "sell_delay3": float(self.main_win.txt_sell_delay3.text().strip() or "0.5"),
                "sell_delay4": float(self.main_win.txt_sell_delay4.text().strip() or "0.12"),
                "sell_delay5": float(self.main_win.txt_sell_delay5.text().strip() or "0.5")
            },
            "buffs": {
                "buff1_use": self.main_win.chk_buff1_use.isChecked(),
                "buff1_key": self.main_win.cb_buff1_key.currentText(),
                "buff1_int": int(self.main_win.txt_buff1_int.text().strip() or "180"),
                "buff1_hold": float(self.main_win.txt_buff1_hold.text().strip() or "0.5"),
                "buff2_use": self.main_win.chk_buff2_use.isChecked(),
                "buff2_key": self.main_win.cb_buff2_key.currentText(),
                "buff2_int": int(self.main_win.txt_buff2_int.text().strip() or "200"),
                "buff2_hold": float(self.main_win.txt_buff2_hold.text().strip() or "0.5")
            },
            "update_url": getattr(self.main_win, 'update_url', "")
        }
        self.main_win.profiles_data["_last_selected"] = n
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.main_win.profiles_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            self.main_win.logger.log(f"설정 백그라운드 자동 저장 실패: {str(e)}", "SYSTEM")

    def save_current_profile(self):
        n = self.main_win.profile_combo.currentText().strip()
        if not n:
            return
            
        self.save_settings_silently()
        self.update_profile_list()
        QMessageBox.information(self.main_win, "저장", "설정이 영구 저장됨")
        self.main_win.logger.log(f"설정 영구 저장 완료 -> 프로필: {n}", "SYSTEM")

    def apply_profile_data(self, n):
        if n not in self.main_win.profiles_data:
            return
            
        self.main_win.is_loading_profile = True
        
        d = self.main_win.profiles_data[n]
        p = d["params"]
        ke = d.get("keys", {})
        
        if "minimap_x" in d:
            self.main_win.reg_l = d.get("minimap_x", 100)
            self.main_win.reg_t = d.get("minimap_y", 100)
            self.main_win.reg_w = d.get("minimap_width", 200)
            self.main_win.reg_h = d.get("minimap_height", 150)
        elif "reg" in d:
            self.main_win.reg_t = d["reg"]["t"]
            self.main_win.reg_l = d["reg"]["l"]
            self.main_win.reg_w = d["reg"]["w"]
            self.main_win.reg_h = d["reg"]["h"]
        else:
            self.main_win.reg_t = 100
            self.main_win.reg_l = 100
            self.main_win.reg_w = 200
            self.main_win.reg_h = 150

        use_saved = d.get("use_saved_minimap", True)
        self.main_win.chk_use_saved_minimap.blockSignals(True)
        self.main_win.chk_use_auto_detect.blockSignals(True)
        self.main_win.chk_use_saved_minimap.setChecked(use_saved)
        self.main_win.chk_use_auto_detect.setChecked(not use_saved)
        self.main_win.chk_use_saved_minimap.blockSignals(False)
        self.main_win.chk_use_auto_detect.blockSignals(False)
        
        self.main_win.x_min_slider.setValue(d["range"]["min"])
        self.main_win.x_max_slider.setValue(d["range"]["max"])
        self.main_win.stat_range_slider.setValue(d["range"]["stat"])
        
        self.main_win.precision_val = 0.0
        self.main_win.color_margin = 0
        
        ad_val = max(50, min(500, p.get("ad", 200)))
        dd_val = max(50, min(1000, p.get("dd", 500)))
        self.main_win.att_slider.setValue(ad_val)
        self.main_win.dash_slider.setValue(dd_val)
        self.main_win.pet_slider.setValue(p["per_int"])
        self.main_win.sell_slider.setValue(p["sell_int"])
        
        self.main_win.chk_alert.setChecked(p["sound"])
        
        # 핑퐁 전용 사냥 모드 (제자리는 고정 체크박스로 병합)
        mode_val = p.get("mode", 0)
        if mode_val == 2:
            mode_val = 0
        self.main_win.hunt_mode = mode_val
        self.main_win.chk_top.setChecked(p.get("top", True))
        
        self.main_win.input_mode = p.get("input_mode", 0)
        self.main_win.input_mode_combo.setCurrentIndex(self.main_win.input_mode)
        
        self.main_win.key_att_cb.setCurrentText(ke.get("att", "end"))
        self.main_win.key_jump_cb.setCurrentText(ke.get("jump", "alt"))
        self.main_win.key_teleport_cb.setCurrentText(ke.get("teleport", "shift"))
        self.main_win.key_pet_cb.setCurrentText(ke.get("pet", "del"))
        
        co = d.get("coord", {})
        self.main_win.chk_bottom_hunt.setChecked(co.get("use_bottom", False))
        self.main_win.bottom_y_slider.setValue(co.get("bottom_y", 80))
        self.main_win.bottom_time_slider.setValue(co.get("bottom_time", 10))
        self.main_win.chk_fall_recovery.setChecked(co.get("use_fall", False))
        self.main_win.fall_y_slider.setValue(co.get("fall_y", 110))
        self.main_win.chk_escape_lost.setChecked(co.get("use_escape", False))
        self.main_win.lost_time_slider.setValue(co.get("lost_time", 5))
        
        self.main_win.chk_fishing_mode.setChecked(co.get("use_fishing", False))
        self.main_win.fish_x = co.get("fish_x", -1)
        self.main_win.fish_y = co.get("fish_y", -1)
        if self.main_win.fish_x != -1 and self.main_win.fish_y != -1:
            self.main_win.lbl_fish_pos.setText(f"낚시 좌표: X: {self.main_win.fish_x}, Y: {self.main_win.fish_y}")
        else:
            self.main_win.lbl_fish_pos.setText("낚시 좌표: X: 미지정, Y: 미지정")
            
        pr = d.get("pingpong_recovery", {})
        self.main_win.chk_pingpong_recovery.setChecked(pr.get("use", False))
        self.main_win.txt_pingpong_recovery_interval.setText(str(pr.get("interval", 60)))
        self.main_win.txt_pingpong_recovery_duration.setText(str(pr.get("duration", 10)))
        
        self.main_win.hunt_y = pr.get("hunt_y", 67)
        self.main_win.recovery_y = pr.get("recovery_y", 81)
        self.main_win.hunt_layer_idx = pr.get("hunt_layer_idx", -1)
        self.main_win.recovery_layer_idx = pr.get("recovery_layer_idx", -1)
        
        self.main_win.txt_pingpong_hunt_y.setText(str(self.main_win.hunt_y))
        self.main_win.txt_pingpong_recovery_y.setText(str(self.main_win.recovery_y))
            
        self.main_win.txt_pingpong_return_x_min.setText(str(pr.get("return_x_min", 45)))
        self.main_win.txt_pingpong_return_x_max.setText(str(pr.get("return_x_max", 50)))
        self.main_win.txt_pingpong_rope_climb_time.setText(str(pr.get("rope_climb_time", 1.5)))
        self.main_win.txt_pingpong_return_seq.setText(pr.get("return_seq", "TELE_UP, TELE_UP"))
        self.main_win.txt_pingpong_recovery_seq.setText(pr.get("recovery_seq", ""))
        seq_delay = pr.get("seq_delay")
        if seq_delay is None:
            seq_delay = pr.get("return_delay", pr.get("recovery_delay", 1.0))
        self.main_win.txt_pingpong_seq_delay.setText(str(seq_delay))
        self.main_win.chk_pingpong_recovery_teleport.setChecked(pr.get("recovery_teleport", False))
        
        self.main_win.teleport_x = pr.get("teleport_x", -1)
        self.main_win.teleport_y = pr.get("teleport_y", -1)
        self.main_win.txt_pingpong_teleport_x.setText(str(self.main_win.teleport_x))
        self.main_win.txt_pingpong_teleport_y.setText(str(self.main_win.teleport_y))
        
        self.main_win.recovery_start_x = pr.get("recovery_start_x", -1)
        self.main_win.recovery_start_y = pr.get("recovery_start_y", -1)
        self.main_win.txt_pingpong_recovery_start_x.setText(str(self.main_win.recovery_start_x))
        self.main_win.txt_pingpong_recovery_start_y.setText(str(self.main_win.recovery_start_y))
        
        self.main_win.chk_pingpong_fixed.setChecked(pr.get("fixed_mode", False))
        self.main_win.txt_att_reset_sec.setText(str(pr.get("att_reset_sec", 59)))
        
        inv_sell = d.get("inventory_sell", {})
        self.main_win.txt_sell_pos1.setText(str(inv_sell.get("sell_pos1", "0, 0")))
        self.main_win.txt_sell_pos2.setText(str(inv_sell.get("sell_pos2", "0, 0")))
        self.main_win.txt_sell_pos3.setText(str(inv_sell.get("sell_pos3", "0, 0")))
        self.main_win.txt_sell_pos4.setText(str(inv_sell.get("sell_pos4", "0, 0")))
        self.main_win.txt_sell_pos5.setText(str(inv_sell.get("sell_pos5", "0, 0")))
        self.main_win.txt_sell_rows.setText(str(inv_sell.get("sell_rows", 8)))
        self.main_win.txt_sell_start_row.setText(str(inv_sell.get("sell_start_row", 2)))
        self.main_win.txt_sell_delay.setText(str(inv_sell.get("sell_delay", 0.05)))
        self.main_win.chk_auto_sell.setChecked(inv_sell.get("use_auto_sell", False))
        self.main_win.txt_auto_sell_interval.setText(str(inv_sell.get("auto_sell_interval", 5)))
        self.main_win.txt_sell_delay1.setText(str(inv_sell.get("sell_delay1", 1.5)))
        self.main_win.txt_sell_delay2.setText(str(inv_sell.get("sell_delay2", 1.0)))
        self.main_win.txt_sell_delay3.setText(str(inv_sell.get("sell_delay3", 0.5)))
        self.main_win.txt_sell_delay4.setText(str(inv_sell.get("sell_delay4", 0.12)))
        self.main_win.txt_sell_delay5.setText(str(inv_sell.get("sell_delay5", 0.5)))
        
        bu = d.get("buffs", {})
        self.main_win.chk_buff1_use.setChecked(bu.get("buff1_use", False))
        self.main_win.cb_buff1_key.setCurrentText(bu.get("buff1_key", "ctrl"))
        self.main_win.txt_buff1_int.setText(str(bu.get("buff1_int", 180)))
        self.main_win.txt_buff1_hold.setText(str(bu.get("buff1_hold", 0.5)))
        self.main_win.chk_buff2_use.setChecked(bu.get("buff2_use", False))
        self.main_win.cb_buff2_key.setCurrentText(bu.get("buff2_key", "alt"))
        self.main_win.txt_buff2_int.setText(str(bu.get("buff2_int", 200)))
        self.main_win.txt_buff2_hold.setText(str(bu.get("buff2_hold", 0.5)))
        self.main_win.update_url = str(d.get("update_url", ""))
        
        # 미니맵 프리뷰 즉시 강제 업데이트
        try:
            import mss
            import cv2
            import numpy as np
            reg = {
                "top": self.main_win.reg_t,
                "left": self.main_win.reg_l,
                "width": self.main_win.reg_w,
                "height": self.main_win.reg_h
            }
            with mss.mss() as sct:
                shot = np.array(sct.grab(reg))
                img = cv2.cvtColor(shot, cv2.COLOR_BGRA2BGR)
                self.main_win.signals.preview_signal.emit(img)
        except:
            pass

        self.main_win.is_loading_profile = False

    def load_all_profiles(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self.main_win.profiles_data = json.load(f)
            else:
                self.main_win.profiles_data = {}
        except Exception as e:
            self.main_win.profiles_data = {}
            if hasattr(self.main_win, 'logger'):
                self.main_win.logger.log(f"설정 로드 실패 (초기화): {str(e)}", "SYSTEM")
                
        if not self.main_win.profiles_data or len([k for k in self.main_win.profiles_data.keys() if not k.startswith("_")]) == 0:
            self.main_win.profiles_data["기본설정"] = {
                "reg": {"t": 100, "l": 100, "w": 200, "h": 150},
                "minimap_x": 100,
                "minimap_y": 100,
                "minimap_width": 200,
                "minimap_height": 150,
                "use_saved_minimap": True,
                "range": {"min": 20, "max": 180, "stat": 15},
                "keys": {"att": "end", "jump": "alt", "teleport": "shift", "pet": "del"},
                "params": {
                    "margin": 0, "precision": 0.0, "ad": 200, "dd": 500, "mode": 0, 
                    "per_int": 5, "sell_int": 15, "sound": True, "input_mode": 0, "top": True
                },
                "coord": {
                    "use_bottom": False, "bottom_y": 80, "bottom_time": 10,
                    "use_fall": False, "fall_y": 110,
                    "use_escape": False, "lost_time": 5,
                    "use_fishing": False, "fish_x": -1, "fish_y": -1
                },
                "pingpong_recovery": {
                    "use": False,
                    "interval": 60,
                    "duration": 10,
                    "hunt_y": 67,
                    "recovery_y": 81,
                    "hunt_layer_idx": -1,
                    "recovery_layer_idx": -1,
                    "return_x_min": 45,
                    "return_x_max": 50,
                    "rope_climb_time": 1.5,
                    "return_seq": "TELE_UP, ATTACK",
                    "recovery_seq": "",
                    "teleport_x": -1,
                    "teleport_y": -1,
                    "recovery_start_x": -1,
                    "recovery_start_y": -1,
                    "fixed_mode": False,
                    "seq_delay": 1.0,
                    "recovery_teleport": False,
                    "att_reset_sec": 59
                },
                "inventory_sell": {
                    "sell_pos1": "0, 0",
                    "sell_pos2": "0, 0",
                    "sell_pos3": "0, 0",
                    "sell_pos4": "0, 0",
                    "sell_pos5": "0, 0",
                    "sell_rows": 8,
                    "sell_start_row": 2,
                    "sell_delay": 0.05,
                    "use_auto_sell": False,
                    "auto_sell_interval": 5,
                    "sell_delay1": 1.5,
                    "sell_delay2": 1.0,
                    "sell_delay3": 0.5,
                    "sell_delay4": 0.12,
                    "sell_delay5": 0.5
                },
                "buffs": {
                    "buff1_use": False,
                    "buff1_key": "ctrl",
                    "buff1_int": 180,
                    "buff1_hold": 0.5,
                    "buff2_use": False,
                    "buff2_key": "alt",
                    "buff2_int": 200,
                    "buff2_hold": 0.5
                },
                "update_url": ""
            }
            try:
                with open(self.config_file, "w", encoding="utf-8") as f:
                    json.dump(self.main_win.profiles_data, f, ensure_ascii=False, indent=4)
            except:
                pass
                
        self.update_profile_list()
        
        last_sel = self.main_win.profiles_data.get("_last_selected", "")
        valid_keys = [k for k in self.main_win.profiles_data.keys() if not k.startswith("_")]
        
        if last_sel in self.main_win.profiles_data and not last_sel.startswith("_"):
            target_profile = last_sel
        elif valid_keys:
            target_profile = valid_keys[0]
        else:
            target_profile = "기본설정"
            
        self.main_win.profile_combo.setCurrentText(target_profile)
        self.apply_profile_data(target_profile)
        if hasattr(self.main_win, 'logger'):
            self.main_win.logger.log(f"설정 복원 완료 -> 프로필: {target_profile}", "SYSTEM")

    def update_profile_list(self):
        self.main_win.profile_combo.blockSignals(True)
        self.main_win.profile_combo.clear()
        
        names = [k for k in self.main_win.profiles_data.keys() if not k.startswith("_")]
        self.main_win.profile_combo.addItems(sorted(names))
        
        last_sel = self.main_win.profiles_data.get("_last_selected", "")
        if last_sel in self.main_win.profiles_data and not last_sel.startswith("_"):
            self.main_win.profile_combo.setCurrentText(last_sel)
        elif names:
            self.main_win.profile_combo.setCurrentText(names[0])
            
        self.main_win.profile_combo.blockSignals(False)

    def on_profile_change(self, text):
        t = text.strip()
        if t in self.main_win.profiles_data and not t.startswith("_"):
            self.apply_profile_data(t)
            self.main_win.profiles_data["_last_selected"] = t
            try:
                with open(self.config_file, "w", encoding="utf-8") as f:
                    json.dump(self.main_win.profiles_data, f, ensure_ascii=False, indent=4)
            except:
                pass
            if hasattr(self.main_win, 'logger'):
                self.main_win.logger.log(f"프로필 변경 적용 완료 -> {t}", "SYSTEM")

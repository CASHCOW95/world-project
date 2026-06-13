import os
import time
from datetime import datetime

class AppLogger:
    def __init__(self, main_win):
        self.main_win = main_win
        # CONFIG_DIR은 main_win.config_dir에서 참조
        self.log_file_path = os.path.join(main_win.config_dir, "automaple.log")
        self.record_file_path = os.path.join(main_win.config_dir, "movement_record.log")
        
    def log(self, message, category="SYSTEM"):
        if category in ["COMBAT", "PINGPONG"]:
            return
        color_map = {
            "SYSTEM": "#c9d1d9",      # 회색/흰색
            "MINIMAP": "#58a6ff",     # 파란색 (미니맵)
            "MOVEMENT": "#56f09b",    # 초록색 (이동)
            "COMBAT": "#ffb454",      # 오렌지색 (공격)
            "WAYPOINT": "#d1a3ff",    # 보라색 (순환)
            "RECORD": "#ff7b72",      # 빨간색 (녹화)
            "PINGPONG": "#00d2ff"     # 하늘색 (핑퐁)
        }
        color = color_map.get(category, "#c9d1d9")
        
        prefix_map = {
            "SYSTEM": "[시스템]",
            "MINIMAP": "[미니맵]",
            "MOVEMENT": "[이동]",
            "COMBAT": "[공격]",
            "WAYPOINT": "[순환]",
            "RECORD": "[녹화]",
            "PINGPONG": "[핑퐁]"
        }
        prefix = prefix_map.get(category, "[알수없음]")
        
        html_msg = f"{prefix} {message}"
        formatted_for_gui = f"<span style='color:{color}'>{html_msg}</span>"
        
        # signals.log_signal을 통해 메인 윈도우 UI에 기록 신호 방출
        self.main_win.signals.log_signal.emit(formatted_for_gui)
        
        # 파일 백업 (automaple.log)
        plain_msg = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {prefix} {message}"
        try:
            with open(self.log_file_path, "a", encoding="utf-8") as f:
                f.write(plain_msg + "\n")
        except:
            pass
            
    def write_movement_record(self, t_offset, x, y, direction, teleport, jump, combat):
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{time_str}] Time:{t_offset:.3f}s | X:{x}, Y:{y} | Dir:{direction} | Teleport:{teleport} | Jump:{jump} | Combat:{combat}"
        try:
            with open(self.record_file_path, "a", encoding="utf-8") as f:
                f.write(log_line + "\n")
        except:
            pass

import sys
import os
import json
import random
import time
import subprocess
import re
import ctypes
import threading
from ctypes import wintypes
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QLabel, 
                             QFrame, QCheckBox, QScrollArea, QGridLayout, 
                             QRadioButton, QButtonGroup, QComboBox)
from PySide6.QtCore import Qt, QSize, Signal, QObject
from PySide6.QtGui import QFont, QScreen

# --- 윈도우 API 및 상수 ---
user32 = ctypes.windll.user32
WM_KEYDOWN = 0x0100
VK_BACKTICK = 0xC0 # ` 키

# 글로벌 키보드 훅을 위한 시그널 객체
class KeySignal(QObject):
    pressed = Signal()

key_notifier = KeySignal()

def global_key_listener():
    """백그라운드에서 ` 키 입력을 감시하는 쓰레드"""
    # 아주 단순하고 가벼운 방식의 키 감시 (GetKeyState)
    last_state = 0
    while True:
        state = user32.GetAsyncKeyState(VK_BACKTICK)
        if state & 0x8000 and not last_state: # 키가 방금 눌렸을 때
            key_notifier.pressed.emit()
            last_state = 1
        elif not (state & 0x8000):
            last_state = 0
        time.sleep(0.05)

# --- 창 제어 함수 ---
def get_chrome_window_handles():
    hwnds = set()
    def callback(hwnd, lParam):
        if user32.IsWindowVisible(hwnd):
            class_name = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, class_name, 256)
            if "Chrome_WidgetWin_1" in class_name.value:
                hwnds.add(hwnd)
        return True
    enum_windows_proc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows(enum_windows_proc(callback), 0)
    return hwnds

def move_and_resize(hwnd, x, y, w, h):
    user32.ShowWindow(hwnd, 9)
    user32.SetWindowPos(hwnd, 0, int(x), int(y), int(w), int(h), 0x0004 | 0x0040)

# --- 경로 설정 ---
CHROME_PATH = ""
for p in [r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe", os.path.expandvars(r"%LOCALAPPDATA%\Google\Application\chrome.exe")]:
    if os.path.exists(p): CHROME_PATH = p; break
USER_DATA_PATH = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

# --- QSS 스타일 ---
CYBERPUNK_QSS = """
QMainWindow { background-color: #080A0C; }
QWidget#CentralWidget { background-color: #080A0C; }
QFrame#MainPanel { background-color: rgba(18, 21, 25, 200); border: 1px solid #00FFFF; border-radius: 2px; }
QLabel { color: #A0A0A0; font-family: '맑은 고딕', sans-serif; font-weight: bold; }
QLabel#TitleLabel { color: #FFB400; font-size: 18px; letter-spacing: 2px; }
QLabel#StatusLabel { color: #00FFFF; font-size: 12px; }
QCheckBox, QRadioButton, QComboBox { color: #E0E0E0; font-size: 11px; font-weight: bold; }
QCheckBox#MasterCheckBox { color: #03DAC6; font-size: 13px; }
QCheckBox::indicator, QRadioButton::indicator { width: 14px; height: 14px; border: 1px solid #323232; background: #121519; }
QCheckBox::indicator:checked, QRadioButton::indicator:checked { background: #03DAC6; border: 1px solid #00FFFF; }
QLineEdit, QComboBox { background-color: #121519; border: 1px solid #323232; border-left: 4px solid #00FFFF; color: #FFFFFF; padding: 5px; }
QScrollArea { border: 1px solid #1A1A1A; background-color: #0D1013; }
QWidget#GridContainer { background-color: #0D1013; }
QFrame#ProfileCard { background-color: #161A1E; border: 1px solid #252525; border-radius: 2px; }
QFrame#ProfileCard[selected="true"] { background-color: #004D4D; border: 1px solid #FFB400; }
QPushButton { background-color: #121519; border: 1px solid #FFB400; color: #FFB400; font-weight: bold; padding: 10px; }
QPushButton#LaunchButton { background-color: #CF6679; border: none; color: white; font-size: 18px; height: 60px; border-bottom: 4px solid #9A4D5A; }
"""

class ProfileCard(QFrame):
    def __init__(self, display_name, parent_launcher):
        super().__init__()
        self.display_name = display_name; self.launcher = parent_launcher
        self.setObjectName("ProfileCard"); self.setFixedSize(108, 28); self.setProperty("selected", "false")
        layout = QHBoxLayout(self); layout.setContentsMargins(5, 0, 5, 0); layout.setSpacing(3)
        self.checkbox = QCheckBox(display_name); self.checkbox.stateChanged.connect(self.on_state_changed)
        layout.addWidget(self.checkbox); self.setCursor(Qt.PointingHandCursor)

    def on_state_changed(self, state):
        self.setProperty("selected", "true" if state == Qt.Checked.value else "false")
        self.style().unpolish(self); self.style().polish(self); self.launcher.update_count()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.checkbox.toggle()
        super().mousePressEvent(event)

    def set_checked(self, checked): self.checkbox.setCheckState(Qt.Checked if checked else Qt.Unchecked)
    def is_checked(self): return self.checkbox.isChecked()

class ChromeLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.all_profile_names = []; self.profile_cards = {}; self.nickname_map = {}; self._block_signals = False
        self.init_ui(); self.load_profiles_data(); self.load_config()
        
        # 글로벌 단축키 연결
        key_notifier.pressed.connect(self.send_trigger_key)
        threading.Thread(target=global_key_listener, daemon=True).start()

    def init_ui(self):
        self.setWindowTitle("구글폼 자동화 HUD v12.6"); self.setFixedSize(480, 900)
        central = QWidget(); self.setCentralWidget(central)
        main_layout = QVBoxLayout(central); main_layout.setContentsMargins(15, 15, 15, 15); main_layout.setSpacing(10)

        # 상단 패널
        status_panel = QFrame(); status_panel.setObjectName("MainPanel")
        status_layout = QVBoxLayout(status_panel)
        status_layout.addWidget(QLabel("격자 배포 및 글로벌 단축키 시스템", objectName="TitleLabel"))
        self.health_label = QLabel("상태: [ ` ] 키 입력 시 자동작성 시작", objectName="StatusLabel"); status_layout.addWidget(self.health_label)
        main_layout.addWidget(status_panel)

        # 설정 구역
        config_box = QFrame(); config_box.setObjectName("MainPanel")
        config_layout = QVBoxLayout(config_box)
        mon_row = QHBoxLayout(); mon_row.addWidget(QLabel("모니터:"))
        self.mon_group = QButtonGroup(self)
        self.rad_p = QRadioButton("주 모니터"); self.rad_s = QRadioButton("보조 모니터")
        self.rad_p.setChecked(True); self.mon_group.addButton(self.rad_p, 0); self.mon_group.addButton(self.rad_s, 1)
        mon_row.addWidget(self.rad_p); mon_row.addWidget(self.rad_s); config_layout.addLayout(mon_row)
        
        opt_row = QHBoxLayout(); opt_row.addWidget(QLabel("격자 열:")); self.col_combo = QComboBox(); self.col_combo.addItems(["4열", "5열"]); opt_row.addWidget(self.col_combo)
        self.chk_auto = QCheckBox("스텔스 자동화(#auto)"); self.chk_auto.setChecked(True); opt_row.addWidget(self.chk_auto)
        config_layout.addLayout(opt_row)
        main_layout.addWidget(config_box)

        # 주소/검색
        main_layout.addWidget(QLabel("구글폼 URL 주소"))
        self.url_input = QLineEdit(); self.url_input.setPlaceholderText("https://docs.google.com/forms/..."); main_layout.addWidget(self.url_input)
        main_layout.addWidget(QLabel("프로필 검색"))
        self.search_input = QLineEdit(); self.search_input.textChanged.connect(self.filter_profiles); main_layout.addWidget(self.search_input)

        # 전체선택
        list_ctrl = QHBoxLayout(); self.master_cb = QCheckBox("전체 프로필 선택", objectName="MasterCheckBox")
        self.master_cb.stateChanged.connect(self.toggle_all); self.count_lbl = QLabel("0 / 0")
        list_ctrl.addWidget(self.master_cb); list_ctrl.addStretch(); list_ctrl.addWidget(self.count_lbl); main_layout.addLayout(list_ctrl)

        # 그리드
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True); self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.grid_cont = QWidget(); self.grid_cont.setObjectName("GridContainer")
        self.grid_lay = QGridLayout(self.grid_cont); self.grid_lay.setContentsMargins(5, 5, 5, 5); self.grid_lay.setSpacing(2); self.grid_lay.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.scroll.setWidget(self.grid_cont); main_layout.addWidget(self.scroll)

        # 기동 버튼
        self.launch_btn = QPushButton("⚡ 번개기동 시작 (격자 정렬)", objectName="LaunchButton"); self.launch_btn.clicked.connect(self.launch_chrome)
        main_layout.addWidget(self.launch_btn); self.setStyleSheet(CYBERPUNK_QSS)

    def load_profiles_data(self):
        lstate = os.path.join(USER_DATA_PATH, "Local State")
        if os.path.exists(lstate):
            try:
                with open(lstate, 'r', encoding='utf-8-sig') as f:
                    data = json.load(f); profiles = data.get("profile", {}).get("info_cache", {})
                    for pk, pi in profiles.items():
                        name = pi.get("name")
                        if name: self.nickname_map[pk] = name
            except Exception: pass
        if os.path.exists(USER_DATA_PATH):
            folders = [d for d in os.listdir(USER_DATA_PATH) if os.path.isdir(os.path.join(USER_DATA_PATH, d)) and d.startswith("Profile ")]
            if os.path.exists(os.path.join(USER_DATA_PATH, "Default")): folders.insert(0, "Default")
            def sort_key(s):
                nick = self.nickname_map.get(s, s); is_dig = 0 if nick and nick[0].isdigit() else 1
                parts = [int(t) if t.isdigit() else t.lower() for t in re.split('([0-9]+)', nick)]
                return (is_dig, parts)
            folders.sort(key=sort_key)
            for p in folders:
                display = f"{self.nickname_map.get(p, p)} ({p})"
                self.all_profile_names.append(display); self.profile_cards[display] = ProfileCard(display, self)
            self.refresh_grid(self.all_profile_names)

    def refresh_grid(self, names):
        self._block_signals = True
        while self.grid_lay.count():
            w = self.grid_lay.takeAt(0).widget()
            if w: w.hide()
        cols = 4; n = len(names)
        if n > 0:
            rows = (n + cols - 1) // cols
            for idx, name in enumerate(names):
                r, c = idx % rows, idx // rows
                card = self.profile_cards[name]; card.show(); self.grid_lay.addWidget(card, r, c)
        self._block_signals = False; self.update_count()

    def filter_profiles(self):
        txt = self.search_input.text().lower(); filtered = [n for n in self.all_profile_names if txt in n.lower()]
        self.refresh_grid(filtered)

    def toggle_all(self, state):
        if self._block_signals: return
        self._block_signals = True; is_chk = (state == Qt.Checked.value)
        for i in range(self.grid_lay.count()):
            w = self.grid_lay.itemAt(i).widget()
            if isinstance(w, ProfileCard): w.set_checked(is_chk)
        self._block_signals = False; self.update_count()

    def update_count(self):
        if self._block_signals: return
        chk_cnt = 0; vis_cnt = 0
        for i in range(self.grid_lay.count()):
            w = self.grid_lay.itemAt(i).widget()
            if isinstance(w, ProfileCard):
                vis_cnt += 1
                if w.is_checked(): chk_cnt += 1
        self.count_lbl.setText(f"선택: {chk_cnt} / 총: {vis_cnt}")
        self._block_signals = True
        if vis_cnt > 0 and chk_cnt == vis_cnt: self.master_cb.setCheckState(Qt.Checked)
        elif chk_cnt == 0: self.master_cb.setCheckState(Qt.Unchecked)
        else: self.master_cb.setCheckState(Qt.PartiallyChecked)
        self._block_signals = False

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8-sig') as f:
                    conf = json.load(f); self.url_input.setText(conf.get("LastUrl", ""))
                    items = set(conf.get("CheckedItems", []))
                    self._block_signals = True
                    for n, c in self.profile_cards.items():
                        if n in items: c.set_checked(True)
                    self._block_signals = False; self.update_count()
            except Exception: pass

    def save_config(self, msg=True):
        items = [n for n, c in self.profile_cards.items() if c.is_checked()]
        conf = {"LastUrl": self.url_input.text(), "CheckedItems": items}
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f: json.dump(conf, f, ensure_ascii=False, indent=4)
        except Exception: pass

    def launch_chrome(self):
        self.save_config(False)
        items = [n for n, c in self.profile_cards.items() if c.is_checked()]
        url = self.url_input.text()
        if not url or not items: return
        if self.chk_auto.isChecked(): url = f"{url}#auto"

        self.health_label.setText(f"{len(items)}개 정렬 배포 중..."); self.health_label.setStyleSheet("color: #00FFFF;")
        
        screens = QApplication.screens()
        target_idx = 1 if self.rad_s.isChecked() and len(screens) > 1 else 0
        screen = screens[target_idx]
        geom = screen.availableGeometry()
        scr_x, scr_y, scr_w, scr_h = geom.x(), geom.y(), geom.width(), geom.height()

        cols = int(re.search(r'\d', self.col_combo.currentText()).group())
        win_w = scr_w // cols; win_h = scr_h // 2

        sinfo = subprocess.STARTUPINFO()
        sinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW; sinfo.wShowWindow = subprocess.SW_HIDE

        for i, name in enumerate(items):
            p_dir = name.split('(')[-1].replace(')', '').strip()
            row = (i // cols) % 2; col = i % cols
            tx, ty = scr_x + (col * win_w), scr_y + (row * win_h)
            before_hwnds = get_chrome_window_handles()
            cmd = f'"{CHROME_PATH}" --profile-directory="{p_dir}" --new-window --no-first-run "{url}"'
            try:
                subprocess.Popen(cmd, startupinfo=sinfo, shell=True)
                for _ in range(30):
                    time.sleep(0.1)
                    after_hwnds = get_chrome_window_handles()
                    new_hwnds = after_hwnds - before_hwnds
                    if new_hwnds:
                        for hwnd in new_hwnds:
                            move_and_resize(hwnd, tx, ty, win_w, win_h)
                        break
                    QApplication.processEvents()
            except Exception: pass
            time.sleep(0.1)

        self.health_label.setText(f"배포 완료. 이제 [ ` ] 키를 누르면 자동작성이 시작됩니다.")

    def send_trigger_key(self):
        """떠있는 모든 크롬 창에 ` 키 전송"""
        hwnds = get_chrome_window_handles()
        if not hwnds: return

        self.health_label.setText(f"🚀 자동작성 신호 광역 전송 중!")
        self.health_label.setStyleSheet("color: #FFB400;")
        
        for hwnd in hwnds:
            user32.PostMessageW(hwnd, WM_KEYDOWN, VK_BACKTICK, 0)
        
        # 1초 뒤 상태 복구
        QTimer.singleShot(1000, lambda: self.health_label.setText("상태: [ ` ] 키 입력 시 자동작성 시작"))
        QTimer.singleShot(1000, lambda: self.health_label.setStyleSheet("color: #00FFFF;"))

if __name__ == "__main__":
    app = QApplication(sys.argv); app.setFont(QFont("맑은 고딕", 9))
    launcher = ChromeLauncher(); launcher.show(); sys.exit(app.exec())

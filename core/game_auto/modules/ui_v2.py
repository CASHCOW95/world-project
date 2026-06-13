from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator, QDoubleValidator
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QLabel, 
    QPushButton, QComboBox, QSlider, QLineEdit, QTabWidget, QCheckBox, 
    QRadioButton, QButtonGroup, QProgressBar, QTextEdit, QScrollArea,
    QGroupBox, QSizePolicy
)

class UiSetupV2:
    @staticmethod
    def setup_ui(main_win):
        # 헬퍼 함수들 정의
        def make_scrollable(widget):
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.NoFrame)
            scroll.setStyleSheet("background-color: transparent;")
            widget.setStyleSheet("background-color: transparent;")
            scroll.setWidget(widget)
            return scroll

        def create_slider_row(layout, label, min_v, max_v, current_v, callback, is_float=False):
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setFixedWidth(120)
            lbl.setObjectName("dataLabel")
            slider = QSlider(Qt.Horizontal)
            slider.setRange(min_v, max_v)
            slider.setValue(int(current_v))
            slider.setFixedHeight(25)
            
            val_txt = QLineEdit(str(current_v/10.0 if is_float else current_v))
            val_txt.setFixedWidth(50)
            val_txt.setFixedHeight(24)
            val_txt.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; font-size: 13px; padding: 2px; text-align: center;")
            
            if is_float:
                val_txt.setValidator(QDoubleValidator(min_v/10.0, max_v/10.0, 1))
            else:
                val_txt.setValidator(QIntValidator(min_v, max_v))
                
            def on_slider_changed(v):
                val_txt.blockSignals(True)
                val_txt.setText(str(v/10.0 if is_float else v))
                val_txt.blockSignals(False)
                callback(v)
                
            def on_text_changed():
                try:
                    text = val_txt.text().strip()
                    if is_float:
                        val = float(text)
                        slider_val = int(val * 10)
                    else:
                        slider_val = int(text)
                    
                    slider_val = max(min_v, min(max_v, slider_val))
                    slider.blockSignals(True)
                    slider.setValue(slider_val)
                    slider.blockSignals(False)
                    val_txt.setText(str(slider_val/10.0 if is_float else slider_val))
                    callback(slider_val)
                except ValueError:
                    val_txt.setText(str(slider.value()/10.0 if is_float else slider.value()))
            
            slider.valueChanged.connect(on_slider_changed)
            val_txt.editingFinished.connect(on_text_changed)
            
            row.addWidget(lbl)
            row.addWidget(slider)
            row.addWidget(val_txt)
            layout.addLayout(row)
            return slider

        def create_key_combo(layout, title, default_v):
            row = QHBoxLayout()
            lbl = QLabel(title)
            lbl.setObjectName("dataLabel")
            cb = QComboBox()
            cb.setFixedHeight(30)
            cb.setFixedWidth(100)
            cb.addItems(["space", "ctrl", "alt", "shift", "insert", "del", "home", "end", "pgup", "pgdn"] + list("abcdefghijklmnopqrstuvwxyz"))
            cb.setCurrentText(default_v)
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(cb)
            layout.addLayout(row)
            return cb

        central_widget = QWidget()
        main_win.setCentralWidget(central_widget)
        
        outer_layout = QVBoxLayout(central_widget)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        
        # 스크롤 가능 영역 (하단 버튼 제외 전체)
        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setFrameShape(QFrame.NoFrame)
        main_scroll.setObjectName("mainScrollArea")
        
        scroll_content = QWidget()
        main_layout = QVBoxLayout(scroll_content)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        main_scroll.setWidget(scroll_content)
        outer_layout.addWidget(main_scroll)
        
        # --- 헤더 라인 (프로필 관리) ---
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(5, 5, 5, 5)
        
        lbl_profile = QLabel("프로필:")
        lbl_profile.setObjectName("subLabel")
        lbl_profile.setStyleSheet("font-weight: bold; color: #8a99af;")
        header_layout.addWidget(lbl_profile)
        
        main_win.profile_combo = QComboBox()
        main_win.profile_combo.setFixedHeight(32)
        main_win.profile_combo.setEditable(True)
        main_win.profile_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        main_win.profile_combo.currentTextChanged.connect(main_win.settings_manager.on_profile_change)
        header_layout.addWidget(main_win.profile_combo)
        
        main_win.save_btn = QPushButton("💾 저장")
        main_win.save_btn.setObjectName("saveBtn")
        main_win.save_btn.setFixedSize(70, 32)
        main_win.save_btn.clicked.connect(main_win.settings_manager.save_current_profile)
        header_layout.addWidget(main_win.save_btn)
        
        main_layout.addWidget(header_frame)
        
        # --- 미니맵 프리뷰 영역 ---
        preview_frame = QFrame()
        preview_frame.setObjectName("panelFrame")
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setContentsMargins(10, 8, 10, 8)
        preview_layout.setSpacing(5)
        
        mini_header = QHBoxLayout()
        mini_header.addWidget(QLabel("미니맵 분석 모니터", objectName="panelTitle"))
        mini_header.addStretch()
        
        main_win.sel_btn = QPushButton("영역 설정")
        main_win.sel_btn.setFixedSize(70, 22)
        main_win.sel_btn.setStyleSheet("font-size: 12px; padding: 2px; border-radius: 5px; background-color: #238636; color: white; font-weight: bold;")
        main_win.sel_btn.clicked.connect(main_win.open_selector)
        mini_header.addWidget(main_win.sel_btn)
        
        main_win.auto_det_btn = QPushButton("자동 인식")
        main_win.auto_det_btn.setFixedSize(70, 22)
        main_win.auto_det_btn.setStyleSheet("font-size: 12px; padding: 2px; border-radius: 5px; background-color: #0288d1; color: white; font-weight: bold;")
        main_win.auto_det_btn.clicked.connect(main_win.minimap_detector.auto_detect_minimap)
        mini_header.addWidget(main_win.auto_det_btn)
        
        preview_layout.addLayout(mini_header)
        
        options_layout = QHBoxLayout()
        main_win.chk_use_saved_minimap = QCheckBox("저장 미니맵")
        main_win.chk_use_auto_detect = QCheckBox("자동 인식")
        main_win.chk_use_saved_minimap.toggled.connect(
            lambda checked: main_win.chk_use_auto_detect.setChecked(not checked)
        )
        main_win.chk_use_auto_detect.toggled.connect(
            lambda checked: main_win.chk_use_saved_minimap.setChecked(not checked)
        )
        main_win.chk_use_saved_minimap.setChecked(True)
        main_win.chk_use_auto_detect.setChecked(False)
        options_layout.addWidget(main_win.chk_use_saved_minimap)
        options_layout.addWidget(main_win.chk_use_auto_detect)
        preview_layout.addLayout(options_layout)
        
        main_win.minimap_preview = QLabel("대기 중...")
        main_win.minimap_preview.setObjectName("previewLabel")
        main_win.minimap_preview.setFixedSize(390, 120)
        main_win.minimap_preview.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(main_win.minimap_preview)
        
        main_layout.addWidget(preview_frame)
        
        # --- 탭 콘텐트 영역 ---
        main_win.main_tabs = QTabWidget()
        main_layout.addWidget(main_win.main_tabs)
        
        # 1) 사냥 설정 탭
        tab_hunt = QWidget()
        tab_hunt_layout = QVBoxLayout(tab_hunt)
        tab_hunt_layout.setContentsMargins(5, 5, 5, 5)
        
        main_win.x_min_slider = create_slider_row(tab_hunt_layout, "좌측 경계 X:", 0, 400, main_win.x_min, main_win.update_x_min)
        main_win.x_max_slider = create_slider_row(tab_hunt_layout, "우측 경계 X:", 0, 400, main_win.x_max, main_win.update_x_max)
        
        txt_bounds_layout = QHBoxLayout()
        lbl_xmin = QLabel("수동 좌측 X:")
        lbl_xmin.setObjectName("subLabel")
        main_win.txt_pingpong_x_min = QLineEdit(str(main_win.x_min))
        main_win.txt_pingpong_x_min.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; font-size: 13px; padding: 2px;")
        main_win.txt_pingpong_x_min.setFixedWidth(50)
        main_win.txt_pingpong_x_min.setValidator(QIntValidator(0, 999))
        main_win.txt_pingpong_x_min.setObjectName("x_min")
        main_win.txt_pingpong_x_min.editingFinished.connect(main_win.on_pingpong_x_min_edited)
        
        lbl_xmax = QLabel("수동 우측 X:")
        lbl_xmax.setObjectName("subLabel")
        main_win.txt_pingpong_x_max = QLineEdit(str(main_win.x_max))
        main_win.txt_pingpong_x_max.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; font-size: 13px; padding: 2px;")
        main_win.txt_pingpong_x_max.setFixedWidth(50)
        main_win.txt_pingpong_x_max.setValidator(QIntValidator(0, 999))
        main_win.txt_pingpong_x_max.setObjectName("x_max")
        main_win.txt_pingpong_x_max.editingFinished.connect(main_win.on_pingpong_x_max_edited)
        
        txt_bounds_layout.addWidget(lbl_xmin)
        txt_bounds_layout.addWidget(main_win.txt_pingpong_x_min)
        txt_bounds_layout.addStretch()
        txt_bounds_layout.addWidget(lbl_xmax)
        txt_bounds_layout.addWidget(main_win.txt_pingpong_x_max)
        tab_hunt_layout.addLayout(txt_bounds_layout)
        
        main_win.chk_pingpong_fixed = QCheckBox("제자리 고정 사냥 (회수 시에만 이동)")
        main_win.chk_pingpong_fixed.setStyleSheet("color: #c9d1d9; font-weight: bold; font-size: 14px; margin-top: 5px;")
        tab_hunt_layout.addWidget(main_win.chk_pingpong_fixed)
        
        main_win.stat_range_slider = create_slider_row(tab_hunt_layout, "제자리 고정 오차:", 1, 100, main_win.stationary_range, main_win.update_stat_range)
        main_win.att_slider = create_slider_row(tab_hunt_layout, "공격 주기 (ms):", 50, 500, main_win.attack_delay_ms, main_win.update_att_delay)
        main_win.dash_slider = create_slider_row(tab_hunt_layout, "텔포 주기 (ms):", 50, 1000, main_win.dash_delay_ms, main_win.update_dash_delay)
        
        # 공격키 리셋 주기 (매크로 차단 우회)
        att_reset_row = QHBoxLayout()
        lbl_att_reset = QLabel("공격키 리셋 주기 (초):")
        lbl_att_reset.setObjectName("dataLabel")
        main_win.txt_att_reset_sec = QLineEdit("59")
        main_win.txt_att_reset_sec.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; font-size: 13px; padding: 2px;")
        main_win.txt_att_reset_sec.setFixedWidth(50)
        main_win.txt_att_reset_sec.setFixedHeight(24)
        main_win.txt_att_reset_sec.setValidator(QIntValidator(5, 300))
        main_win.txt_att_reset_sec.setObjectName("att_reset_sec")
        main_win.txt_att_reset_sec.setToolTip("인게임 60초 매크로 차단 우회용. 설정된 초마다 공격키를 떼었다 다시 누릅니다.")
        att_reset_row.addWidget(lbl_att_reset)
        att_reset_row.addStretch()
        att_reset_row.addWidget(main_win.txt_att_reset_sec)
        tab_hunt_layout.addLayout(att_reset_row)
        
        tab_hunt_layout.addStretch()
        main_win.main_tabs.addTab(make_scrollable(tab_hunt), "사냥")
        
        # 2) 회수 설정 탭
        tab_recovery = QWidget()
        recovery_box_layout = QVBoxLayout(tab_recovery)
        recovery_box_layout.setContentsMargins(5, 5, 5, 5)
        recovery_box_layout.setSpacing(10)

        main_win.chk_pingpong_recovery = QCheckBox("아이템 회수 모드 활성화")
        main_win.chk_pingpong_recovery.setStyleSheet("color: #00d2ff; font-weight: bold; font-size: 14px;")
        recovery_box_layout.addWidget(main_win.chk_pingpong_recovery)

        def create_txt_row(layout, label, default_val, obj_name):
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setObjectName("dataLabel")
            txt = QLineEdit(default_val)
            txt.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; font-size: 13px; padding: 2px;")
            txt.setFixedHeight(24)
            txt.setObjectName(obj_name)
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(txt)
            layout.addLayout(row)
            return txt

        def create_txt_pair_row(layout, label1, default_val1, obj_name1, label2, default_val2, obj_name2):
            row = QHBoxLayout()

            lbl1 = QLabel(label1)
            lbl1.setObjectName("dataLabel")
            txt1 = QLineEdit(default_val1)
            txt1.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; font-size: 11px; padding: 2px;")
            txt1.setFixedHeight(24)
            txt1.setObjectName(obj_name1)

            lbl2 = QLabel(label2)
            lbl2.setObjectName("dataLabel")
            txt2 = QLineEdit(default_val2)
            txt2.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; font-size: 11px; padding: 2px;")
            txt2.setFixedHeight(24)
            txt2.setObjectName(obj_name2)

            row.addWidget(lbl1)
            row.addStretch()
            row.addWidget(txt1, 0)
            row.addSpacing(10)
            row.addWidget(lbl2)
            row.addStretch()
            row.addWidget(txt2, 0)
            layout.addLayout(row)
            return txt1, txt2

        # 회수 주기/시간 그룹
        interval_grp = QGroupBox("회수 주기/시간")
        interval_layout = QVBoxLayout(interval_grp)
        interval_layout.setContentsMargins(5, 5, 5, 5)
        interval_layout.setSpacing(5)
        main_win.txt_pingpong_recovery_interval = create_txt_row(interval_layout, "회수 주기 (초):", "60", "recovery_interval")
        main_win.txt_pingpong_recovery_duration = create_txt_row(interval_layout, "회수 시간 (초):", "10", "recovery_duration")
        recovery_box_layout.addWidget(interval_grp)

        # 좌표 설정 그룹
        coord_grp = QGroupBox("좌표 설정 (F2로 자동 입력)")
        coord_layout = QVBoxLayout(coord_grp)
        coord_layout.setContentsMargins(5, 5, 5, 5)
        coord_layout.setSpacing(5)
        main_win.txt_pingpong_hunt_y, main_win.txt_pingpong_recovery_y = create_txt_pair_row(
            coord_layout, "사냥층 Y:", "67", "hunt_y", "회수층 Y:", "81", "recovery_y"
        )
        main_win.txt_pingpong_recovery_start_x, main_win.txt_pingpong_recovery_start_y = create_txt_pair_row(
            coord_layout, "회수 시작 X:", "-1", "recovery_start_x", "Y:", "-1", "recovery_start_y"
        )
        main_win.txt_pingpong_teleport_x, main_win.txt_pingpong_teleport_y = create_txt_pair_row(
            coord_layout, "복귀 텔포 X:", "-1", "teleport_x", "Y:", "-1", "teleport_y"
        )
        main_win.txt_pingpong_return_x_min, main_win.txt_pingpong_return_x_max = create_txt_pair_row(
            coord_layout, "복귀 범위 X Min:", "45", "return_x_min", "Max:", "50", "return_x_max"
        )
        main_win.txt_pingpong_rope_climb_time = create_txt_row(coord_layout, "로프 등반 시간 (초):", "1.5", "rope_climb_time")
        recovery_box_layout.addWidget(coord_grp)

        # 시퀀스 설정 그룹
        seq_grp = QGroupBox("시퀀스 설정")
        seq_layout = QVBoxLayout(seq_grp)
        seq_layout.setContentsMargins(5, 5, 5, 5)
        seq_layout.setSpacing(5)
        main_win.txt_pingpong_recovery_seq = create_txt_row(seq_layout, "회수층 이동 시퀀스:", "", "recovery_seq")
        main_win.txt_pingpong_return_seq = create_txt_row(seq_layout, "복귀 시퀀스:", "TELE_UP, TELE_UP", "return_seq")
        main_win.txt_pingpong_seq_delay = create_txt_row(seq_layout, "액션 간 지연 (초):", "1.0", "seq_delay")
        recovery_box_layout.addWidget(seq_grp)

        main_win.chk_pingpong_recovery_teleport = QCheckBox("회수 및 수직이동 시 텔레포트 적용")
        main_win.chk_pingpong_recovery_teleport.setStyleSheet("color: #c9d1d9; font-size: 11px;")
        recovery_box_layout.addWidget(main_win.chk_pingpong_recovery_teleport)

        recovery_box_layout.addStretch()
        main_win.main_tabs.addTab(make_scrollable(tab_recovery), "회수")
        
        # 3) 상점 판매 및 낚시 탭
        tab_sell = QWidget()
        sell_box_layout = QVBoxLayout(tab_sell)
        sell_box_layout.setContentsMargins(5, 5, 5, 5)
        
        main_win.chk_auto_sell = QCheckBox("자동 상점 판매 기능 사용")
        main_win.chk_auto_sell.setStyleSheet("color: #00d2ff; font-weight: bold; font-size: 14px;")
        sell_box_layout.addWidget(main_win.chk_auto_sell)
        
        main_win.txt_auto_sell_interval = create_txt_row(sell_box_layout, "자동판매 주기 (분):", "5", "auto_sell_interval")
        
        sell_pos_grp = QGroupBox("상점 판매 마우스 좌표 (QLineEdit F1 등록)")
        sell_pos_layout = QVBoxLayout(sell_pos_grp)
        sell_pos_layout.setContentsMargins(5, 5, 5, 5)
        
        main_win.txt_sell_pos1 = create_txt_row(sell_pos_layout, "1. 인벤토리(NPC더블클릭):", "0, 0", "sell_pos1")
        main_win.txt_sell_pos2 = create_txt_row(sell_pos_layout, "2. 상점확인(엔터유도클릭):", "0, 0", "sell_pos2")
        main_win.txt_sell_pos3 = create_txt_row(sell_pos_layout, "3. 인벤토리 기타 탭:", "0, 0", "sell_pos3")
        main_win.txt_sell_pos4 = create_txt_row(sell_pos_layout, "4. 판매대상 아이템(더블클릭):", "0, 0", "sell_pos4")
        main_win.txt_sell_pos5 = create_txt_row(sell_pos_layout, "5. 상점 닫기 X 버튼:", "0, 0", "sell_pos5")
        sell_box_layout.addWidget(sell_pos_grp)
        
        main_win.txt_sell_rows = create_txt_row(sell_box_layout, "판매 대상 인벤행수 (1~8):", "8", "sell_rows")
        main_win.txt_sell_start_row = create_txt_row(sell_box_layout, "판매 시작 행 (1~8):", "2", "sell_start_row")
        main_win.txt_sell_delay = create_txt_row(sell_box_layout, "아이템 간 판매 지연:", "0.05", "sell_delay")
        
        # 세부 딜레이
        main_win.txt_sell_delay1 = create_txt_row(sell_box_layout, "상점 로딩 지연 (딜레이 1):", "1.5", "sell_delay1")
        main_win.txt_sell_delay2 = create_txt_row(sell_box_layout, "상점 진입 지연 (딜레이 2):", "1.0", "sell_delay2")
        main_win.txt_sell_delay3 = create_txt_row(sell_box_layout, "기타탭 전환 지연 (딜레이 3):", "0.5", "sell_delay3")
        main_win.txt_sell_delay4 = create_txt_row(sell_box_layout, "확인창 로딩 지연 (딜레이 4):", "0.12", "sell_delay4")
        main_win.txt_sell_delay5 = create_txt_row(sell_box_layout, "상점 종료 지연 (딜레이 5):", "0.5", "sell_delay5")
        
        # 낚시 설정
        fish_grp = QGroupBox("낚시 사냥 옵션")
        fish_layout = QVBoxLayout(fish_grp)
        fish_layout.setContentsMargins(5, 5, 5, 5)
        main_win.chk_fishing_mode = QCheckBox("낚시 사냥 모드 활성화 (F9 좌표 고정)")
        main_win.chk_fishing_mode.setStyleSheet("color: #c9d1d9;")
        main_win.lbl_fish_pos = QLabel("낚시 좌표: X: 미지정, Y: 미지정")
        main_win.lbl_fish_pos.setStyleSheet("color: #58a6ff; font-weight: bold;")
        fish_layout.addWidget(main_win.chk_fishing_mode)
        fish_layout.addWidget(main_win.lbl_fish_pos)
        sell_box_layout.addWidget(fish_grp)
        
        sell_box_layout.addStretch()
        main_win.main_tabs.addTab(make_scrollable(tab_sell), "상점/기타")
        
        # 4) 단축키/소모품 설정 탭
        tab_keys = QWidget()
        keys_box_layout = QVBoxLayout(tab_keys)
        keys_box_layout.setContentsMargins(5, 5, 5, 5)
        
        main_win.key_att_cb = create_key_combo(keys_box_layout, "공격 단축키:", "end")
        main_win.key_jump_cb = create_key_combo(keys_box_layout, "점프 단축키:", "alt")
        main_win.key_teleport_cb = create_key_combo(keys_box_layout, "텔포/이동 단축키:", "shift")
        
        pet_grp = QGroupBox("소모품 및 펫 자동 물약")
        pet_layout = QVBoxLayout(pet_grp)
        pet_layout.setContentsMargins(5, 5, 5, 5)
        main_win.key_pet_cb = create_key_combo(pet_layout, "소모품 단축키:", "del")
        main_win.pet_slider = create_slider_row(pet_layout, "소모품 주기 (분):", 1, 30, 5, main_win.update_pet_interval)
        keys_box_layout.addWidget(pet_grp)
        
        buff1_grp = QGroupBox("버프 단축키 1")
        buff1_layout = QVBoxLayout(buff1_grp)
        buff1_layout.setContentsMargins(5, 5, 5, 5)
        main_win.chk_buff1_use = QCheckBox("버프 1 활성화")
        main_win.chk_buff1_use.setStyleSheet("color: #c9d1d9;")
        main_win.cb_buff1_key = create_key_combo(buff1_layout, "단축키:", "ctrl")
        main_win.txt_buff1_int = create_txt_row(buff1_layout, "주기 (초):", "180", "buff1_int")
        main_win.txt_buff1_hold = create_txt_row(buff1_layout, "누름 유지 시간(초):", "0.5", "buff1_hold")
        buff1_layout.addWidget(main_win.chk_buff1_use)
        keys_box_layout.addWidget(buff1_grp)
        
        buff2_grp = QGroupBox("버프 단축키 2")
        buff2_layout = QVBoxLayout(buff2_grp)
        buff2_layout.setContentsMargins(5, 5, 5, 5)
        main_win.chk_buff2_use = QCheckBox("버프 2 활성화")
        main_win.chk_buff2_use.setStyleSheet("color: #c9d1d9;")
        main_win.cb_buff2_key = create_key_combo(buff2_layout, "단축키:", "alt")
        main_win.txt_buff2_int = create_txt_row(buff2_layout, "주기 (초):", "200", "buff2_int")
        main_win.txt_buff2_hold = create_txt_row(buff2_layout, "누름 유지 시간(초):", "0.5", "buff2_hold")
        buff2_layout.addWidget(main_win.chk_buff2_use)
        keys_box_layout.addWidget(buff2_grp)
        
        keys_box_layout.addStretch()
        main_win.main_tabs.addTab(make_scrollable(tab_keys), "단축키")

        # 5) 실시간 로그 및 제어 탭 (로그 Terminal 통합)
        tab_log = QWidget()
        log_box_layout = QVBoxLayout(tab_log)
        log_box_layout.setContentsMargins(5, 5, 5, 5)
        log_box_layout.setSpacing(5)
        
        main_win.log_text = QTextEdit()
        main_win.log_text.setReadOnly(True)
        main_win.log_text.setObjectName("logTerminal")
        main_win.log_text.setStyleSheet("color: #34d399; font-size: 13px; background-color: #0d1117;")
        log_box_layout.addWidget(main_win.log_text)
        
        status_layout = QHBoxLayout()
        lbl_run = QLabel("사냥 시간:")
        lbl_run.setObjectName("subLabel")
        main_win.data_runtime = QLabel("00:00:00")
        main_win.data_runtime.setStyleSheet("color: #00d2ff; font-weight: bold;")
        lbl_tot = QLabel("누적 시간:")
        lbl_tot.setObjectName("subLabel")
        main_win.data_total_time = QLabel("00:00:00")
        main_win.data_total_time.setStyleSheet("color: #a78bfa; font-weight: bold;")
        
        status_layout.addWidget(lbl_run)
        status_layout.addWidget(main_win.data_runtime)
        status_layout.addStretch()
        status_layout.addWidget(lbl_tot)
        status_layout.addWidget(main_win.data_total_time)
        log_box_layout.addLayout(status_layout)
        
        coords_layout = QHBoxLayout()
        main_win.data_char_pos = QLabel("캐릭터 좌표: 인식 불가")
        main_win.data_char_pos.setStyleSheet("color: #fbbf24; font-weight: bold; font-size: 13px;")
        main_win.data_errors = QLabel("에러: 0회")
        main_win.data_errors.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 13px;")
        coords_layout.addWidget(main_win.data_char_pos)
        coords_layout.addStretch()
        coords_layout.addWidget(main_win.data_errors)
        log_box_layout.addLayout(coords_layout)
        
        # 더미로 선언해두어 기존 로직 호환성 유지
        main_win.data_recovery_left = QLabel("")
        main_win.data_pet_left = QLabel("")
        
        main_win.main_tabs.addTab(tab_log, "로그")
        
        # --- 최하단: 사냥 시작/정지/수동판매 버튼 고정 ---
        btn_layout = QHBoxLayout()
        main_win.start_btn = QPushButton("▶ 사냥 시작")
        main_win.start_btn.setObjectName("startBtn")
        main_win.start_btn.setFixedHeight(45)
        main_win.start_btn.setStyleSheet("font-size: 15px; font-weight: bold; background-color: #238636;")
        main_win.start_btn.clicked.connect(main_win.start_hunting)
        
        main_win.stop_btn = QPushButton("■ 사냥 중지")
        main_win.stop_btn.setObjectName("stopBtn")
        main_win.stop_btn.setFixedHeight(45)
        main_win.stop_btn.setEnabled(False)
        main_win.stop_btn.setStyleSheet("font-size: 15px; font-weight: bold; background-color: #da3637;")
        main_win.stop_btn.clicked.connect(main_win.stop_hunting)
        
        main_win.manual_sell_btn = QPushButton("상점 판매")
        main_win.manual_sell_btn.setObjectName("sellBtn")
        main_win.manual_sell_btn.setFixedSize(80, 45)
        main_win.manual_sell_btn.setStyleSheet("font-size: 13px; font-weight: bold; background-color: #21262d; border: 1px solid #30363d; border-radius: 8px;")
        main_win.manual_sell_btn.clicked.connect(main_win.run_manual_sell)
        
        btn_layout.addWidget(main_win.start_btn)
        btn_layout.addWidget(main_win.stop_btn)
        btn_layout.addWidget(main_win.manual_sell_btn)
        
        # 하단 버튼은 스크롤 밖에 고정 배치
        btn_frame = QFrame()
        btn_frame.setObjectName("btnFrame")
        btn_frame_layout = QVBoxLayout(btn_frame)
        btn_frame_layout.setContentsMargins(15, 8, 15, 10)
        btn_frame_layout.addLayout(btn_layout)
        outer_layout.addWidget(btn_frame)
        
        # 기타 탭과 슬라이더 더미 연결로 로직 에러 방지
        main_win.chk_alert = QCheckBox()
        main_win.chk_alert.setChecked(True)
        main_win.chk_top = QCheckBox()
        main_win.chk_top.setChecked(True)
        main_win.input_mode_combo = QComboBox()
        main_win.input_mode_combo.addItems(["PyAutoGUI", "Windows SendInput", "Logitech G HUB"])
        
        # 낚시 탭 라벨 연결
        main_win.chk_bottom_hunt = QCheckBox()
        main_win.bottom_y_slider = QSlider()
        main_win.bottom_time_slider = QSlider()
        main_win.chk_fall_recovery = QCheckBox()
        main_win.fall_y_slider = QSlider()
        main_win.chk_escape_lost = QCheckBox()
        main_win.lost_time_slider = QSlider()
        main_win.sell_slider = QSlider()
        
    @staticmethod
    def apply_qss(main_win):
        qss = """
        QMainWindow {
            background-color: #0d1117;
        }
        QScrollArea#mainScrollArea {
            background-color: #0d1117;
            border: none;
        }
        QScrollArea#mainScrollArea > QWidget > QWidget {
            background-color: #0d1117;
        }
        QFrame#btnFrame {
            background-color: #0d1117;
            border-top: 1px solid #30363d;
        }
        QFrame#headerFrame {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
        }
        QFrame#panelFrame {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
        }
        QLabel#mainTitle {
            font-size: 18px;
            font-weight: bold;
            color: #00d2ff;
        }
        QLabel#panelTitle {
            font-size: 13px;
            font-weight: bold;
            color: #58a6ff;
        }
        QLabel#dataLabel {
            font-size: 13px;
            font-weight: bold;
            color: #c9d1d9;
        }
        QLabel#subLabel {
            font-size: 13px;
            color: #8a99af;
        }
        QLabel#previewLabel {
            background-color: #070a0f;
            border: 1px dashed #30363d;
            border-radius: 8px;
            color: #8a99af;
            font-size: 13px;
            font-weight: bold;
        }
        QTabWidget::pane {
            border: 1px solid #30363d;
            background: #161b22;
            border-radius: 8px;
        }
        QTabBar::tab {
            background: #0d1117;
            border: 1px solid #30363d;
            border-bottom-color: transparent;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
            padding: 5px 8px;
            color: #8a99af;
            font-weight: bold;
            font-size: 12px;
        }
        QTabBar::tab:selected {
            background: #161b22;
            color: #00d2ff;
            border-color: #30363d;
            border-bottom-color: #161b22;
        }
        QGroupBox {
            border: 1px solid #30363d;
            border-radius: 6px;
            margin-top: 10px;
            font-weight: bold;
            font-size: 13px;
            color: #58a6ff;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 3px;
        }
        QPushButton {
            border: 1px solid #30363d;
            border-radius: 8px;
            color: #c9d1d9;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #30363d;
        }
        QPushButton#saveBtn {
            background-color: #21262d;
            border: 1px solid #30363d;
            color: #58a6ff;
        }
        QPushButton#saveBtn:hover {
            background-color: #30363d;
            color: #00d2ff;
        }
        QPushButton#startBtn {
            border: none;
            color: #ffffff;
        }
        QPushButton#startBtn:hover {
            background-color: #2ea44f;
        }
        QPushButton#stopBtn {
            border: none;
            color: #ffffff;
        }
        QPushButton#stopBtn:hover {
            background-color: #b91c1c;
        }
        QComboBox {
            background-color: #0d1117;
            border: 1px solid #30363d;
            border-radius: 5px;
            padding: 2px 10px 2px 3px;
            color: #c9d1d9;
            font-weight: bold;
            font-size: 13px;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 15px;
            border-left-width: 1px;
            border-left-color: #30363d;
            border-left-style: solid;
        }
        QCheckBox {
            color: #c9d1d9;
            font-size: 13px;
            font-weight: bold;
        }
        QSlider::groove:horizontal {
            border: 1px solid #30363d;
            height: 6px;
            background: #0d1117;
            border-radius: 3px;
        }
        QSlider::handle:horizontal {
            background: #00d2ff;
            border: 1px solid #00d2ff;
            width: 12px;
            height: 12px;
            margin: -3px 0;
            border-radius: 6px;
        }
        QScrollBar:vertical {
            border: none;
            background: #0d1117;
            width: 8px;
            margin: 0px 0 0px 0;
        }
        QScrollBar::handle:vertical {
            background: #30363d;
            min-height: 20px;
            border-radius: 4px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
        }
        QTextEdit#logTerminal {
            border: 1px solid #30363d;
            border-radius: 6px;
            font-family: 'Consolas', monospace;
        }
        """
        main_win.setStyleSheet(qss)

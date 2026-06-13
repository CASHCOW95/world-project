from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator, QDoubleValidator
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QLabel, 
    QPushButton, QComboBox, QSlider, QLineEdit, QTabWidget, QCheckBox, 
    QRadioButton, QButtonGroup, QProgressBar, QTextEdit, QScrollArea,
    QGroupBox
)

class UiSetup:
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

        def create_data_row(layout, label, value):
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setObjectName("dataLabel")
            val = QLabel(value)
            val.setObjectName("dataValue")
            val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(val)
            layout.addLayout(row)
            return val

        def create_slider_row(layout, label, min_v, max_v, current_v, callback, is_float=False):
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setFixedWidth(110)
            lbl.setObjectName("dataLabel")
            slider = QSlider(Qt.Horizontal)
            slider.setRange(min_v, max_v)
            slider.setValue(int(current_v))
            slider.setFixedHeight(25)
            
            val_txt = QLineEdit(str(current_v/10.0 if is_float else current_v))
            val_txt.setFixedWidth(45)
            val_txt.setFixedHeight(22)
            val_txt.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; font-size: 11px; padding: 2px; text-align: center;")
            
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

        def create_key_combo(grid, title, r, c, default_v):
            box = QVBoxLayout()
            lbl = QLabel(title)
            lbl.setObjectName("subLabel")
            cb = QComboBox()
            cb.setFixedHeight(28)
            cb.addItems(["space", "ctrl", "alt", "shift", "insert", "del", "home", "end", "pgup", "pgdn"] + list("abcdefghijklmnopqrstuvwxyz"))
            cb.setCurrentText(default_v)
            box.addWidget(lbl)
            box.addWidget(cb)
            grid.addLayout(box, r, c)
            return cb

        # 관리자 위젯 목록 리스트 초기화
        main_win.admin_widgets = []

        central_widget = QWidget()
        main_win.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(6)
        
        # --- 1. 상단 헤더 영역 ---
        header_widget = QWidget()
        header_vbox = QVBoxLayout(header_widget)
        header_vbox.setContentsMargins(0, 0, 0, 0)
        header_vbox.setSpacing(4)

        # 타이틀 및 관리자 권한 경고 라벨 행
        title_row = QHBoxLayout()
        main_win.title_label = QLabel("AUTOmaple v2.0.0")
        main_win.title_label.setObjectName("mainTitle")
        title_row.addWidget(main_win.title_label)
        title_row.addStretch()

        # UAC 관리자 권한 경고 라벨 (기본 숨김, 비관리자 시 메인 파일에서 활성화)
        main_win.admin_status_lbl = QLabel("")
        main_win.admin_status_lbl.setObjectName("adminStatusLbl")
        main_win.admin_status_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        title_row.addWidget(main_win.admin_status_lbl)
        header_vbox.addLayout(title_row)
        
        # AI 프로필 셀렉터 행
        profile_row = QHBoxLayout()
        lbl_prof = QLabel("AI 프로필:")
        lbl_prof.setObjectName("subLabel")
        lbl_prof.setFixedWidth(60)
        main_win.profile_combo = QComboBox()
        main_win.profile_combo.setFixedHeight(30)
        main_win.profile_combo.setEditable(True)
        main_win.profile_combo.currentTextChanged.connect(main_win.settings_manager.on_profile_change)
        profile_row.addWidget(lbl_prof)
        profile_row.addWidget(main_win.profile_combo)
        header_vbox.addLayout(profile_row)

        # 헤더 기능 버튼 행 (💾저장, 🔍업데이트, 🌓테마, 🛡️관리자)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(4)
        
        main_win.save_btn = QPushButton("💾 저장")
        main_win.save_btn.setObjectName("headerBtn")
        main_win.save_btn.setFixedHeight(28)
        main_win.save_btn.clicked.connect(main_win.settings_manager.save_current_profile)
        btn_row.addWidget(main_win.save_btn)
        
        main_win.btn_check_update = QPushButton("🔍 검사")
        main_win.btn_check_update.setObjectName("headerBtn")
        main_win.btn_check_update.setFixedHeight(28)
        main_win.btn_check_update.clicked.connect(main_win.check_startup_update)
        btn_row.addWidget(main_win.btn_check_update)

        main_win.btn_theme_toggle = QPushButton("🌓 테마")
        main_win.btn_theme_toggle.setObjectName("headerBtn")
        main_win.btn_theme_toggle.setFixedHeight(28)
        # theme_toggle은 메인 윈도우의 toggle_theme() 메서드에 연동됨
        btn_row.addWidget(main_win.btn_theme_toggle)

        main_win.btn_admin_mode = QPushButton("🛡️ 관리자")
        main_win.btn_admin_mode.setObjectName("headerBtn")
        main_win.btn_admin_mode.setFixedHeight(28)
        # admin_mode는 메인 윈도우의 toggle_admin_mode() 메서드에 연동됨
        btn_row.addWidget(main_win.btn_admin_mode)
        
        header_vbox.addLayout(btn_row)
        main_layout.addWidget(header_widget)
        
        # --- 2. 중앙 탭 영역 ---
        main_win.main_tabs = QTabWidget()
        main_win.main_tabs.setObjectName("mainTabs")
        
        # ==========================================
        # 탭 1: 사냥/상태 (Hunt & Metrics)
        # ==========================================
        tab1_widget = QWidget()
        tab1_vbox = QVBoxLayout(tab1_widget)
        tab1_vbox.setContentsMargins(5, 5, 5, 5)
        tab1_vbox.setSpacing(6)
        
        # 시스템 상태 지표 그룹
        metrics_group = QGroupBox("시스템 상태 지표")
        metrics_vbox = QVBoxLayout(metrics_group)
        metrics_vbox.setContentsMargins(10, 10, 10, 10)
        metrics_vbox.setSpacing(4)
        
        main_win.data_runtime = create_data_row(metrics_vbox, "가동 시간", "00:00:00")
        main_win.data_total_time = create_data_row(metrics_vbox, "누적 사냥", "00:00:00")
        main_win.data_recovery_left = create_data_row(metrics_vbox, "회수 남은시간", "비활성")
        main_win.data_recovery_left.setStyleSheet("color: #56f09b; font-weight: bold;")
        main_win.data_pet_left = create_data_row(metrics_vbox, "펫먹이 남은시간", "비활성")
        main_win.data_pet_left.setStyleSheet("color: #56f09b; font-weight: bold;")
        main_win.data_errors = create_data_row(metrics_vbox, "탐지 기록", "0회")
        main_win.data_char_pos = create_data_row(metrics_vbox, "캐릭터 좌표", "인식 불가")
        
        # CPU/RAM
        cpu_row = QHBoxLayout()
        main_win.cpu_label = QLabel("CPU 0%", objectName="subLabel")
        main_win.cpu_label.setFixedWidth(55)
        main_win.cpu_bar = QProgressBar(objectName="metricBar")
        main_win.cpu_bar.setFixedHeight(8)
        main_win.cpu_bar.setTextVisible(False)
        cpu_row.addWidget(main_win.cpu_label)
        cpu_row.addWidget(main_win.cpu_bar)
        metrics_vbox.addLayout(cpu_row)
        
        ram_row = QHBoxLayout()
        main_win.ram_label = QLabel("RAM 0%", objectName="subLabel")
        main_win.ram_label.setFixedWidth(55)
        main_win.ram_bar = QProgressBar(objectName="metricBar")
        main_win.ram_bar.setFixedHeight(8)
        main_win.ram_bar.setTextVisible(False)
        ram_row.addWidget(main_win.ram_label)
        ram_row.addWidget(main_win.ram_bar)
        metrics_vbox.addLayout(ram_row)
        
        tab1_vbox.addWidget(metrics_group)
        
        # 미니맵 분석 시각화 그룹
        minimap_group = QGroupBox("미니맵 분석 및 시각화")
        minimap_vbox = QVBoxLayout(minimap_group)
        minimap_vbox.setContentsMargins(10, 10, 10, 10)
        minimap_vbox.setSpacing(6)
        
        # 영역설정, 자동인식 버튼 행
        det_btn_row = QHBoxLayout()
        main_win.sel_btn = QPushButton("영역 설정")
        main_win.sel_btn.setFixedHeight(24)
        main_win.sel_btn.setStyleSheet("font-size: 11px; padding: 2px; border-radius: 5px; background-color: #238636; color: white; font-weight: bold;")
        main_win.sel_btn.clicked.connect(main_win.open_selector)
        det_btn_row.addWidget(main_win.sel_btn)
        
        main_win.auto_det_btn = QPushButton("자동 인식")
        main_win.auto_det_btn.setFixedHeight(24)
        main_win.auto_det_btn.setStyleSheet("font-size: 11px; padding: 2px; border-radius: 5px; background-color: #0288d1; color: white; font-weight: bold;")
        main_win.auto_det_btn.clicked.connect(main_win.minimap_detector.auto_detect_minimap)
        det_btn_row.addWidget(main_win.auto_det_btn)
        minimap_vbox.addLayout(det_btn_row)
        
        # 미니맵 모드 라디오 토글 형식
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
        minimap_vbox.addLayout(options_layout)
        
        # 미니맵 프리뷰 라벨
        main_win.minimap_preview = QLabel("대기 중...")
        main_win.minimap_preview.setObjectName("previewLabel")
        main_win.minimap_preview.setFixedHeight(160)
        main_win.minimap_preview.setAlignment(Qt.AlignCenter)
        minimap_vbox.addWidget(main_win.minimap_preview)
        
        tab1_vbox.addWidget(minimap_group)
        tab1_vbox.addStretch()
        
        main_win.main_tabs.addTab(make_scrollable(tab1_widget), "사냥/상태")
        
        # ==========================================
        # 탭 2: 상점/회수 (Shop & Recovery)
        # ==========================================
        tab2_widget = QWidget()
        tab2_vbox = QVBoxLayout(tab2_widget)
        tab2_vbox.setContentsMargins(5, 5, 5, 5)
        tab2_vbox.setSpacing(6)
        
        # 2.1 상점 자동 판매 시퀀스 그룹
        sell_group = QGroupBox("인벤토리 자동 판매")
        sell_vbox = QVBoxLayout(sell_group)
        sell_vbox.setContentsMargins(10, 10, 10, 10)
        sell_vbox.setSpacing(6)
        
        # 설명 라벨
        guide_lbl = QLabel("💡 좌표 설정창 클릭 후 마우스를 대고 F1 누르면 자동 등록")
        guide_lbl.setStyleSheet("color: #56f09b; font-size: 10px; font-weight: bold;")
        guide_lbl.setWordWrap(True)
        sell_vbox.addWidget(guide_lbl)
        
        # 자동 판매 체크박스 및 주기
        auto_sell_row = QHBoxLayout()
        main_win.chk_auto_sell = QCheckBox("자동 판매 활성화")
        main_win.chk_auto_sell.setStyleSheet("color: #00d2ff; font-weight: bold;")
        main_win.chk_auto_sell.stateChanged.connect(main_win.settings_manager.save_settings_silently)
        
        lbl_auto_sell_interval = QLabel("주기:")
        main_win.txt_auto_sell_interval = QLineEdit("5")
        main_win.txt_auto_sell_interval.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; text-align: center;")
        main_win.txt_auto_sell_interval.setFixedWidth(35)
        main_win.txt_auto_sell_interval.setValidator(QIntValidator(1, 120))
        main_win.txt_auto_sell_interval.editingFinished.connect(main_win.settings_manager.save_settings_silently)
        lbl_unit_m = QLabel("분")
        
        auto_sell_row.addWidget(main_win.chk_auto_sell)
        auto_sell_row.addSpacing(10)
        auto_sell_row.addWidget(lbl_auto_sell_interval)
        auto_sell_row.addWidget(main_win.txt_auto_sell_interval)
        auto_sell_row.addWidget(lbl_unit_m)
        auto_sell_row.addStretch()
        sell_vbox.addLayout(auto_sell_row)
        
        # 좌표 및 딜레이 그리드 레이아웃
        pos_grid = QGridLayout()
        pos_grid.setSpacing(4)
        
        # 헬퍼 함수: 좌표 및 딜레이 행 추가
        def add_sell_pos_row(grid, row_idx, label, name, def_pos, def_del, tooltip):
            grid.addWidget(QLabel(label, objectName="subLabel"), row_idx, 0)
            txt_pos = QLineEdit(def_pos)
            txt_pos.setObjectName(name)
            txt_pos.setToolTip(tooltip)
            txt_pos.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; font-size: 11px; padding: 2px;")
            txt_pos.editingFinished.connect(main_win.settings_manager.save_settings_silently)
            grid.addWidget(txt_pos, row_idx, 1)
            
            lbl_d = QLabel("대기:")
            lbl_d.setStyleSheet("color: #8a99af; font-size: 11px; margin-left: 5px;")
            grid.addWidget(lbl_d, row_idx, 2)
            
            txt_del = QLineEdit(def_del)
            txt_del.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; font-size: 11px; padding: 2px; text-align: center;")
            txt_del.setFixedWidth(35)
            txt_del.setValidator(QDoubleValidator(0.0, 10.0, 2))
            txt_del.editingFinished.connect(main_win.settings_manager.save_settings_silently)
            grid.addWidget(txt_del, row_idx, 3)
            
            # 딜레이 필드와 라벨은 관리자 위젯으로 수집
            main_win.admin_widgets.append(lbl_d)
            main_win.admin_widgets.append(txt_del)
            return txt_pos, txt_del
            
        main_win.txt_sell_pos1, main_win.txt_sell_delay1 = add_sell_pos_row(pos_grid, 0, "1(상점열기):", "sell_pos1", "0, 0", "1.5", "좌표1 (상점열기)")
        main_win.txt_sell_pos2, main_win.txt_sell_delay2 = add_sell_pos_row(pos_grid, 1, "2(거래클릭):", "sell_pos2", "0, 0", "1.0", "좌표2 (거래클릭/엔터)")
        main_win.txt_sell_pos3, main_win.txt_sell_delay3 = add_sell_pos_row(pos_grid, 2, "3(기타탭):", "sell_pos3", "0, 0", "0.5", "좌표3 (기타창이동)")
        main_win.txt_sell_pos4, main_win.txt_sell_delay4 = add_sell_pos_row(pos_grid, 3, "4(반복더블):", "sell_pos4", "0, 0", "0.12", "좌표4 (판매슬롯반복)")
        main_win.txt_sell_pos5, main_win.txt_sell_delay5 = add_sell_pos_row(pos_grid, 4, "5(나가기):", "sell_pos5", "0, 0", "0.5", "좌표5 (상점나가기)")
        sell_vbox.addLayout(pos_grid)
        
        # 추가 설정 행
        sell_opt_row = QHBoxLayout()
        sell_opt_row.setSpacing(4)
        lbl_r = QLabel("행수:")
        lbl_r.setStyleSheet("font-size: 11px;")
        main_win.txt_sell_rows = QLineEdit("8")
        main_win.txt_sell_rows.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; text-align: center;")
        main_win.txt_sell_rows.setFixedWidth(28)
        main_win.txt_sell_rows.setValidator(QIntValidator(1, 20))
        main_win.txt_sell_rows.editingFinished.connect(main_win.settings_manager.save_settings_silently)
        
        lbl_sr = QLabel("시작:")
        lbl_sr.setStyleSheet("font-size: 11px;")
        main_win.txt_sell_start_row = QLineEdit("2")
        main_win.txt_sell_start_row.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; text-align: center;")
        main_win.txt_sell_start_row.setFixedWidth(28)
        main_win.txt_sell_start_row.setValidator(QIntValidator(1, 20))
        main_win.txt_sell_start_row.editingFinished.connect(main_win.settings_manager.save_settings_silently)
        
        lbl_sd = QLabel("딜레이:")
        lbl_sd.setStyleSheet("font-size: 11px;")
        main_win.txt_sell_delay = QLineEdit("0.05")
        main_win.txt_sell_delay.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; text-align: center;")
        main_win.txt_sell_delay.setFixedWidth(35)
        main_win.txt_sell_delay.setValidator(QDoubleValidator(0.01, 2.0, 2))
        main_win.txt_sell_delay.editingFinished.connect(main_win.settings_manager.save_settings_silently)
        
        sell_opt_row.addWidget(lbl_r)
        sell_opt_row.addWidget(main_win.txt_sell_rows)
        sell_opt_row.addWidget(lbl_sr)
        sell_opt_row.addWidget(main_win.txt_sell_start_row)
        sell_opt_row.addWidget(lbl_sd)
        sell_opt_row.addWidget(main_win.txt_sell_delay)
        sell_opt_row.addStretch()
        
        # 추가 판매 설정들은 관리자 필드로 숨김
        main_win.admin_widgets.append(lbl_r)
        main_win.admin_widgets.append(main_win.txt_sell_rows)
        main_win.admin_widgets.append(lbl_sr)
        main_win.admin_widgets.append(main_win.txt_sell_start_row)
        main_win.admin_widgets.append(lbl_sd)
        main_win.admin_widgets.append(main_win.txt_sell_delay)
        
        sell_vbox.addLayout(sell_opt_row)
        tab2_vbox.addWidget(sell_group)
        
        # 2.2 아이템 회수 설정 그룹
        rec_group = QGroupBox("아이템 회수 및 복귀 모드")
        rec_vbox = QVBoxLayout(rec_group)
        rec_vbox.setContentsMargins(10, 10, 10, 10)
        rec_vbox.setSpacing(6)
        
        # 활성화 체크박스
        main_win.chk_pingpong_recovery = QCheckBox("아이템 회수 모드 사용")
        main_win.chk_pingpong_recovery.setStyleSheet("QCheckBox { color: #c9d1d9; font-weight: bold; font-size: 12px; }")
        rec_vbox.addWidget(main_win.chk_pingpong_recovery)
        
        rec_input_grid = QGridLayout()
        rec_input_grid.setSpacing(4)
        
        lbl_style = "color: #8a99af; font-size: 11px; font-weight: bold;"
        input_style = "background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; font-size: 11px; padding: 2px; text-align: center;"
        
        # 주기 및 시간
        lbl_int = QLabel("회수주기(초):")
        lbl_int.setStyleSheet(lbl_style)
        main_win.txt_pingpong_recovery_interval = QLineEdit("60")
        main_win.txt_pingpong_recovery_interval.setStyleSheet(input_style)
        main_win.txt_pingpong_recovery_interval.setFixedWidth(45)
        main_win.txt_pingpong_recovery_interval.setValidator(QIntValidator(1, 9999))
        
        lbl_dur = QLabel("회수시간(초):")
        lbl_dur.setStyleSheet(lbl_style)
        main_win.txt_pingpong_recovery_duration = QLineEdit("10")
        main_win.txt_pingpong_recovery_duration.setStyleSheet(input_style)
        main_win.txt_pingpong_recovery_duration.setFixedWidth(45)
        main_win.txt_pingpong_recovery_duration.setValidator(QIntValidator(1, 999))
        
        rec_input_grid.addWidget(lbl_int, 0, 0)
        rec_input_grid.addWidget(main_win.txt_pingpong_recovery_interval, 0, 1)
        rec_input_grid.addWidget(lbl_dur, 0, 2)
        rec_input_grid.addWidget(main_win.txt_pingpong_recovery_duration, 0, 3)
        
        # 사냥층 Y / 등록 버튼
        lbl_hy = QLabel("사냥층 Y:")
        lbl_hy.setStyleSheet(lbl_style)
        main_win.txt_pingpong_hunt_y = QLineEdit("67")
        main_win.txt_pingpong_hunt_y.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; font-size: 11px; padding: 2px;")
        main_win.txt_pingpong_hunt_y.setReadOnly(True)
        main_win.txt_pingpong_hunt_y.setFixedHeight(22)
        
        main_win.btn_register_hunt_y = QPushButton("등록")
        main_win.btn_register_hunt_y.setStyleSheet("font-size: 10px; padding: 2px; border-radius: 4px; background-color: #238636; color: white; font-weight: bold;")
        main_win.btn_register_hunt_y.setFixedSize(45, 22)
        main_win.btn_register_hunt_y.clicked.connect(lambda: main_win.register_current_layer('hunt'))
        
        rec_input_grid.addWidget(lbl_hy, 1, 0)
        rec_input_grid.addWidget(main_win.txt_pingpong_hunt_y, 1, 1, 1, 2)
        rec_input_grid.addWidget(main_win.btn_register_hunt_y, 1, 3)
        
        # 회수층 Y / 등록 버튼
        lbl_ry = QLabel("회수층 Y:")
        lbl_ry.setStyleSheet(lbl_style)
        main_win.txt_pingpong_recovery_y = QLineEdit("81")
        main_win.txt_pingpong_recovery_y.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; font-size: 11px; padding: 2px;")
        main_win.txt_pingpong_recovery_y.setReadOnly(True)
        main_win.txt_pingpong_recovery_y.setFixedHeight(22)
        
        main_win.btn_register_recovery_y = QPushButton("등록")
        main_win.btn_register_recovery_y.setStyleSheet("font-size: 10px; padding: 2px; border-radius: 4px; background-color: #238636; color: white; font-weight: bold;")
        main_win.btn_register_recovery_y.setFixedSize(45, 22)
        main_win.btn_register_recovery_y.clicked.connect(lambda: main_win.register_current_layer('recovery'))
        
        rec_input_grid.addWidget(lbl_ry, 2, 0)
        rec_input_grid.addWidget(main_win.txt_pingpong_recovery_y, 2, 1, 1, 2)
        rec_input_grid.addWidget(main_win.btn_register_recovery_y, 2, 3)
        
        # 복귀 X범위
        lbl_rx = QLabel("복귀 X범위:")
        lbl_rx.setStyleSheet(lbl_style)
        
        rx_box = QHBoxLayout()
        rx_box.setSpacing(2)
        main_win.txt_pingpong_return_x_min = QLineEdit("45")
        main_win.txt_pingpong_return_x_min.setStyleSheet(input_style)
        main_win.txt_pingpong_return_x_min.setFixedWidth(30)
        main_win.txt_pingpong_return_x_min.setObjectName("return_x_min")
        
        lbl_tld = QLabel("~")
        lbl_tld.setStyleSheet("color: #8a99af;")
        
        main_win.txt_pingpong_return_x_max = QLineEdit("50")
        main_win.txt_pingpong_return_x_max.setStyleSheet(input_style)
        main_win.txt_pingpong_return_x_max.setFixedWidth(30)
        main_win.txt_pingpong_return_x_max.setObjectName("return_x_max")
        
        rx_box.addWidget(main_win.txt_pingpong_return_x_min)
        rx_box.addWidget(lbl_tld)
        rx_box.addWidget(main_win.txt_pingpong_return_x_max)
        rx_widget = QWidget()
        rx_widget.setLayout(rx_box)
        
        # 로프 상승 시간
        lbl_rtime = QLabel("로프(초):")
        lbl_rtime.setStyleSheet(lbl_style)
        main_win.txt_pingpong_rope_climb_time = QLineEdit("1.5")
        main_win.txt_pingpong_rope_climb_time.setStyleSheet(input_style)
        main_win.txt_pingpong_rope_climb_time.setFixedWidth(40)
        main_win.txt_pingpong_rope_climb_time.setValidator(QDoubleValidator(0.1, 10.0, 1))
        
        rec_input_grid.addWidget(lbl_rx, 3, 0)
        rec_input_grid.addWidget(rx_widget, 3, 1)
        rec_input_grid.addWidget(lbl_rtime, 3, 2)
        rec_input_grid.addWidget(main_win.txt_pingpong_rope_climb_time, 3, 3)
        
        rec_vbox.addLayout(rec_input_grid)
        
        # 복귀 시퀀스 텍스트 창
        lbl_rseq = QLabel("복귀 시퀀스 (Y축 회복 이동 명령):", objectName="subLabel")
        rec_vbox.addWidget(lbl_rseq)
        main_win.txt_pingpong_return_seq = QLineEdit("TELE_UP, TELE_UP")
        main_win.txt_pingpong_return_seq.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; font-size: 11px; padding: 2px;")
        main_win.txt_pingpong_return_seq.setObjectName("return_seq")
        rec_vbox.addWidget(main_win.txt_pingpong_return_seq)
        
        # 텔포 포인트 및 회수 시퀀스 (고급)
        teleport_layout = QHBoxLayout()
        teleport_layout.setSpacing(4)
        lbl_t_lbl = QLabel("텔포포인트 (T):")
        lbl_t_lbl.setStyleSheet(lbl_style)
        
        lbl_tx_ = QLabel("X:")
        lbl_tx_.setStyleSheet("color: #8a99af;")
        main_win.txt_pingpong_teleport_x = QLineEdit("-1")
        main_win.txt_pingpong_teleport_x.setStyleSheet(input_style)
        main_win.txt_pingpong_teleport_x.setFixedWidth(35)
        main_win.txt_pingpong_teleport_x.setObjectName("teleport_x")
        main_win.txt_pingpong_teleport_x.editingFinished.connect(main_win.settings_manager.save_settings_silently)
        
        lbl_ty_ = QLabel("Y:")
        lbl_ty_.setStyleSheet("color: #8a99af;")
        main_win.txt_pingpong_teleport_y = QLineEdit("-1")
        main_win.txt_pingpong_teleport_y.setStyleSheet(input_style)
        main_win.txt_pingpong_teleport_y.setFixedWidth(35)
        main_win.txt_pingpong_teleport_y.setObjectName("teleport_y")
        main_win.txt_pingpong_teleport_y.editingFinished.connect(main_win.settings_manager.save_settings_silently)
        
        teleport_layout.addWidget(lbl_t_lbl)
        teleport_layout.addWidget(lbl_tx_)
        teleport_layout.addWidget(main_win.txt_pingpong_teleport_x)
        teleport_layout.addWidget(lbl_ty_)
        teleport_layout.addWidget(main_win.txt_pingpong_teleport_y)
        teleport_layout.addStretch()
        rec_vbox.addLayout(teleport_layout)
        
        lbl_rec_seq_lbl = QLabel("회수 시퀀스 (회수층 진입 이동 명령):", objectName="subLabel")
        rec_vbox.addWidget(lbl_rec_seq_lbl)
        main_win.txt_pingpong_recovery_seq = QLineEdit("")
        main_win.txt_pingpong_recovery_seq.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; font-size: 11px; padding: 2px;")
        main_win.txt_pingpong_recovery_seq.setObjectName("recovery_seq")
        main_win.txt_pingpong_recovery_seq.editingFinished.connect(main_win.settings_manager.save_settings_silently)
        rec_vbox.addWidget(main_win.txt_pingpong_recovery_seq)
        
        # 회수 모드 활성화/비활성화 시 내부 위젯 Enable/Disable 처리 바인딩
        def toggle_recovery_inputs(checked):
            main_win.txt_pingpong_recovery_interval.setEnabled(checked)
            main_win.txt_pingpong_recovery_duration.setEnabled(checked)
            main_win.txt_pingpong_hunt_y.setEnabled(checked)
            main_win.txt_pingpong_recovery_y.setEnabled(checked)
            main_win.btn_register_hunt_y.setEnabled(checked)
            main_win.btn_register_recovery_y.setEnabled(checked)
            main_win.txt_pingpong_return_x_min.setEnabled(checked)
            main_win.txt_pingpong_return_x_max.setEnabled(checked)
            main_win.txt_pingpong_rope_climb_time.setEnabled(checked)
            main_win.txt_pingpong_return_seq.setEnabled(checked)
            main_win.txt_pingpong_teleport_x.setEnabled(checked)
            main_win.txt_pingpong_teleport_y.setEnabled(checked)
            main_win.txt_pingpong_recovery_seq.setEnabled(checked)
            
        main_win.chk_pingpong_recovery.toggled.connect(toggle_recovery_inputs)
        toggle_recovery_inputs(False)
        
        tab2_vbox.addWidget(rec_group)
        tab2_vbox.addStretch()
        
        main_win.main_tabs.addTab(make_scrollable(tab2_widget), "상점/회수")
        
        # ==========================================
        # 탭 3: 감시/버프 (Watch & Buff)
        # ==========================================
        tab3_widget = QWidget()
        tab3_vbox = QVBoxLayout(tab3_widget)
        tab3_vbox.setContentsMargins(5, 5, 5, 5)
        tab3_vbox.setSpacing(6)
        
        # 3.1 버프 시전 설정 그룹
        buff_group = QGroupBox("버프 자동 시전 설정")
        buff_layout = QVBoxLayout(buff_group)
        buff_layout.setContentsMargins(10, 10, 10, 10)
        buff_layout.setSpacing(6)
        
        def add_buff_row(layout, idx, label, def_k, def_i, def_h):
            row = QHBoxLayout()
            row.setSpacing(2)
            chk = QCheckBox(label)
            chk.setStyleSheet("color: #c9d1d9; font-weight: bold; font-size: 11px;")
            chk.toggled.connect(main_win.settings_manager.save_settings_silently)
            
            cb_k = QComboBox()
            cb_k.setFixedWidth(55)
            cb_k.setFixedHeight(22)
            cb_k.addItems(["ctrl", "alt", "shift", "insert", "del", "home", "end", "pgup", "pgdn"] + list("abcdefghijklmnopqrstuvwxyz") + ["f1", "f2", "f3", "f7", "f10"])
            cb_k.setCurrentText(def_k)
            cb_k.currentIndexChanged.connect(main_win.settings_manager.save_settings_silently)
            
            txt_i = QLineEdit(def_i)
            txt_i.setFixedWidth(40)
            txt_i.setFixedHeight(22)
            txt_i.setValidator(QIntValidator(1, 99999))
            txt_i.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; text-align: center;")
            txt_i.editingFinished.connect(main_win.settings_manager.save_settings_silently)
            
            txt_h = QLineEdit(def_h)
            txt_h.setFixedWidth(30)
            txt_h.setFixedHeight(22)
            txt_h.setValidator(QDoubleValidator(0.01, 10.0, 2))
            txt_h.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; text-align: center;")
            txt_h.editingFinished.connect(main_win.settings_manager.save_settings_silently)
            
            row.addWidget(chk)
            row.addWidget(QLabel("키:", objectName="subLabel"))
            row.addWidget(cb_k)
            row.addWidget(QLabel("초:", objectName="subLabel"))
            row.addWidget(txt_i)
            row.addWidget(QLabel("홀드:", objectName="subLabel"))
            row.addWidget(txt_h)
            
            layout.addLayout(row)
            return chk, cb_k, txt_i, txt_h
            
        main_win.chk_buff1_use, main_win.cb_buff1_key, main_win.txt_buff1_int, main_win.txt_buff1_hold = add_buff_row(buff_layout, 1, "버프1", "ctrl", "180", "0.5")
        main_win.chk_buff2_use, main_win.cb_buff2_key, main_win.txt_buff2_int, main_win.txt_buff2_hold = add_buff_row(buff_layout, 2, "버프2", "home", "200", "0.5")
        
        tab3_vbox.addWidget(buff_group)
        
        # 3.2 안전 감시 설정 그룹
        safety_group = QGroupBox("안전 감시 설정")
        safety_layout = QVBoxLayout(safety_group)
        safety_layout.setContentsMargins(10, 10, 10, 10)
        safety_layout.setSpacing(6)
        
        # 하단 사냥
        main_win.chk_bottom_hunt = QCheckBox("하단 사냥 활성화 (시간 후 복귀)")
        main_win.chk_bottom_hunt.setChecked(False)
        main_win.chk_bottom_hunt.toggled.connect(main_win.update_use_bottom_hunt)
        safety_layout.addWidget(main_win.chk_bottom_hunt)
        
        # 하단 Y / 유지 시간 슬라이더 (가로가 좁아 한 슬롯으로 통합)
        main_win.bottom_y_slider = create_slider_row(safety_layout, "하단 Y 기준:", 0, 150, 80, main_win.update_bottom_y)
        main_win.bottom_time_slider = create_slider_row(safety_layout, "하단 유지(초):", 5, 30, 10, main_win.update_bottom_time)
        
        # 추락 감지 복귀
        main_win.chk_fall_recovery = QCheckBox("추락 감지 시 복귀 (텔포 시퀀스)")
        main_win.chk_fall_recovery.setChecked(False)
        main_win.chk_fall_recovery.toggled.connect(main_win.update_use_fall_recovery)
        safety_layout.addWidget(main_win.chk_fall_recovery)
        main_win.fall_y_slider = create_slider_row(safety_layout, "추락 Y 기준:", 0, 150, 110, main_win.update_fall_y)
        
        # 캐릭터 인식 불가 중단
        main_win.chk_escape_lost = QCheckBox("캐릭터 미인식 시 사냥 일시중단")
        main_win.chk_escape_lost.setChecked(False)
        main_win.chk_escape_lost.toggled.connect(main_win.update_use_escape_lost)
        safety_layout.addWidget(main_win.chk_escape_lost)
        main_win.lost_time_slider = create_slider_row(safety_layout, "탈출 대기(초):", 2, 15, 5, main_win.update_lost_timeout)
        
        # 감시(잠수) 모드, 마을 이동 방지
        main_win.chk_watch_mode = QCheckBox("감시(잠수) 모드 활성화 (안티매크로만 감시)")
        main_win.chk_watch_mode.setChecked(False)
        main_win.chk_watch_mode.toggled.connect(main_win.update_use_watch_mode)
        safety_layout.addWidget(main_win.chk_watch_mode)
        
        main_win.chk_anti_town = QCheckBox("마을 이동 방지 활성화 (미세 좌우 이동)")
        main_win.chk_anti_town.setChecked(False)
        main_win.chk_anti_town.toggled.connect(main_win.update_use_anti_town)
        safety_layout.addWidget(main_win.chk_anti_town)
        
        tab3_vbox.addWidget(safety_group)
        
        # 3.3 낚시 및 복층 사냥 그룹
        special_group = QGroupBox("특수 사냥 기동 설정")
        special_layout = QVBoxLayout(special_group)
        special_layout.setContentsMargins(10, 10, 10, 10)
        special_layout.setSpacing(6)
        
        main_win.chk_fishing_mode = QCheckBox("낚시사냥 활성화 (F9 지정자리 고정)")
        main_win.chk_fishing_mode.setChecked(False)
        main_win.chk_fishing_mode.toggled.connect(main_win.update_use_fishing_mode)
        special_layout.addWidget(main_win.chk_fishing_mode)
        
        main_win.lbl_fish_pos = QLabel("지정된 낚시 좌표: X: 미지정, Y: 미지정")
        main_win.lbl_fish_pos.setStyleSheet("color: #00d2ff; font-weight: bold; font-size: 11px; margin-left: 10px;")
        special_layout.addWidget(main_win.lbl_fish_pos)
        
        main_win.chk_multifloor = QCheckBox("복층 순환사냥 활성화")
        main_win.chk_multifloor.setChecked(False)
        main_win.chk_multifloor.toggled.connect(main_win.update_use_multifloor)
        special_layout.addWidget(main_win.chk_multifloor)
        main_win.multifloor_up_slider = create_slider_row(special_layout, "상승 횟수:", 0, 3, 1, main_win.update_multifloor_up_count)
        
        tab3_vbox.addWidget(special_group)
        tab3_vbox.addStretch()
        
        main_win.main_tabs.addTab(make_scrollable(tab3_widget), "감시/버프")
        
        # ==========================================
        # 탭 4: 경로/웨이포인트 (Route & Waypoints)
        # ==========================================
        tab4_widget = QWidget()
        tab4_vbox = QVBoxLayout(tab4_widget)
        tab4_vbox.setContentsMargins(5, 5, 5, 5)
        tab4_vbox.setSpacing(6)
        
        # F2 안내문
        guide_lbl_f2 = QLabel("📍 순환 좌표 기록 슬롯 (QLineEdit 클릭 후 F2 누르면 자동 입력)")
        guide_lbl_f2.setStyleSheet("color: #56f09b; font-size: 10px; font-weight: bold;")
        guide_lbl_f2.setWordWrap(True)
        tab4_vbox.addWidget(guide_lbl_f2)
        
        # 30개 웨이포인트 스크롤 리스트
        main_win.lbl_waypoints = []
        main_win.txt_waypoints_x_min = []
        main_win.txt_waypoints_x_max = []
        main_win.txt_waypoints_y = []
        main_win.cb_waypoints_move = []
        main_win.txt_waypoints_stay = []
        
        wp_scroll = QScrollArea()
        wp_scroll.setWidgetResizable(True)
        wp_scroll.setFrameShape(QFrame.NoFrame)
        wp_scroll.setStyleSheet("background-color: transparent;")
        
        wp_scroll_content = QWidget()
        wp_scroll_content.setStyleSheet("background-color: transparent;")
        wp_scroll_grid = QGridLayout(wp_scroll_content)
        wp_scroll_grid.setContentsMargins(0, 0, 5, 0)
        wp_scroll_grid.setSpacing(4)
        
        # 가로 공간을 극대화하기 위해 각 슬롯 당 2개 행으로 구성
        # 1행: [슬롯번호] [x_min]~[x_max] [Y] [대기] [🗑️] [▲] [▼]
        # 2행: [  ↓ 이동방식:] [QComboBox]
        for idx in range(main_win.waypoint_count):
            row_idx = 2 * idx
            
            lbl = QLabel(f"{idx+1:02d}:")
            lbl.setStyleSheet("color: #8a99af; font-weight: bold; font-size: 12px;")
            lbl.setFixedWidth(20)
            main_win.lbl_waypoints.append(lbl)
            wp_scroll_grid.addWidget(lbl, row_idx, 0)
            
            # X min/max 상자
            x_box = QHBoxLayout()
            x_box.setSpacing(1)
            x_box.setContentsMargins(0, 0, 0, 0)
            
            txt_x_min = QLineEdit()
            txt_x_min.setFixedWidth(26)
            txt_x_min.setFixedHeight(20)
            txt_x_min.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 4px; font-weight: bold; font-size: 10px; padding: 1px; text-align: center;")
            txt_x_min.setValidator(QIntValidator(-1, 9999))
            txt_x_min.setObjectName(f"waypoint_{idx}_x_min")
            txt_x_min.editingFinished.connect(lambda i=idx: main_win.waypoint_manager.on_waypoint_editing_finished(i, 'x_min'))
            
            lbl_tilde_x = QLabel("~")
            lbl_tilde_x.setStyleSheet("color: #8a99af; font-weight: bold;")
            lbl_tilde_x.setFixedWidth(6)
            lbl_tilde_x.setAlignment(Qt.AlignCenter)
            
            txt_x_max = QLineEdit()
            txt_x_max.setFixedWidth(26)
            txt_x_max.setFixedHeight(20)
            txt_x_max.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 4px; font-weight: bold; font-size: 10px; padding: 1px; text-align: center;")
            txt_x_max.setValidator(QIntValidator(-1, 9999))
            txt_x_max.setObjectName(f"waypoint_{idx}_x_max")
            txt_x_max.editingFinished.connect(lambda i=idx: main_win.waypoint_manager.on_waypoint_editing_finished(i, 'x_max'))
            
            x_box.addWidget(txt_x_min)
            x_box.addWidget(lbl_tilde_x)
            x_box.addWidget(txt_x_max)
            
            x_widget = QWidget()
            x_widget.setLayout(x_box)
            x_widget.setFixedWidth(60)
            wp_scroll_grid.addWidget(x_widget, row_idx, 1)
            
            main_win.txt_waypoints_x_min.append(txt_x_min)
            main_win.txt_waypoints_x_max.append(txt_x_max)
            
            # Y
            txt_y = QLineEdit()
            txt_y.setFixedWidth(30)
            txt_y.setFixedHeight(20)
            txt_y.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 4px; font-weight: bold; font-size: 10px; padding: 1px; text-align: center;")
            txt_y.setValidator(QIntValidator(-1, 9999))
            txt_y.setObjectName(f"waypoint_{idx}_y")
            txt_y.editingFinished.connect(lambda i=idx: main_win.waypoint_manager.on_waypoint_editing_finished(i, 'y'))
            wp_scroll_grid.addWidget(txt_y, row_idx, 2)
            main_win.txt_waypoints_y.append(txt_y)
            
            # 대기 시간
            txt_stay = QLineEdit()
            txt_stay.setFixedWidth(26)
            txt_stay.setFixedHeight(20)
            txt_stay.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 4px; font-weight: bold; font-size: 10px; padding: 1px; text-align: center;")
            dbl_val = QDoubleValidator(0.1, 10.0, 1)
            dbl_val.setNotation(QDoubleValidator.StandardNotation)
            txt_stay.setValidator(dbl_val)
            txt_stay.editingFinished.connect(lambda i=idx: main_win.waypoint_manager.on_waypoint_stay_editing_finished(i))
            wp_scroll_grid.addWidget(txt_stay, row_idx, 3)
            main_win.txt_waypoints_stay.append(txt_stay)
            
            # 🗑️ 삭제 버튼
            del_btn = QPushButton("🗑️")
            del_btn.setFixedSize(22, 20)
            del_btn.setStyleSheet("background-color: #21262d; border: 1px solid #f85149; color: #f85149; border-radius: 4px; padding: 0px;")
            del_btn.clicked.connect(lambda checked=False, i=idx: main_win.waypoint_manager.delete_waypoint(i))
            wp_scroll_grid.addWidget(del_btn, row_idx, 4)
            
            # ▲ 버튼
            up_btn = QPushButton("▲")
            up_btn.setFixedSize(20, 20)
            up_btn.setStyleSheet("background-color: #21262d; border: 1px solid #30363d; color: #c9d1d9; border-radius: 4px; font-size: 9px; padding: 0px;")
            up_btn.clicked.connect(lambda checked=False, i=idx: main_win.waypoint_manager.shift_waypoint(i, -1))
            wp_scroll_grid.addWidget(up_btn, row_idx, 5)
            
            # ▼ 버튼
            dn_btn = QPushButton("▼")
            dn_btn.setFixedSize(20, 20)
            dn_btn.setStyleSheet("background-color: #21262d; border: 1px solid #30363d; color: #c9d1d9; border-radius: 4px; font-size: 9px; padding: 0px;")
            dn_btn.clicked.connect(lambda checked=False, i=idx: main_win.waypoint_manager.shift_waypoint(i, 1))
            wp_scroll_grid.addWidget(dn_btn, row_idx, 6)
            
            # 2행: 이동 방식 QComboBox
            cb_move = QComboBox()
            cb_move.setFixedHeight(20)
            cb_move.addItems([
                "TELE_LEFT", "TELE_RIGHT", "TELE_UP", 
                "JUMP_LEFT", "JUMP_RIGHT", "JUMP_UP",
                "WALK_LEFT", "WALK_RIGHT", "DROP"
            ])
            cb_move.setStyleSheet("QComboBox { background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 4px; font-weight: bold; font-size: 10px; padding: 1px 3px; } QComboBox::drop-down { border: none; }")
            cb_move.currentIndexChanged.connect(lambda c_idx, i=idx: main_win.waypoint_manager.on_waypoint_move_changed(i, c_idx))
            main_win.cb_waypoints_move.append(cb_move)
            
            next_idx = (idx + 2) if idx < main_win.waypoint_count - 1 else 1
            arrow_lbl = QLabel(f"   ↓ {idx+1}→{next_idx} 방식:")
            arrow_lbl.setStyleSheet("color: #8a99af; font-size: 10px;")
            
            wp_scroll_grid.addWidget(arrow_lbl, row_idx + 1, 1, 1, 2)
            wp_scroll_grid.addWidget(cb_move, row_idx + 1, 3, 1, 4)
            
        wp_scroll.setWidget(wp_scroll_content)
        wp_scroll.setFixedHeight(240)
        tab4_vbox.addWidget(wp_scroll)
        
        main_win.reset_waypoints_btn = QPushButton("순환 좌표 전체 초기화")
        main_win.reset_waypoints_btn.setFixedHeight(30)
        main_win.reset_waypoints_btn.setStyleSheet("font-weight: bold; border-radius: 8px;")
        main_win.reset_waypoints_btn.clicked.connect(main_win.waypoint_manager.reset_waypoints)
        tab4_vbox.addWidget(main_win.reset_waypoints_btn)
        
        # 사냥 경로 녹화 관련 (베타 탭에서 여기로 병합 이동)
        rec_route_group = QGroupBox("사냥 경로 녹화 및 분석")
        rec_route_vbox = QVBoxLayout(rec_route_group)
        rec_route_vbox.setContentsMargins(8, 8, 8, 8)
        rec_route_vbox.setSpacing(4)
        
        main_win.btn_record_start = QPushButton("🔴 녹화 시작")
        main_win.btn_record_start.setFixedHeight(30)
        main_win.btn_record_start.setStyleSheet("background-color: #9e1c1c; color: white; font-size: 12px; font-weight: bold; border-radius: 6px;")
        main_win.btn_record_start.clicked.connect(main_win.waypoint_manager.start_route_recording)
        rec_route_vbox.addWidget(main_win.btn_record_start)
        
        main_win.btn_record_stop = QPushButton("⏹️ 녹화 종료 및 경로 분석")
        main_win.btn_record_stop.setFixedHeight(30)
        main_win.btn_record_stop.setStyleSheet("background-color: #21262d; color: #8a99af; font-size: 12px; font-weight: bold; border-radius: 6px;")
        main_win.btn_record_stop.setEnabled(False)
        main_win.btn_record_stop.clicked.connect(main_win.waypoint_manager.stop_route_recording)
        rec_route_vbox.addWidget(main_win.btn_record_stop)
        
        main_win.lbl_record_status = QLabel("현재 상태: 녹화 대기 중...")
        main_win.lbl_record_status.setStyleSheet("color: #8a99af; font-size: 11px; font-weight: bold;")
        rec_route_vbox.addWidget(main_win.lbl_record_status)
        
        main_win.chk_auto_apply_route = QCheckBox("녹화 종료 시 순환사냥 좌표에 즉시 적용")
        main_win.chk_auto_apply_route.setChecked(True)
        rec_route_vbox.addWidget(main_win.chk_auto_apply_route)
        
        tab4_vbox.addWidget(rec_route_group)
        tab4_vbox.addStretch()
        
        main_win.main_tabs.addTab(make_scrollable(tab4_widget), "경로/웨이포인트")
        
        # ==========================================
        # 탭 5: 로그/디버그 (Log & Debug & System)
        # ==========================================
        tab5_widget = QWidget()
        tab5_vbox = QVBoxLayout(tab5_widget)
        tab5_vbox.setContentsMargins(5, 5, 5, 5)
        tab5_vbox.setSpacing(6)
        
        # 안티매크로 감지 창
        anti_group = QGroupBox("거짓말탐지기 감지 모니터링")
        anti_vbox = QVBoxLayout(anti_group)
        anti_vbox.setContentsMargins(8, 8, 8, 8)
        anti_vbox.setSpacing(4)
        
        main_win.shape_preview = QLabel("탐색 중...")
        main_win.shape_preview.setObjectName("previewLabel")
        main_win.shape_preview.setFixedHeight(120)
        main_win.shape_preview.setAlignment(Qt.AlignCenter)
        anti_vbox.addWidget(main_win.shape_preview)
        
        main_win.shape_console = QTextEdit()
        main_win.shape_console.setReadOnly(True)
        main_win.shape_console.setFixedHeight(60)
        main_win.shape_console.setObjectName("logTerminal")
        main_win.shape_console.setStyleSheet("color: #58a6ff; font-size: 10px;")
        anti_vbox.addWidget(main_win.shape_console)
        
        tab5_vbox.addWidget(anti_group)
        
        # 시스템 로그 텍스트창
        log_group = QGroupBox("시스템 로그 콘솔")
        log_vbox = QVBoxLayout(log_group)
        log_vbox.setContentsMargins(8, 8, 8, 8)
        log_vbox.setSpacing(4)
        
        main_win.log_text = QTextEdit()
        main_win.log_text.setObjectName("logTerminal")
        main_win.log_text.setReadOnly(True)
        main_win.log_text.setFixedHeight(180)
        log_vbox.addWidget(main_win.log_text)
        tab5_vbox.addWidget(log_group)
        
        # 시스템 옵션 셋 (원래 사냥탭에 있던 단축키/주기 및 환경설정이 좁아짐에 따라 병합 배치)
        sys_opt_group = QGroupBox("환경 및 입력 설정")
        sys_opt_vbox = QVBoxLayout(sys_opt_group)
        sys_opt_vbox.setContentsMargins(10, 10, 10, 10)
        sys_opt_vbox.setSpacing(4)
        
        # 공격 주기/텔포 주기/소모품 주기 (관리자 전용 격리)
        main_win.att_slider = create_slider_row(sys_opt_vbox, "공격 주기:", 50, 500, main_win.attack_delay_ms, main_win.update_att_delay)
        main_win.dash_slider = create_slider_row(sys_opt_vbox, "텔포 주기:", 50, 1000, main_win.dash_delay_ms, main_win.update_dash_delay)
        main_win.pet_slider = create_slider_row(sys_opt_vbox, "소모품(분):", 1, 60, main_win.periodic_interval_min, main_win.update_pet_interval)
        main_win.precision_slider = create_slider_row(sys_opt_vbox, "정밀도(고급):", 0, 30, 0, main_win.update_precision, is_float=True)
        main_win.precision_slider.setEnabled(False)
        
        main_win.admin_widgets.append(main_win.att_slider)
        main_win.admin_widgets.append(main_win.dash_slider)
        main_win.admin_widgets.append(main_win.pet_slider)
        main_win.admin_widgets.append(main_win.precision_slider)
        
        # 키 매핑 Grid
        key_grid = QGridLayout()
        key_grid.setSpacing(4)
        main_win.key_att_cb = create_key_combo(key_grid, "공격", 0, 0, "end")
        main_win.key_jump_cb = create_key_combo(key_grid, "점프", 0, 1, "alt")
        main_win.key_teleport_cb = create_key_combo(key_grid, "텔포", 1, 0, "shift")
        main_win.key_pet_cb = create_key_combo(key_grid, "물약", 1, 1, "del")
        sys_opt_vbox.addLayout(key_grid)
        
        # 공격키 리셋 시 떼는 지연 시간 (초) 설정 행
        reset_delay_layout = QHBoxLayout()
        lbl_reset_delay = QLabel("공격키 떼기 지연(초):")
        lbl_reset_delay.setStyleSheet("color: #8a99af; font-size: 11px; font-weight: bold;")
        main_win.txt_att_reset_delay = QLineEdit("0.15")
        main_win.txt_att_reset_delay.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; font-size: 11px; padding: 2px; text-align: center;")
        main_win.txt_att_reset_delay.setFixedWidth(50)
        from PySide6.QtGui import QDoubleValidator
        main_win.txt_att_reset_delay.setValidator(QDoubleValidator(0.01, 5.0, 2))
        main_win.txt_att_reset_delay.editingFinished.connect(main_win.settings_manager.save_settings_silently)
        reset_delay_layout.addWidget(lbl_reset_delay)
        reset_delay_layout.addStretch()
        reset_delay_layout.addWidget(main_win.txt_att_reset_delay)
        sys_opt_vbox.addLayout(reset_delay_layout)
        
        # 기본 시스템 체크박스
        main_win.chk_alert = QCheckBox("안티매크로 경고음 알람")
        main_win.chk_alert.setChecked(True)
        main_win.chk_alert.toggled.connect(main_win.update_use_alert)
        sys_opt_vbox.addWidget(main_win.chk_alert)
        
        main_win.chk_shape_anti = QCheckBox("투명 도형 감지 추적 활성")
        main_win.chk_shape_anti.setChecked(False)
        main_win.chk_shape_anti.toggled.connect(main_win.update_use_shape_anti)
        sys_opt_vbox.addWidget(main_win.chk_shape_anti)
        
        # 자동 판매 슬라이더와 체크박스 (더미)
        main_win.chk_sell = QCheckBox("자동 판매 (베타 연동)")
        main_win.chk_sell.setEnabled(False)
        main_win.chk_sell.setVisible(False) # 비노출로 숨김 처리
        main_win.sell_slider = create_slider_row(sys_opt_vbox, "판매 주기:", 10, 60, main_win.sell_interval_min, main_win.update_sell_interval)
        main_win.sell_slider.setVisible(False)
        
        main_win.chk_top = QCheckBox("항상 윈도우 창 맨 위로 고정")
        main_win.chk_top.setChecked(True)
        main_win.chk_top.toggled.connect(main_win.update_window_flags)
        sys_opt_vbox.addWidget(main_win.chk_top)
        
        main_win.opacity_slider = create_slider_row(sys_opt_vbox, "창 투명도:", 30, 100, 100, main_win.update_opacity)
        
        # 입력 시뮬레이션
        input_row = QHBoxLayout()
        input_lbl = QLabel("입력방식:")
        input_lbl.setObjectName("dataLabel")
        input_lbl.setFixedWidth(65)
        main_win.input_mode_combo = QComboBox()
        main_win.input_mode_combo.setFixedHeight(24)
        main_win.input_mode_combo.addItems(["PyAutoGUI (기본)", "Windows API (커스텀)", "Logitech (드라이버)"])
        main_win.input_mode_combo.setCurrentIndex(main_win.input_mode)
        main_win.input_mode_combo.currentIndexChanged.connect(main_win.update_input_mode)
        input_row.addWidget(input_lbl)
        input_row.addWidget(main_win.input_mode_combo)
        sys_opt_vbox.addLayout(input_row)
        
        # 관리자 위젯에 입력 시뮬레이션 관련도 수집하여 격리
        main_win.admin_widgets.append(main_win.input_mode_combo)
        main_win.admin_widgets.append(input_lbl)
        
        # 업데이트 런처 트리거용 숨김 버튼 (안전 바인딩 유지)
        main_win.btn_oneclick_update = QPushButton()
        main_win.btn_oneclick_update.setVisible(False)
        main_win.btn_oneclick_update.clicked.connect(main_win.trigger_update)
        sys_opt_vbox.addWidget(main_win.btn_oneclick_update)
        
        tab5_vbox.addWidget(sys_opt_group)
        tab5_vbox.addStretch()
        
        main_win.main_tabs.addTab(make_scrollable(tab5_widget), "로그/디버그")
        
        main_layout.addWidget(main_win.main_tabs)
        
        # 사냥 모드 라디오 버튼 (헤더 또는 탭에 미포함되어 임시로 숨김 바인딩 처리하여 에러 방지)
        main_win.btn_group_mode = QButtonGroup(main_win)
        main_win.radio_lr = QRadioButton("핑퐁사냥")
        main_win.radio_v2 = QRadioButton("순환사냥 V2")
        main_win.btn_group_mode.addButton(main_win.radio_lr, 0)
        main_win.btn_group_mode.addButton(main_win.radio_v2, 2)
        
        # 보이지 않는 위젯으로 바인딩하여 백그라운드 연동 안정성 유지
        hidden_mode_widget = QWidget()
        hidden_layout = QHBoxLayout(hidden_mode_widget)
        hidden_layout.addWidget(main_win.radio_lr)
        hidden_layout.addWidget(main_win.radio_v2)
        hidden_mode_widget.setVisible(False)
        main_layout.addWidget(hidden_mode_widget)
        
        # 사냥 모드 변경 라디오 연결
        main_win.btn_group_mode.buttonClicked.connect(main_win.on_hunt_mode_radio_changed)
        
        # 핑퐁사냥 설정 접기 버튼 및 컨테이너 더미 바인딩 (UI 미노출이나 에러 방지용)
        main_win.grp_lr_settings = QGroupBox()
        main_win.grp_lr_settings.setVisible(False)
        main_win.lr_toggle_btn = QPushButton()
        main_win.lr_container = QWidget()
        main_win.grp_v2_settings = QGroupBox()
        main_win.grp_v2_settings.setVisible(False)
        
        main_layout.addWidget(main_win.grp_lr_settings)
        main_layout.addWidget(main_win.grp_v2_settings)

        # 슬라이더 더미 바인딩 (에러 방지용)
        dummy_layout = QVBoxLayout()
        main_win.x_min_slider = QSlider(Qt.Horizontal)
        main_win.x_max_slider = QSlider(Qt.Horizontal)
        main_win.stat_range_slider = QSlider(Qt.Horizontal)
        dummy_layout.addWidget(main_win.x_min_slider)
        dummy_layout.addWidget(main_win.x_max_slider)
        dummy_layout.addWidget(main_win.stat_range_slider)
        dummy_widget = QWidget()
        dummy_widget.setLayout(dummy_layout)
        dummy_widget.setVisible(False)
        main_layout.addWidget(dummy_widget)

        main_win.txt_pingpong_x_min = QLineEdit("20")
        main_win.txt_pingpong_x_min.setVisible(False)
        main_win.txt_pingpong_x_max = QLineEdit("180")
        main_win.txt_pingpong_x_max.setVisible(False)
        main_layout.addWidget(main_win.txt_pingpong_x_min)
        main_layout.addWidget(main_win.txt_pingpong_x_max)

        # --- 3. 최하단 고정 푸터 버튼들 ---
        footer_layout = QGridLayout()
        footer_layout.setSpacing(4)
        
        main_win.start_btn = QPushButton("사냥 시작 [F5]", objectName="startBtn")
        main_win.start_btn.setFixedHeight(50)
        main_win.start_btn.clicked.connect(main_win.start_hunting)
        footer_layout.addWidget(main_win.start_btn, 0, 0)
        
        main_win.stop_btn = QPushButton("사냥 중지 [F6]", objectName="stopBtn")
        main_win.stop_btn.setFixedHeight(50)
        main_win.stop_btn.clicked.connect(main_win.stop_hunting)
        main_win.stop_btn.setEnabled(False)
        footer_layout.addWidget(main_win.stop_btn, 0, 1)
        
        main_win.manual_sell_btn = QPushButton("인벤 판매 [F1]", objectName="sellBtn")
        main_win.manual_sell_btn.setFixedHeight(32)
        main_win.manual_sell_btn.clicked.connect(main_win.run_manual_sell)
        footer_layout.addWidget(main_win.manual_sell_btn, 1, 0)
        
        main_win.stop_all_btn = QPushButton("종료", objectName="exitBtn")
        main_win.stop_all_btn.setFixedHeight(32)
        main_win.stop_all_btn.clicked.connect(main_win.close)
        footer_layout.addWidget(main_win.stop_all_btn, 1, 1)
        
        main_layout.addLayout(footer_layout)

    @staticmethod
    def apply_qss(main_win, theme_mode="dark"):
        if theme_mode == "dark":
            # 다크 고대비 테마 QSS
            style = (
                "QMainWindow { background-color: #0b0e14; } "
                "#mainTitle { color: #ffffff; font-size: 16px; font-weight: 900; } "
                "#adminStatusLbl { color: #f85149; font-size: 10px; font-weight: bold; } "
                "#panelTitle { color: #00d2ff; font-size: 13px; font-weight: 800; } "
                "#subLabel { color: #8a99af; font-size: 11px; } "
                "#dataLabel { color: #8b949e; font-size: 11px; } "
                "#dataValue { color: #00d2ff; font-size: 12px; font-weight: 700; } "
                "QTabWidget::pane { border: 2px solid #30363d; background: #161b22; border-radius: 8px; } "
                "QTabBar::tab { background: #0d1117; color: #8b949e; padding: 6px 4px; min-width: 65px; font-size: 10px; font-weight: bold; border: 1px solid #30363d; } "
                "QTabBar::tab:selected { background: #161b22; color: #00d2ff; border-bottom: 2px solid #00d2ff; } "
                "QPushButton { background-color: #21262d; color: #c9d1d9; border: 2px solid #30363d; border-radius: 8px; font-weight: 700; font-size: 11px; } "
                "QPushButton:hover { background-color: #30363d; border-color: #8b949e; } "
                "#headerBtn { background-color: #21262d; border: 1px solid #30363d; color: #c9d1d9; font-size: 10px; border-radius: 5px; } "
                "#headerBtn:hover { background-color: #00d2ff; color: #0b0e14; font-weight: bold; } "
                "#startBtn { background-color: #238636; color: #ffffff; font-size: 15px; border: 2px solid #2ea44f; } "
                "#startBtn:hover { background-color: #2ea44f; } "
                "#stopBtn { background-color: #21262d; border: 2px solid #f85149; color: #f85149; font-size: 15px; } "
                "#stopBtn:hover { background-color: #f85149; color: white; } "
                "#sellBtn { background-color: #0969da; color: white; border: 1px solid #0a73ec; } "
                "#sellBtn:hover { background-color: #0c7dfd; } "
                "#exitBtn { background-color: #21262d; border: 2px solid #8b949e; color: #c9d1d9; } "
                "#exitBtn:hover { background-color: #30363d; } "
                "#logTerminal { background-color: #0d1117; color: #8b949e; border: 1px solid #30363d; border-radius: 8px; padding: 4px; font-size: 11px; } "
                "QLabel#previewLabel { background-color: #000000; border-radius: 10px; border: 2px solid #30363d; } "
                "QGroupBox { color: #00d2ff; font-weight: bold; border: 2px solid #30363d; border-radius: 8px; margin-top: 6px; padding-top: 10px; font-size: 11px; } "
                "QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; left: 8px; } "
                "QCheckBox { color: #c9d1d9; font-size: 11px; font-weight: bold; } "
                "QComboBox { background-color: #0d1117; color: #c9d1d9; border: 1px solid #30363d; border-radius: 5px; font-size: 11px; padding: 2px; } "
                "QLineEdit { background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-size: 11px; } "
                "QLineEdit:focus { border: 1px solid #00d2ff; } "
                "QSlider::groove:horizontal { border: 1px solid #30363d; height: 6px; background: #0d1117; border-radius: 3px; } "
                "QSlider::handle:horizontal { background: #00d2ff; border: 1px solid #00d2ff; width: 12px; margin-top: -3px; margin-bottom: -3px; border-radius: 6px; } "
                "QProgressBar { border: 1px solid #30363d; background-color: #0d1117; border-radius: 4px; } "
                "QProgressBar::chunk { background-color: #00d2ff; } "
                "QScrollBar:vertical { border: 1px solid #30363d; background: #0d1117; width: 12px; margin: 0px; } "
                "QScrollBar::handle:vertical { background: #58a6ff; min-height: 20px; border-radius: 5px; } "
                "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; height: 0px; } "
            )
        else:
            # 라이트 고대비 테마 QSS (가독성 강화)
            style = (
                "QMainWindow { background-color: #f6f8fa; } "
                "#mainTitle { color: #24292f; font-size: 16px; font-weight: 900; } "
                "#adminStatusLbl { color: #cf222e; font-size: 10px; font-weight: bold; } "
                "#panelTitle { color: #0969da; font-size: 13px; font-weight: 800; } "
                "#subLabel { color: #57606a; font-size: 11px; } "
                "#dataLabel { color: #57606a; font-size: 11px; } "
                "#dataValue { color: #0969da; font-size: 12px; font-weight: 700; } "
                "QTabWidget::pane { border: 2px solid #d0d7de; background: #ffffff; border-radius: 8px; } "
                "QTabBar::tab { background: #f6f8fa; color: #57606a; padding: 6px 4px; min-width: 65px; font-size: 10px; font-weight: bold; border: 1px solid #d0d7de; } "
                "QTabBar::tab:selected { background: #ffffff; color: #0969da; border-bottom: 2px solid #0969da; } "
                "QPushButton { background-color: #ffffff; color: #24292f; border: 2px solid #d0d7de; border-radius: 8px; font-weight: 700; font-size: 11px; } "
                "QPushButton:hover { background-color: #f3f4f6; border-color: #57606a; } "
                "#headerBtn { background-color: #ffffff; border: 1px solid #d0d7de; color: #24292f; font-size: 10px; border-radius: 5px; } "
                "#headerBtn:hover { background-color: #0969da; color: white; font-weight: bold; } "
                "#startBtn { background-color: #1a7f37; color: #ffffff; font-size: 15px; border: 2px solid #1a7f37; } "
                "#startBtn:hover { background-color: #116329; } "
                "#stopBtn { background-color: #ffffff; border: 2px solid #cf222e; color: #cf222e; font-size: 15px; } "
                "#stopBtn:hover { background-color: #cf222e; color: white; } "
                "#sellBtn { background-color: #0969da; color: white; border: 1px solid #0969da; } "
                "#sellBtn:hover { background-color: #0550ae; } "
                "#exitBtn { background-color: #ffffff; border: 2px solid #57606a; color: #24292f; } "
                "#exitBtn:hover { background-color: #f3f4f6; } "
                "#logTerminal { background-color: #ffffff; color: #24292f; border: 1px solid #d0d7de; border-radius: 8px; padding: 4px; font-size: 11px; } "
                "QLabel#previewLabel { background-color: #eaeef2; border-radius: 10px; border: 2px solid #d0d7de; } "
                "QGroupBox { color: #0969da; font-weight: bold; border: 2px solid #d0d7de; border-radius: 8px; margin-top: 6px; padding-top: 10px; font-size: 11px; } "
                "QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; left: 8px; } "
                "QCheckBox { color: #24292f; font-size: 11px; font-weight: bold; } "
                "QComboBox { background-color: #ffffff; color: #24292f; border: 1px solid #d0d7de; border-radius: 5px; font-size: 11px; padding: 2px; } "
                "QLineEdit { background-color: #ffffff; color: #24292f; border: 1px solid #d0d7de; border-radius: 5px; font-size: 11px; } "
                "QLineEdit:focus { border: 1px solid #0969da; } "
                "QSlider::groove:horizontal { border: 1px solid #d0d7de; height: 6px; background: #eaeef2; border-radius: 3px; } "
                "QSlider::handle:horizontal { background: #0969da; border: 1px solid #0969da; width: 12px; margin-top: -3px; margin-bottom: -3px; border-radius: 6px; } "
                "QProgressBar { border: 1px solid #d0d7de; background-color: #eaeef2; border-radius: 4px; } "
                "QProgressBar::chunk { background-color: #0969da; } "
                "QScrollBar:vertical { border: 1px solid #d0d7de; background: #f6f8fa; width: 12px; margin: 0px; } "
                "QScrollBar::handle:vertical { background: #0969da; min-height: 20px; border-radius: 5px; } "
                "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; height: 0px; } "
            )
        main_win.setStyleSheet(style)

    @staticmethod
    def set_admin_mode_visibility(main_win, show: bool):
        # 관리자 위젯 일괄 보이기/숨기기 제어
        for widget in main_win.admin_widgets:
            widget.setVisible(show)

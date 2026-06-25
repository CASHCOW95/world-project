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
            from PySide6.QtWidgets import QScrollArea
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
            lbl.setFixedWidth(140)
            lbl.setObjectName("dataLabel")
            slider = QSlider(Qt.Horizontal)
            slider.setRange(min_v, max_v)
            slider.setValue(int(current_v))
            slider.setFixedHeight(30)
            
            val_txt = QLineEdit(str(current_v/10.0 if is_float else current_v))
            val_txt.setFixedWidth(55)
            val_txt.setFixedHeight(26)
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
            cb.setFixedHeight(35)
            cb.addItems(["space", "ctrl", "alt", "shift", "insert", "del", "home", "end", "pgup", "pgdn"] + list("abcdefghijklmnopqrstuvwxyz"))
            cb.setCurrentText(default_v)
            box.addWidget(lbl)
            box.addWidget(cb)
            grid.addLayout(box, r, c)
            return cb

        central_widget = QWidget()
        main_win.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(25, 25, 25, 40)
        main_layout.setSpacing(20)
        
        header = QHBoxLayout()
        main_win.title_label = QLabel("AUTOmaple")
        main_win.title_label.setObjectName("mainTitle")
        header.addWidget(main_win.title_label)
        header.addStretch()
        
        p_box = QVBoxLayout()
        p_box.addWidget(QLabel("AI 프로필 관리 센터 /", objectName="subLabel"))
        main_win.profile_combo = QComboBox()
        main_win.profile_combo.setMinimumWidth(320)
        main_win.profile_combo.setFixedHeight(45)
        main_win.profile_combo.setEditable(True)
        main_win.profile_combo.currentTextChanged.connect(main_win.settings_manager.on_profile_change)
        p_box.addWidget(main_win.profile_combo)
        header.addLayout(p_box)
        
        main_win.save_btn = QPushButton("💾 설정 저장")
        main_win.save_btn.setObjectName("saveBtn")
        main_win.save_btn.setFixedSize(140, 60)
        main_win.save_btn.clicked.connect(main_win.settings_manager.save_current_profile)
        header.addWidget(main_win.save_btn)
        
        main_win.btn_check_update = QPushButton("🔍 업데이트 확인")
        main_win.btn_check_update.setObjectName("updateBtn")
        main_win.btn_check_update.setFixedSize(140, 60)
        main_win.btn_check_update.setStyleSheet("background-color: #21262d; border: 1px solid #30363d; color: #c9d1d9; font-weight: bold; border-radius: 15px; font-size: 13px;")
        main_win.btn_check_update.clicked.connect(main_win.check_startup_update)
        header.addWidget(main_win.btn_check_update)
        
        main_layout.addLayout(header)
        
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        left_frame = QFrame()
        left_frame.setObjectName("panelFrame")
        left_frame.setFixedWidth(500)
        left_vbox = QVBoxLayout(left_frame)
        left_vbox.setContentsMargins(15, 20, 15, 15)
        
        mini_header = QHBoxLayout()
        mini_header.addWidget(QLabel("미니맵 분석 및 시각화", objectName="panelTitle"))
        mini_header.addStretch()
        
        main_win.sel_btn = QPushButton("영역 설정")
        main_win.sel_btn.setFixedSize(80, 25)
        main_win.sel_btn.setStyleSheet("font-size: 10px; padding: 2px; border-radius: 5px; background-color: #238636; color: white;")
        main_win.sel_btn.clicked.connect(main_win.open_selector)
        mini_header.addWidget(main_win.sel_btn)
        
        main_win.auto_det_btn = QPushButton("자동 인식")
        main_win.auto_det_btn.setFixedSize(80, 25)
        main_win.auto_det_btn.setStyleSheet("font-size: 10px; padding: 2px; border-radius: 5px; background-color: #0288d1; color: white;")
        main_win.auto_det_btn.clicked.connect(main_win.minimap_detector.auto_detect_minimap)
        mini_header.addWidget(main_win.auto_det_btn)
        
        left_vbox.addLayout(mini_header)
        
        # 미니맵 고정 사용 설정 체크박스 추가
        options_layout = QHBoxLayout()
        main_win.chk_use_saved_minimap = QCheckBox("저장된 미니맵 위치 사용")
        main_win.chk_use_auto_detect = QCheckBox("자동 인식 사용")
        
        # 라디오 버튼처럼 상호배타적으로 작동하도록 연결
        main_win.chk_use_saved_minimap.toggled.connect(
            lambda checked: main_win.chk_use_auto_detect.setChecked(not checked)
        )
        main_win.chk_use_auto_detect.toggled.connect(
            lambda checked: main_win.chk_use_saved_minimap.setChecked(not checked)
        )
        
        # 기본값 설정
        main_win.chk_use_saved_minimap.setChecked(True)
        main_win.chk_use_auto_detect.setChecked(False)
        
        options_layout.addWidget(main_win.chk_use_saved_minimap)
        options_layout.addWidget(main_win.chk_use_auto_detect)
        left_vbox.addLayout(options_layout)

        
        main_win.minimap_preview = QLabel("대기 중...")
        main_win.minimap_preview.setObjectName("previewLabel")
        main_win.minimap_preview.setFixedSize(470, 200)
        main_win.minimap_preview.setAlignment(Qt.AlignCenter)
        left_vbox.addWidget(main_win.minimap_preview)
        left_vbox.addSpacing(15)
        
        left_vbox.addWidget(QLabel("거짓말탐지기 감지 엔진 [실시간]", objectName="panelTitle"))
        main_win.shape_preview = QLabel("탐색 중...")
        main_win.shape_preview.setObjectName("previewLabel")
        main_win.shape_preview.setFixedSize(470, 260)
        main_win.shape_preview.setAlignment(Qt.AlignCenter)
        left_vbox.addWidget(main_win.shape_preview)
        
        main_win.shape_console = QTextEdit()
        main_win.shape_console.setReadOnly(True)
        main_win.shape_console.setFixedHeight(100)
        main_win.shape_console.setObjectName("logTerminal")
        main_win.shape_console.setStyleSheet("color: #58a6ff; font-size: 10px;")
        left_vbox.addWidget(main_win.shape_console)
        content_layout.addWidget(left_frame)
        
        center_frame = QFrame(objectName="panelFrame")
        center_vbox = QVBoxLayout(center_frame)
        center_vbox.setContentsMargins(15, 30, 15, 15)
        center_vbox.addWidget(QLabel("코어 알고리즘 설정", objectName="panelTitle"))
        
        main_win.main_tabs = QTabWidget()
        center_vbox.addWidget(main_win.main_tabs)
        
        # 사냥 모드 설정 탭
        tab_hunt_mode_widget = QWidget()
        tab_hunt_mode_vbox = QVBoxLayout(tab_hunt_mode_widget)
        
        mode_select_box = QGroupBox("사냥 모드 선택")
        mode_select_layout = QHBoxLayout(mode_select_box)
        mode_select_layout.setContentsMargins(15, 15, 15, 15)
        
        main_win.btn_group_mode = QButtonGroup(main_win)
        main_win.radio_lr = QRadioButton("핑퐁사냥")
        main_win.radio_v2 = QRadioButton("순환사냥 V2")
        
        for r_btn in [main_win.radio_lr, main_win.radio_v2]:
            r_btn.setStyleSheet("QRadioButton { color: #c9d1d9; font-size: 14px; font-weight: bold; padding: 5px; } QRadioButton::indicator { width: 16px; height: 16px; }")
            
        main_win.btn_group_mode.addButton(main_win.radio_lr, 0)
        main_win.btn_group_mode.addButton(main_win.radio_v2, 2)
        
        mode_select_layout.addWidget(main_win.radio_lr)
        mode_select_layout.addWidget(main_win.radio_v2)
        tab_hunt_mode_vbox.addWidget(mode_select_box)
        
        # A. 핑퐁사냥 설정 그룹
        main_win.grp_lr_settings = QGroupBox("핑퐁사냥 설정")
        lr_layout = QVBoxLayout(main_win.grp_lr_settings)
        
        main_win.lr_toggle_btn = QPushButton("▲ 설정 접기")
        main_win.lr_toggle_btn.setCheckable(True)
        main_win.lr_toggle_btn.setFixedHeight(28)
        main_win.lr_toggle_btn.setStyleSheet(
            "QPushButton { background-color: #21262d; border: 1px solid #30363d; border-radius: 6px; color: #8a99af; font-weight: bold; font-size: 11px; } "
            "QPushButton:checked { background-color: #30363d; color: #00d2ff; }"
        )
        lr_layout.addWidget(main_win.lr_toggle_btn)
        
        main_win.lr_container = QWidget()
        main_win.lr_container.setStyleSheet("background-color: transparent;")
        lr_container_layout = QVBoxLayout(main_win.lr_container)
        lr_container_layout.setContentsMargins(0, 5, 0, 0)
        lr_container_layout.setSpacing(10)
        
        main_win.x_min_slider = create_slider_row(lr_container_layout, "좌측 경계:", 0, 400, main_win.x_min, main_win.update_x_min)
        main_win.x_max_slider = create_slider_row(lr_container_layout, "우측 경계:", 0, 400, main_win.x_max, main_win.update_x_max)
        
        bounds_box = QHBoxLayout()
        bounds_box.setSpacing(10)
        
        lbl_xmin = QLabel("좌측 경계 X:")
        lbl_xmin.setStyleSheet("color: #8a99af; font-size: 12px; font-weight: bold;")
        main_win.txt_pingpong_x_min = QLineEdit(str(main_win.x_min))
        main_win.txt_pingpong_x_min.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; font-size: 11px; padding: 2px;")
        main_win.txt_pingpong_x_min.setFixedWidth(50)
        main_win.txt_pingpong_x_min.setValidator(QIntValidator(0, 999))
        main_win.txt_pingpong_x_min.setObjectName("x_min")
        main_win.txt_pingpong_x_min.editingFinished.connect(main_win.on_pingpong_x_min_edited)
        
        lbl_xmax = QLabel("우측 경계 X:")
        lbl_xmax.setStyleSheet("color: #8a99af; font-size: 12px; font-weight: bold;")
        main_win.txt_pingpong_x_max = QLineEdit(str(main_win.x_max))
        main_win.txt_pingpong_x_max.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; font-size: 11px; padding: 2px;")
        main_win.txt_pingpong_x_max.setFixedWidth(50)
        main_win.txt_pingpong_x_max.setValidator(QIntValidator(0, 999))
        main_win.txt_pingpong_x_max.setObjectName("x_max")
        main_win.txt_pingpong_x_max.editingFinished.connect(main_win.on_pingpong_x_max_edited)
        
        bounds_box.addWidget(lbl_xmin)
        bounds_box.addWidget(main_win.txt_pingpong_x_min)
        bounds_box.addWidget(lbl_xmax)
        bounds_box.addWidget(main_win.txt_pingpong_x_max)
        lr_container_layout.addLayout(bounds_box)
        
        # 제자리 고정 모드 UI 추가
        main_win.chk_pingpong_fixed = QCheckBox("제자리 고정 (아이템 회수 시에만 이동)")
        main_win.chk_pingpong_fixed.setStyleSheet("QCheckBox { color: #c9d1d9; font-weight: bold; font-size: 13px; margin-top: 5px; }")
        lr_container_layout.addWidget(main_win.chk_pingpong_fixed)
        
        # 아이템 회수 모드 UI 추가
        main_win.chk_pingpong_recovery = QCheckBox("아이템 회수 모드 사용")
        main_win.chk_pingpong_recovery.setStyleSheet("QCheckBox { color: #c9d1d9; font-weight: bold; font-size: 13px; margin-top: 10px; }")
        lr_container_layout.addWidget(main_win.chk_pingpong_recovery)
        
        recovery_grid_widget = QWidget()
        recovery_grid = QGridLayout(recovery_grid_widget)
        recovery_grid.setContentsMargins(10, 5, 10, 5)
        recovery_grid.setSpacing(8)
        
        lbl_style = "color: #8a99af; font-size: 12px; font-weight: bold;"
        input_style = "background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; font-size: 11px; padding: 2px;"
        
        # 1. 회수 주기 & 회수 시간
        lbl_interval = QLabel("회수 주기(초):")
        lbl_interval.setStyleSheet(lbl_style)
        main_win.txt_pingpong_recovery_interval = QLineEdit("60")
        main_win.txt_pingpong_recovery_interval.setStyleSheet(input_style)
        main_win.txt_pingpong_recovery_interval.setFixedWidth(50)
        main_win.txt_pingpong_recovery_interval.setValidator(QIntValidator(1, 9999))
        main_win.txt_pingpong_recovery_interval.setObjectName("recovery_interval")
        
        lbl_duration = QLabel("회수 시간(초):")
        lbl_duration.setStyleSheet(lbl_style)
        main_win.txt_pingpong_recovery_duration = QLineEdit("10")
        main_win.txt_pingpong_recovery_duration.setStyleSheet(input_style)
        main_win.txt_pingpong_recovery_duration.setFixedWidth(50)
        main_win.txt_pingpong_recovery_duration.setValidator(QIntValidator(1, 999))
        main_win.txt_pingpong_recovery_duration.setObjectName("recovery_duration")
        
        recovery_grid.addWidget(lbl_interval, 0, 0)
        recovery_grid.addWidget(main_win.txt_pingpong_recovery_interval, 0, 1)
        recovery_grid.addWidget(lbl_duration, 0, 2)
        recovery_grid.addWidget(main_win.txt_pingpong_recovery_duration, 0, 3)
        
        # 2. 사냥층 Y & 회수층 Y
        lbl_hunt_y = QLabel("사냥층 Y:")
        lbl_hunt_y.setStyleSheet(lbl_style)
        main_win.txt_pingpong_hunt_y = QLineEdit("67")
        main_win.txt_pingpong_hunt_y.setStyleSheet(input_style)
        main_win.txt_pingpong_hunt_y.setFixedWidth(110)
        main_win.txt_pingpong_hunt_y.setReadOnly(True)
        main_win.txt_pingpong_hunt_y.setObjectName("hunt_y")
        
        main_win.btn_register_hunt_y = QPushButton("현재층 등록")
        main_win.btn_register_hunt_y.setStyleSheet("font-size: 11px; padding: 2px; border-radius: 5px; background-color: #238636; color: white; font-weight: bold;")
        main_win.btn_register_hunt_y.setFixedSize(85, 26)
        main_win.btn_register_hunt_y.clicked.connect(lambda: main_win.register_current_layer('hunt'))
        
        lbl_rec_y = QLabel("회수층 Y:")
        lbl_rec_y.setStyleSheet(lbl_style)
        main_win.txt_pingpong_recovery_y = QLineEdit("81")
        main_win.txt_pingpong_recovery_y.setStyleSheet(input_style)
        main_win.txt_pingpong_recovery_y.setFixedWidth(110)
        main_win.txt_pingpong_recovery_y.setReadOnly(True)
        main_win.txt_pingpong_recovery_y.setObjectName("recovery_y")
        
        main_win.btn_register_recovery_y = QPushButton("현재층 등록")
        main_win.btn_register_recovery_y.setStyleSheet("font-size: 11px; padding: 2px; border-radius: 5px; background-color: #238636; color: white; font-weight: bold;")
        main_win.btn_register_recovery_y.setFixedSize(85, 26)
        main_win.btn_register_recovery_y.clicked.connect(lambda: main_win.register_current_layer('recovery'))
        
        recovery_grid.addWidget(lbl_hunt_y, 1, 0)
        recovery_grid.addWidget(main_win.txt_pingpong_hunt_y, 1, 1)
        recovery_grid.addWidget(main_win.btn_register_hunt_y, 1, 2)
        
        recovery_grid.addWidget(lbl_rec_y, 2, 0)
        recovery_grid.addWidget(main_win.txt_pingpong_recovery_y, 2, 1)
        recovery_grid.addWidget(main_win.btn_register_recovery_y, 2, 2)
        
        # 3. 복귀 시작 X 범위 & 로프 상승 시간
        lbl_ret_x = QLabel("복귀 X범위:")
        lbl_ret_x.setStyleSheet(lbl_style)
        
        ret_x_box = QHBoxLayout()
        ret_x_box.setSpacing(2)
        ret_x_box.setContentsMargins(0, 0, 0, 0)
        
        main_win.txt_pingpong_return_x_min = QLineEdit("45")
        main_win.txt_pingpong_return_x_min.setStyleSheet(input_style)
        main_win.txt_pingpong_return_x_min.setFixedWidth(30)
        main_win.txt_pingpong_return_x_min.setValidator(QIntValidator(0, 9999))
        main_win.txt_pingpong_return_x_min.setObjectName("return_x_min")
        
        lbl_tilde = QLabel("~")
        lbl_tilde.setStyleSheet("color: #8a99af; font-weight: bold;")
        lbl_tilde.setFixedWidth(8)
        lbl_tilde.setAlignment(Qt.AlignCenter)
        
        main_win.txt_pingpong_return_x_max = QLineEdit("50")
        main_win.txt_pingpong_return_x_max.setStyleSheet(input_style)
        main_win.txt_pingpong_return_x_max.setFixedWidth(30)
        main_win.txt_pingpong_return_x_max.setValidator(QIntValidator(0, 9999))
        main_win.txt_pingpong_return_x_max.setObjectName("return_x_max")
        
        ret_x_box.addWidget(main_win.txt_pingpong_return_x_min)
        ret_x_box.addWidget(lbl_tilde)
        ret_x_box.addWidget(main_win.txt_pingpong_return_x_max)
        
        ret_x_widget = QWidget()
        ret_x_widget.setLayout(ret_x_box)
        
        lbl_rope = QLabel("로프 시간(초):")
        lbl_rope.setStyleSheet(lbl_style)
        
        main_win.txt_pingpong_rope_climb_time = QLineEdit("1.5")
        main_win.txt_pingpong_rope_climb_time.setStyleSheet(input_style)
        main_win.txt_pingpong_rope_climb_time.setFixedWidth(50)
        main_win.txt_pingpong_rope_climb_time.setValidator(QDoubleValidator(0.1, 10.0, 1))
        
        recovery_grid.addWidget(lbl_ret_x, 3, 0)
        recovery_grid.addWidget(ret_x_widget, 3, 1)
        recovery_grid.addWidget(lbl_rope, 3, 2)
        recovery_grid.addWidget(main_win.txt_pingpong_rope_climb_time, 3, 3)
        
        # 4. 복귀동작 시퀀스
        lbl_seq = QLabel("복귀 시퀀스:")
        lbl_seq.setStyleSheet(lbl_style)
        main_win.txt_pingpong_return_seq = QLineEdit("TELE_UP, TELE_UP")
        main_win.txt_pingpong_return_seq.setStyleSheet(input_style)
        main_win.txt_pingpong_return_seq.setFixedWidth(240)
        main_win.txt_pingpong_return_seq.setObjectName("return_seq")
        
        recovery_grid.addWidget(lbl_seq, 4, 0)
        recovery_grid.addWidget(main_win.txt_pingpong_return_seq, 4, 1, 1, 3)
        
        # 5. 텔레포트 포인트 (T)
        lbl_t_pt = QLabel("텔포포인트 (T):")
        lbl_t_pt.setStyleSheet(lbl_style)
        
        t_pt_box = QHBoxLayout()
        t_pt_box.setSpacing(5)
        t_pt_box.setContentsMargins(0, 0, 0, 0)
        
        lbl_tx = QLabel("X:")
        lbl_tx.setStyleSheet("color: #8a99af; font-size: 11px;")
        main_win.txt_pingpong_teleport_x = QLineEdit("-1")
        main_win.txt_pingpong_teleport_x.setStyleSheet(input_style)
        main_win.txt_pingpong_teleport_x.setFixedWidth(40)
        main_win.txt_pingpong_teleport_x.setValidator(QIntValidator(-1, 9999))
        main_win.txt_pingpong_teleport_x.setObjectName("teleport_x")
        main_win.txt_pingpong_teleport_x.editingFinished.connect(main_win.settings_manager.save_settings_silently)
        
        lbl_ty = QLabel("Y:")
        lbl_ty.setStyleSheet("color: #8a99af; font-size: 11px;")
        main_win.txt_pingpong_teleport_y = QLineEdit("-1")
        main_win.txt_pingpong_teleport_y.setStyleSheet(input_style)
        main_win.txt_pingpong_teleport_y.setFixedWidth(40)
        main_win.txt_pingpong_teleport_y.setValidator(QIntValidator(-1, 9999))
        main_win.txt_pingpong_teleport_y.setObjectName("teleport_y")
        main_win.txt_pingpong_teleport_y.editingFinished.connect(main_win.settings_manager.save_settings_silently)
        
        t_pt_box.addWidget(lbl_tx)
        t_pt_box.addWidget(main_win.txt_pingpong_teleport_x)
        t_pt_box.addWidget(lbl_ty)
        t_pt_box.addWidget(main_win.txt_pingpong_teleport_y)
        t_pt_box.addStretch()
        
        t_pt_widget = QWidget()
        t_pt_widget.setLayout(t_pt_box)
        
        recovery_grid.addWidget(lbl_t_pt, 5, 0)
        recovery_grid.addWidget(t_pt_widget, 5, 1, 1, 3)
        
        # 6. 회수동작 시퀀스
        lbl_rec_seq = QLabel("회수 시퀀스:")
        lbl_rec_seq.setStyleSheet(lbl_style)
        main_win.txt_pingpong_recovery_seq = QLineEdit("")
        main_win.txt_pingpong_recovery_seq.setStyleSheet(input_style)
        main_win.txt_pingpong_recovery_seq.setFixedWidth(240)
        main_win.txt_pingpong_recovery_seq.setObjectName("recovery_seq")
        main_win.txt_pingpong_recovery_seq.editingFinished.connect(main_win.settings_manager.save_settings_silently)
        
        recovery_grid.addWidget(lbl_rec_seq, 6, 0)
        recovery_grid.addWidget(main_win.txt_pingpong_recovery_seq, 6, 1, 1, 3)
        
        # 7. 복귀동작 힌트
        lbl_hint = QLabel("명령어: TELE_LEFT, TELE_RIGHT, TELE_UP, JUMP_LEFT, JUMP_RIGHT, JUMP_UP, WALK_LEFT, WALK_RIGHT, DROP, ROPE_UP (한글 별칭 지원: 위텔포, 아래텔포, 좌텔포, 우텔포, 위점프, 좌점프, 우점프, 좌, 우, 아래, 공격 등)")
        lbl_hint.setStyleSheet("color: #58a6ff; font-size: 9px; font-weight: normal;")
        lbl_hint.setWordWrap(True)
        recovery_grid.addWidget(lbl_hint, 7, 0, 1, 4)
        
        lr_container_layout.addWidget(recovery_grid_widget)
        
        lr_layout.addWidget(main_win.lr_container)
        
        def toggle_lr_settings(checked):
            if checked:
                main_win.lr_container.setVisible(False)
                main_win.lr_toggle_btn.setText("▼ 설정 펼치기")
            else:
                main_win.lr_container.setVisible(True)
                main_win.lr_toggle_btn.setText("▲ 설정 접기")
                
        main_win.lr_toggle_btn.toggled.connect(toggle_lr_settings)
        
        # 비활성화 연동
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
            
        main_win.chk_pingpong_recovery.toggled.connect(toggle_recovery_inputs)
        toggle_recovery_inputs(False)
        
        tab_hunt_mode_vbox.addWidget(main_win.grp_lr_settings)
        
        # B. 제자리 사냥 설정 그룹 (UI에서 표시 제외)
        main_win.grp_stat_settings = QGroupBox("제자리 사냥 설정")
        stat_layout = QVBoxLayout(main_win.grp_stat_settings)
        main_win.stat_range_slider = create_slider_row(stat_layout, "제자리 범위:", 1, 100, main_win.stationary_range, main_win.update_stat_range)
        # tab_hunt_mode_vbox.addWidget(main_win.grp_stat_settings)
        
        # C. 순환 사냥 V2 설정 그룹 (V3)
        main_win.grp_v2_settings = QGroupBox("순환사냥 V2 설정 (V3 확장)")
        v2_outer_layout = QVBoxLayout(main_win.grp_v2_settings)
        v2_outer_layout.addWidget(QLabel("📍 순환 좌표 기록 슬롯 (F2 등록 및 수동 입력)", objectName="subLabel"))
        
        main_win.lbl_waypoints = []
        main_win.txt_waypoints_x_min = []
        main_win.txt_waypoints_x_max = []
        main_win.txt_waypoints_y = []
        main_win.cb_waypoints_move = []
        main_win.txt_waypoints_stay = []
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        scroll_grid = QGridLayout(scroll_content)
        scroll_grid.setContentsMargins(0, 0, 0, 0)
        scroll_grid.setSpacing(6)
        
        for idx in range(main_win.waypoint_count):
            row_idx = 2 * idx
            
            lbl = QLabel(f"슬롯 {idx+1:02d}:")
            lbl.setStyleSheet("color: #8a99af; font-weight: bold; font-size: 13px;")
            lbl.setFixedWidth(50)
            main_win.lbl_waypoints.append(lbl)
            scroll_grid.addWidget(lbl, row_idx, 0)
            
            x_box = QHBoxLayout()
            x_box.setSpacing(2)
            x_box.setContentsMargins(0, 0, 0, 0)
            
            txt_x_min = QLineEdit()
            txt_x_min.setFixedWidth(30)
            txt_x_min.setFixedHeight(26)
            txt_x_min.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; font-size: 11px; padding: 1px;")
            txt_x_min.setValidator(QIntValidator(-1, 9999))
            txt_x_min.setObjectName(f"waypoint_{idx}_x_min")
            txt_x_min.editingFinished.connect(lambda i=idx: main_win.waypoint_manager.on_waypoint_editing_finished(i, 'x_min'))
            
            lbl_tilde_x = QLabel("~")
            lbl_tilde_x.setStyleSheet("color: #8a99af; font-weight: bold;")
            lbl_tilde_x.setFixedWidth(8)
            lbl_tilde_x.setAlignment(Qt.AlignCenter)
            
            txt_x_max = QLineEdit()
            txt_x_max.setFixedWidth(30)
            txt_x_max.setFixedHeight(26)
            txt_x_max.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; font-size: 11px; padding: 1px;")
            txt_x_max.setValidator(QIntValidator(-1, 9999))
            txt_x_max.setObjectName(f"waypoint_{idx}_x_max")
            txt_x_max.editingFinished.connect(lambda i=idx: main_win.waypoint_manager.on_waypoint_editing_finished(i, 'x_max'))
            
            x_box.addWidget(txt_x_min)
            x_box.addWidget(lbl_tilde_x)
            x_box.addWidget(txt_x_max)
            
            x_widget = QWidget()
            x_widget.setLayout(x_box)
            x_widget.setFixedWidth(75)
            scroll_grid.addWidget(x_widget, row_idx, 1)
            
            main_win.txt_waypoints_x_min.append(txt_x_min)
            main_win.txt_waypoints_x_max.append(txt_x_max)
            
            txt_y = QLineEdit()
            txt_y.setFixedWidth(75)
            txt_y.setFixedHeight(26)
            txt_y.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; font-size: 11px; padding: 1px;")
            txt_y.setValidator(QIntValidator(-1, 9999))
            txt_y.setObjectName(f"waypoint_{idx}_y")
            txt_y.editingFinished.connect(lambda i=idx: main_win.waypoint_manager.on_waypoint_editing_finished(i, 'y'))
            scroll_grid.addWidget(txt_y, row_idx, 2)
            main_win.txt_waypoints_y.append(txt_y)
            
            cb_move = QComboBox()
            cb_move.setFixedWidth(110)
            cb_move.setFixedHeight(26)
            cb_move.addItems([
                "TELE_LEFT", "TELE_RIGHT", "TELE_UP", 
                "JUMP_LEFT", "JUMP_RIGHT", "JUMP_UP",
                "WALK_LEFT", "WALK_RIGHT", "DROP"
            ])
            cb_move.setStyleSheet("QComboBox { background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; font-size: 11px; padding: 1px 3px; } QComboBox::drop-down { border: none; }")
            cb_move.currentIndexChanged.connect(lambda c_idx, i=idx: main_win.waypoint_manager.on_waypoint_move_changed(i, c_idx))
            main_win.cb_waypoints_move.append(cb_move)
            
            next_idx = (idx + 2) if idx < main_win.waypoint_count - 1 else 1
            arrow_lbl = QLabel(f"    ↓ 슬롯 {idx+1:02d} → {next_idx:02d} 이동방식:")
            arrow_lbl.setStyleSheet("color: #00d2ff; font-weight: bold; font-size: 11px;")
            scroll_grid.addWidget(arrow_lbl, row_idx + 1, 1)
            scroll_grid.addWidget(cb_move, row_idx + 1, 2, 1, 2)
            
            txt_stay = QLineEdit()
            txt_stay.setFixedWidth(40)
            txt_stay.setFixedHeight(26)
            txt_stay.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; font-size: 11px; padding: 1px;")
            
            dbl_val = QDoubleValidator(0.1, 10.0, 1)
            dbl_val.setNotation(QDoubleValidator.StandardNotation)
            txt_stay.setValidator(dbl_val)
            txt_stay.editingFinished.connect(lambda i=idx: main_win.waypoint_manager.on_waypoint_stay_editing_finished(i))
            main_win.txt_waypoints_stay.append(txt_stay)
            scroll_grid.addWidget(txt_stay, row_idx, 3)
            
            del_btn = QPushButton("🗑️")
            del_btn.setFixedSize(26, 26)
            del_btn.setStyleSheet("background-color: #21262d; border: 1px solid #f85149; color: #f85149; border-radius: 5px; padding: 0px;")
            del_btn.clicked.connect(lambda checked=False, i=idx: main_win.waypoint_manager.delete_waypoint(i))
            scroll_grid.addWidget(del_btn, row_idx, 4)
            
            up_btn = QPushButton("▲")
            up_btn.setFixedSize(24, 26)
            up_btn.setStyleSheet("background-color: #21262d; border: 1px solid #30363d; color: #c9d1d9; border-radius: 5px; font-size: 9px; padding: 0px;")
            up_btn.clicked.connect(lambda checked=False, i=idx: main_win.waypoint_manager.shift_waypoint(i, -1))
            scroll_grid.addWidget(up_btn, row_idx, 5)
            
            dn_btn = QPushButton("▼")
            dn_btn.setFixedSize(24, 26)
            dn_btn.setStyleSheet("background-color: #21262d; border: 1px solid #30363d; color: #c9d1d9; border-radius: 5px; font-size: 9px; padding: 0px;")
            dn_btn.clicked.connect(lambda checked=False, i=idx: main_win.waypoint_manager.shift_waypoint(i, 1))
            scroll_grid.addWidget(dn_btn, row_idx, 6)
            
        scroll.setWidget(scroll_content)
        scroll.setFixedHeight(280)
        v2_outer_layout.addWidget(scroll)
        
        main_win.reset_waypoints_btn = QPushButton("순환 좌표 전체 초기화")
        main_win.reset_waypoints_btn.setFixedHeight(35)
        main_win.reset_waypoints_btn.clicked.connect(main_win.waypoint_manager.reset_waypoints)
        v2_outer_layout.addWidget(main_win.reset_waypoints_btn)
        v2_outer_layout.addSpacing(10)
        
        tab_hunt_mode_vbox.addWidget(main_win.grp_v2_settings)
        tab_hunt_mode_vbox.addStretch()
        
        main_win.main_tabs.addTab(make_scrollable(tab_hunt_mode_widget), "사냥 모드 설정")
        main_win.btn_group_mode.buttonClicked.connect(main_win.on_hunt_mode_radio_changed)
        
        # 단축키/정밀도 탭
        tab_skill_widget = QWidget()
        tab_skill_vbox = QVBoxLayout(tab_skill_widget)
        main_win.precision_slider = create_slider_row(tab_skill_vbox, "인식 정밀도:", 0, 30, 0, main_win.update_precision, is_float=True)
        main_win.precision_slider.setEnabled(False)
        main_win.att_slider = create_slider_row(tab_skill_vbox, "공격 주기:", 50, 500, main_win.attack_delay_ms, main_win.update_att_delay)
        main_win.dash_slider = create_slider_row(tab_skill_vbox, "텔레포트 주기:", 50, 1000, main_win.dash_delay_ms, main_win.update_dash_delay)
        main_win.pet_slider = create_slider_row(tab_skill_vbox, "소모품(분):", 1, 60, main_win.periodic_interval_min, main_win.update_pet_interval)
        
        key_grid = QGridLayout()
        key_grid.setSpacing(12)
        main_win.key_att_cb = create_key_combo(key_grid, "공격", 0, 0, "end")
        main_win.key_jump_cb = create_key_combo(key_grid, "점프", 0, 1, "alt")
        main_win.key_teleport_cb = create_key_combo(key_grid, "텔레포트", 1, 0, "shift")
        main_win.key_pet_cb = create_key_combo(key_grid, "소모품", 1, 1, "del")
        tab_skill_vbox.addLayout(key_grid)
        
        # 버프 자동 시전 설정 그룹
        buff_group = QGroupBox("버프 자동 시전 설정 (초/홀드)")
        buff_group.setStyleSheet("QGroupBox { color: #00d2ff; font-weight: bold; border: 1px solid #30363d; border-radius: 12px; margin-top: 15px; padding: 15px; font-size: 14px; }")
        buff_layout = QVBoxLayout(buff_group)
        
        # 버프 1
        row1 = QHBoxLayout()
        main_win.chk_buff1_use = QCheckBox("버프 1 사용")
        main_win.chk_buff1_use.setStyleSheet("color: #c9d1d9; font-weight: bold;")
        main_win.chk_buff1_use.toggled.connect(main_win.settings_manager.save_settings_silently)
        main_win.cb_buff1_key = QComboBox()
        main_win.cb_buff1_key.setFixedWidth(80)
        main_win.cb_buff1_key.addItems(["ctrl", "alt", "shift", "insert", "del", "home", "end", "pgup", "pgdn"] + list("abcdefghijklmnopqrstuvwxyz") + ["f1", "f2", "f3", "f7", "f10"])
        main_win.cb_buff1_key.setCurrentText("ctrl")
        main_win.cb_buff1_key.currentIndexChanged.connect(main_win.settings_manager.save_settings_silently)
        
        main_win.txt_buff1_int = QLineEdit("180")
        main_win.txt_buff1_int.setFixedWidth(50)
        main_win.txt_buff1_int.setValidator(QIntValidator(1, 99999))
        main_win.txt_buff1_int.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; text-align: center;")
        main_win.txt_buff1_int.editingFinished.connect(main_win.settings_manager.save_settings_silently)
        
        main_win.txt_buff1_hold = QLineEdit("0.5")
        main_win.txt_buff1_hold.setFixedWidth(40)
        main_win.txt_buff1_hold.setValidator(QDoubleValidator(0.01, 10.0, 2))
        main_win.txt_buff1_hold.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; text-align: center;")
        main_win.txt_buff1_hold.editingFinished.connect(main_win.settings_manager.save_settings_silently)
        
        row1.addWidget(main_win.chk_buff1_use)
        row1.addWidget(QLabel("키:"))
        row1.addWidget(main_win.cb_buff1_key)
        row1.addWidget(QLabel("주기(초):"))
        row1.addWidget(main_win.txt_buff1_int)
        row1.addWidget(QLabel("홀드(초):"))
        row1.addWidget(main_win.txt_buff1_hold)
        buff_layout.addLayout(row1)
        
        # 버프 2
        row2 = QHBoxLayout()
        main_win.chk_buff2_use = QCheckBox("버프 2 사용")
        main_win.chk_buff2_use.setStyleSheet("color: #c9d1d9; font-weight: bold;")
        main_win.chk_buff2_use.toggled.connect(main_win.settings_manager.save_settings_silently)
        main_win.cb_buff2_key = QComboBox()
        main_win.cb_buff2_key.setFixedWidth(80)
        main_win.cb_buff2_key.addItems(["ctrl", "alt", "shift", "insert", "del", "home", "end", "pgup", "pgdn"] + list("abcdefghijklmnopqrstuvwxyz") + ["f1", "f2", "f3", "f7", "f10"])
        main_win.cb_buff2_key.setCurrentText("alt")
        main_win.cb_buff2_key.currentIndexChanged.connect(main_win.settings_manager.save_settings_silently)
        
        main_win.txt_buff2_int = QLineEdit("200")
        main_win.txt_buff2_int.setFixedWidth(50)
        main_win.txt_buff2_int.setValidator(QIntValidator(1, 99999))
        main_win.txt_buff2_int.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; text-align: center;")
        main_win.txt_buff2_int.editingFinished.connect(main_win.settings_manager.save_settings_silently)
        
        main_win.txt_buff2_hold = QLineEdit("0.5")
        main_win.txt_buff2_hold.setFixedWidth(40)
        main_win.txt_buff2_hold.setValidator(QDoubleValidator(0.01, 10.0, 2))
        main_win.txt_buff2_hold.setStyleSheet("background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; text-align: center;")
        main_win.txt_buff2_hold.editingFinished.connect(main_win.settings_manager.save_settings_silently)
        
        row2.addWidget(main_win.chk_buff2_use)
        row2.addWidget(QLabel("키:"))
        row2.addWidget(main_win.cb_buff2_key)
        row2.addWidget(QLabel("주기(초):"))
        row2.addWidget(main_win.txt_buff2_int)
        row2.addWidget(QLabel("홀드(초):"))
        row2.addWidget(main_win.txt_buff2_hold)
        buff_layout.addLayout(row2)
        
        tab_skill_vbox.addWidget(buff_group)
        tab_skill_vbox.addStretch()
        main_win.main_tabs.addTab(make_scrollable(tab_skill_widget), "단축키/정밀도")
        
        # 시스템 환경 탭
        tab_adv_widget = QWidget()
        tab_adv_vbox = QVBoxLayout(tab_adv_widget)
        
        main_win.chk_alert = QCheckBox("거탐 알람 울리기")
        main_win.chk_alert.setChecked(True)
        main_win.chk_alert.toggled.connect(main_win.update_use_alert)
        tab_adv_vbox.addWidget(main_win.chk_alert)
        
        main_win.chk_shape_anti = QCheckBox("투명 도형 추적 엔진 활성화")
        main_win.chk_shape_anti.setChecked(False)
        main_win.chk_shape_anti.toggled.connect(main_win.update_use_shape_anti)
        tab_adv_vbox.addWidget(main_win.chk_shape_anti)
        
        main_win.chk_sell = QCheckBox("자동 판매 (준비 중)")
        main_win.chk_sell.setEnabled(False)
        tab_adv_vbox.addWidget(main_win.chk_sell)
        
        main_win.sell_slider = create_slider_row(tab_adv_vbox, "판매 주기:", 10, 60, main_win.sell_interval_min, main_win.update_sell_interval)
        
        main_win.chk_top = QCheckBox("창 항상 맨 위로 고정")
        main_win.chk_top.setChecked(True)
        main_win.chk_top.toggled.connect(main_win.update_window_flags)
        tab_adv_vbox.addWidget(main_win.chk_top)
        
        main_win.opacity_slider = create_slider_row(tab_adv_vbox, "투명도:", 30, 100, 100, main_win.update_opacity)
        
        input_row = QHBoxLayout()
        input_lbl = QLabel("입력 시뮬레이션:")
        input_lbl.setObjectName("dataLabel")
        input_lbl.setFixedWidth(140)
        
        main_win.input_mode_combo = QComboBox()
        main_win.input_mode_combo.setFixedHeight(35)
        main_win.input_mode_combo.addItems(["PyAutoGUI (기본)", "Windows SendInput (커스텀 API)", "Logitech G HUB (드라이버 레벨)"])
        main_win.input_mode_combo.setCurrentIndex(main_win.input_mode)
        main_win.input_mode_combo.currentIndexChanged.connect(main_win.update_input_mode)
        input_row.addWidget(input_lbl)
        input_row.addWidget(main_win.input_mode_combo)
        tab_adv_vbox.addLayout(input_row)
        
        # 업데이트 실행 버튼은 레이아웃에 추가하지 않고 메모리 객체로만 바인딩하여 안전성 유지
        main_win.btn_oneclick_update = QPushButton()
        main_win.btn_oneclick_update.clicked.connect(main_win.trigger_update)
        
        tab_adv_vbox.addStretch()
        main_win.main_tabs.addTab(make_scrollable(tab_adv_widget), "시스템 환경")
        
        # 좌표/안전 설정 탭
        tab_coord_widget = QWidget()
        tab_coord_vbox = QVBoxLayout(tab_coord_widget)
        
        main_win.chk_bottom_hunt = QCheckBox("하단 사냥 활성화 (지정 시간 후 자동 복귀)")
        main_win.chk_bottom_hunt.setChecked(False)
        main_win.chk_bottom_hunt.toggled.connect(main_win.update_use_bottom_hunt)
        tab_coord_vbox.addWidget(main_win.chk_bottom_hunt)
        main_win.bottom_y_slider = create_slider_row(tab_coord_vbox, "하단 Y 기준값:", 0, 150, main_win.bottom_y_threshold, main_win.update_bottom_y)
        main_win.bottom_time_slider = create_slider_row(tab_coord_vbox, "하단 유지 시간(초):", 5, 30, main_win.bottom_hunt_time_sec, main_win.update_bottom_time)
        tab_coord_vbox.addSpacing(10)
        
        main_win.chk_fall_recovery = QCheckBox("추락 감지 시 복귀 (텔레포트 시퀀스)")
        main_win.chk_fall_recovery.setChecked(False)
        main_win.chk_fall_recovery.toggled.connect(main_win.update_use_fall_recovery)
        tab_coord_vbox.addWidget(main_win.chk_fall_recovery)
        main_win.fall_y_slider = create_slider_row(tab_coord_vbox, "추락 Y 기준값:", 0, 150, main_win.fall_y_threshold, main_win.update_fall_y)
        tab_coord_vbox.addSpacing(10)
        
        main_win.chk_escape_lost = QCheckBox("캐릭터 인식 불가 시 사냥 일시 중단")
        main_win.chk_escape_lost.setChecked(False)
        main_win.chk_escape_lost.toggled.connect(main_win.update_use_escape_lost)
        tab_coord_vbox.addWidget(main_win.chk_escape_lost)
        main_win.lost_time_slider = create_slider_row(tab_coord_vbox, "탈출 대기 시간(초):", 2, 15, main_win.lost_timeout_sec, main_win.update_lost_timeout)
        tab_coord_vbox.addSpacing(10)
        
        main_win.chk_watch_mode = QCheckBox("감시(잠수) 모드 활성화 (사냥 중지 및 안티매크로 감시)")
        main_win.chk_watch_mode.setChecked(False)
        main_win.chk_watch_mode.toggled.connect(main_win.update_use_watch_mode)
        tab_coord_vbox.addWidget(main_win.chk_watch_mode)
        
        main_win.chk_anti_town = QCheckBox("마을 이동 방지 활성화 (주기적 미세 좌우 이동)")
        main_win.chk_anti_town.setChecked(False)
        main_win.chk_anti_town.toggled.connect(main_win.update_use_anti_town)
        tab_coord_vbox.addWidget(main_win.chk_anti_town)
        tab_coord_vbox.addSpacing(10)
        
        main_win.chk_fishing_mode = QCheckBox("낚시사냥 활성화 (F9키로 지정한 자리에 고정)")
        main_win.chk_fishing_mode.setChecked(False)
        main_win.chk_fishing_mode.toggled.connect(main_win.update_use_fishing_mode)
        tab_coord_vbox.addWidget(main_win.chk_fishing_mode)
        
        main_win.lbl_fish_pos = QLabel("지정된 낚시 좌표: X: 미지정, Y: 미지정")
        main_win.lbl_fish_pos.setStyleSheet("color: #00d2ff; font-weight: bold; font-size: 13px; margin-left: 20px;")
        tab_coord_vbox.addWidget(main_win.lbl_fish_pos)
        tab_coord_vbox.addSpacing(10)
        
        main_win.chk_multifloor = QCheckBox("복층 순환사냥 활성화 (방향전환 시 텔레포트 상승)")
        main_win.chk_multifloor.setChecked(False)
        main_win.chk_multifloor.toggled.connect(main_win.update_use_multifloor)
        tab_coord_vbox.addWidget(main_win.chk_multifloor)
        main_win.multifloor_up_slider = create_slider_row(tab_coord_vbox, "텔레포트 상승 횟수:", 0, 3, main_win.multifloor_up_count, main_win.update_multifloor_up_count)
        tab_coord_vbox.addStretch()
        main_win.main_tabs.addTab(make_scrollable(tab_coord_widget), "좌표/안전 설정")
        
        # 실험 기능(베타) 탭
        tab_beta_widget = QWidget()
        tab_beta_vbox = QVBoxLayout(tab_beta_widget)
        tab_beta_vbox.addWidget(QLabel("🧪 실험 기능 (베타) - 사냥 경로 녹화 및 CSV 저장", objectName="panelTitle"))
        tab_beta_vbox.addWidget(QLabel("사용자가 직접 캐릭터를 조작하여 사냥하면 캐릭터 좌표와 핵심 조작 상태를 녹화하고,\n종료 시 CSV 파일로 저장한 뒤 주요 정차 구간을 분석하여 순환 슬롯 경로를 자동 생성합니다.", objectName="subLabel"))
        tab_beta_vbox.addSpacing(15)
        
        main_win.btn_record_start = QPushButton("🔴 사냥 경로 녹화 시작")
        main_win.btn_record_start.setFixedHeight(45)
        main_win.btn_record_start.setStyleSheet("background-color: #9e1c1c; color: white; font-size: 15px; font-weight: bold; border-radius: 10px;")
        main_win.btn_record_start.clicked.connect(main_win.waypoint_manager.start_route_recording)
        tab_beta_vbox.addWidget(main_win.btn_record_start)
        
        main_win.btn_record_stop = QPushButton("⏹️ 녹화 종료 및 경로 자동 분석")
        main_win.btn_record_stop.setFixedHeight(45)
        main_win.btn_record_stop.setStyleSheet("background-color: #21262d; color: #8a99af; font-size: 15px; font-weight: bold; border-radius: 10px;")
        main_win.btn_record_stop.setEnabled(False)
        main_win.btn_record_stop.clicked.connect(main_win.waypoint_manager.stop_route_recording)
        tab_beta_vbox.addWidget(main_win.btn_record_stop)
        tab_beta_vbox.addSpacing(15)
        
        main_win.lbl_record_status = QLabel("현재 상태: 녹화 대기 중...")
        main_win.lbl_record_status.setStyleSheet("color: #8a99af; font-size: 14px; font-weight: bold;")
        tab_beta_vbox.addWidget(main_win.lbl_record_status)
        
        main_win.chk_auto_apply_route = QCheckBox("녹화 종료 시 순환사냥 좌표에 즉시 자동 적용")
        main_win.chk_auto_apply_route.setChecked(True)
        tab_beta_vbox.addWidget(main_win.chk_auto_apply_route)
        
        # 인벤토리 자동 판매 설정
        tab_beta_vbox.addSpacing(10)
        sell_group = QGroupBox("인벤토리 판매 설정 (자동/수동 고도화)")
        sell_group.setStyleSheet("QGroupBox { color: #58a6ff; font-size: 13px; font-weight: bold; border: 1px solid #30363d; border-radius: 8px; margin-top: 15px; padding: 15px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }")
        sell_vbox = QVBoxLayout(sell_group)
        
        lbl_sell_style = "color: #8a99af; font-size: 12px; font-weight: bold;"
        sell_input_style = "background-color: #0d1117; color: #00d2ff; border: 1px solid #30363d; border-radius: 5px; font-weight: bold; font-size: 11px; padding: 4px;"
        lbl_delay_style = "color: #8a99af; font-size: 11px; font-weight: bold; margin-left: 10px;"
        
        # 안내 가이드 라벨
        guide_lbl = QLabel("💡 좌표 입력창을 클릭(포커스)한 뒤, 마우스를 원하는 위치에 대고 F1 키를 누르면 자동 등록됩니다.")
        guide_lbl.setStyleSheet("color: #56f09b; font-size: 10px; font-weight: bold; margin-bottom: 8px;")
        guide_lbl.setWordWrap(True)
        sell_vbox.addWidget(guide_lbl)
        
        # 자동 판매 설정행 추가
        auto_sell_layout = QHBoxLayout()
        main_win.chk_auto_sell = QCheckBox("자동 판매 활성화")
        main_win.chk_auto_sell.setStyleSheet("color: #00d2ff; font-weight: bold; font-size: 12px;")
        main_win.chk_auto_sell.stateChanged.connect(main_win.settings_manager.save_settings_silently)
        
        lbl_auto_sell_interval = QLabel("판매 주기:")
        lbl_auto_sell_interval.setStyleSheet(lbl_sell_style)
        main_win.txt_auto_sell_interval = QLineEdit("5")
        main_win.txt_auto_sell_interval.setStyleSheet(sell_input_style)
        main_win.txt_auto_sell_interval.setFixedWidth(40)
        main_win.txt_auto_sell_interval.setValidator(QIntValidator(1, 120))
        main_win.txt_auto_sell_interval.editingFinished.connect(main_win.settings_manager.save_settings_silently)
        lbl_auto_sell_unit = QLabel("분마다")
        lbl_auto_sell_unit.setStyleSheet(lbl_sell_style)
        
        auto_sell_layout.addWidget(main_win.chk_auto_sell)
        auto_sell_layout.addSpacing(15)
        auto_sell_layout.addWidget(lbl_auto_sell_interval)
        auto_sell_layout.addWidget(main_win.txt_auto_sell_interval)
        auto_sell_layout.addWidget(lbl_auto_sell_unit)
        auto_sell_layout.addStretch()
        
        sell_vbox.addLayout(auto_sell_layout)
        sell_vbox.addSpacing(8)
        
        # 5개 좌표 및 딜레이 레이아웃
        pos_grid = QGridLayout()
        pos_grid.setSpacing(6)
        
        # 좌표1
        pos_grid.addWidget(QLabel("좌표1 (상점열기 더블클릭):", objectName="subLabel"), 0, 0)
        main_win.txt_sell_pos1 = QLineEdit("0, 0")
        main_win.txt_sell_pos1.setObjectName("sell_pos1")
        main_win.txt_sell_pos1.setToolTip("좌표1 (상점열기)")
        main_win.txt_sell_pos1.setStyleSheet(sell_input_style)
        main_win.txt_sell_pos1.editingFinished.connect(main_win.settings_manager.save_settings_silently)
        pos_grid.addWidget(main_win.txt_sell_pos1, 0, 1)
        
        lbl_d1 = QLabel("대기(초):")
        lbl_d1.setStyleSheet(lbl_delay_style)
        pos_grid.addWidget(lbl_d1, 0, 2)
        main_win.txt_sell_delay1 = QLineEdit("1.5")
        main_win.txt_sell_delay1.setStyleSheet(sell_input_style)
        main_win.txt_sell_delay1.setFixedWidth(50)
        main_win.txt_sell_delay1.setValidator(QDoubleValidator(0.0, 10.0, 2))
        main_win.txt_sell_delay1.editingFinished.connect(main_win.settings_manager.save_settings_silently)
        pos_grid.addWidget(main_win.txt_sell_delay1, 0, 3)
        
        # 좌표2
        pos_grid.addWidget(QLabel("좌표2 (거래클릭 및 엔터):", objectName="subLabel"), 1, 0)
        main_win.txt_sell_pos2 = QLineEdit("0, 0")
        main_win.txt_sell_pos2.setObjectName("sell_pos2")
        main_win.txt_sell_pos2.setToolTip("좌표2 (거래클릭/엔터)")
        main_win.txt_sell_pos2.setStyleSheet(sell_input_style)
        main_win.txt_sell_pos2.editingFinished.connect(main_win.settings_manager.save_settings_silently)
        pos_grid.addWidget(main_win.txt_sell_pos2, 1, 1)
        
        lbl_d2 = QLabel("대기(초):")
        lbl_d2.setStyleSheet(lbl_delay_style)
        pos_grid.addWidget(lbl_d2, 1, 2)
        main_win.txt_sell_delay2 = QLineEdit("1.0")
        main_win.txt_sell_delay2.setStyleSheet(sell_input_style)
        main_win.txt_sell_delay2.setFixedWidth(50)
        main_win.txt_sell_delay2.setValidator(QDoubleValidator(0.0, 10.0, 2))
        main_win.txt_sell_delay2.editingFinished.connect(main_win.settings_manager.save_settings_silently)
        pos_grid.addWidget(main_win.txt_sell_delay2, 1, 3)
        
        # 좌표3
        pos_grid.addWidget(QLabel("좌표3 (기타창 탭 클릭):", objectName="subLabel"), 2, 0)
        main_win.txt_sell_pos3 = QLineEdit("0, 0")
        main_win.txt_sell_pos3.setObjectName("sell_pos3")
        main_win.txt_sell_pos3.setToolTip("좌표3 (기타창이동)")
        main_win.txt_sell_pos3.setStyleSheet(sell_input_style)
        main_win.txt_sell_pos3.editingFinished.connect(main_win.settings_manager.save_settings_silently)
        pos_grid.addWidget(main_win.txt_sell_pos3, 2, 1)
        
        lbl_d3 = QLabel("대기(초):")
        lbl_d3.setStyleSheet(lbl_delay_style)
        pos_grid.addWidget(lbl_d3, 2, 2)
        main_win.txt_sell_delay3 = QLineEdit("0.5")
        main_win.txt_sell_delay3.setStyleSheet(sell_input_style)
        main_win.txt_sell_delay3.setFixedWidth(50)
        main_win.txt_sell_delay3.setValidator(QDoubleValidator(0.0, 10.0, 2))
        main_win.txt_sell_delay3.editingFinished.connect(main_win.settings_manager.save_settings_silently)
        pos_grid.addWidget(main_win.txt_sell_delay3, 2, 3)
        
        # 좌표4
        pos_grid.addWidget(QLabel("좌표4 (판매슬롯 반복더블):", objectName="subLabel"), 3, 0)
        main_win.txt_sell_pos4 = QLineEdit("0, 0")
        main_win.txt_sell_pos4.setObjectName("sell_pos4")
        main_win.txt_sell_pos4.setToolTip("좌표4 (판매슬롯반복)")
        main_win.txt_sell_pos4.setStyleSheet(sell_input_style)
        main_win.txt_sell_pos4.editingFinished.connect(main_win.settings_manager.save_settings_silently)
        pos_grid.addWidget(main_win.txt_sell_pos4, 3, 1)
        
        lbl_d4 = QLabel("확인대기(초):")
        lbl_d4.setStyleSheet(lbl_delay_style)
        pos_grid.addWidget(lbl_d4, 3, 2)
        main_win.txt_sell_delay4 = QLineEdit("0.12")
        main_win.txt_sell_delay4.setStyleSheet(sell_input_style)
        main_win.txt_sell_delay4.setFixedWidth(50)
        main_win.txt_sell_delay4.setValidator(QDoubleValidator(0.0, 10.0, 2))
        main_win.txt_sell_delay4.editingFinished.connect(main_win.settings_manager.save_settings_silently)
        pos_grid.addWidget(main_win.txt_sell_delay4, 3, 3)
        
        # 좌표5
        pos_grid.addWidget(QLabel("좌표5 (상점나가기 클릭):", objectName="subLabel"), 4, 0)
        main_win.txt_sell_pos5 = QLineEdit("0, 0")
        main_win.txt_sell_pos5.setObjectName("sell_pos5")
        main_win.txt_sell_pos5.setToolTip("좌표5 (상점나가기)")
        main_win.txt_sell_pos5.setStyleSheet(sell_input_style)
        main_win.txt_sell_pos5.editingFinished.connect(main_win.settings_manager.save_settings_silently)
        pos_grid.addWidget(main_win.txt_sell_pos5, 4, 1)
        
        lbl_d5 = QLabel("대기(초):")
        lbl_d5.setStyleSheet(lbl_delay_style)
        pos_grid.addWidget(lbl_d5, 4, 2)
        main_win.txt_sell_delay5 = QLineEdit("0.5")
        main_win.txt_sell_delay5.setStyleSheet(sell_input_style)
        main_win.txt_sell_delay5.setFixedWidth(50)
        main_win.txt_sell_delay5.setValidator(QDoubleValidator(0.0, 10.0, 2))
        main_win.txt_sell_delay5.editingFinished.connect(main_win.settings_manager.save_settings_silently)
        pos_grid.addWidget(main_win.txt_sell_delay5, 4, 3)
        
        sell_vbox.addLayout(pos_grid)
        sell_vbox.addSpacing(10)
        
        # 추가 옵션 레이아웃
        opt_row = QHBoxLayout()
        lbl_sell_rows = QLabel("판매 행 개수:")
        lbl_sell_rows.setStyleSheet(lbl_sell_style)
        main_win.txt_sell_rows = QLineEdit("8")
        main_win.txt_sell_rows.setStyleSheet(sell_input_style)
        main_win.txt_sell_rows.setFixedWidth(40)
        main_win.txt_sell_rows.setValidator(QIntValidator(1, 20))
        main_win.txt_sell_rows.editingFinished.connect(main_win.settings_manager.save_settings_silently)
        
        lbl_sell_start_row = QLabel("판매 시작 행:")
        lbl_sell_start_row.setStyleSheet(lbl_sell_style)
        main_win.txt_sell_start_row = QLineEdit("2")
        main_win.txt_sell_start_row.setStyleSheet(sell_input_style)
        main_win.txt_sell_start_row.setFixedWidth(40)
        main_win.txt_sell_start_row.setValidator(QIntValidator(1, 20))
        main_win.txt_sell_start_row.editingFinished.connect(main_win.settings_manager.save_settings_silently)
        
        lbl_sell_delay = QLabel("판매 딜레이(초):")
        lbl_sell_delay.setStyleSheet(lbl_sell_style)
        main_win.txt_sell_delay = QLineEdit("0.05")
        main_win.txt_sell_delay.setStyleSheet(sell_input_style)
        main_win.txt_sell_delay.setFixedWidth(40)
        main_win.txt_sell_delay.setValidator(QDoubleValidator(0.01, 2.0, 2))
        main_win.txt_sell_delay.editingFinished.connect(main_win.settings_manager.save_settings_silently)
        
        opt_row.addWidget(lbl_sell_rows)
        opt_row.addWidget(main_win.txt_sell_rows)
        opt_row.addSpacing(10)
        opt_row.addWidget(lbl_sell_start_row)
        opt_row.addWidget(main_win.txt_sell_start_row)
        opt_row.addSpacing(10)
        opt_row.addWidget(lbl_sell_delay)
        opt_row.addWidget(main_win.txt_sell_delay)
        sell_vbox.addLayout(opt_row)
        
        tab_beta_vbox.addWidget(sell_group)
        tab_beta_vbox.addStretch()
        main_win.main_tabs.addTab(make_scrollable(tab_beta_widget), "실험 기능(베타)")
        
        content_layout.addWidget(center_frame)
        
        # 시스템 매트릭스 / 로그 프레임
        right_frame = QFrame(objectName="panelFrame")
        right_frame.setFixedWidth(330)
        right_vbox = QVBoxLayout(right_frame)
        right_vbox.setContentsMargins(20, 30, 20, 20)
        right_vbox.addWidget(QLabel("시스템 상태 지표", objectName="panelTitle"))
        
        main_win.cpu_label = QLabel("CPU 사용률(0%)", objectName="subLabel")
        right_vbox.addWidget(main_win.cpu_label)
        main_win.cpu_bar = QProgressBar(objectName="metricBar")
        main_win.cpu_bar.setFixedHeight(12)
        main_win.cpu_bar.setTextVisible(False)
        right_vbox.addWidget(main_win.cpu_bar)
        right_vbox.addSpacing(10)
        
        main_win.ram_label = QLabel("RAM 점유율(0%)", objectName="subLabel")
        right_vbox.addWidget(main_win.ram_label)
        main_win.ram_bar = QProgressBar(objectName="metricBar")
        main_win.ram_bar.setFixedHeight(12)
        main_win.ram_bar.setTextVisible(False)
        right_vbox.addWidget(main_win.ram_bar)
        right_vbox.addSpacing(25)
        
        main_win.data_runtime = create_data_row(right_vbox, "가동 시간", "00:00:00")
        main_win.data_total_time = create_data_row(right_vbox, "누적 사냥", "00:00:00")
        main_win.data_recovery_left = create_data_row(right_vbox, "회수 남은시간", "비활성")
        main_win.data_recovery_left.setStyleSheet("color: #56f09b; font-weight: bold;")
        main_win.data_pet_left = create_data_row(right_vbox, "펫먹이 남은시간", "비활성")
        main_win.data_pet_left.setStyleSheet("color: #56f09b; font-weight: bold;")
        main_win.data_errors = create_data_row(right_vbox, "탐지 기록", "0회")
        main_win.data_char_pos = create_data_row(right_vbox, "캐릭터 좌표", "인식 불가")
        right_vbox.addSpacing(25)
        
        right_vbox.addWidget(QLabel("시스템 로그", objectName="panelTitle"))
        main_win.log_text = QTextEdit()
        main_win.log_text.setObjectName("logTerminal")
        main_win.log_text.setReadOnly(True)
        right_vbox.addWidget(main_win.log_text)
        content_layout.addWidget(right_frame)
        main_layout.addLayout(content_layout)
        
        # 하단 푸터 버튼들
        footer = QHBoxLayout()
        footer.setSpacing(15)
        
        main_win.start_btn = QPushButton("사냥 시작 [F5]", objectName="startBtn")
        main_win.start_btn.setFixedHeight(85)
        main_win.start_btn.clicked.connect(main_win.start_hunting)
        footer.addWidget(main_win.start_btn, 2)
        
        main_win.stop_btn = QPushButton("사냥 중지 [F6]", objectName="stopBtn")
        main_win.stop_btn.setFixedHeight(85)
        main_win.stop_btn.clicked.connect(main_win.stop_hunting)
        main_win.stop_btn.setEnabled(False)
        footer.addWidget(main_win.stop_btn, 2)
        
        main_win.manual_sell_btn = QPushButton("인벤 판매 [버튼]", objectName="sellBtn")
        main_win.manual_sell_btn.setFixedHeight(85)
        main_win.manual_sell_btn.clicked.connect(main_win.run_manual_sell)
        footer.addWidget(main_win.manual_sell_btn, 1)
        
        main_win.stop_all_btn = QPushButton("종료")
        main_win.stop_all_btn.setObjectName("stopBtn")
        main_win.stop_all_btn.setFixedHeight(85)
        main_win.stop_all_btn.clicked.connect(main_win.close)
        footer.addWidget(main_win.stop_all_btn, 1)
        main_layout.addLayout(footer)

    @staticmethod
    def apply_qss(main_win):
        style = (
            "QMainWindow { background-color: #0b0e14; } "
            "#mainTitle { color: #ffffff; font-size: 42px; font-weight: 900; } "
            "#panelTitle { color: #00d2ff; font-size: 16px; font-weight: 800; } "
            "#subLabel { color: #8a99af; font-size: 13px; } "
            "#dataLabel { color: #64748b; font-size: 15px; } "
            "#dataValue { color: #ffffff; font-size: 18px; font-weight: 700; } "
            "#panelFrame { background-color: #161b22; border: 1px solid #30363d; border-radius: 25px; } "
            "QTabWidget::pane { border: 1px solid #30363d; background: #161b22; border-radius: 15px; } "
            "QTabBar::tab { background: #0d1117; color: #8b949e; padding: 12px 10px; min-width: 110px; } "
            "QTabBar::tab:selected { background: #161b22; color: #00d2ff; border-bottom: 3px solid #00d2ff; } "
            "QPushButton { background-color: #21262d; color: #c9d1d9; border-radius: 15px; font-weight: 700; } "
            "#startBtn { background-color: #238636; color: #ffffff; font-size: 28px; } "
            "#stopBtn { border: 2px solid #f85149; color: #f85149; font-size: 24px; } "
            "#logTerminal { background-color: #0d1117; color: #8b949e; border-radius: 15px; padding: 10px; } "
            "QLabel#previewLabel { background-color: #000000; border-radius: 20px; border: 2px solid #30363d; } "
            "QGroupBox { color: #00d2ff; font-weight: bold; border: 1px solid #30363d; border-radius: 12px; margin-top: 10px; padding-top: 15px; font-size: 14px; } "
            "QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; left: 10px; }"
        )
        main_win.setStyleSheet(style)

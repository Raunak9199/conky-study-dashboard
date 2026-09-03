#!/usr/bin/env python3
import sys
import datetime as dt
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QLabel, QPushButton, QHBoxLayout, QFrame, QSizePolicy,
                             QScrollArea, QGridLayout, QStackedWidget, QLineEdit, QComboBox)
from PyQt5.QtGui import QFont, QColor, QPalette, QBrush, QPixmap
from PyQt5.QtCore import QTimer, Qt, QPropertyAnimation, QEasingCurve

import study_schedule as ss
import schedule_manager

class DashboardApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("30-Day Study Dashboard")
        self.resize(1000, 700)
        
        # Enable translucent capability
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.is_glass_mode = False
        
        # Floating above all (Always on Top)
        self.is_always_on_top = True
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: transparent;
            }
            #MainCentralWidget {
                border: 4px solid #9C27B0;
                border-radius: 8px;
                background-color: #F8F9FA;
            }
        """)
        
        self.central_widget = QFrame()
        self.central_widget.setObjectName("MainCentralWidget")
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.setup_sidebar()
        self.setup_right_pane()
        
        # Update timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(1000)
        
        self.update_ui()
        self.switch_view(0)
        
    def setup_sidebar(self):
        self.sidebar_container = QFrame()
        self.sidebar_container.setMaximumWidth(220)
        self.sidebar_container.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-right: 1px solid #E0E0E0;
            }
        """)
        self.sidebar_layout = QVBoxLayout(self.sidebar_container)
        self.sidebar_layout.setContentsMargins(20, 20, 20, 30)
        self.sidebar_layout.setSpacing(15)
        
        # Title
        lbl_focus = QLabel("Focus Mode")
        lbl_focus.setStyleSheet("border:none; color: #004D40; font-weight: bold; font-size: 16px;")
        
        lbl_deep = QLabel("Deep Work Session")
        lbl_deep.setStyleSheet("border:none; color: #757575; font-size: 12px;")
        
        self.sidebar_layout.addWidget(lbl_focus)
        self.sidebar_layout.addWidget(lbl_deep)
        self.sidebar_layout.addSpacing(20)
        
        # Nav Buttons
        nav_style = """
            QPushButton {
                text-align: left; padding: 10px; border: none; background: transparent;
                font-size: 13px; color: #424242; border-radius: 5px;
            }
            QPushButton:hover { background-color: #F5F5F5; color: #004D40; }
        """
        self.nav_default_style = nav_style
        
        self.btn_dash = QPushButton("🪟 Dashboard")
        self.btn_sch = QPushButton("📅 Schedule")
        self.btn_prog = QPushButton("📈 Progress")
        self.btn_sync = QPushButton("📱 Mobile Sync")
        self.btn_sync.setStyleSheet(nav_style)
        
        self.nav_buttons = [self.btn_dash, self.btn_sch, self.btn_prog]
        
        self.sidebar_layout.addWidget(self.btn_dash)
        self.sidebar_layout.addWidget(self.btn_sch)
        self.sidebar_layout.addWidget(self.btn_prog)
        self.sidebar_layout.addWidget(self.btn_sync)
        
        self.btn_dash.clicked.connect(lambda: self.switch_view(0))
        self.btn_sch.clicked.connect(lambda: self.switch_view(1))
        self.btn_prog.clicked.connect(lambda: self.switch_view(2))
        self.btn_sync.clicked.connect(self.show_sync_qr)
        
        self.sidebar_layout.addStretch()
        
        # Start Session ("Mark Online") Button
        self.btn_start = QPushButton("🟢 Start Session")
        self.btn_start.setFixedSize(160, 40)
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: #004D40; color: white; border-radius: 8px; font-weight: bold; font-size: 13px; border: none;
            }
            QPushButton:hover { background-color: #00695C; }
        """)
        self.btn_start.clicked.connect(self.toggle_study_session)
        self.sidebar_layout.addWidget(self.btn_start, alignment=Qt.AlignCenter)
        
        self.main_layout.addWidget(self.sidebar_container)
        
    def setup_right_pane(self):
        self.right_pane = QWidget()
        self.right_pane.setStyleSheet("background-color: #F8F9FA;")
        
        self.right_layout = QVBoxLayout(self.right_pane)
        self.right_layout.setContentsMargins(30, 20, 30, 20)
        
        # Hamburger Toggle & Top Header
        top_hbox = QHBoxLayout()
        self.btn_toggle = QPushButton("≡")
        self.btn_toggle.setFixedSize(40, 40)
        self.btn_toggle.setStyleSheet("QPushButton { font-size: 24px; font-weight: bold; border: none; background: transparent; color: #424242; } QPushButton:hover { color: #004D40; }")
        self.btn_toggle.clicked.connect(self.toggle_sidebar)
        
        self.lbl_hud = QLabel("MY STUDY HUD")
        self.lbl_hud.setStyleSheet("color: #004D40; font-weight: bold; font-size: 24px;")
        
        self.lbl_day_top = QLabel("Day 1")
        self.lbl_day_top.setStyleSheet("color: #424242; font-weight: bold; font-size: 13px;")
        self.lbl_day_top.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.btn_pin = QPushButton("📌 Pinned")
        self.btn_pin.setFixedSize(85, 30)
        self.btn_pin.setStyleSheet("""
            QPushButton {
                font-size: 11px; font-weight: bold; border-radius: 15px;
                background: #E0F2F1; color: #004D40; border: 1px solid #00897B;
            }
            QPushButton:hover { background: #B2DFDB; }
        """)
        self.btn_pin.clicked.connect(self.toggle_pin)
        
        self.btn_glass = QPushButton("⚪ Glass Mode")
        self.btn_glass.setFixedSize(100, 30)
        self.btn_glass.setStyleSheet("QPushButton { font-size: 12px; font-weight: bold; border-radius: 15px; background: #E0E0E0; color: #424242; border: none; } QPushButton:hover { background: #D6D6D6; }")
        self.btn_glass.clicked.connect(self.toggle_glass)
        
        top_hbox.addWidget(self.btn_toggle)
        top_hbox.addWidget(self.lbl_hud)
        top_hbox.addStretch()
        top_hbox.addWidget(self.btn_pin)
        top_hbox.addSpacing(10)
        top_hbox.addWidget(self.btn_glass)
        top_hbox.addSpacing(15)
        top_hbox.addWidget(self.lbl_day_top)
        
        # A thin horizontal line
        h_line = QFrame()
        h_line.setFrameShape(QFrame.HLine)
        h_line.setStyleSheet("color: #E0E0E0;")
        
        self.right_layout.addLayout(top_hbox)
        self.right_layout.addWidget(h_line)
        self.right_layout.addSpacing(15)
        
        # Day and Date
        self.lbl_day_big = QLabel("DAY 1")
        self.lbl_day_big.setStyleSheet("color: #E53935; font-weight: bold; font-size: 32px;")
        self.lbl_date = QLabel("Tuesday, 01 Sep 2026")
        self.lbl_date.setStyleSheet("color: #616161; font-size: 12px;")
        
        self.right_layout.addWidget(self.lbl_day_big)
        self.right_layout.addWidget(self.lbl_date)
        self.right_layout.addSpacing(15)

        # QStackedWidget for Views
        self.stacked_widget = QStackedWidget()
        self.right_layout.addWidget(self.stacked_widget)
        
        # --- VIEW 0: Dashboard ---
        self.dashboard_view = QWidget()
        dash_vbox = QVBoxLayout(self.dashboard_view)
        dash_vbox.setContentsMargins(0,0,0,0)

        # Content Split Layout (TODAY list vs NOW card)
        content_hbox = QHBoxLayout()
        
        # Left side: TODAY
        today_vbox = QVBoxLayout()
        lbl_today = QLabel("TODAY")
        lbl_today.setStyleSheet("color: #00897B; font-weight: bold; font-size: 16px;")
        today_vbox.addWidget(lbl_today)
        today_vbox.addSpacing(10)
        
        self.topics_layout = QVBoxLayout()
        self.topics_layout.setSpacing(10)
        today_vbox.addLayout(self.topics_layout)
        today_vbox.addStretch()
        
        # Right side: NOW card
        self.now_card = QFrame()
        self.now_card.setFixedWidth(300)
        self.now_card.setStyleSheet("""
            QFrame#NowCard {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
        """)
        self.now_card.setObjectName("NowCard")
        
        now_vbox = QVBoxLayout(self.now_card)
        now_vbox.setContentsMargins(20, 20, 20, 20)
        
        lbl_now_header = QLabel("▶ NOW")
        lbl_now_header.setStyleSheet("color: #E53935; font-weight: bold; font-size: 14px; border: none;")
        
        self.lbl_now_title = QLabel("Bank — English + Computer/GA")
        self.lbl_now_title.setWordWrap(True)
        self.lbl_now_title.setStyleSheet("color: #212121; font-weight: bold; font-size: 16px; border: none;")
        
        now_card_hline = QFrame()
        now_card_hline.setFrameShape(QFrame.HLine)
        now_card_hline.setStyleSheet("color: #F5F5F5; border: none;")
        
        self.lbl_now_time_rem = QLabel("01h 08m remaining")
        self.lbl_now_time_rem.setStyleSheet("border: none; font-size: 12px; color: #616161;")
        
        self.lbl_now_bounds = QLabel("🕒 15:45 - 17:45")
        self.lbl_now_bounds.setStyleSheet("border: none; font-size: 11px; color: #757575;")
        
        now_vbox.addWidget(lbl_now_header)
        now_vbox.addSpacing(10)
        now_vbox.addWidget(self.lbl_now_title)
        now_vbox.addSpacing(10)
        now_vbox.addWidget(now_card_hline)
        now_vbox.addSpacing(10)
        now_vbox.addWidget(self.lbl_now_time_rem)
        now_vbox.addWidget(self.lbl_now_bounds)
        now_vbox.addSpacing(15)
        
        # Pause Controls in NOW Card
        pause_hbox = QHBoxLayout()
        self.btn_pause = QPushButton("Pause")
        self.btn_pause.setFixedSize(100, 35)
        self.btn_pause.setStyleSheet("""
            QPushButton {
                background-color: #E53935; color: white; border-radius: 4px; font-weight: bold; border: none;
            }
            QPushButton:hover { background-color: #D32F2F; }
        """)
        self.btn_pause.clicked.connect(self.toggle_pause)
        
        self.lbl_shift = QLabel("Shift today: +0s")
        self.lbl_shift.setStyleSheet("border: none; font-size: 11px; color: #757575;")
        
        pause_hbox.addWidget(self.btn_pause)
        pause_hbox.addWidget(self.lbl_shift)
        pause_hbox.addStretch()
        
        now_vbox.addLayout(pause_hbox)
        
        now_vbox.addSpacing(10)
        sess_divider = QFrame()
        sess_divider.setFrameShape(QFrame.HLine)
        sess_divider.setStyleSheet("color: #F5F5F5; border: none;")
        now_vbox.addWidget(sess_divider)
        now_vbox.addSpacing(6)
        
        sess_header = QLabel("SESSION TRACKER")
        sess_header.setStyleSheet("color: #757575; font-weight: bold; font-size: 10px; border: none;")
        now_vbox.addWidget(sess_header)
        
        self.lbl_now_session_status = QLabel("⚪ OFFLINE")
        self.lbl_now_session_status.setStyleSheet("font-size: 12px; font-weight: bold; color: #757575; border: none;")
        now_vbox.addWidget(self.lbl_now_session_status)
        now_vbox.addSpacing(4)
        
        self.btn_now_session = QPushButton("🟢 Mark Online (Start)")
        self.btn_now_session.setFixedHeight(32)
        self.btn_now_session.setStyleSheet("""
            QPushButton {
                background-color: #004D40; color: white; border-radius: 4px; font-weight: bold; border: none; font-size: 11px;
            }
            QPushButton:hover { background-color: #00695C; }
        """)
        self.btn_now_session.clicked.connect(self.toggle_study_session)
        now_vbox.addWidget(self.btn_now_session)
        
        content_hbox.addLayout(today_vbox, stretch=2)
        content_hbox.addSpacing(30)
        content_hbox.addWidget(self.now_card, alignment=Qt.AlignTop)
        
        dash_vbox.addLayout(content_hbox)
        dash_vbox.addStretch()
        
        self.stacked_widget.addWidget(self.dashboard_view)
        
        # --- VIEW 1: Schedule Editor ---
        self.schedule_editor_view = QWidget()
        self.setup_schedule_editor()
        self.stacked_widget.addWidget(self.schedule_editor_view)
        
        # --- VIEW 2: Progress & Analytics ---
        self.progress_view = QWidget()
        self.setup_progress_view()
        self.stacked_widget.addWidget(self.progress_view)
        
        self.lbl_time = QLabel("TIME 16:36:18")
        self.lbl_time.setStyleSheet("color: #757575; font-weight: bold; font-size: 11px;")
        self.lbl_time.setAlignment(Qt.AlignRight)
        self.right_layout.addWidget(self.lbl_time)
        
        self.main_layout.addWidget(self.right_pane)

    def setup_schedule_editor(self):
        from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox, QGroupBox
        
        self.editor_layout = QVBoxLayout(self.schedule_editor_view)
        
        lbl_title = QLabel("Schedule Editor")
        lbl_title.setStyleSheet("color: #004D40; font-weight: bold; font-size: 20px;")
        self.editor_layout.addWidget(lbl_title)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setObjectName("ScrollContent")
        scroll_content.setStyleSheet("#ScrollContent { background: transparent; }")
        self.scroll_layout = QVBoxLayout(scroll_content)
        
        # PROFILES GROUP
        self.profiles_group = QGroupBox("Schedule Profile")
        self.profiles_group.setStyleSheet("QGroupBox { font-weight: bold; color: #424242; }")
        profiles_vbox = QVBoxLayout(self.profiles_group)
        
        prof_hbox1 = QHBoxLayout()
        prof_hbox1.addWidget(QLabel("Select Profile:"))
        self.profile_combo = QComboBox()
        self.profile_combo.setStyleSheet("QComboBox { background-color: white; color: black; border: 1px solid #BDBDBD; padding: 2px; }")
        self.profile_combo.currentIndexChanged.connect(self.on_profile_selected)
        prof_hbox1.addWidget(self.profile_combo)
        
        self.lbl_active_prof = QLabel("")
        self.lbl_active_prof.setStyleSheet("color: #43A047; font-weight: bold;")
        prof_hbox1.addWidget(self.lbl_active_prof)
        prof_hbox1.addStretch()
        
        prof_hbox2 = QHBoxLayout()
        btn_new_prof = QPushButton("+ New Profile")
        btn_new_prof.clicked.connect(self.ui_new_profile)
        btn_del_prof = QPushButton("Delete Profile")
        btn_del_prof.setStyleSheet("color: red;")
        btn_del_prof.clicked.connect(self.ui_delete_profile)
        self.btn_make_active = QPushButton("Make ACTIVE")
        self.btn_make_active.setStyleSheet("background-color: #43A047; color: white; font-weight: bold;")
        self.btn_make_active.clicked.connect(self.ui_make_active)
        
        prof_hbox2.addWidget(btn_new_prof)
        prof_hbox2.addWidget(btn_del_prof)
        prof_hbox2.addStretch()
        prof_hbox2.addWidget(self.btn_make_active)
        
        profiles_vbox.addLayout(prof_hbox1)
        profiles_vbox.addLayout(prof_hbox2)
        self.scroll_layout.addWidget(self.profiles_group)
        
        # SLOTS GROUP
        self.slots_group = QGroupBox("Time Slots (Applies to all days)")
        self.slots_group.setStyleSheet("QGroupBox { font-weight: bold; color: #424242; }")
        self.slots_layout = QVBoxLayout()
        self.slots_group.setLayout(self.slots_layout)
        
        btn_add_slot = QPushButton("+ Add Time Slot")
        btn_add_slot.setStyleSheet("QPushButton { background-color: #E0E0E0; color: #424242; padding: 5px; border-radius: 3px; border: 1px solid #BDBDBD; } QPushButton:hover { background-color: #D6D6D6; }")
        btn_add_slot.clicked.connect(lambda: self.ui_add_slot())
        self.slots_layout.addWidget(btn_add_slot)
        
        # DAYS GROUP
        self.days_group = QGroupBox("Daily Topics")
        self.days_group.setStyleSheet("QGroupBox { font-weight: bold; color: #424242; }")
        self.days_layout = QVBoxLayout()
        self.days_group.setLayout(self.days_layout)
        
        mode_hbox = QHBoxLayout()
        mode_hbox.addWidget(QLabel("Schedule Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.setStyleSheet("QComboBox { background-color: white; color: black; border: 1px solid #BDBDBD; padding: 2px; }")
        self.mode_combo.addItems(["Daily (Same for all days)", "Weekly (7-day cycle)", "Monthly (31-day cycle)"])
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        mode_hbox.addWidget(self.mode_combo)
        
        self.day_lbl = QLabel("Select Day:")
        self.day_lbl.hide()
        mode_hbox.addWidget(self.day_lbl)
        
        self.day_combo = QComboBox()
        self.day_combo.setStyleSheet("QComboBox { background-color: white; color: black; border: 1px solid #BDBDBD; padding: 2px; }")
        self.day_combo.currentIndexChanged.connect(self.ui_load_day_topics)
        self.day_combo.hide()
        mode_hbox.addWidget(self.day_combo)
        
        mode_hbox.addStretch()
        self.days_layout.addLayout(mode_hbox)
        
        self.topics_container = QVBoxLayout()
        self.days_layout.addLayout(self.topics_container)
        
        btn_add_topic = QPushButton("+ Add Topic to Day")
        btn_add_topic.setStyleSheet("QPushButton { background-color: #E0E0E0; color: #424242; padding: 5px; border-radius: 3px; border: 1px solid #BDBDBD; } QPushButton:hover { background-color: #D6D6D6; }")
        btn_add_topic.clicked.connect(lambda: self.ui_add_topic())
        self.days_layout.addWidget(btn_add_topic)
        
        self.scroll_layout.addWidget(self.slots_group)
        self.scroll_layout.addWidget(self.days_group)
        
        # JSON GROUP
        self.json_group = QGroupBox("Advanced: JSON Import/Export")
        self.json_group.setStyleSheet("QGroupBox { font-weight: bold; color: #424242; margin-top: 10px; }")
        self.json_layout = QVBoxLayout()
        self.json_group.setLayout(self.json_layout)
        
        json_desc = QLabel("Download a template, modify it in any text editor, and upload it back to bulk-add your timetable.")
        json_desc.setStyleSheet("color: #757575; font-weight: normal; font-size: 11px;")
        json_desc.setWordWrap(True)
        self.json_layout.addWidget(json_desc)
        
        json_controls = QHBoxLayout()
        self.template_combo = QComboBox()
        self.template_combo.addItems(["Daily (Same for all days)", "Weekly (7-day cycle)", "Monthly (30-day cycle)"])
        self.template_combo.setStyleSheet("QComboBox { background-color: white; color: black; border: 1px solid #BDBDBD; padding: 4px; }")
        
        btn_export = QPushButton("⬇️ Export Template")
        btn_export.setStyleSheet("QPushButton { background-color: #E0E0E0; color: #424242; padding: 5px 10px; border-radius: 3px; border: 1px solid #BDBDBD; } QPushButton:hover { background-color: #D6D6D6; }")
        btn_export.clicked.connect(self.export_json_template)
        
        btn_import = QPushButton("⬆️ Import JSON")
        btn_import.setStyleSheet("QPushButton { background-color: #00897B; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold; } QPushButton:hover { background-color: #00695C; }")
        btn_import.clicked.connect(self.import_json_template)
        
        json_controls.addWidget(self.template_combo)
        json_controls.addWidget(btn_export)
        json_controls.addWidget(btn_import)
        
        self.json_layout.addLayout(json_controls)
        self.scroll_layout.addWidget(self.json_group)
        
        self.scroll_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        self.editor_layout.addWidget(scroll)
        
        # Bottom controls
        bottom_hbox = QHBoxLayout()
        btn_save = QPushButton("Save Schedule")
        btn_save.setStyleSheet("background-color: #004D40; color: white; padding: 10px; border-radius: 5px; font-weight: bold;")
        btn_save.clicked.connect(self.save_schedule_from_ui)
        bottom_hbox.addStretch()
        bottom_hbox.addWidget(btn_save)
        
        self.editor_layout.addLayout(bottom_hbox)
        
        self.load_editor_data()

    def ui_add_slot(self, start="00:00", end="01:00", name="New Subject"):
        # If called by a signal without lambda, PyQt5 passes 'False' as start. Guard against it.
        if isinstance(start, bool):
            start = "00:00"
        
        from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QPushButton
        hbox = QHBoxLayout()
        start_edit = QLineEdit(str(start))
        start_edit.setPlaceholderText("Start (HH:MM)")
        start_edit.setFixedWidth(80)
        end_edit = QLineEdit(end)
        end_edit.setPlaceholderText("End (HH:MM)")
        end_edit.setFixedWidth(80)
        name_edit = QLineEdit(name)
        name_edit.setPlaceholderText("Subject Name")
        name_edit._original_name = name
        
        def on_name_changed(new_text):
            old_name = name_edit._original_name
            # Update memory
            for day, topics in self.edit_days.items():
                for i in range(len(topics)):
                    if topics[i][0] == old_name:
                        topics[i] = (new_text, topics[i][1])
            # Update UI
            for i in range(self.topics_container.count()):
                t_hbox = self.topics_container.itemAt(i)
                if t_hbox:
                    combo = t_hbox.itemAt(0).widget()
                    if combo.currentText() == old_name:
                        if combo.findText(new_text) == -1:
                            combo.addItem(new_text)
                        combo.setCurrentText(new_text)
            name_edit._original_name = new_text
            self.update_topic_comboboxes()
            
        name_edit.textChanged.connect(on_name_changed)
        
        btn_del = QPushButton("X")
        btn_del.setFixedWidth(30)
        btn_del.setStyleSheet("color: red; font-weight: bold;")
        btn_del.clicked.connect(lambda: self.delete_slot_row(hbox))
        
        hbox.addWidget(start_edit)
        hbox.addWidget(end_edit)
        hbox.addWidget(name_edit)
        hbox.addWidget(btn_del)
        
        # Insert before the "Add" button (which is at the end)
        self.slots_layout.insertLayout(self.slots_layout.count() - 1, hbox)
        # We don't call update_topic_comboboxes here directly if it's initial load, but it's safe to call.
        # Actually it's fine.
        QTimer.singleShot(10, self.update_topic_comboboxes)
        
    def delete_slot_row(self, layout):
        self.delete_layout_row(layout, self.slots_layout)
        self.update_topic_comboboxes()

    def update_topic_comboboxes(self):
        slot_names = []
        for i in range(self.slots_layout.count() - 1):
            s_hbox = self.slots_layout.itemAt(i)
            if s_hbox:
                name_widget = s_hbox.itemAt(2).widget()
                if name_widget:
                    slot_names.append(name_widget.text())
                    
        for i in range(self.topics_container.count()):
            t_hbox = self.topics_container.itemAt(i)
            if t_hbox:
                combo = t_hbox.itemAt(0).widget()
                current = combo.currentText()
                combo.blockSignals(True)
                combo.clear()
                combo.addItems(slot_names)
                if current in slot_names:
                    combo.setCurrentText(current)
                elif current:
                    combo.addItem(current)
                    combo.setCurrentText(current)
                combo.blockSignals(False)

    def ui_add_topic(self, cat="Category", desc="Description"):
        # Guard against PyQt5 passing a boolean 'False' from the clicked signal
        if isinstance(cat, bool):
            cat = "Category"
            
        from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QComboBox
        hbox = QHBoxLayout()
        
        # Harvest current slot names for binding
        slot_names = []
        for i in range(self.slots_layout.count() - 1):
            s_hbox = self.slots_layout.itemAt(i)
            if s_hbox:
                name_widget = s_hbox.itemAt(2).widget()
                if name_widget:
                    slot_names.append(name_widget.text())
                    
        cat_edit = QComboBox()
        cat_edit.setEditable(False)
        cat_edit.setStyleSheet("QComboBox { background-color: white; color: black; border: 1px solid #BDBDBD; padding: 2px; }")
        
        if slot_names:
            cat_edit.addItems(slot_names)
        if str(cat) and str(cat) not in slot_names:
            cat_edit.addItem(str(cat))
        
        cat_edit.setCurrentText(str(cat))
        cat_edit.setFixedWidth(120)
        
        desc_edit = QLineEdit(desc)
        desc_edit.setPlaceholderText("Topic description")
        
        btn_del = QPushButton("X")
        btn_del.setFixedWidth(30)
        btn_del.setStyleSheet("color: red; font-weight: bold;")
        btn_del.clicked.connect(lambda: self.delete_layout_row(hbox, self.topics_container))
        
        hbox.addWidget(cat_edit)
        hbox.addWidget(desc_edit)
        hbox.addWidget(btn_del)
        self.topics_container.addLayout(hbox)
        
    def delete_layout_row(self, layout_to_delete, parent_layout):
        while layout_to_delete.count():
            item = layout_to_delete.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self.delete_layout_row(item.layout(), layout_to_delete)
        parent_layout.removeItem(layout_to_delete)

    def load_editor_data(self):
        import schedule_manager
        self.profiles_data = schedule_manager.load_profiles()
        self.active_profile_name = self.profiles_data.get("active_profile", "Default Plan")
        
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        self.profile_combo.addItems(list(self.profiles_data.get("profiles", {}).keys()))
        
        idx = self.profile_combo.findText(self.active_profile_name)
        if idx >= 0:
            self.profile_combo.setCurrentIndex(idx)
        self.profile_combo.blockSignals(False)
        
        self.load_profile_into_editor(self.active_profile_name)

    def load_profile_into_editor(self, prof_name):
        pdata = self.profiles_data.get("profiles", {}).get(prof_name)
        if not pdata:
            return
            
        self.edit_slots = pdata.get("slots", [])
        self.edit_days = {k: list(v) for k, v in pdata.get("days", {}).items()}
        mode = pdata.get("mode", 0)
        
        # Clear existing slots in UI
        while self.slots_layout.count() > 1: # keep the add button
            item = self.slots_layout.takeAt(0)
            self.delete_layout_row(item, self.slots_layout)
            
        for s in self.edit_slots:
            self.ui_add_slot(s[0], s[1], s[2])
            
        if hasattr(self, '_current_edit_day'):
            del self._current_edit_day
            
        self.mode_combo.setCurrentIndex(mode)
        self.ui_load_day_topics()
        
        if prof_name == self.active_profile_name:
            self.lbl_active_prof.setText("(ACTIVE)")
            self.btn_make_active.hide()
        else:
            self.lbl_active_prof.setText("")
            self.btn_make_active.show()

    def on_profile_selected(self):
        prof_name = self.profile_combo.currentText()
        if prof_name:
            self.load_profile_into_editor(prof_name)

    def ui_new_profile(self):
        from PyQt5.QtWidgets import QInputDialog, QMessageBox
        name, ok = QInputDialog.getText(self, "New Profile", "Enter profile name:")
        if ok and name.strip():
            name = name.strip()
            if name in self.profiles_data.get("profiles", {}):
                QMessageBox.warning(self, "Error", "Profile name already exists.")
                return
            
            # Start fresh
            self.profiles_data["profiles"][name] = {
                "mode": 0,
                "slots": [],
                "days": {"1": []}
            }
            import schedule_manager
            schedule_manager.save_profiles(self.profiles_data)
            
            self.profile_combo.blockSignals(True)
            self.profile_combo.addItem(name)
            self.profile_combo.setCurrentText(name)
            self.profile_combo.blockSignals(False)
            self.load_profile_into_editor(name)

    def ui_delete_profile(self):
        from PyQt5.QtWidgets import QMessageBox
        prof_name = self.profile_combo.currentText()
        if prof_name == self.active_profile_name:
            QMessageBox.warning(self, "Error", "Cannot delete the active profile.")
            return
            
        reply = QMessageBox.question(self, "Confirm Delete", f"Delete profile '{prof_name}'?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            del self.profiles_data["profiles"][prof_name]
            import schedule_manager
            schedule_manager.save_profiles(self.profiles_data)
            
            self.profile_combo.blockSignals(True)
            self.profile_combo.removeItem(self.profile_combo.currentIndex())
            self.profile_combo.setCurrentText(self.active_profile_name)
            self.profile_combo.blockSignals(False)
            self.load_profile_into_editor(self.active_profile_name)

    def ui_make_active(self):
        from PyQt5.QtWidgets import QMessageBox
        prof_name = self.profile_combo.currentText()
        self.profiles_data["active_profile"] = prof_name
        self.active_profile_name = prof_name
        
        # Save active into schedule.json and profiles.json
        self.save_schedule_from_ui()
        
        self.lbl_active_prof.setText("(ACTIVE)")
        self.btn_make_active.hide()
        QMessageBox.information(self, "Success", f"Profile '{prof_name}' is now active! Sync your mobile app to receive it.")
            
        self.on_mode_changed()
        
    def on_mode_changed(self):
        mode = self.mode_combo.currentIndex()
        self.day_combo.blockSignals(True)
        self.day_combo.clear()
        if mode == 0:
            self.day_lbl.hide()
            self.day_combo.hide()
            self.day_combo.addItems(["Day 1"])
        elif mode == 1:
            self.day_lbl.show()
            self.day_combo.show()
            self.day_lbl.setText("Select Day:")
            days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            self.day_combo.addItems([f"{days_of_week[i-1]} (Day {i})" for i in range(1, 8)])
        elif mode == 2:
            self.day_lbl.show()
            self.day_combo.show()
            self.day_lbl.setText("Select Day:")
            self.day_combo.addItems([f"Day {i}" for i in range(1, 32)])
        self.day_combo.blockSignals(False)
        self.ui_load_day_topics()
        
    def ui_load_day_topics(self):
        if hasattr(self, '_current_edit_day'):
            topics = []
            for i in range(self.topics_container.count()):
                hbox = self.topics_container.itemAt(i)
                if hbox:
                    cat = hbox.itemAt(0).widget().currentText()
                    desc = hbox.itemAt(1).widget().text()
                    topics.append([cat, desc])
            self.edit_days[self._current_edit_day] = topics

        day_num = str(self.day_combo.currentIndex() + 1) if self.day_combo.isVisible() else "1"
        self._current_edit_day = day_num
        
        while self.topics_container.count() > 0:
            item = self.topics_container.takeAt(0)
            self.delete_layout_row(item, self.topics_container)
            
        topics = self.edit_days.get(day_num, [])
        for t in topics:
            self.ui_add_topic(t[0], t[1])
        

            
    def save_schedule_from_ui(self):
        import schedule_manager
        import study_schedule as ss
        
        self.ui_load_day_topics()
        mode = self.mode_combo.currentIndex()
        final_days = {}
        
        if mode == 0:
            topics = self.edit_days.get("1", [])
            final_days = {"1": [list(t) for t in topics]}
        elif mode == 1:
            final_days = {str(i): self.edit_days.get(str(i), []) for i in range(1, 8)}
        elif mode == 2:
            final_days = {str(i): self.edit_days.get(str(i), []) for i in range(1, 32)}
        
        # Harvest slots
        new_slots = []
        for i in range(self.slots_layout.count() - 1):
            hbox = self.slots_layout.itemAt(i)
            if hbox:
                start = hbox.itemAt(0).widget().text()
                end = hbox.itemAt(1).widget().text()
                name = hbox.itemAt(2).widget().text()
                new_slots.append([start, end, name])
                
        prof_name = self.profile_combo.currentText()
        if prof_name in self.profiles_data.get("profiles", {}):
            self.profiles_data["profiles"][prof_name]["mode"] = mode
            self.profiles_data["profiles"][prof_name]["slots"] = new_slots
            self.profiles_data["profiles"][prof_name]["days"] = {k: list(v) for k, v in final_days.items()}
            schedule_manager.save_profiles(self.profiles_data)
            
        if prof_name == self.active_profile_name:
            schedule_manager.save_schedule(new_slots, final_days)
            # Live update study_schedule variables
            ss.SLOTS = [(s[0], s[1], s[2]) for s in new_slots]
            ss.DAYS = {int(k): [(t[0], t[1]) for t in v] for k, v in final_days.items()}
            self.update_ui()
            
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Success", "Profile saved successfully!")

    def export_json_template(self):
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        import json
        
        mode = self.template_combo.currentIndex()
        
        template = {
            "slots": [
                ["09:00", "12:00", "Morning Block"],
                ["13:00", "16:00", "Afternoon Block"]
            ],
            "days": {}
        }
        
        sample_topics = [
            ["Morning Block", "Topic for morning"],
            ["Afternoon Block", "Topic for afternoon"]
        ]
        
        if mode == 0:
            template["days"] = {"1": sample_topics}
        elif mode == 1:
            template["days"] = {str(i): sample_topics for i in range(1, 8)}
        elif mode == 2:
            template["days"] = {str(i): sample_topics for i in range(1, 32)}
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Save JSON Template", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(template, f, indent=2)
                QMessageBox.information(self, "Success", f"Template saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save template:\n{e}")

    def import_json_template(self):
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        import json
        import schedule_manager
        
        file_path, _ = QFileDialog.getOpenFileName(self, "Open JSON Template", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                if "slots" not in data or "days" not in data:
                    raise ValueError("JSON must contain both 'slots' and 'days' keys.")
                    
                self.edit_slots = data["slots"]
                self.edit_days = {str(k): list(v) for k, v in data["days"].items()}
                
                # We update the internal mode combo automatically based on length
                days_len = len([k for k in self.edit_days.keys() if int(k) <= 31])
                if days_len <= 7 and days_len > 1:
                    self.mode_combo.setCurrentIndex(1)
                elif days_len > 7:
                    self.mode_combo.setCurrentIndex(2)
                else:
                    self.mode_combo.setCurrentIndex(0)
                
                # Re-render the UI elements for edit_slots & edit_days
                while self.slots_layout.count() > 1:
                    item = self.slots_layout.takeAt(0)
                    self.delete_layout_row(item, self.slots_layout)
                    
                for s in self.edit_slots:
                    self.ui_add_slot(s[0], s[1], s[2])
                    
                self.on_mode_changed()
                
                # Ensure we also save and broadcast changes immediately
                self.save_schedule_from_ui()
                QMessageBox.information(self, "Success", "Schedule successfully imported and applied!")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import schedule:\n{e}")

    def toggle_sidebar(self):
        target_width = 0 if self.sidebar_container.width() > 100 else 220
        self.anim = QPropertyAnimation(self.sidebar_container, b"maximumWidth")
        self.anim.setDuration(300)
        self.anim.setStartValue(self.sidebar_container.width())
        self.anim.setEndValue(target_width)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.anim.start()
        
    def toggle_glass(self):
        self.is_glass_mode = not self.is_glass_mode
        if self.is_glass_mode:
            self.btn_glass.setText("⚫ Solid Mode")
            self.setStyleSheet("""
                QMainWindow { background-color: transparent; }
                #MainCentralWidget {
                    border: 4px solid rgba(156, 39, 176, 180);
                    border-radius: 8px;
                    background-color: rgba(248, 249, 250, 150);
                }
            """)
            self.right_pane.setStyleSheet("background-color: transparent;")
            self.sidebar_container.setStyleSheet("""
                QFrame {
                    background-color: rgba(255, 255, 255, 100);
                    border-right: 1px solid rgba(224, 224, 224, 150);
                }
            """)
        else:
            self.btn_glass.setText("⚪ Glass Mode")
            self.setStyleSheet("""
                QMainWindow { background-color: transparent; }
                #MainCentralWidget {
                    border: 4px solid #9C27B0;
                    border-radius: 8px;
                    background-color: #F8F9FA;
                }
            """)
            self.right_pane.setStyleSheet("background-color: #F8F9FA;")
            self.sidebar_container.setStyleSheet("""
                QFrame {
                    background-color: #FFFFFF;
                    border-right: 1px solid #E0E0E0;
                }
            """)

    def toggle_pin(self):
        self.is_always_on_top = not self.is_always_on_top
        self.setWindowFlag(Qt.WindowStaysOnTopHint, self.is_always_on_top)
        self.show()
        if self.is_always_on_top:
            self.btn_pin.setText("📌 Pinned")
            self.btn_pin.setStyleSheet("""
                QPushButton {
                    font-size: 11px; font-weight: bold; border-radius: 15px;
                    background: #E0F2F1; color: #004D40; border: 1px solid #00897B;
                }
                QPushButton:hover { background: #B2DFDB; }
            """)
        else:
            self.btn_pin.setText("📍 Unpinned")
            self.btn_pin.setStyleSheet("""
                QPushButton {
                    font-size: 11px; font-weight: bold; border-radius: 15px;
                    background: #E0E0E0; color: #616161; border: 1px solid #BDBDBD;
                }
                QPushButton:hover { background: #D6D6D6; }
            """)

    def switch_view(self, idx):
        self.stacked_widget.setCurrentIndex(idx)
        for i, btn in enumerate(self.nav_buttons):
            if i == idx:
                btn.setStyleSheet("""
                    QPushButton {
                        text-align: left; padding: 10px; border: none;
                        background-color: #E0F2F1; font-size: 13px;
                        color: #004D40; font-weight: bold; border-radius: 5px;
                        border-left: 4px solid #004D40;
                    }
                """)
            else:
                btn.setStyleSheet(self.nav_default_style)
        if idx == 2 and hasattr(self, 'refresh_progress_view'):
            self.refresh_progress_view()

    def toggle_study_session(self):
        import analytics_manager as am
        active_sess = am.get_active_session()
        now = dt.datetime.now()
        
        if active_sess.get("is_active"):
            completed = am.stop_session()
            mins = completed.get("duration_minutes", 0) if completed else 0
            subj = completed.get("subject", "General Study")
            tot_today = am.get_subject_time_today(subj)
            tot_mins = tot_today.get("minutes", mins)
            th, tm = divmod(tot_mins, 60)
            tot_str = f"{th}h {tm}m" if th > 0 else f"{tm}m"
            
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(
                self, "Session Completed",
                f"🎉 Great job! Study session saved:\n\n"
                f"• Subject: {subj}\n"
                f"• This Session: {mins} minutes\n"
                f"• Total Studied for {subj} Today: {tot_str}\n"
                f"• Status: {completed.get('status')}"
            )
        else:
            state = ss.get_state() or {}
            shift_seconds = state.get("shift_seconds", 0)
            is_paused = state.get("is_paused", False)
            if is_paused:
                pause_start = state.get("pause_start_timestamp", now.timestamp())
                effective_now = dt.datetime.fromtimestamp(pause_start) - dt.timedelta(seconds=shift_seconds)
            else:
                effective_now = now - dt.timedelta(seconds=shift_seconds)
                
            total_days = max(ss.DAYS.keys()) if ss.DAYS else 1
            raw_d = ss.day_number(effective_now.date())
            d_display = ((raw_d - 1) % 7) + 1 if total_days == 7 else min(30, max(1, raw_d))
            day_topics = {cat.upper(): topic for cat, topic in ss.DAYS.get(d_display, [])}
            
            cur = ss.current_slot(effective_now)
            if cur:
                s_start, s_end, s_name, _ = cur
                s_topic = day_topics.get(s_name.upper(), "Scheduled Session")
            else:
                s_start, s_end = now.strftime("%H:%M"), ""
                s_name = "Self Study"
                s_topic = "Independent Focus"
                
            prev_info = am.get_subject_time_today(s_name)
            prev_mins = prev_info.get("minutes", 0)
            
            am.start_session(subject=s_name, topic=s_topic, slot_start=s_start, slot_end=s_end)
            if is_paused:
                am.update_session_pause(True)
                
            from PyQt5.QtWidgets import QMessageBox
            if prev_mins > 0:
                ph, pm = divmod(prev_mins, 60)
                p_str = f"{ph}h {pm}m" if ph > 0 else f"{pm}m"
                msg = (
                    f"🟢 Resuming Study Session for {s_name}!\n\n"
                    f"• Previous progress today: {p_str}\n"
                    f"• Topic: {s_topic}\n\n"
                    f"The timer continues accumulating your total study time for this subject."
                )
            else:
                msg = (
                    f"🟢 You are now ONLINE & STUDYING!\n\n"
                    f"• Subject: {s_name}\n"
                    f"• Topic: {s_topic}\n\n"
                    f"Your active study time is being accurately recorded."
                )
            QMessageBox.information(self, "Session Started", msg)
            
        self.update_ui()
        if hasattr(self, 'refresh_progress_view'):
            self.refresh_progress_view()

    def setup_progress_view(self):
        from PyQt5.QtWidgets import (
            QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
            QPushButton, QComboBox, QProgressBar, QTableWidget,
            QTableWidgetItem, QHeaderView, QFrame, QFileDialog, QMessageBox
        )
        import analytics_manager as am
        
        self.progress_layout = QVBoxLayout(self.progress_view)
        self.progress_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setObjectName("ProgScrollContent")
        scroll_content.setStyleSheet("#ProgScrollContent { background: transparent; }")
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(10, 10, 20, 30)
        layout.setSpacing(20)
        
        # 1. Header Section
        header_hbox = QHBoxLayout()
        title_vbox = QVBoxLayout()
        lbl_title = QLabel("📈 Progress & Analytics")
        lbl_title.setStyleSheet("color: #004D40; font-weight: bold; font-size: 22px;")
        lbl_subtitle = QLabel("Track verified study hours, completion rates, and historical logs")
        lbl_subtitle.setStyleSheet("color: #757575; font-size: 12px;")
        title_vbox.addWidget(lbl_title)
        title_vbox.addWidget(lbl_subtitle)
        header_hbox.addLayout(title_vbox)
        header_hbox.addStretch()
        
        header_hbox.addWidget(QLabel("Timeframe:"))
        self.prog_timeframe_combo = QComboBox()
        self.prog_timeframe_combo.setStyleSheet("""
            QComboBox {
                background-color: white; color: black; border: 1px solid #BDBDBD;
                border-radius: 4px; padding: 4px 10px; font-weight: bold; font-size: 12px;
            }
        """)
        self.prog_timeframe_combo.addItem("This Week (7 Days)", "7_days")
        self.prog_timeframe_combo.addItem("Today", "today")
        self.prog_timeframe_combo.addItem("This Month (30 Days)", "30_days")
        self.prog_timeframe_combo.addItem("All Time", "all")
        self.prog_timeframe_combo.currentIndexChanged.connect(self.refresh_progress_view)
        header_hbox.addWidget(self.prog_timeframe_combo)
        
        btn_csv = QPushButton("📥 Export CSV")
        btn_csv.setStyleSheet("background-color: #E0E0E0; color: #424242; padding: 5px 12px; border-radius: 4px; font-weight: bold; border: 1px solid #BDBDBD;")
        btn_csv.clicked.connect(self.export_progress_csv)
        header_hbox.addWidget(btn_csv)
        
        btn_json = QPushButton("📥 Export JSON")
        btn_json.setStyleSheet("background-color: #E0E0E0; color: #424242; padding: 5px 12px; border-radius: 4px; font-weight: bold; border: 1px solid #BDBDBD;")
        btn_json.clicked.connect(self.export_progress_json)
        header_hbox.addWidget(btn_json)
        
        layout.addLayout(header_hbox)
        
        # 2. KPI Stat Cards Row
        kpi_hbox = QHBoxLayout()
        kpi_hbox.setSpacing(15)
        
        def create_kpi_card(title, value_obj, sub_obj, accent_color="#004D40"):
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: #FFFFFF;
                    border: 1px solid #E0E0E0;
                    border-radius: 8px;
                    border-left: 4px solid {accent_color};
                }}
            """)
            cvbox = QVBoxLayout(card)
            cvbox.setContentsMargins(15, 12, 15, 12)
            lbl_t = QLabel(title)
            lbl_t.setStyleSheet("color: #757575; font-size: 11px; font-weight: bold; border: none;")
            cvbox.addWidget(lbl_t)
            cvbox.addWidget(value_obj)
            cvbox.addWidget(sub_obj)
            return card
            
        self.kpi_time_val = QLabel("0h 00m")
        self.kpi_time_val.setStyleSheet("color: #004D40; font-size: 22px; font-weight: bold; border: none;")
        self.kpi_time_sub = QLabel("Target: 0h 00m")
        self.kpi_time_sub.setStyleSheet("color: #757575; font-size: 11px; border: none;")
        card1 = create_kpi_card("⏱️ TOTAL STUDY TIME", self.kpi_time_val, self.kpi_time_sub, "#004D40")
        
        self.kpi_comp_val = QLabel("0.0%")
        self.kpi_comp_val.setStyleSheet("color: #1E88E5; font-size: 22px; font-weight: bold; border: none;")
        self.kpi_comp_bar = QProgressBar()
        self.kpi_comp_bar.setFixedHeight(8)
        self.kpi_comp_bar.setTextVisible(False)
        self.kpi_comp_bar.setStyleSheet("""
            QProgressBar { background: #E0E0E0; border-radius: 4px; border: none; }
            QProgressBar::chunk { background: #1E88E5; border-radius: 4px; }
        """)
        card2 = create_kpi_card("🎯 COMPLETION RATE", self.kpi_comp_val, self.kpi_comp_bar, "#1E88E5")
        
        self.kpi_streak_val = QLabel("0 Days")
        self.kpi_streak_val.setStyleSheet("color: #FB8C00; font-size: 22px; font-weight: bold; border: none;")
        self.kpi_streak_sub = QLabel("Consecutive study streak")
        self.kpi_streak_sub.setStyleSheet("color: #757575; font-size: 11px; border: none;")
        card3 = create_kpi_card("🔥 ACTIVE STREAK", self.kpi_streak_val, self.kpi_streak_sub, "#FB8C00")
        
        self.kpi_focus_val = QLabel("100%")
        self.kpi_focus_val.setStyleSheet("color: #43A047; font-size: 22px; font-weight: bold; border: none;")
        self.kpi_focus_sub = QLabel("Pauses: 0m total")
        self.kpi_focus_sub.setStyleSheet("color: #757575; font-size: 11px; border: none;")
        card4 = create_kpi_card("⚡ FOCUS EFFICIENCY", self.kpi_focus_val, self.kpi_focus_sub, "#43A047")
        
        kpi_hbox.addWidget(card1)
        kpi_hbox.addWidget(card2)
        kpi_hbox.addWidget(card3)
        kpi_hbox.addWidget(card4)
        layout.addLayout(kpi_hbox)
        
        # 3. Middle Visual Analytics Section
        charts_hbox = QHBoxLayout()
        charts_hbox.setSpacing(15)
        
        # Daily Activity Card
        daily_card = QFrame()
        daily_card.setStyleSheet("QFrame { background-color: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 8px; }")
        daily_vbox = QVBoxLayout(daily_card)
        daily_vbox.setContentsMargins(15, 15, 15, 15)
        lbl_daily_h = QLabel("📅 Daily Study Activity")
        lbl_daily_h.setStyleSheet("color: #212121; font-weight: bold; font-size: 14px; border: none;")
        lbl_daily_s = QLabel("Comparison of daily study hours (Planned vs. Actual)")
        lbl_daily_s.setStyleSheet("color: #757575; font-size: 11px; border: none;")
        daily_vbox.addWidget(lbl_daily_h)
        daily_vbox.addWidget(lbl_daily_s)
        daily_vbox.addSpacing(10)
        
        self.daily_chart_container = QVBoxLayout()
        daily_vbox.addLayout(self.daily_chart_container)
        daily_vbox.addStretch()
        charts_hbox.addWidget(daily_card, stretch=3)
        
        # Subject Distribution Card
        subj_card = QFrame()
        subj_card.setStyleSheet("QFrame { background-color: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 8px; }")
        subj_vbox = QVBoxLayout(subj_card)
        subj_vbox.setContentsMargins(15, 15, 15, 15)
        lbl_subj_h = QLabel("📚 Subject Distribution")
        lbl_subj_h.setStyleSheet("color: #212121; font-weight: bold; font-size: 14px; border: none;")
        lbl_subj_s = QLabel("Time spent and share by subject")
        lbl_subj_s.setStyleSheet("color: #757575; font-size: 11px; border: none;")
        subj_vbox.addWidget(lbl_subj_h)
        subj_vbox.addWidget(lbl_subj_s)
        subj_vbox.addSpacing(10)
        
        self.subj_container = QVBoxLayout()
        subj_vbox.addLayout(self.subj_container)
        subj_vbox.addStretch()
        charts_hbox.addWidget(subj_card, stretch=2)
        
        layout.addLayout(charts_hbox)
        
        # 4. Session Logs & Reports Table Card
        table_card = QFrame()
        table_card.setStyleSheet("QFrame { background-color: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 8px; }")
        table_vbox = QVBoxLayout(table_card)
        table_vbox.setContentsMargins(15, 15, 15, 15)
        
        lbl_tbl_h = QLabel("📋 Verified Study Sessions & Reports")
        lbl_tbl_h.setStyleSheet("color: #212121; font-weight: bold; font-size: 14px; border: none;")
        lbl_tbl_s = QLabel("Complete chronological history of study sessions")
        lbl_tbl_s.setStyleSheet("color: #757575; font-size: 11px; border: none;")
        table_vbox.addWidget(lbl_tbl_h)
        table_vbox.addWidget(lbl_tbl_s)
        table_vbox.addSpacing(10)
        
        self.session_table = QTableWidget()
        self.session_table.setColumnCount(7)
        self.session_table.setHorizontalHeaderLabels([
            "Date", "Time", "Subject", "Topic", "Duration", "Status", "Pause"
        ])
        self.session_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.session_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.session_table.setAlternatingRowColors(True)
        self.session_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #EEEEEE;
                gridline-color: #F0F0F0;
                font-size: 12px;
                background-color: white;
                alternate-background-color: #FAFAFA;
            }
            QHeaderView::section {
                background-color: #ECEFF1;
                color: #37474F;
                font-weight: bold;
                font-size: 11px;
                padding: 6px;
                border: none;
                border-right: 1px solid #CFD8DC;
            }
        """)
        self.session_table.setMinimumHeight(240)
        table_vbox.addWidget(self.session_table)
        
        layout.addWidget(table_card)
        
        scroll.setWidget(scroll_content)
        self.progress_layout.addWidget(scroll)
        
        self.refresh_progress_view()

    def refresh_progress_view(self):
        from PyQt5.QtWidgets import QLabel, QProgressBar, QHBoxLayout, QVBoxLayout, QTableWidgetItem
        from PyQt5.QtCore import Qt
        import analytics_manager as am
        
        if not hasattr(self, 'prog_timeframe_combo'):
            return
            
        timeframe = self.prog_timeframe_combo.currentData() or "7_days"
        
        planned_mins = 0
        for s_start, s_end, _ in ss.SLOTS:
            try:
                t1 = dt.datetime.strptime(s_start, "%H:%M")
                t2 = dt.datetime.strptime(s_end, "%H:%M")
                planned_mins += int((t2 - t1).total_seconds() // 60)
            except Exception:
                planned_mins += 120
        if planned_mins <= 0: planned_mins = 360
        
        m = am.get_metrics(timeframe=timeframe, planned_daily_minutes=planned_mins)
        
        # 1. Update KPI cards
        self.kpi_time_val.setText(m["total_actual_hours_str"])
        self.kpi_time_sub.setText(f"Target: {m['total_planned_hours_str']}")
        
        comp_pct = m["completion_rate_pct"]
        self.kpi_comp_val.setText(f"{comp_pct}%")
        self.kpi_comp_bar.setValue(int(min(100, comp_pct)))
        
        streak = m["streak_days"]
        self.kpi_streak_val.setText(f"{streak} Day{'s' if streak != 1 else ''}")
        self.kpi_streak_sub.setText("🔥 On a roll!" if streak >= 3 else "Keep it up!")
        
        self.kpi_focus_val.setText(f"{m['focus_efficiency_pct']}%")
        self.kpi_focus_sub.setText(f"Pauses: {m['total_pause_minutes']}m total")
        
        # 2. Update Daily Activity Chart
        while self.daily_chart_container.count():
            child = self.daily_chart_container.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            elif child.layout():
                while child.layout().count():
                    sub = child.layout().takeAt(0)
                    if sub.widget(): sub.widget().deleteLater()
                    
        daily_points = m.get("daily_chart", [])
        max_hrs = max([p["planned_hours"] for p in daily_points] + [p["actual_hours"] for p in daily_points] + [1.0])
        
        for p in daily_points[-7:]:
            row = QHBoxLayout()
            lbl_d = QLabel(p["label"])
            lbl_d.setFixedWidth(60)
            lbl_d.setStyleSheet("font-size: 11px; font-weight: bold; color: #424242; border: none;")
            
            bar = QProgressBar()
            bar.setFixedHeight(12)
            bar.setTextVisible(False)
            bar_val = int((p["actual_hours"] / max_hrs) * 100)
            bar.setValue(min(100, bar_val))
            bar.setStyleSheet("""
                QProgressBar { background: #ECEFF1; border-radius: 6px; border: none; }
                QProgressBar::chunk { background: #00897B; border-radius: 6px; }
            """)
            
            lbl_val = QLabel(f"{p['actual_hours']}h / {p['planned_hours']}h")
            lbl_val.setFixedWidth(85)
            lbl_val.setStyleSheet("font-size: 11px; color: #616161; border: none;")
            
            row.addWidget(lbl_d)
            row.addWidget(bar)
            row.addWidget(lbl_val)
            self.daily_chart_container.addLayout(row)
            
        # 3. Update Subject Distribution
        while self.subj_container.count():
            child = self.subj_container.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            elif child.layout():
                while child.layout().count():
                    sub = child.layout().takeAt(0)
                    if sub.widget(): sub.widget().deleteLater()
                    
        subjs = m.get("subject_breakdown", [])
        if not subjs:
            lbl_none = QLabel("No subject data in this period")
            lbl_none.setStyleSheet("color: #9E9E9E; font-size: 12px; border: none;")
            self.subj_container.addWidget(lbl_none)
        else:
            for s in subjs:
                row = QVBoxLayout()
                row.setSpacing(2)
                top_row = QHBoxLayout()
                lbl_name = QLabel(s["subject"])
                lbl_name.setStyleSheet("font-size: 12px; font-weight: bold; color: #212121; border: none;")
                lbl_pct = QLabel(f"{s['hours_str']} ({s['pct']}%)")
                lbl_pct.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {s['color']}; border: none;")
                top_row.addWidget(lbl_name)
                top_row.addStretch()
                top_row.addWidget(lbl_pct)
                
                bar = QProgressBar()
                bar.setFixedHeight(8)
                bar.setTextVisible(False)
                bar.setValue(int(s["pct"]))
                bar.setStyleSheet(f"""
                    QProgressBar {{ background: #ECEFF1; border-radius: 4px; border: none; }}
                    QProgressBar::chunk {{ background: {s['color']}; border-radius: 4px; }}
                """)
                row.addLayout(top_row)
                row.addWidget(bar)
                self.subj_container.addLayout(row)
                
        # 4. Update Session Table
        sessions = m.get("sessions", [])
        self.session_table.setRowCount(len(sessions))
        for row_idx, s in enumerate(sessions):
            t_win = f"{s.get('start_time', '')} - {s.get('end_time', '')}"
            dur_mins = s.get("duration_minutes", 0)
            dur_secs = s.get("duration_seconds")
            if dur_secs is not None and dur_secs < 60:
                dur_str = f"{dur_secs}s"
            elif dur_mins >= 60:
                dur_str = f"{dur_mins // 60}h {dur_mins % 60}m"
            else:
                dur_str = f"{dur_mins}m"
            pause_str = f"{s.get('pause_seconds', 0) // 60}m"
            
            self.session_table.setItem(row_idx, 0, QTableWidgetItem(s.get("date", "")))
            self.session_table.setItem(row_idx, 1, QTableWidgetItem(t_win))
            self.session_table.setItem(row_idx, 2, QTableWidgetItem(s.get("subject", "")))
            self.session_table.setItem(row_idx, 3, QTableWidgetItem(s.get("topic", "")))
            self.session_table.setItem(row_idx, 4, QTableWidgetItem(dur_str))
            
            status_item = QTableWidgetItem(s.get("status", "COMPLETED"))
            if s.get("status") == "COMPLETED":
                status_item.setForeground(Qt.darkGreen)
            else:
                status_item.setForeground(Qt.darkYellow)
            self.session_table.setItem(row_idx, 5, status_item)
            
            self.session_table.setItem(row_idx, 6, QTableWidgetItem(pause_str))

    def export_progress_csv(self):
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        import analytics_manager as am
        default_name = f"study_report_{dt.date.today()}.csv"
        path, _ = QFileDialog.getSaveFileName(self, "Export Progress Report (CSV)", default_name, "CSV Files (*.csv)")
        if path:
            ok, msg = am.export_csv(path)
            if ok:
                QMessageBox.information(self, "Export Success", f"Report successfully exported to:\n{path}")
            else:
                QMessageBox.warning(self, "Export Error", f"Failed to export CSV: {msg}")

    def export_progress_json(self):
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        import analytics_manager as am
        default_name = f"study_report_{dt.date.today()}.json"
        path, _ = QFileDialog.getSaveFileName(self, "Export Progress Report (JSON)", default_name, "JSON Files (*.json)")
        if path:
            ok, msg = am.export_json(path)
            if ok:
                QMessageBox.information(self, "Export Success", f"Report successfully exported to:\n{path}")
            else:
                QMessageBox.warning(self, "Export Error", f"Failed to export JSON: {msg}")
            
    def toggle_pause(self):
        now = dt.datetime.now()
        today_str = str(now.date())
        state = ss.get_state()
        was_paused_yesterday = False
        
        if not state or state.get("date") != today_str:
            if state and state.get("is_paused"):
                was_paused_yesterday = True
            state = {"date": today_str, "shift_seconds": 0, "is_paused": False, "pause_start_timestamp": 0}
            
        if was_paused_yesterday:
            pass
        elif state["is_paused"]:
            pause_duration = now.timestamp() - state["pause_start_timestamp"]
            state["shift_seconds"] += max(0, pause_duration)
            state["is_paused"] = False
            state["pause_start_timestamp"] = 0
        else:
            state["is_paused"] = True
            state["pause_start_timestamp"] = now.timestamp()
            
        ss.save_state(state)
        import analytics_manager as am
        am.update_session_pause(state.get("is_paused", False))
        self.update_ui()

    def update_ui(self):
        now = dt.datetime.now()
        today_str = str(now.date())
        
        state = ss.get_state()
        if not state or state.get("date") != today_str:
            state = {"date": today_str, "shift_seconds": 0, "is_paused": False, "pause_start_timestamp": 0}
            ss.save_state(state)
            
        shift_seconds = state.get("shift_seconds", 0)
        is_paused = state.get("is_paused", False)
        
        if is_paused:
            pause_start = state.get("pause_start_timestamp", now.timestamp())
            effective_now = dt.datetime.fromtimestamp(pause_start) - dt.timedelta(seconds=shift_seconds)
            current_pause_duration = now.timestamp() - pause_start
        else:
            effective_now = now - dt.timedelta(seconds=shift_seconds)
            current_pause_duration = 0
            
        total_days = max(ss.DAYS.keys()) if ss.DAYS else 1
        
        raw_d = ss.day_number(effective_now.date())
        
        if total_days == 7:
            d_display = ((raw_d - 1) % 7) + 1
            total_lbl = 7
        else:
            d_display = raw_d
            if d_display > 30:
                d_display = 30
            elif d_display < 1:
                d_display = 1
            total_lbl = 30
        
        if not is_paused and (1 <= d_display <= total_lbl):
            import subprocess
            for start, end, name in ss.SLOTS:
                target = ss.parse(start, effective_now.date())
                if effective_now >= target:
                    stamp = Path("/tmp") / f"conky-study-{effective_now.date()}-{start.replace(':','')}"
                    if not stamp.exists():
                        stamp.touch()
                        try:
                            subprocess.Popen([
                                "notify-send", "-u", "normal",
                                f"Study Time — {name}",
                                f"Day {d_display} • {start}–{end}\nStart your scheduled session now."
                            ])
                        except Exception:
                            pass
                            
        self.lbl_day_top.setText(f"Day {d_display} / {total_lbl}")
        self.lbl_day_big.setText(f"DAY {d_display} / {total_lbl}")
        self.lbl_date.setText(now.strftime("%A, %d %b %Y"))
        self.lbl_time.setText(f"TIME {now.strftime('%H:%M:%S')}")
        
        # Populate topics cards chronologically based on SLOTS
        while self.topics_layout.count():
            child = self.topics_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        color_map = {"DSA": "#00897B", "MOBILE": "#43A047", "BANK": "#9C27B0"}
        fallback_colors = ["#E53935", "#1E88E5", "#F4511E", "#3949AB", "#FFB300", "#00ACC1", "#8E24AA", "#43A047"]
        
        # Get topics for today as a dict for easy lookup
        day_topics = {cat.upper(): topic for cat, topic in ss.DAYS.get(d_display, [])}
        
        for start_str, end_str, name in ss.SLOTS:
            name_upper = name.upper()
            topic_desc = day_topics.get(name_upper, "General Study")
            
            # Determine status: Past, Current, Future
            s_time = ss.parse(start_str, effective_now.date())
            e_time = ss.parse(end_str, effective_now.date())
            
            status = "FUTURE"
            if effective_now > e_time:
                status = "PAST"
            elif s_time <= effective_now <= e_time:
                status = "CURRENT"
            
            if name_upper in color_map:
                col = color_map[name_upper]
            else:
                col_idx = hash(name_upper) % len(fallback_colors)
                col = fallback_colors[col_idx]
                
            card = QFrame()
            
            if status == "PAST":
                card.setStyleSheet(f"""
                    QFrame {{
                        background-color: #F5F5F5;
                        border: 1px solid #EEEEEE;
                        border-radius: 4px;
                        border-left: 4px solid #BDBDBD;
                    }}
                """)
                text_col = "#9E9E9E"
                cat_text = f"{name_upper}\n({start_str})"
            elif status == "CURRENT":
                card.setStyleSheet(f"""
                    QFrame {{
                        background-color: #E0F2F1;
                        border: 2px solid {col};
                        border-radius: 4px;
                        border-left: 6px solid {col};
                    }}
                """)
                text_col = "#212121"
                cat_text = f"▶ NOW\n{name_upper}\n({start_str})"
            else:
                card.setStyleSheet(f"""
                    QFrame {{
                        background-color: #FFFFFF;
                        border: 1px solid #E0E0E0;
                        border-radius: 4px;
                        border-left: 4px solid {col};
                    }}
                """)
                text_col = "#424242"
                cat_text = f"{name_upper}\n({start_str})"
            
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(15, 15, 15, 15)
            
            lbl_cat = QLabel(cat_text)
            if status == "PAST":
                lbl_cat.setStyleSheet(f"color: #9E9E9E; font-weight: bold; font-size: 12px; border: none;")
            else:
                lbl_cat.setStyleSheet(f"color: {col}; font-weight: bold; font-size: 13px; border: none;")
            lbl_cat.setMinimumWidth(120)
            lbl_cat.setMaximumWidth(160)
            lbl_cat.setWordWrap(True)
            
            lbl_top = QLabel(topic_desc)
            if status == "CURRENT":
                lbl_top.setStyleSheet(f"color: {text_col}; font-weight: bold; font-size: 14px; border: none;")
            else:
                lbl_top.setStyleSheet(f"color: {text_col}; font-size: 13px; border: none;")
            lbl_top.setWordWrap(True)
            
            card_layout.addWidget(lbl_cat)
            card_layout.addWidget(lbl_top)
            
            # Show verified time studied today for this subject if any
            import analytics_manager as am
            subj_stat = am.get_subject_time_today(name)
            if subj_stat.get("minutes", 0) > 0:
                sm = subj_stat["minutes"]
                sh, smin = divmod(sm, 60)
                sd_str = f"{sh}h {smin}m" if sh > 0 else f"{smin}m"
                lbl_done = QLabel(f"✓ {sd_str} studied")
                lbl_done.setStyleSheet("color: #00897B; font-size: 11px; font-weight: bold; border: none; background-color: #E0F2F1; padding: 3px 7px; border-radius: 4px;")
                card_layout.addStretch()
                card_layout.addWidget(lbl_done)
            
            self.topics_layout.addWidget(card)
            
        cur = ss.current_slot(effective_now)
        nxt = ss.next_slot(effective_now)
        
        if cur:
            start, end, name, rem = cur
            m = max(0, int(rem.total_seconds() // 60))
            self.now_card.show()
            self.lbl_now_title.setText(name)
            self.lbl_now_bounds.setText(f"🕒 {start} - {end}")
            
            if m >= 60:
                self.lbl_now_time_rem.setText(f'<span style="font-size:24px; font-weight:bold; color:#212121;">{m//60:02d}h {m%60:02d}m</span> <span style="font-size:12px; color:#757575;">remaining</span>')
            else:
                self.lbl_now_time_rem.setText(f'<span style="font-size:24px; font-weight:bold; color:#212121;">{m:02d}m</span> <span style="font-size:12px; color:#757575;">remaining</span>')
                
        elif nxt:
            start, end, name, until = nxt
            m = max(0, int(until.total_seconds() // 60))
            self.now_card.show()
            self.lbl_now_title.setText(name)
            self.lbl_now_bounds.setText(f"🕒 {start} - {end}")
            
            if m >= 60:
                self.lbl_now_time_rem.setText(f'<span style="font-size:24px; font-weight:bold; color:#212121;">{m//60:02d}h {m%60:02d}m</span> <span style="font-size:12px; color:#757575;">starts in</span>')
            else:
                self.lbl_now_time_rem.setText(f'<span style="font-size:24px; font-weight:bold; color:#212121;">{m:02d}m</span> <span style="font-size:12px; color:#757575;">starts in</span>')
        else:
            self.now_card.hide()
            
        total_shift = int(shift_seconds + current_pause_duration)
        shift_str = ""
        if total_shift > 0:
            th, t_rem = divmod(total_shift, 3600)
            tm, ts = divmod(t_rem, 60)
            if th > 0: shift_str += f"{th}h "
            if tm > 0 or th > 0: shift_str += f"{tm}m "
            shift_str += f"{ts}s"
            self.lbl_shift.setText(f"Shift today: +{shift_str}")
        else:
            self.lbl_shift.setText("Shift today: 0s")
            
        if is_paused:
            ph, p_rem = divmod(int(current_pause_duration), 3600)
            pm, ps = divmod(p_rem, 60)
            self.lbl_shift.setText(f"PAUSED: {ph:02d}:{pm:02d}:{ps:02d} | " + self.lbl_shift.text())
            self.btn_pause.setText("Resume")
            self.btn_pause.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; border-radius: 4px; font-weight: bold; border: none; } QPushButton:hover { background-color: #388E3C; }")
        else:
            self.btn_pause.setText("Pause")
            self.btn_pause.setStyleSheet("QPushButton { background-color: #E53935; color: white; border-radius: 4px; font-weight: bold; border: none; } QPushButton:hover { background-color: #D32F2F; }")

        # Update Session Tracker Status & Stopwatch
        import analytics_manager as am
        active_sess = am.get_active_session()
        if active_sess.get("is_active"):
            elapsed = active_sess.get("elapsed_seconds", 0)
            prev_sec = active_sess.get("previous_subject_seconds", 0)
            tot_sec = active_sess.get("total_subject_seconds", elapsed)
            subj = active_sess.get("subject", "Study")
            
            # Format elapsed for this session
            eh, erem = divmod(elapsed, 3600)
            em, es = divmod(erem, 60)
            sess_str = f"{eh:02d}:{em:02d}:{es:02d}" if eh > 0 else f"{em:02d}:{es:02d}"
            
            # Format total today for this subject
            th, trem = divmod(tot_sec, 3600)
            tm, ts = divmod(trem, 60)
            tot_str = f"{th:02d}:{tm:02d}:{ts:02d}" if th > 0 else f"{tm:02d}:{ts:02d}"
            
            if active_sess.get("is_paused"):
                if prev_sec > 0:
                    status_text = f"⏸️ PAUSED • {tot_str} ({subj})\n[+{sess_str} this session]"
                else:
                    status_text = f"⏸️ PAUSED • {sess_str}"
                status_color = "#FB8C00"
            else:
                if prev_sec > 0:
                    status_text = f"🟢 ONLINE • {tot_str} ({subj})\n[+{sess_str} this session]"
                else:
                    status_text = f"🟢 ONLINE • {sess_str}"
                status_color = "#00897B"
                
            self.lbl_now_session_status.setText(status_text)
            self.lbl_now_session_status.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {status_color}; border: none;")
            self.btn_now_session.setText("🔴 Stop Session")
            self.btn_now_session.setStyleSheet("QPushButton { background-color: #D32F2F; color: white; border-radius: 4px; font-weight: bold; border: none; font-size: 11px; } QPushButton:hover { background-color: #C62828; }")
            self.btn_start.setText("🔴 Stop Session")
            self.btn_start.setStyleSheet("QPushButton { background-color: #D32F2F; color: white; border-radius: 8px; font-weight: bold; font-size: 13px; border: none; } QPushButton:hover { background-color: #C62828; }")
        else:
            cur_slot = ss.current_slot(effective_now)
            curr_subj = cur_slot[2] if cur_slot else ""
            prev_stat = am.get_subject_time_today(curr_subj) if curr_subj else {"seconds": 0, "minutes": 0}
            
            if prev_stat["seconds"] > 0:
                pmins = prev_stat["minutes"]
                ph, pm = divmod(pmins, 60)
                p_str = f"{ph}h {pm}m" if ph > 0 else f"{pm}m"
                self.lbl_now_session_status.setText(f"⚪ OFFLINE • {curr_subj} Today: {p_str}")
                self.lbl_now_session_status.setStyleSheet("font-size: 11px; font-weight: bold; color: #00897B; border: none;")
                self.btn_now_session.setText(f"🟢 Resume {curr_subj} ({p_str})")
                self.btn_now_session.setStyleSheet("QPushButton { background-color: #00897B; color: white; border-radius: 4px; font-weight: bold; border: none; font-size: 11px; } QPushButton:hover { background-color: #00695C; }")
                self.btn_start.setText("🟢 Resume Session")
                self.btn_start.setStyleSheet("QPushButton { background-color: #00897B; color: white; border-radius: 8px; font-weight: bold; font-size: 13px; border: none; } QPushButton:hover { background-color: #00695C; }")
            else:
                self.lbl_now_session_status.setText("⚪ OFFLINE")
                self.lbl_now_session_status.setStyleSheet("font-size: 12px; font-weight: bold; color: #757575; border: none;")
                self.btn_now_session.setText("🟢 Mark Online (Start)")
                self.btn_now_session.setStyleSheet("QPushButton { background-color: #004D40; color: white; border-radius: 4px; font-weight: bold; border: none; font-size: 11px; } QPushButton:hover { background-color: #00695C; }")
                self.btn_start.setText("🟢 Start Session")
                self.btn_start.setStyleSheet("QPushButton { background-color: #004D40; color: white; border-radius: 8px; font-weight: bold; font-size: 13px; border: none; } QPushButton:hover { background-color: #00695C; }")
            
        # Refresh progress view if currently active
        if hasattr(self, 'stacked_widget') and self.stacked_widget.currentIndex() == 2:
            if not hasattr(self, '_prog_refresh_tick'):
                self._prog_refresh_tick = 0
            self._prog_refresh_tick += 1
            if self._prog_refresh_tick % 5 == 0:
                self.refresh_progress_view()

    def show_sync_qr(self):
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
        from PyQt5.QtGui import QPixmap, QImage
        import socket
        import json
        import qrcode
        from pathlib import Path
        
        # Get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
            
        # Get Token
        token = ""
        port = 8080
        config_path = Path.home() / ".config/conky-study/sync_config.json"
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    data = json.load(f)
                    token = data.get("token", "")
                    port = data.get("port", 8080)
            except Exception:
                pass
                
        sync_data = json.dumps({"ip": ip, "port": port, "token": token})
        
        qr = qrcode.QRCode(box_size=10, border=4)
        qr.add_data(sync_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
        
        data = img.tobytes("raw", "RGBA")
        qim = QImage(data, img.width, img.height, QImage.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qim)
        
        dlg = QDialog(self)
        dlg.setWindowTitle("Mobile Sync QR Code")
        dlg.resize(400, 450)
        
        vbox = QVBoxLayout(dlg)
        lbl_info = QLabel(f"Scan this QR code from the Flutter app.\\nIP: {ip} | Port: {port}")
        lbl_info.setStyleSheet("font-size: 14px; font-weight: bold; color: #424242;")
        lbl_info.setAlignment(Qt.AlignCenter)
        
        lbl_qr = QLabel()
        lbl_qr.setPixmap(pixmap)
        lbl_qr.setAlignment(Qt.AlignCenter)
        
        vbox.addWidget(lbl_info)
        vbox.addWidget(lbl_qr)
        
        dlg.exec_()

    def closeEvent(self, event):
        if hasattr(self, 'sync_server_proc') and self.sync_server_proc:
            self.sync_server_proc.terminate()
            try:
                self.sync_server_proc.wait(timeout=1)
            except Exception:
                self.sync_server_proc.kill()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DashboardApp()
    
    import subprocess
    # Start Sync Server
    try:
        window.sync_server_proc = subprocess.Popen([sys.executable, "sync_server.py"])
    except Exception as e:
        print(f"Failed to start sync server: {e}")
        
    window.show()
    sys.exit(app.exec_())

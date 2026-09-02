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
        
        self.btn_dash = QPushButton("🪟 Dashboard")
        self.btn_dash.setStyleSheet(nav_style)
        self.btn_sch = QPushButton("📅 Schedule")
        self.btn_sch.setStyleSheet(nav_style)
        self.btn_prog = QPushButton("📈 Progress")
        self.btn_prog.setStyleSheet(nav_style)
        self.btn_sync = QPushButton("📱 Mobile Sync")
        self.btn_sync.setStyleSheet(nav_style)
        
        self.sidebar_layout.addWidget(self.btn_dash)
        self.sidebar_layout.addWidget(self.btn_sch)
        self.sidebar_layout.addWidget(self.btn_prog)
        self.sidebar_layout.addWidget(self.btn_sync)
        
        self.btn_dash.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.btn_sch.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.btn_sync.clicked.connect(self.show_sync_qr)
        
        self.sidebar_layout.addStretch()
        
        # Start Session Button
        btn_start = QPushButton("Start Session")
        btn_start.setFixedSize(160, 40)
        btn_start.setStyleSheet("""
            QPushButton {
                background-color: #004D40; color: white; border-radius: 8px; font-weight: bold; font-size: 13px;
            }
            QPushButton:hover { background-color: #00695C; }
        """)
        self.sidebar_layout.addWidget(btn_start, alignment=Qt.AlignCenter)
        
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
        
        self.btn_glass = QPushButton("⚪ Glass Mode")
        self.btn_glass.setFixedSize(100, 30)
        self.btn_glass.setStyleSheet("QPushButton { font-size: 12px; font-weight: bold; border-radius: 15px; background: #E0E0E0; color: #424242; border: none; } QPushButton:hover { background: #D6D6D6; }")
        self.btn_glass.clicked.connect(self.toggle_glass)
        
        top_hbox.addWidget(self.btn_toggle)
        top_hbox.addWidget(self.lbl_hud)
        top_hbox.addStretch()
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
        self.edit_slots, self.edit_days = schedule_manager.load_schedule()
        
        # Clear existing slots in UI
        while self.slots_layout.count() > 1: # keep the add button
            item = self.slots_layout.takeAt(0)
            self.delete_layout_row(item, self.slots_layout)
            
        for s in self.edit_slots:
            self.ui_add_slot(s[0], s[1], s[2])
            
        days_len = len([k for k in self.edit_days.keys() if int(k) <= 31])
        if hasattr(self, '_current_edit_day'):
            del self._current_edit_day
            
        if days_len <= 7 and days_len > 1:
            self.mode_combo.setCurrentIndex(1)
        elif days_len > 7:
            self.mode_combo.setCurrentIndex(2)
        else:
            self.mode_combo.setCurrentIndex(0)
            
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
            final_days = {str(i): [list(t) for t in topics] for i in range(1, 32)}
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
                
        schedule_manager.save_schedule(new_slots, self.edit_days)
        
        # Live update study_schedule variables
        ss.SLOTS = [(s[0], s[1], s[2]) for s in new_slots]
        ss.DAYS = {int(k): [(t[0], t[1]) for t in v] for k, v in self.edit_days.items()}
        
        self.update_ui()
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Success", "Schedule saved successfully!")

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

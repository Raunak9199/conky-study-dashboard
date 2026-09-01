#!/usr/bin/env python3
import sys
import datetime as dt
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QLabel, QPushButton, QHBoxLayout, QFrame, QSizePolicy,
                             QScrollArea, QGridLayout)
from PyQt5.QtGui import QFont, QColor, QPalette, QBrush, QPixmap
from PyQt5.QtCore import QTimer, Qt, QPropertyAnimation, QEasingCurve

import study_schedule as ss

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
        
        btn_dash = QPushButton("🪟 Dashboard")
        btn_dash.setStyleSheet(nav_style)
        btn_sch = QPushButton("📅 Schedule")
        btn_sch.setStyleSheet(nav_style)
        btn_prog = QPushButton("📈 Progress")
        btn_prog.setStyleSheet(nav_style)
        btn_res = QPushButton("📖 Resources")
        btn_res.setStyleSheet(nav_style)
        
        self.sidebar_layout.addWidget(btn_dash)
        self.sidebar_layout.addWidget(btn_sch)
        self.sidebar_layout.addWidget(btn_prog)
        self.sidebar_layout.addWidget(btn_res)
        
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
        
        self.lbl_hud = QLabel("30-DAY STUDY HUD")
        self.lbl_hud.setStyleSheet("color: #004D40; font-weight: bold; font-size: 24px;")
        
        self.lbl_day_top = QLabel("Day 1/30")
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
        self.lbl_day_big = QLabel("DAY 1 / 30")
        self.lbl_day_big.setStyleSheet("color: #E53935; font-weight: bold; font-size: 32px;")
        self.lbl_date = QLabel("Tuesday, 01 Sep 2026")
        self.lbl_date.setStyleSheet("color: #616161; font-size: 12px;")
        
        self.right_layout.addWidget(self.lbl_day_big)
        self.right_layout.addWidget(self.lbl_date)
        self.right_layout.addSpacing(30)
        
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
        
        self.right_layout.addLayout(content_hbox)
        self.right_layout.addStretch()
        
        self.lbl_time = QLabel("TIME 16:36:18")
        self.lbl_time.setStyleSheet("color: #757575; font-weight: bold; font-size: 11px;")
        self.lbl_time.setAlignment(Qt.AlignRight)
        self.right_layout.addWidget(self.lbl_time)
        
        self.main_layout.addWidget(self.right_pane)

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
            
        d = ss.day_number(effective_now.date())
        d = max(1, min(d, 30))
        
        if not is_paused and (1 <= d <= 30):
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
                                f"Day {d}/30 • {start}–{end}\nStart your scheduled session now."
                            ])
                        except Exception:
                            pass
                            
        self.lbl_day_top.setText(f"Day {d}/30")
        self.lbl_day_big.setText(f"DAY {d} / 30")
        self.lbl_date.setText(now.strftime("%A, %d %b %Y"))
        self.lbl_time.setText(f"TIME {now.strftime('%H:%M:%S')}")
        
        # Populate topics cards
        while self.topics_layout.count():
            child = self.topics_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        color_map = {"DSA": "#00897B", "MOBILE": "#43A047", "BANK": "#9C27B0"}
        for cat, topic in ss.DAYS.get(d, []):
            cat_upper = cat.upper()
            col = color_map.get(cat_upper, "#00897B")
            
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: #FFFFFF;
                    border: 1px solid #E0E0E0;
                    border-radius: 4px;
                    border-left: 4px solid {col};
                }}
            """)
            
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(15, 15, 15, 15)
            
            lbl_cat = QLabel(cat_upper)
            lbl_cat.setStyleSheet(f"color: {col}; font-weight: bold; font-size: 13px; border: none;")
            lbl_cat.setFixedWidth(80)
            
            lbl_top = QLabel(topic)
            lbl_top.setStyleSheet("color: #424242; font-size: 13px; border: none;")
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DashboardApp()
    window.show()
    sys.exit(app.exec_())

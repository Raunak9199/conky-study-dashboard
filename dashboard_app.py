#!/usr/bin/env python3
import sys
import datetime as dt
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QLabel, QPushButton, QHBoxLayout, QFrame, QSizePolicy)
from PyQt5.QtGui import QFont, QColor, QPalette, QBrush, QPixmap
from PyQt5.QtCore import QTimer, Qt

# Import all data structures and logic from our existing script
import study_schedule as ss

class DashboardApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("30-Day Study Dashboard")
        self.resize(760, 600)
        
        # Central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(10)
        
        # Background
        self.bg_label = QLabel(self.central_widget)
        self.bg_label.lower()
        self.bg_label.setStyleSheet("background-color: #F8F9FA;")
        # (Optional) If you want the image back, you can set it here:
        # pixmap = QPixmap(str(Path.home() / ".config/conky-study/card.png"))
        # self.bg_label.setPixmap(pixmap)
        
        # Header
        self.lbl_hud = QLabel("30-DAY STUDY HUD")
        self.lbl_hud.setStyleSheet("color: #3949AB; font-weight: bold; font-size: 14px;")
        
        self.lbl_day = QLabel("DAY -- / 30")
        self.lbl_day.setStyleSheet("color: #D81B60; font-weight: bold; font-size: 32px;")
        
        self.lbl_date = QLabel("--")
        self.lbl_date.setStyleSheet("color: #757575; font-size: 14px;")
        
        self.layout.addWidget(self.lbl_hud)
        self.layout.addWidget(self.lbl_day)
        self.layout.addWidget(self.lbl_date)
        
        self.layout.addSpacing(20)
        
        self.lbl_today = QLabel("TODAY")
        self.lbl_today.setStyleSheet("color: #00897B; font-weight: bold; font-size: 18px;")
        self.layout.addWidget(self.lbl_today)
        
        self.topics_frame = QFrame()
        self.topics_layout = QVBoxLayout(self.topics_frame)
        self.topics_layout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(self.topics_frame)
        
        self.layout.addSpacing(20)
        
        self.lbl_now_next = QLabel("")
        self.lbl_now_next.setWordWrap(True)
        self.layout.addWidget(self.lbl_now_next)
        
        self.layout.addSpacing(20)
        
        # Pause Controls
        self.pause_layout = QHBoxLayout()
        self.btn_pause = QPushButton("Pause / Resume")
        self.btn_pause.setFixedSize(150, 40)
        self.btn_pause.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0; border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #D6D6D6; }
        """)
        self.btn_pause.clicked.connect(self.toggle_pause)
        
        self.lbl_pause_status = QLabel("")
        self.lbl_pause_status.setStyleSheet("color: #F4511E; font-size: 16px; font-weight: bold;")
        
        self.pause_layout.addWidget(self.btn_pause)
        self.pause_layout.addWidget(self.lbl_pause_status)
        self.pause_layout.addStretch()
        
        self.layout.addLayout(self.pause_layout)
        
        self.layout.addStretch()
        
        self.lbl_time = QLabel("TIME --:--:--")
        self.lbl_time.setStyleSheet("color: #9E9E9E; font-size: 14px;")
        self.lbl_time.setAlignment(Qt.AlignRight)
        self.layout.addWidget(self.lbl_time)
        
        # Update timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(1000)
        
        self.update_ui()
        
    def resizeEvent(self, event):
        self.bg_label.resize(self.size())
        super().resizeEvent(event)
        
    def toggle_pause(self):
        # We can just call the toggle logic
        now = dt.datetime.now()
        today_str = str(now.date())
        state = ss.get_state()
        was_paused_yesterday = False
        
        if not state or state.get("date") != today_str:
            if state and state.get("is_paused"):
                was_paused_yesterday = True
            state = {"date": today_str, "shift_seconds": 0, "is_paused": False, "pause_start_timestamp": 0}
            
        if was_paused_yesterday:
            pass # just leaves it unpaused
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
            
        self.lbl_day.setText(f"DAY {d} / 30")
        self.lbl_date.setText(now.strftime("%A, %d %b %Y"))
        self.lbl_time.setText(f"TIME  {now.strftime('%H:%M:%S')}")
        
        # Topics
        # Clear old topics
        while self.topics_layout.count():
            child = self.topics_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        color_map = {"DSA": "#1E88E5", "MOBILE": "#43A047", "BANK": "#8E24AA"}
        for cat, topic in ss.DAYS.get(d, []):
            cat_upper = cat.upper()
            col = color_map.get(cat_upper, "#00897B")
            lbl = QLabel(f'<span style="color:{col}; font-weight:bold; font-size:16px;">{cat_upper}</span> &nbsp;&nbsp; <span style="color:#424242; font-size:14px;">{topic}</span>')
            lbl.setWordWrap(True)
            self.topics_layout.addWidget(lbl)
            
        cur = ss.current_slot(effective_now)
        nxt = ss.next_slot(effective_now)
        
        if cur:
            start, end, name, rem = cur
            m = max(0, int(rem.total_seconds() // 60))
            self.lbl_now_next.setText(f'<span style="color:#E53935; font-weight:bold; font-size:18px;">▶ NOW</span> &nbsp;&nbsp; <span style="color:#333333; font-weight:bold; font-size:18px;">{name}</span><br><span style="color:#555555; font-size:14px;">{start} ─ {end}</span> &nbsp;&nbsp; <span style="color:#757575; font-size:14px;">{m//60:02d}h {m%60:02d}m remaining</span>')
        elif nxt:
            start, end, name, until = nxt
            m = max(0, int(until.total_seconds() // 60))
            self.lbl_now_next.setText(f'<span style="color:#F4511E; font-weight:bold; font-size:18px;">⏭ NEXT</span> &nbsp;&nbsp; <span style="color:#333333; font-weight:bold; font-size:18px;">{name}</span><br><span style="color:#555555; font-size:14px;">{start} ─ {end}</span> &nbsp;&nbsp; <span style="color:#757575; font-size:14px;">starts in {m//60:02d}h {m%60:02d}m</span>')
        else:
            self.lbl_now_next.setText('<span style="color:#757575; font-size:16px;">✓ Today\'s scheduled study blocks are complete.</span>')
            
        total_shift = int(shift_seconds + current_pause_duration)
        
        status_text = ""
        if is_paused:
            ph, p_rem = divmod(int(current_pause_duration), 3600)
            pm, ps = divmod(p_rem, 60)
            status_text += f'⏸ PAUSED  <span style="color:#333333;">{ph:02d}:{pm:02d}:{ps:02d}</span><br>'
            
        if total_shift > 0:
            th, t_rem = divmod(total_shift, 3600)
            tm, ts = divmod(t_rem, 60)
            shift_str = ""
            if th > 0: shift_str += f"{th}h "
            if tm > 0 or th > 0: shift_str += f"{tm}m "
            shift_str += f"{ts}s"
            status_text += f'<span style="color:#757575; font-size:14px; font-weight:normal;">Shift today: +{shift_str}</span>'
            
        self.lbl_pause_status.setText(status_text)
        
        if is_paused:
            self.btn_pause.setText("Resume")
            self.btn_pause.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; border-radius: 5px; font-weight: bold; }")
        else:
            self.btn_pause.setText("Pause")
            self.btn_pause.setStyleSheet("QPushButton { background-color: #F44336; color: white; border-radius: 5px; font-weight: bold; }")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DashboardApp()
    window.show()
    sys.exit(app.exec_())

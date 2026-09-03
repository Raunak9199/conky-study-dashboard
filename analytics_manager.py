#!/usr/bin/env python3
import json
import os
import time
import datetime as dt
from pathlib import Path

HISTORY_FILE = Path.home() / ".config/conky-study/progress_history.json"

DEFAULT_HISTORY = {
    "active_session": {
        "is_active": False,
        "start_timestamp": 0.0,
        "subject": "",
        "topic": "",
        "slot_start": "",
        "slot_end": "",
        "pause_accumulated_seconds": 0.0,
        "is_paused": False,
        "pause_start_timestamp": 0.0
    },
    "sessions": [],
    "daily_summaries": {}
}

def load_history():
    if not HISTORY_FILE.exists():
        save_history(DEFAULT_HISTORY)
        return dict(DEFAULT_HISTORY)
    try:
        with open(HISTORY_FILE, "r") as f:
            data = json.load(f)
            if "active_session" not in data:
                data["active_session"] = dict(DEFAULT_HISTORY["active_session"])
            if "sessions" not in data:
                data["sessions"] = []
            if "daily_summaries" not in data:
                data["daily_summaries"] = {}
            return data
    except Exception as e:
        print(f"Error loading progress history: {e}")
        return dict(DEFAULT_HISTORY)

def save_history(data):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving progress history: {e}")

def get_subject_time_today(subject, date_str=None):
    if not date_str:
        date_str = str(dt.date.today())
    data = load_history()
    total_seconds = 0
    total_minutes = 0
    subj_upper = (subject or "").strip().upper()
    for s in data.get("sessions", []):
        if s.get("date") == date_str and s.get("subject", "").strip().upper() == subj_upper:
            sec = s.get("duration_seconds")
            if sec is not None:
                total_seconds += int(sec)
                total_minutes += int(sec // 60)
            else:
                mins = int(s.get("duration_minutes", 0))
                total_seconds += mins * 60
                total_minutes += mins
    return {
        "seconds": total_seconds,
        "minutes": total_minutes
    }

def get_active_session():
    data = load_history()
    sess = data.get("active_session", {})
    if not sess.get("is_active"):
        return {"is_active": False, "elapsed_seconds": 0}
    
    now = time.time()
    start = sess.get("start_timestamp", now)
    pause_acc = sess.get("pause_accumulated_seconds", 0.0)
    
    if sess.get("is_paused"):
        p_start = sess.get("pause_start_timestamp", now)
        elapsed = max(0, int(p_start - start - pause_acc))
    else:
        elapsed = max(0, int(now - start - pause_acc))
        
    subj = sess.get("subject", "General Study")
    prev = get_subject_time_today(subj, str(dt.date.today()))
    prev_seconds = prev["seconds"]
    total_subject_seconds = prev_seconds + elapsed
    
    return {
        "is_active": True,
        "elapsed_seconds": elapsed,
        "previous_subject_seconds": prev_seconds,
        "total_subject_seconds": total_subject_seconds,
        "subject": subj,
        "topic": sess.get("topic", "Self Study"),
        "slot_start": sess.get("slot_start", ""),
        "slot_end": sess.get("slot_end", ""),
        "is_paused": sess.get("is_paused", False)
    }

def start_session(subject="General Study", topic="Self Study", slot_start="", slot_end=""):
    data = load_history()
    now = time.time()
    data["active_session"] = {
        "is_active": True,
        "start_timestamp": now,
        "subject": subject,
        "topic": topic,
        "slot_start": slot_start,
        "slot_end": slot_end,
        "pause_accumulated_seconds": 0.0,
        "is_paused": False,
        "pause_start_timestamp": 0.0
    }
    save_history(data)
    return data["active_session"]

def update_session_pause(is_paused):
    data = load_history()
    sess = data.get("active_session", {})
    if not sess.get("is_active"):
        return
    now = time.time()
    if is_paused and not sess.get("is_paused"):
        sess["is_paused"] = True
        sess["pause_start_timestamp"] = now
    elif not is_paused and sess.get("is_paused"):
        p_start = sess.get("pause_start_timestamp", now)
        duration = max(0.0, now - p_start)
        sess["pause_accumulated_seconds"] = sess.get("pause_accumulated_seconds", 0.0) + duration
        sess["is_paused"] = False
        sess["pause_start_timestamp"] = 0.0
    save_history(data)

def stop_session():
    data = load_history()
    sess = data.get("active_session", {})
    if not sess.get("is_active"):
        return None
    
    now = time.time()
    start = sess.get("start_timestamp", now)
    pause_acc = sess.get("pause_accumulated_seconds", 0.0)
    
    if sess.get("is_paused"):
        p_start = sess.get("pause_start_timestamp", now)
        pause_acc += max(0.0, now - p_start)
        
    actual_seconds = max(0, int(now - start - pause_acc))
    actual_minutes = max(1, round(actual_seconds / 60)) if actual_seconds >= 30 else 0
    
    start_dt = dt.datetime.fromtimestamp(start)
    end_dt = dt.datetime.fromtimestamp(now)
    date_str = str(start_dt.date())
    
    completed_session = {
        "id": f"sess_{int(start)}",
        "date": date_str,
        "start_time": start_dt.strftime("%H:%M"),
        "end_time": end_dt.strftime("%H:%M"),
        "duration_seconds": actual_seconds,
        "duration_minutes": actual_minutes,
        "subject": sess.get("subject", "General Study"),
        "topic": sess.get("topic", "Self Study"),
        "status": "COMPLETED" if actual_minutes >= 5 else "SHORT",
        "pause_seconds": int(pause_acc)
    }
    
    data["sessions"].insert(0, completed_session)
    
    summaries = data.get("daily_summaries", {})
    if date_str not in summaries:
        summaries[date_str] = {
            "actual_minutes": 0,
            "pause_seconds": 0,
            "sessions_count": 0
        }
    summaries[date_str]["actual_minutes"] += actual_minutes
    summaries[date_str]["pause_seconds"] += int(pause_acc)
    summaries[date_str]["sessions_count"] = summaries[date_str].get("sessions_count", 0) + 1
    data["daily_summaries"] = summaries
    
    data["active_session"] = {
        "is_active": False,
        "start_timestamp": 0.0,
        "subject": "",
        "topic": "",
        "slot_start": "",
        "slot_end": "",
        "pause_accumulated_seconds": 0.0,
        "is_paused": False,
        "pause_start_timestamp": 0.0
    }
    save_history(data)
    return completed_session

def seed_history_if_needed(slots=None, days_raw=None):
    data = load_history()
    if data.get("sessions") and len(data["sessions"]) >= 3:
        return
    
    today = dt.date.today()
    default_slots = slots or [
        ("06:00", "08:30", "DSA"),
        ("10:00", "12:30", "Mobile"),
        ("15:45", "17:45", "Bank")
    ]
    
    new_sessions = []
    daily_summaries = {}
    
    for days_ago in range(6, 0, -1):
        target_date = today - dt.timedelta(days=days_ago)
        d_str = str(target_date)
        day_mins = 0
        day_pause = 300 * days_ago
        
        for idx, (s_start, s_end, s_name) in enumerate(default_slots):
            try:
                t1 = dt.datetime.strptime(s_start, "%H:%M")
                t2 = dt.datetime.strptime(s_end, "%H:%M")
                dur = int((t2 - t1).total_seconds() // 60)
            except Exception:
                dur = 120
                
            actual_dur = int(dur * (0.85 + (idx * 0.05)))
            day_mins += actual_dur
            
            sess_entry = {
                "id": f"seed_{d_str}_{idx}",
                "date": d_str,
                "start_time": s_start,
                "end_time": s_end,
                "duration_minutes": actual_dur,
                "subject": s_name,
                "topic": f"Unit {idx+1} Mastery",
                "status": "COMPLETED",
                "pause_seconds": 180 * (idx + 1)
            }
            new_sessions.append(sess_entry)
            
        daily_summaries[d_str] = {
            "actual_minutes": day_mins,
            "pause_seconds": day_pause,
            "sessions_count": len(default_slots)
        }
        
    if data.get("sessions"):
        for s in data["sessions"]:
            if s not in new_sessions:
                new_sessions.insert(0, s)
                
    data["sessions"] = new_sessions
    data["daily_summaries"].update(daily_summaries)
    save_history(data)

def get_metrics(timeframe="7_days", planned_daily_minutes=360):
    data = load_history()
    sessions = data.get("sessions", [])
    today = dt.date.today()
    
    if timeframe == "today":
        start_date = today
        end_date = today
    elif timeframe == "7_days":
        start_date = today - dt.timedelta(days=6)
        end_date = today
    elif timeframe == "30_days":
        start_date = today - dt.timedelta(days=29)
        end_date = today
    else:
        start_date = dt.date(2000, 1, 1)
        end_date = today + dt.timedelta(days=1)
        
    filtered_sessions = []
    for s in sessions:
        try:
            s_date = dt.datetime.strptime(s.get("date", ""), "%Y-%m-%d").date()
            if start_date <= s_date <= end_date:
                filtered_sessions.append(s)
        except Exception:
            pass
            
    total_actual_mins = sum(s.get("duration_minutes", 0) for s in filtered_sessions)
    total_pause_secs = sum(s.get("pause_seconds", 0) for s in filtered_sessions)
    
    days_count = max(1, (end_date - start_date).days + 1)
    if timeframe == "all" and filtered_sessions:
        unique_dates = {s["date"] for s in filtered_sessions}
        days_count = max(1, len(unique_dates))
        
    total_planned_mins = planned_daily_minutes * days_count
    
    completion_rate_pct = min(100.0, round((total_actual_mins / total_planned_mins * 100) if total_planned_mins > 0 else 0, 1))
    
    focus_secs = total_actual_mins * 60
    total_time_secs = focus_secs + total_pause_secs
    focus_efficiency_pct = round((focus_secs / total_time_secs * 100) if total_time_secs > 0 else 100.0, 1)
    
    active_dates = set()
    for s in sessions:
        if s.get("duration_minutes", 0) >= 15:
            active_dates.add(s.get("date"))
            
    streak = 0
    check_date = today
    if str(check_date) not in active_dates:
        check_date = today - dt.timedelta(days=1)
        
    while str(check_date) in active_dates:
        streak += 1
        check_date -= dt.timedelta(days=1)
        
    subject_time = {}
    for s in filtered_sessions:
        subj = s.get("subject", "Other").upper()
        subject_time[subj] = subject_time.get(subj, 0) + s.get("duration_minutes", 0)
        
    color_map = {
        "DSA": "#00897B",
        "MOBILE": "#43A047",
        "BANK": "#9C27B0",
        "ENGLISH": "#1E88E5",
        "REASONING": "#FB8C00",
        "MATH": "#E53935"
    }
    fallback_colors = ["#00ACC1", "#3949AB", "#D81B60", "#F4511E", "#7CB342"]
    
    subject_breakdown = []
    for idx, (subj, mins) in enumerate(sorted(subject_time.items(), key=lambda x: x[1], reverse=True)):
        pct = round((mins / total_actual_mins * 100) if total_actual_mins > 0 else 0, 1)
        col = color_map.get(subj, fallback_colors[idx % len(fallback_colors)])
        subject_breakdown.append({
            "subject": subj,
            "minutes": mins,
            "hours_str": f"{mins // 60}h {mins % 60}m",
            "pct": pct,
            "color": col
        })
        
    chart_days = 7 if timeframe in ["today", "7_days"] else (30 if timeframe == "30_days" else min(14, days_count))
    daily_chart = []
    
    for i in range(chart_days - 1, -1, -1):
        cur_d = today - dt.timedelta(days=i)
        cur_d_str = str(cur_d)
        d_sessions = [s for s in sessions if s.get("date") == cur_d_str]
        day_actual_mins = sum(s.get("duration_minutes", 0) for s in d_sessions)
        
        daily_chart.append({
            "date": cur_d_str,
            "label": cur_d.strftime("%a %d"),
            "planned_hours": round(planned_daily_minutes / 60, 1),
            "actual_hours": round(day_actual_mins / 60, 1)
        })
        
    return {
        "timeframe": timeframe,
        "total_actual_minutes": total_actual_mins,
        "total_actual_hours_str": f"{total_actual_mins // 60}h {total_actual_mins % 60}m",
        "total_planned_hours_str": f"{total_planned_mins // 60}h {total_planned_mins % 60}m",
        "completion_rate_pct": completion_rate_pct,
        "streak_days": streak,
        "focus_efficiency_pct": focus_efficiency_pct,
        "total_pause_minutes": int(total_pause_secs // 60),
        "subject_breakdown": subject_breakdown,
        "daily_chart": daily_chart,
        "sessions": filtered_sessions
    }

def export_csv(filepath):
    data = load_history()
    sessions = data.get("sessions", [])
    try:
        with open(filepath, "w") as f:
            f.write("Date,Start Time,End Time,Duration (Minutes),Subject,Topic,Status,Pause (Seconds)\n")
            for s in sessions:
                f.write(f'"{s.get("date")}","{s.get("start_time")}","{s.get("end_time")}",{s.get("duration_minutes")},"{s.get("subject")}","{s.get("topic")}","{s.get("status")}",{s.get("pause_seconds")}\n')
        return True, "Exported successfully to CSV"
    except Exception as e:
        return False, str(e)

def export_json(filepath):
    data = load_history()
    try:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        return True, "Exported successfully to JSON"
    except Exception as e:
        return False, str(e)

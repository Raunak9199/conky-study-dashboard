import json
from pathlib import Path

SCHEDULE_FILE = Path.home() / ".config/conky-study/schedule.json"

DEFAULT_SLOTS = []

DEFAULT_DAYS = {}

def load_schedule():
    if not SCHEDULE_FILE.exists():
        save_schedule(DEFAULT_SLOTS, DEFAULT_DAYS)
        return DEFAULT_SLOTS, DEFAULT_DAYS

    try:
        with open(SCHEDULE_FILE, "r") as f:
            data = json.load(f)
            
        slots = data.get("slots", DEFAULT_SLOTS)
        days = data.get("days", DEFAULT_DAYS)
        
        # Ensure slots is a list of tuples (it's parsed as a list of lists by json)
        formatted_slots = [(s[0], s[1], s[2]) for s in slots]
        
        # Ensure days has tuples inside its lists
        formatted_days = {}
        for day_num, topics in days.items():
            formatted_days[str(day_num)] = [(t[0], t[1]) for t in topics]
            
        return formatted_slots, formatted_days
    except Exception as e:
        print(f"Error loading schedule: {e}")
        return DEFAULT_SLOTS, DEFAULT_DAYS

def save_schedule(slots, days):
    SCHEDULE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SCHEDULE_FILE, "w") as f:
        json.dump({"slots": slots, "days": days}, f, indent=2)

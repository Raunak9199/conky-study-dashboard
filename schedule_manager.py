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

PROFILES_FILE = Path.home() / ".config/conky-study/profiles.json"

def load_profiles():
    if not PROFILES_FILE.exists():
        # Migrate existing schedule to a Default Profile
        slots, days = load_schedule()
        
        # Determine implicit mode based on days
        mode = 0 # Daily by default
        if len(days) == 7: mode = 1
        elif len(days) > 7: mode = 2
        
        default_data = {
            "active_profile": "Default Plan",
            "profiles": {
                "Default Plan": {
                    "mode": mode,
                    "slots": slots,
                    "days": days
                }
            }
        }
        save_profiles(default_data)
        return default_data

    try:
        with open(PROFILES_FILE, "r") as f:
            data = json.load(f)
            
        # Ensure correct formatting just in case
        for pname, pdata in data.get("profiles", {}).items():
            s = pdata.get("slots", [])
            d = pdata.get("days", {})
            pdata["slots"] = [(x[0], x[1], x[2]) for x in s]
            new_d = {}
            for k, v in d.items():
                new_d[str(k)] = [(t[0], t[1]) for t in v]
            pdata["days"] = new_d
            
        return data
    except Exception as e:
        print(f"Error loading profiles: {e}")
        return {"active_profile": "Default Plan", "profiles": {"Default Plan": {"mode": 1, "slots": [], "days": {}}}}

def save_profiles(data):
    PROFILES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROFILES_FILE, "w") as f:
        json.dump(data, f, indent=2)

#!/usr/bin/env python3
import json
import os
import datetime as dt
import time
from pathlib import Path

STATE_FILE = Path.home() / ".config/conky-study/state.json"

def load_state():
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return None

def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def main():
    now = dt.datetime.now()
    today_str = str(now.date())
    
    state = load_state()
    
    was_paused_yesterday = False
    
    # Initialize or Reset state if missing or if it's a new day
    if not state or state.get("date") != today_str:
        if state and state.get("is_paused"):
            was_paused_yesterday = True
            
        state = {
            "date": today_str,
            "shift_seconds": 0,
            "is_paused": False,
            "pause_start_timestamp": 0
        }
        
    if was_paused_yesterday:
        # We crossed midnight while paused. 
        # The act of toggling now should just leave it unpaused (resumed for the new day).
        print("Crossed midnight while paused. Resetting to unpaused for the new day.")
    elif state["is_paused"]:
        # We are resuming
        pause_duration = now.timestamp() - state["pause_start_timestamp"]
        if pause_duration < 0: 
            pause_duration = 0
            
        state["shift_seconds"] += pause_duration
        state["is_paused"] = False
        state["pause_start_timestamp"] = 0
        print(f"Resumed. Total shift for today is now {int(state['shift_seconds'])} seconds.")
    else:
        # We are pausing
        state["is_paused"] = True
        state["pause_start_timestamp"] = now.timestamp()
        print("Paused.")
        
    save_state(state)

if __name__ == "__main__":
    main()

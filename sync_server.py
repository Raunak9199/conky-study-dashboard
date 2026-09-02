#!/usr/bin/env python3
import json
import os
import secrets
import socketserver
import threading
import time
from datetime import datetime, timezone, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# Config Paths
CONFIG_DIR = Path.home() / ".config/conky-study"
SYNC_CONFIG_FILE = CONFIG_DIR / "sync_config.json"
STATE_FILE = CONFIG_DIR / "state.json"
SCHEDULE_FILE = CONFIG_DIR / "schedule.json"

class SyncConfig:
    def __init__(self):
        self.port = 8080
        self.token = ""
        self.load_or_create()

    def load_or_create(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        if SYNC_CONFIG_FILE.exists():
            try:
                with open(SYNC_CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    self.port = data.get("port", 8080)
                    self.token = data.get("token", "")
            except Exception:
                pass
        
        if not self.token:
            self.token = secrets.token_hex(16)
            self.save()

    def save(self):
        with open(SYNC_CONFIG_FILE, "w") as f:
            json.dump({"port": self.port, "token": self.token}, f, indent=2)

config = SyncConfig()

class SyncRequestHandler(BaseHTTPRequestHandler):
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
        
    def do_GET(self):
        if self.path == '/api/status':
            self.send_json({"status": "ok", "version": 1})
            return
            
        if self.path == '/api/sync':
            # Check Token
            client_token = self.headers.get('Sync-Token')
            if not client_token or client_token != config.token:
                self.send_json({"error": "Unauthorized"}, 401)
                return
                
            try:
                # Load State
                state = {}
                if STATE_FILE.exists():
                    with open(STATE_FILE, "r") as f:
                        state = json.load(f)
                
                # Load Schedule
                schedule = {"slots": [], "days": {}}
                if SCHEDULE_FILE.exists():
                    with open(SCHEDULE_FILE, "r") as f:
                        schedule = json.load(f)
                        
                # Format payload
                is_paused = state.get("is_paused", False)
                pause_start = state.get("pause_start_timestamp", 0)
                shift_seconds = state.get("shift_seconds", 0)
                
                # Calculate Day Number natively
                date_str = state.get("date", datetime.now().strftime("%Y-%m-%d"))
                
                total_days = max([int(k) for k in schedule.get("days", {}).keys()] + [1])
                
                import study_schedule as ss
                raw_d = ss.day_number(datetime.fromtimestamp(state.get("pause_start_timestamp", datetime.now().timestamp())).date() if is_paused else datetime.now().date())
                # Actually simpler: just use datetime.now().date() assuming shift_seconds doesn't push us over midnight.
                # To be exact with dashboard:
                now = datetime.now()
                if is_paused:
                    effective_now = datetime.fromtimestamp(pause_start) - timedelta(seconds=shift_seconds)
                else:
                    effective_now = now - timedelta(seconds=shift_seconds)
                
                raw_d = ss.day_number(effective_now.date())
                
                if total_days == 7:
                    d_display = ((raw_d - 1) % 7) + 1
                else:
                    d_display = raw_d
                    if d_display > 30: d_display = 30
                    if d_display < 1: d_display = 1
                    
                payload = {
                    "protocolVersion": 1,
                    "scheduleVersion": 1,
                    "stateVersion": 1,
                    "date": date_str,
                    "dayNumber": d_display,
                    "schedule": schedule,
                    "state": {
                        "isPaused": is_paused,
                        "pauseStartedAt": datetime.fromtimestamp(pause_start, tz=timezone.utc).isoformat() if is_paused and pause_start else None,
                        "totalPauseSeconds": shift_seconds
                    },
                    "serverTime": datetime.now(timezone.utc).isoformat(),
                    "updatedAt": datetime.now(timezone.utc).isoformat(),
                    "updatedBy": "desktop"
                }
                
                self.send_json(payload)
            except Exception as e:
                self.send_json({"error": str(e)}, 500)
            return

        self.send_json({"error": "Not Found"}, 404)

    def log_message(self, format, *args):
        # Suppress standard logging to prevent console flooding
        pass

def run_server():
    server_address = ('0.0.0.0', config.port)
    httpd = HTTPServer(server_address, SyncRequestHandler)
    print(f"[Sync Server] Running on port {config.port} | Token: {config.token}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == '__main__':
    run_server()

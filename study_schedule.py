#!/usr/bin/env python3
import datetime as dt
import os
import subprocess
import sys
from pathlib import Path

START_DATE = dt.date(2026, 9, 1)

# Times follow the timetable we discussed:
# 08:00 DSA (1.5h)
# 09:30 Mobile (2h)
# 11:30 Break (30m)
# 12:00 Bank Quant + Reasoning (3h)
# 15:00 Lunch/Break (45m)
# 15:45 Bank English + Computer/GA (2h)
# 17:45 Current Affairs + revision (45m)
SLOTS = [
    ("08:00", "09:30", "DSA"),
    ("09:30", "11:30", "Mobile Development"),
    ("12:00", "15:00", "Bank — Quant + Reasoning"),
    ("15:45", "17:45", "Bank — English + Computer/GA"),
    ("17:45", "18:30", "Current Affairs + Revision"),
]

DAYS = {
1: [
    ("DSA", "Time/space complexity, arrays basics, 5 easy problems"),
    ("Mobile", "Kotlin core: null safety, data classes, sealed classes, scope functions"),
    ("Bank", "Quant: number series, simplification, approximation | Reasoning: coding-decoding | English: grammar + vocab"),
],
2: [
    ("DSA", "Strings: patterns, in-place manipulation, 5 problems"),
    ("Mobile", "Kotlin coroutines: suspend, launch vs async, structured concurrency"),
    ("Bank", "Quant: percentage, profit & loss | Reasoning: blood relations | English: RC technique"),
],
3: [
    ("DSA", "Two pointers & sliding window, 5 problems"),
    ("Mobile", "Kotlin Flow vs StateFlow vs SharedFlow"),
    ("Bank", "Quant: ratio-proportion, average | Reasoning: direction sense | English: cloze test"),
],
4: [
    ("DSA", "Hashing: HashMap/HashSet, 5 problems"),
    ("Mobile", "Flutter fundamentals: widget tree, Stateless/Stateful, BuildContext, keys"),
    ("Bank", "Quant: SI/CI, mixture-alligation | Reasoning: syllogism | English: error spotting"),
],
5: [
    ("DSA", "Recursion basics + 3 backtracking problems"),
    ("Mobile", "Flutter rendering pipeline: widget/element/render tree, why const matters"),
    ("Bank", "Quant: time-speed-distance, time & work | Reasoning: seating arrangement | English: sentence improvement"),
],
6: [
    ("DSA", "Sorting overview + binary search, 5 problems"),
    ("Mobile", "Compose basics: recomposition, remember/mutableStateOf, state hoisting"),
    ("Bank", "Quant: DI intro | Reasoning: puzzles intro | English: para jumbles"),
],
7: [
    ("DSA", "Weekly mock: 25 mixed easy problems + review"),
    ("Mobile", "Rapid-fire Q&A + flashcards"),
    ("Bank", "Full sectional mock: Quant + Reasoning + English + error analysis"),
],
8: [
    ("DSA", "Linked list: reverse, cycle detection, merge, 5 problems"),
    ("Mobile", "Compose side-effects: LaunchedEffect, DisposableEffect, derivedStateOf, SideEffect"),
    ("Bank", "Quant: quadratic equations, number system | Reasoning: coded inequality | English: fill blanks"),
],
9: [
    ("DSA", "Stacks: valid parentheses, monotonic stack, 5 problems"),
    ("Mobile", "Compose performance: stability, recomposition, @Stable/@Immutable"),
    ("Bank", "Quant: mensuration 2D | Reasoning: input-output | English: vocabulary"),
],
10: [
    ("DSA", "Queues + deque, 5 problems"),
    ("Mobile", "Flutter state management: Provider vs Riverpod vs Bloc"),
    ("Bank", "Quant: mensuration 3D | Reasoning: floor puzzles | Computer awareness"),
],
11: [
    ("DSA", "Binary trees: traversals, 5 problems"),
    ("Mobile", "KMP fundamentals: expect/actual, shared module, platform-specific"),
    ("Bank", "DI sets | Reasoning: box puzzles | RBI basics"),
],
12: [
    ("DSA", "BST: operations, height, diameter, LCA, 5 problems"),
    ("Mobile", "Compose Multiplatform vs Flutter: trade-offs"),
    ("Bank", "DI practice 2 | Reasoning: circular seating | Monetary policy"),
],
13: [
    ("DSA", "Heaps/priority queue, 5 problems"),
    ("Mobile", "Koin DI in KMP — explain Lumora setup"),
    ("Bank", "Probability, P&C intro | English banking comprehension"),
],
14: [
    ("DSA", "Weekly medium mixed mock"),
    ("Mobile", "Mock Q&A: state hoisting, recomposition, KMP sharing"),
    ("Bank", "Full sectional mock + detailed error log"),
],
15: [
    ("DSA", "Graphs: BFS/DFS, 5 problems"),
    ("Mobile", "Navigation: Voyager vs Navigation Compose vs Flutter Navigator 2.0"),
    ("Bank", "Advanced DI puzzles | Reasoning puzzle-cum-DI hybrid"),
],
16: [
    ("DSA", "Topological sort, union-find, 5 problems"),
    ("Mobile", "Networking: Ktor/Retrofit, errors, offline-first"),
    ("Bank", "Quant + Reasoning speed drill"),
],
17: [
    ("DSA", "1D DP: fibonacci, climbing stairs, 5 problems"),
    ("Mobile", "Room/SQLDelight, caching strategy"),
    ("Bank", "Static GK: schemes, banking history, committees"),
],
18: [
    ("DSA", "DP: knapsack, subsequence, 5 problems"),
    ("Mobile", "Clean architecture: MVVM/MVI, layering, testability"),
    ("Bank", "Computer awareness: shortcuts, generations, networking"),
],
19: [
    ("DSA", "Greedy algorithms, 5 problems"),
    ("Mobile", "Design systems + animation; explain Midnight Glass"),
    ("Bank", "English full mock, 30 min timed"),
],
20: [
    ("DSA", "Bit manipulation + math tricks, 5 problems"),
    ("Mobile", "Mock interview: 5 rapid Flutter/Kotlin/KMP questions"),
    ("Bank", "Reasoning full mock, 20 min timed"),
],
21: [
    ("DSA", "Mixed medium mock + weak-topic revision"),
    ("Mobile", "One-page project cheat-sheet: Lumora, VigilBooks, Peblo"),
    ("Bank", "Full prelims-pattern mock + deep error analysis"),
],
22: [
    ("DSA", "Mixed arrays/strings/hashing timed"),
    ("Mobile", "Revise Kotlin coroutines + Flow"),
    ("Bank", "Quant sectional mock — speed focus"),
],
23: [
    ("DSA", "Mixed trees/graphs timed"),
    ("Mobile", "Revise Compose recomposition + performance"),
    ("Bank", "Reasoning sectional mock — speed focus"),
],
24: [
    ("DSA", "Mixed DP/greedy timed"),
    ("Mobile", "Revise KMP architecture + DI"),
    ("Bank", "English + Computer Aptitude sectional mock"),
],
25: [
    ("DSA", "Weak-topic drilling from error log"),
    ("Mobile", "45-min mock technical interview"),
    ("Bank", "Static GK + banking awareness revision"),
],
26: [
    ("DSA", "Weak-topic drilling continued"),
    ("Mobile", "Resume walkthrough + mobile system-design-lite"),
    ("Bank", "Full mains-pattern mock with GA + Computer"),
],
27: [
    ("DSA", "90-min contest: 4–5 medium problems"),
    ("Mobile", "Behavioral prep: STAR answers using real projects"),
    ("Bank", "Error analysis + formula/shortcut revision"),
],
28: [
    ("DSA", "Weekly mock + full revision"),
    ("Mobile", "Final Kotlin/Compose/KMP flashcard pass"),
    ("Bank", "Full prelims-pattern mock, strict timing"),
],
29: [
    ("DSA", "Light revision: re-solve 10 missed problems"),
    ("Mobile", "Light revision: project cheat-sheet"),
    ("Bank", "Full mock under exam-day conditions"),
],
30: [
    ("DSA", "Rest + light notes"),
    ("Mobile", "Rest + light notes"),
    ("Bank", "Final formulas, GK flashcards, exam-day strategy"),
],
}

def day_number(today):
    return (today - START_DATE).days + 1

def parse(t, date):
    h, m = map(int, t.split(":"))
    return dt.datetime.combine(date, dt.time(h, m))

def current_slot(now):
    for start, end, name in SLOTS:
        a, b = parse(start, now.date()), parse(end, now.date())
        if a <= now < b:
            return (start, end, name, b - now)
    return None

def next_slot(now):
    for start, end, name in SLOTS:
        a = parse(start, now.date())
        if a > now:
            return (start, end, name, a - now)
    return None

import json
import fcntl

STATE_FILE = Path.home() / ".config/conky-study/state.json"
LOCK_FILE = Path.home() / ".config/conky-study/state.lock"

def get_state():
    state = None
    with open(LOCK_FILE, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if STATE_FILE.exists():
            with open(STATE_FILE, "r") as f:
                try: state = json.load(f)
                except Exception: pass
        fcntl.flock(lock, fcntl.LOCK_UN)
    return state

def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOCK_FILE, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
        fcntl.flock(lock, fcntl.LOCK_UN)

def display():
    now = dt.datetime.now()
    today_str = str(now.date())
    
    state = get_state()
    # Reset if missing or new day
    if not state or state.get("date") != today_str:
        state = {
            "date": today_str,
            "shift_seconds": 0,
            "is_paused": False,
            "pause_start_timestamp": 0
        }
        save_state(state)
        
    shift_seconds = state.get("shift_seconds", 0)
    is_paused = state.get("is_paused", False)
    
    if is_paused:
        pause_start = state.get("pause_start_timestamp", now.timestamp())
        effective_now = dt.datetime.fromtimestamp(pause_start) - dt.timedelta(seconds=shift_seconds)
        current_pause_duration = now.timestamp() - pause_start
    else:
        effective_now = now - dt.timedelta(seconds=shift_seconds)
        current_pause_duration = 0

    d = day_number(effective_now.date())
    if d < 1:
        d = 1
    if d > 30:
        d = 30

    # Notification Logic
    if not is_paused and (1 <= d <= 30):
        for start, end, name in SLOTS:
            target = parse(start, effective_now.date())
            # Trigger if effective time has crossed the scheduled start
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
        
    topics = DAYS.get(d, [])
    cur = current_slot(effective_now)
    nxt = next_slot(effective_now)

    # Determine size mode
    size_file = Path.home() / ".config/conky-study/size"
    mode = "large"
    if size_file.exists():
        mode = size_file.read_text().strip()
        
    scale = 0.65 if mode == "small" else 1.0
    def s(val): return max(1, int(val * scale))
    def fs(val): return max(8, int(val * scale)) # min font size 8

    lines = []
    
    def add_line(text, voff=0, xoff=50):
        prefix = f"${{voffset {s(voff)}}}" if voff else ""
        lines.append(f"{prefix}${{goto {s(xoff)}}}{text}")

    add_line("${color #3949AB}${font DejaVu Sans:bold:size=%d}30-DAY STUDY HUD${font}${color}" % fs(10), voff=40)
    add_line("${color #D81B60}${font DejaVu Sans:bold:size=%d}DAY %%d / 30${font}${color}" % fs(22) % d)
    add_line("${color #757575}%s${color}" % now.strftime("%A, %d %b %Y"), voff=5)
    
    add_line("", voff=15)
    add_line("${color #00897B}${font DejaVu Sans:bold:size=%d}TODAY${font}${color}" % fs(12))
    
    color_map = {
        "DSA": "#1E88E5",
        "MOBILE": "#43A047",
        "BANK": "#8E24AA"
    }
    
    for category, topic in topics:
        cat_upper = category.upper()
        col = color_map.get(cat_upper, "#00897B")
        if mode == "small" and len(topic) > 45:
            topic = topic[:42] + "..."
        add_line("${color %s}${font DejaVu Sans:bold:size=%d}%s${font}${color}  ${color #424242}%s${color}" % (col, fs(11), cat_upper, topic), voff=8)

    add_line("", voff=15)
    if cur:
        start, end, name, remaining = cur
        mins = max(0, int(remaining.total_seconds() // 60))
        add_line("${color #E53935}${font DejaVu Sans:bold:size=%d}▶ NOW${font}${color}   ${color #333333}${font DejaVu Sans:bold:size=%d}%s${font}${color}" % (fs(12), fs(12), name))
        add_line("${color #555555}%s ─ %s${color}" % (start, end), voff=4, xoff=70)
        add_line("${color #757575}%02dh %02dm remaining${color}" % (mins//60, mins%60), voff=2, xoff=70)
    elif nxt:
        start, end, name, until = nxt
        mins = max(0, int(until.total_seconds() // 60))
        add_line("${color #F4511E}${font DejaVu Sans:bold:size=%d}⏭ NEXT${color}  ${color #333333}${font DejaVu Sans:bold:size=%d}%s${font}${color}" % (fs(12), fs(12), name))
        add_line("${color #555555}%s ─ %s${color}" % (start, end), voff=4, xoff=70)
        add_line("${color #757575}starts in %02dh %02dm${color}" % (mins//60, mins%60), voff=2, xoff=70)
    else:
        add_line("${color #757575}✓ Today's scheduled study blocks are complete.${color}")

    # Display Pause Status
    add_line("", voff=15)
    total_shift = int(shift_seconds + current_pause_duration)
    
    if is_paused:
        ph, p_rem = divmod(int(current_pause_duration), 3600)
        pm, ps = divmod(p_rem, 60)
        add_line("${color #F4511E}${font DejaVu Sans:bold:size=%d}⏸ PAUSED${font}${color}  ${color #333333}%02d:%02d:%02d${color}" % (fs(12), ph, pm, ps))
    
    if total_shift > 0:
        th, t_rem = divmod(total_shift, 3600)
        tm, ts = divmod(t_rem, 60)
        shift_str = ""
        if th > 0:
            shift_str += f"{th}h "
        if tm > 0 or th > 0:
            shift_str += f"{tm}m "
        shift_str += f"{ts}s"
        add_line("${color #757575}Shift today: +%s${color}" % shift_str, voff=4 if is_paused else 0)

    add_line("", voff=20)
    add_line("${color #9E9E9E}${font DejaVu Sans:size=%d}TIME  ${time %%H:%%M:%%S}${font}${color}" % fs(10))
    
    print("\n".join(lines))

if __name__ == "__main__":
    display()

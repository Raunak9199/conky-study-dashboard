import json
from pathlib import Path

SCHEDULE_FILE = Path.home() / ".config/conky-study/schedule.json"

DEFAULT_SLOTS = [
    ("08:00", "09:30", "DSA"),
    ("09:30", "11:30", "Mobile Development"),
    ("12:00", "15:00", "Bank — Quant + Reasoning"),
    ("15:45", "17:45", "Bank — English + Computer/GA"),
    ("17:45", "18:30", "Current Affairs + Revision"),
]

DEFAULT_DAYS = {
"1": [
    ("DSA", "Time/space complexity, arrays basics, 5 easy problems"),
    ("Mobile", "Kotlin core: null safety, data classes, sealed classes, scope functions"),
    ("Bank", "Quant: number series, simplification, approximation | Reasoning: coding-decoding | English: grammar + vocab"),
],
"2": [
    ("DSA", "Strings: patterns, in-place manipulation, 5 problems"),
    ("Mobile", "Kotlin coroutines: suspend, launch vs async, structured concurrency"),
    ("Bank", "Quant: percentage, profit & loss | Reasoning: blood relations | English: RC technique"),
],
"3": [
    ("DSA", "Two pointers & sliding window, 5 problems"),
    ("Mobile", "Kotlin Flow vs StateFlow vs SharedFlow"),
    ("Bank", "Quant: ratio-proportion, average | Reasoning: direction sense | English: cloze test"),
],
"4": [
    ("DSA", "Hashing: HashMap/HashSet, 5 problems"),
    ("Mobile", "Flutter fundamentals: widget tree, Stateless/Stateful, BuildContext, keys"),
    ("Bank", "Quant: SI/CI, mixture-alligation | Reasoning: syllogism | English: error spotting"),
],
"5": [
    ("DSA", "Recursion basics + 3 backtracking problems"),
    ("Mobile", "Flutter rendering pipeline: widget/element/render tree, why const matters"),
    ("Bank", "Quant: time-speed-distance, time & work | Reasoning: seating arrangement | English: sentence improvement"),
],
"6": [
    ("DSA", "Sorting overview + binary search, 5 problems"),
    ("Mobile", "Compose basics: recomposition, remember/mutableStateOf, state hoisting"),
    ("Bank", "Quant: DI intro | Reasoning: puzzles intro | English: para jumbles"),
],
"7": [
    ("DSA", "Weekly mock: 25 mixed easy problems + review"),
    ("Mobile", "Rapid-fire Q&A + flashcards"),
    ("Bank", "Full sectional mock: Quant + Reasoning + English + error analysis"),
],
"8": [
    ("DSA", "Linked list: reverse, cycle detection, merge, 5 problems"),
    ("Mobile", "Compose side-effects: LaunchedEffect, DisposableEffect, derivedStateOf, SideEffect"),
    ("Bank", "Quant: quadratic equations, number system | Reasoning: coded inequality | English: fill blanks"),
],
"9": [
    ("DSA", "Stacks: valid parentheses, monotonic stack, 5 problems"),
    ("Mobile", "Compose performance: stability, recomposition, @Stable/@Immutable"),
    ("Bank", "Quant: mensuration 2D | Reasoning: input-output | English: vocabulary"),
],
"10": [
    ("DSA", "Queues + deque, 5 problems"),
    ("Mobile", "Flutter state management: Provider vs Riverpod vs Bloc"),
    ("Bank", "Quant: mensuration 3D | Reasoning: floor puzzles | Computer awareness"),
],
"11": [
    ("DSA", "Binary trees: traversals, 5 problems"),
    ("Mobile", "KMP fundamentals: expect/actual, shared module, platform-specific"),
    ("Bank", "DI sets | Reasoning: box puzzles | RBI basics"),
],
"12": [
    ("DSA", "BST: operations, height, diameter, LCA, 5 problems"),
    ("Mobile", "Compose Multiplatform vs Flutter: trade-offs"),
    ("Bank", "DI practice 2 | Reasoning: circular seating | Monetary policy"),
],
"13": [
    ("DSA", "Heaps/priority queue, 5 problems"),
    ("Mobile", "Koin DI in KMP — explain Lumora setup"),
    ("Bank", "Probability, P&C intro | English banking comprehension"),
],
"14": [
    ("DSA", "Weekly medium mixed mock"),
    ("Mobile", "Mock Q&A: state hoisting, recomposition, KMP sharing"),
    ("Bank", "Full sectional mock + detailed error log"),
],
"15": [
    ("DSA", "Graphs: BFS/DFS, 5 problems"),
    ("Mobile", "Navigation: Voyager vs Navigation Compose vs Flutter Navigator 2.0"),
    ("Bank", "Advanced DI puzzles | Reasoning puzzle-cum-DI hybrid"),
],
"16": [
    ("DSA", "Topological sort, union-find, 5 problems"),
    ("Mobile", "Networking: Ktor/Retrofit, errors, offline-first"),
    ("Bank", "Quant + Reasoning speed drill"),
],
"17": [
    ("DSA", "1D DP: fibonacci, climbing stairs, 5 problems"),
    ("Mobile", "Room/SQLDelight, caching strategy"),
    ("Bank", "Static GK: schemes, banking history, committees"),
],
"18": [
    ("DSA", "DP: knapsack, subsequence, 5 problems"),
    ("Mobile", "Clean architecture: MVVM/MVI, layering, testability"),
    ("Bank", "Computer awareness: shortcuts, generations, networking"),
],
"19": [
    ("DSA", "Greedy algorithms, 5 problems"),
    ("Mobile", "Design systems + animation; explain Midnight Glass"),
    ("Bank", "English full mock, 30 min timed"),
],
"20": [
    ("DSA", "Bit manipulation + math tricks, 5 problems"),
    ("Mobile", "Mock interview: 5 rapid Flutter/Kotlin/KMP questions"),
    ("Bank", "Reasoning full mock, 20 min timed"),
],
"21": [
    ("DSA", "Mixed medium mock + weak-topic revision"),
    ("Mobile", "One-page project cheat-sheet: Lumora, VigilBooks, Peblo"),
    ("Bank", "Full prelims-pattern mock + deep error analysis"),
],
"22": [
    ("DSA", "Mixed arrays/strings/hashing timed"),
    ("Mobile", "Revise Kotlin coroutines + Flow"),
    ("Bank", "Quant sectional mock — speed focus"),
],
"23": [
    ("DSA", "Mixed trees/graphs timed"),
    ("Mobile", "Revise Compose recomposition + performance"),
    ("Bank", "Reasoning sectional mock — speed focus"),
],
"24": [
    ("DSA", "Mixed DP/greedy timed"),
    ("Mobile", "Revise KMP architecture + DI"),
    ("Bank", "English + Computer Aptitude sectional mock"),
],
"25": [
    ("DSA", "Weak-topic drilling from error log"),
    ("Mobile", "45-min mock technical interview"),
    ("Bank", "Static GK + banking awareness revision"),
],
"26": [
    ("DSA", "Weak-topic drilling continued"),
    ("Mobile", "Resume walkthrough + mobile system-design-lite"),
    ("Bank", "Full mains-pattern mock with GA + Computer"),
],
"27": [
    ("DSA", "90-min contest: 4–5 medium problems"),
    ("Mobile", "Behavioral prep: STAR answers using real projects"),
    ("Bank", "Error analysis + formula/shortcut revision"),
],
"28": [
    ("DSA", "Weekly mock + full revision"),
    ("Mobile", "Final Kotlin/Compose/KMP flashcard pass"),
    ("Bank", "Full prelims-pattern mock, strict timing"),
],
"29": [
    ("DSA", "Light revision: re-solve 10 missed problems"),
    ("Mobile", "Light revision: project cheat-sheet"),
    ("Bank", "Full mock under exam-day conditions"),
],
"30": [
    ("DSA", "Rest + light notes"),
    ("Mobile", "Rest + light notes"),
    ("Bank", "Final formulas, GK flashcards, exam-day strategy"),
],
}

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

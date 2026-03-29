---
name: gui-act
description: "Execute GUI actions — click, type, send messages. Includes detection, memory matching, component saving, execution, diff, and transition recording as one unified flow."
---

# Act — Detect, Match, Save, Execute, Diff, Record

This is the core action loop. Every action follows this flow. Do not skip any part.

---

## The Complete Action Flow

```
┌──────────────────────────────────────────────────────────────────┐
│ 1. DETECT:  Screenshot → OCR + GPA-GUI-Detector                 │
│ 2. MATCH:   Compare detected elements against saved memory       │
│ 3. SAVE COMPONENTS: New elements → crop + save + label           │
│             ↑ Save BEFORE clicking — even if click fails,        │
│               components are in memory for next time             │
│ 4. DECIDE & EXECUTE: Pick target → click/type at coordinates     │
│ 5. DETECT AGAIN: Screenshot → OCR (only if action might fail)    │
│ 6. DIFF:    Compare before vs after OCR texts                    │
│ 7. SAVE TRANSITION: Record state change to transitions.json      │
└──────────────────────────────────────────────────────────────────┘
```

**Key change from previous version:** Component saving (step 3) happens BEFORE execution (step 4), not after. This means:
- Even if the click fails, you've already saved what you learned about the current page
- The next visit to this page can use template matching immediately
- You never "lose" detected components by skipping saves after action

---

## Automation API

Two platform-independent functions handle ALL saving automatically.
They work on any screenshot (local Mac, remote VM, downloaded image).
**The LLM does NOT manually crop or write JSON files** — call these functions instead.

### `learn_from_screenshot(img_path, domain, app_name, page_name)`
Runs GPA-GUI-Detector + OCR on a screenshot, crops all components, saves to memory.
Call this ONCE per page state you observe (step 3).

```python
from scripts.app_memory import learn_from_screenshot

# After taking a screenshot and before clicking anything:
result = learn_from_screenshot(
    img_path="/path/to/screenshot.png",
    domain="united.com",           # None for non-browser apps
    app_name="chromium",           # Browser or app name
    page_name="homepage",          # Human-readable page label
)
# Note: Scale (detection→click) is computed dynamically by detect_all()
# via refresh_screen_info(). No manual retina flag needed.
# result = {"saved": 42, "new": 38, "components": ["Booking", "Travel_info", ...]}
```

### `record_page_transition(before_img, after_img, click_label, click_pos, domain, app_name)`
Runs OCR on before/after screenshots, computes diff, saves state transition.
Call this ONCE per click (step 7).

```python
from scripts.app_memory import record_page_transition

# After clicking and taking a new screenshot:
result = record_page_transition(
    before_img_path="/path/to/before.png",
    after_img_path="/path/to/after.png",
    click_label="Travel_info",     # What was clicked
    click_pos=(779, 187),          # Where it was clicked (click space)
    domain="united.com",
    app_name="chromium",
)
# result = {"appeared": [...], "disappeared": [...], "from": "...", "to": "..."}
```

---

## Step-by-Step Walkthrough

### Step 1: DETECT (before action)

Take a screenshot. Run OCR + GPA-GUI-Detector on it:

```python
from scripts.ui_detector import detect_text, detect_icons

ocr_results = detect_text(screenshot_path)
# [{"label": "Travel info", "cx": 779, "cy": 187, ...}, ...]

icon_results = detect_icons(screenshot_path)
# [{"cx": 849, "cy": 783, "confidence": 0.85, "label": null, ...}, ...]
```

For remote VMs: download screenshot to Mac first, then run detection locally.

### Step 2: MATCH against saved memory

Check if components are already in memory:

```python
from scripts.app_memory import match_all_components

matched = match_all_components(app_name, img=screenshot_path, threshold=0.8)
# {"travel_info_btn": (661, 188, 0.95), "book_btn": (490, 283, 0.92), ...}
```

**If components match:** coordinates come from template matching (most precise). Skip to step 4.
**If components are NEW:** coordinates come from OCR/GPA-GUI-Detector. Continue to step 3.

### Step 3: SAVE COMPONENTS (before clicking!)

**Call `learn_from_screenshot()` to save all detected components automatically.**

```python
from scripts.app_memory import learn_from_screenshot

learn_from_screenshot(
    img_path=screenshot_path,
    domain="united.com",
    page_name="homepage",
)
```

This is automated — no manual cropping, no manual JSON editing.
The function handles: detection, filtering, naming, dedup, cropping, saving.

### Step 4: DECIDE & EXECUTE

Pick the target element, get coordinates from detection (step 1) or memory (step 2), click.

**Local Mac apps:**
```python
from scripts.app_memory import click_and_record, click_component

# Known component (template matched):
click_component(app_name, component_name)

# New element (detected coordinates):
click_and_record(app_name, "Travel_info", 779, 187)
```

**Remote VMs (OSWorld):**
```python
# Send click via VM API
import pyautogui
pyautogui.click(779, 187)
```

**CRITICAL:** Always use `gui_action.py click` (with appropriate --remote if needed), never raw platform-specific calls.

### Step 5: DETECT AGAIN (if needed)

Take another screenshot after the action. Run OCR to verify the result.

This step is needed when:
- You need to verify the click worked (page changed)
- You need to find the next element to click
- The action might have failed (wrong element, popup appeared)

For simple keyboard shortcuts (Ctrl+L, typing text), you can skip this step.

### Step 6: DIFF

Compare OCR texts from before and after screenshots:
- **Appeared:** new text = new page/state
- **Disappeared:** gone text = left previous state
- **Persisted:** unchanged text = persistent UI (nav bar, etc.)

This is done automatically by `record_page_transition()` in step 7.

### Step 7: SAVE TRANSITION

**Call `record_page_transition()` to save the state change automatically.**

```python
from scripts.app_memory import record_page_transition

record_page_transition(
    before_img_path=before_screenshot,
    after_img_path=after_screenshot,
    click_label="Travel_info",
    click_pos=(779, 187),
    domain="united.com",
)
```

This automatically: runs OCR on both images, diffs them, saves states + transition to `states.json` / `transitions.json`.

---

## Concrete Example: OSWorld Task

```python
from scripts.ui_detector import ImageContext, detect_all

# Step 1: Screenshot + detect (returns IMAGE PIXEL coords)
# Download VM screenshot to Mac, then detect locally
elements = detect_all("screenshot.png")  # returns image pixel coords

# Step 2: Match — first visit, no memory yet → all new

# Step 3: Save components BEFORE clicking
learn_from_screenshot("screenshot.png", domain="united.com", page_name="homepage")
# → 42 components saved automatically (crops use pixel coords directly)

# Step 4: Click — convert pixel coords to click-space
ctx = ImageContext.remote()  # VM screenshot = 1:1
click_x, click_y = ctx.image_to_click(779, 187)  # → (779, 187) for remote
pyautogui.click(click_x, click_y)  # via VM API

# Step 5: Detect again
new_elements = detect_all("new_screenshot.png")

# Step 6+7: Diff + save transition
record_page_transition("screenshot.png", "new_screenshot.png",
                       click_label="Travel_info", click_pos=(779, 187),
                       domain="united.com")
# → appeared: ["Bags", "United app", ...], disappeared: [...]
# → transition saved to transitions.json
```

---

## The Payoff

**First visit to united.com:**
```
Screenshot → GPA-GUI-Detector + OCR → learn_from_screenshot() saves everything
→ click → record_page_transition() saves state change
→ Total: ~5 seconds of detection, everything in memory
```

**Second visit to united.com:**
```
Screenshot → template match against saved components → instant recognition
→ "I see Travel_info at (661, 188), Bags at (485, 324)"
→ click directly. No GPA. No image tool. Fast.
```

---

## How Coordinates Work

`detect_all()` returns **image pixel coordinates**. Use `ImageContext` to convert to click-space:

```python
from scripts.ui_detector import ImageContext

# Choose context based on screenshot source:
ctx = ImageContext.remote()              # VM / remote screenshots
ctx = ImageContext.mac_fullscreen()      # Mac fullscreen
ctx = ImageContext.mac_window(wx, wy)    # Mac window crop

# Convert for clicking:
click_x, click_y = ctx.image_to_click(el["cx"], el["cy"])
```

| Source | Method | Returns |
|---|---|---|
| Saved component | Template matching (`match_all_components`) | Click-space (already converted) |
| Text element | OCR via `detect_all()` | **Image pixels** → use `ctx.image_to_click()` |
| UI component | GPA via `detect_all()` | **Image pixels** → use `ctx.image_to_click()` |
| **image tool** | **NEVER for coordinates** | **Understanding only** |

## Not Found?

Component not matching (conf < 0.8) = not on screen in its saved form.
**Don't lower threshold.** Run `learn_from_screenshot()` on current page to discover what IS on screen.

## Input Methods (gui_action.py)

All GUI operations go through `gui_action.py`. Add `--remote URL` for remote targets.

```bash
gui_action.py click X Y                   # Left click
gui_action.py right_click X Y             # Right click
gui_action.py type "text"                 # Type text (handles special chars)
gui_action.py key enter                   # Single key (enter/tab/escape...)
gui_action.py shortcut ctrl+s             # Key combination
gui_action.py screenshot /tmp/s.png       # Screenshot
gui_action.py focus "window title"        # Focus window
gui_action.py close "window title"        # Close window
gui_action.py list_windows                # List all windows
# Remote: add --remote http://IP:PORT
```

---

## REPORT — Track Task Performance

Call gui-report at the START and END of every gui-agent workflow (not per-click, per-task).

```bash
TRACKER="python3 ~/.openclaw/workspace/skills/gui-agent/skills/gui-report/scripts/tracker.py"

# At task start (get context from session_status):
$TRACKER start --task "OSWorld Task 25: United Airlines baggage calculator" --context 94000

# During task: image_calls need manual tick (clicks/screenshots auto-tick)
$TRACKER tick image_calls

# At task end (get context again from session_status):
$TRACKER report --context 120000
```

See `gui-report/SKILL.md` for details.

## ⛔ ABSOLUTE RULES — Coordinate Sources

```
✅ ALLOWED coordinate sources:
   1. GPA-GUI-Detector (detect_icons) → bounding box center
   2. OCR (detect_text) → text bounding box center
   3. Template matching → saved component position

❌ FORBIDDEN:
   - LLM/vision model guessing coordinates
   - Hardcoded pixel positions from memory or documentation
   - Coordinates from image tool analysis (image tool = understanding ONLY)
```

Every click: screenshot → detect → get coordinates from detection → click. No exceptions.

## Key Principles

1. **Vision-driven** — screenshot → detect → match → click
2. **Coordinates from detection only** — image tool is for understanding, NOT coordinates
3. **Not found = not on screen** — re-learn, don't guess
4. **State graph drives navigation** — each click records a transition
5. **First time: screenshot + image. Repeat: detection only** — saves tokens
6. **Paste > Type** for CJK text
7. **Integer logical coordinates** — use detect_to_click() for Retina
8. **ALWAYS save to memory** — every GUI operation saves to memory/apps/

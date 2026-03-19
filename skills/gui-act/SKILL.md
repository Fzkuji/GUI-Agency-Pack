---
name: gui-act
description: "Execute GUI actions — click, type, send messages. Auto-verification via state detection."
---

# Act — Execute and Verify

## How coordinates work

| Content type | Method | Precision |
|---|---|---|
| Saved component | Template matching (`click_component`) | Pixel-precise (conf≈1.0) |
| Dynamic content (menu, search result) | YOLO/OCR detection (`detect_all`) | Bbox-precise |
| Unknown element | Learn first, then template match | Pixel-precise |

**`image` tool = understanding only.** Never ask it for coordinates.

## Clicking a Known Component

```bash
python3 scripts/agent.py click --app AppName --component ButtonName
```

Or directly:
```python
from app_memory import click_component
ok, msg = click_component(app_name, component_name)
```

`click_component` does everything automatically:
1. Screenshot (one, shared)
2. Detect visible components before click
3. Template match target → precise coordinates
4. Click
5. Detect visible components after click
6. Verify state (first time: learn, repeat: compare)
7. Record state transition
8. Report visible components

## Clicking Dynamic Content

For elements without saved templates (menus, search results, chat messages):

```bash
# Step 1: Detect with YOLO+OCR
# Step 2: Find target coordinates
# Step 3: Click AND record state transition:
python3 scripts/app_memory.py click_at --app AppName --label "button_text" --x 977 --y 653
```

Or in Python:
```python
from app_memory import click_and_record
ok, msg, visible = click_and_record(app_name, "button_text", x, y)
```

**CRITICAL: Never use raw `click_at()` from platform_input directly.**
Always use `click_and_record()` or `click_component()` so the state graph gets updated.
Every click must build the graph — otherwise the agent learns nothing from its actions.

OCR returns logical coordinates. YOLO returns physical (÷2 for logical).

## Not Found?

Component not matching (conf < 0.8) means it's **not on screen** in its saved form:
- Different visual state (selected vs unselected tab)
- Different page
- App not in foreground

**Don't lower the threshold.** Re-learn current state to discover what IS on screen.

## Input Methods (platform_input.py)

```python
click_at(x, y)                    # Left click
mouse_right_click(x, y)           # Right click (context menus)
paste_text("中文")                 # Clipboard + Cmd+V (CJK safe)
type_text("hello")                # Direct typing (ASCII only)
key_press("return")               # Single key
key_combo("command", "v")         # Key combination
set_clipboard("text")             # Set clipboard
get_clipboard()                   # Read clipboard
screenshot("/tmp/check.png")      # Full screen capture
```

## Sending Messages

No hardcoded flow. First time: follow steps manually with screenshot verification at each step. After success: save as workflow for replay.

Generic steps:
1. Find contact (search or scroll) — use YOLO/OCR detection for coordinates
2. Verify chat header shows correct contact — `image` tool for understanding
3. Click input field — template match or YOLO detection
4. Paste message — `paste_text()`
5. Verify text in input — `image` tool or `get_clipboard()`
6. Send — `key_press("return")`
7. Verify sent — `image` tool

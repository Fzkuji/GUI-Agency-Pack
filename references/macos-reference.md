# macOS Reference

## Coordinate System

- **Screen**: top-left origin (0,0), logical pixels (Retina physical ÷ 2)
- **Window**: relative to window's top-left corner
- **Retina**: screenshots are 2x physical pixels; divide by 2 for logical
- **cliclick**: uses screen logical pixels, integer only
- **Formula**: `screen_x = window_x + relative_x`, `screen_y = window_y + relative_y`

## Window Management

```bash
# Get window bounds
osascript -e 'tell application "System Events" to tell process "AppName" to return {position, size} of window 1'

# Get window ID (for screencapture)
# Use Swift CGWindowListCopyWindowInfo — see ui_detector.py

# Capture window only
screencapture -x -l <windowID> output.png

# Activate app
osascript -e 'tell application "AppName" to activate'

# Resize window
osascript -e 'tell application "System Events" to tell process "AppName" to set size of window 1 to {900, 650}'
```

## Input Methods

```bash
# Click (logical screen coords, integers only)
/opt/homebrew/bin/cliclick c:<x>,<y>

# Type ASCII only
cliclick t:"text"

# Paste CJK/special chars (MUST set LANG)
LANG=en_US.UTF-8 pbcopy <<< "中文"
osascript -e 'tell app "System Events" to keystroke "v" using command down'

# Key press
cliclick kp:return    # valid: return, esc, tab, delete, space, arrow-*, f1-f16

# Keyboard shortcut
osascript -e 'tell app "System Events" to keystroke "v" using command down'
```

## Browser Input Quirks

- **Autocomplete fields** (e.g. 12306): typing alone is NOT enough. Must click dropdown suggestion.
  - Flow: click input → type pinyin → wait for dropdown → click suggestion
- **Chinese input**: System IME interferes with website autocomplete.
  - Solution: switch to English input, type pinyin abbreviation, let website autocomplete handle it
- **Cmd+V in web forms**: May garble text. Use `cliclick t:text` for ASCII/pinyin.
- **Date pickers**: Usually need to click calendar UI, not type date string.

## Detection Stack

| Detector | Finds | Speed | Best for |
|----------|-------|-------|----------|
| **GPA-GUI-Detector (YOLO)** | Icons, buttons, UI elements | 0.3s | Any app's buttons |
| **Apple Vision OCR** | Text (Chinese + English) | 1.6s | Labels, menus, content |
| **Template Match** | Previously seen components | 0.3s | Known elements (conf=1.0) |

Priority: Template Match → OCR → YOLO → LLM (cheapest first)

## Scripts

| Script | Purpose |
|--------|---------|
| `agent.py` | **Unified entry point** — all GUI ops go through here |
| `ui_detector.py` | Detection engine (YOLO + OCR) |
| `app_memory.py` | Per-app visual memory (learn/detect/click/verify) |
| `gui_agent.py` | Legacy task executor |
| `template_match.py` | Template matching utilities |

All scripts use venv: `source ~/gui-agent-env/bin/activate`

## Setup (New Machine)

```bash
git clone https://github.com/Fzkuji/GUIClaw.git
cd GUIClaw
bash scripts/setup.sh
```

Installs: cliclick, Python 3.12, PyTorch, ultralytics, OpenCV, GPA-GUI-Detector (40MB)

Grant **Accessibility permissions**: System Settings → Privacy → Accessibility → Add Terminal/OpenClaw

## Path Conventions

- Venv: `~/gui-agent-env/`
- Model: `~/GPA-GUI-Detector/model.pt`
- Memory: `<skill-dir>/memory/apps/<appname>/`
- All paths use `os.path.expanduser("~")`, NOT hardcoded usernames

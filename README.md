<div align="center">
  <img src="assets/banner.png" alt="GUIClaw" width="100%" />

  <h1>🦞 GUIClaw</h1>

  <p>
    <strong>See your screen. Learn every button. Click precisely.</strong>
    <br />
    Vision-based desktop automation skills for <a href="https://github.com/openclaw/openclaw">OpenClaw</a> agents on macOS.
  </p>

  <p>
    <a href="#-quick-start"><img src="https://img.shields.io/badge/Quick_Start-blue?style=for-the-badge" /></a>
    <a href="#-openclaw-integration"><img src="https://img.shields.io/badge/🦞_OpenClaw-red?style=for-the-badge" /></a>
    <a href="https://discord.com/invite/clawd"><img src="https://img.shields.io/badge/Discord-7289da?style=for-the-badge&logo=discord&logoColor=white" /></a>
  </p>

  <p>
    <img src="https://img.shields.io/badge/Platform-macOS_Apple_Silicon-black?logo=apple" />
    <img src="https://img.shields.io/badge/Detection-GPA_GUI_Detector-green" />
    <img src="https://img.shields.io/badge/OCR-Apple_Vision-blue" />
    <img src="https://img.shields.io/badge/License-MIT-yellow" />
  </p>
</div>

---

## 🔥 News

- **[03/17/2026]** v0.2.0 — Workflow-based revise, event-driven polling, mandatory operation protocol (observe→verify→act→confirm), per-app visual memory with auto-cleanup.
- **[03/16/2026]** v0.1.0 — GPA-GUI-Detector integration, Apple Vision OCR, template matching, browser automation, per-site memory.
- **[03/10/2026]** v0.0.1 — Initial release: WeChat/Discord/Telegram automation, app profiles, fuzzy app matching.

## 💬 What It Looks Like

> **You**: "Send a message to John in WeChat saying see you tomorrow"

```
OBSERVE  → Screenshot, identify current state
           ├── Current app: Finder (not WeChat)
           └── Action: need to switch to WeChat

REVISE   → Check memory for WeChat
           ├── Learned before? Yes (24 components)
           └── Workflow "send_message" known? Yes → use existing memory

NAVIGATE → Find contact "John"
           ├── Template match sidebar → not visible
           ├── Template match search_bar_icon → found (conf=0.96) → click
           ├── Paste "John" into search field (clipboard → Cmd+V)
           └── OCR search results → found → click

VERIFY   → Confirm correct chat opened
           ├── OCR chat header → "John" ✅
           └── Wrong contact? → ABORT

ACT      → Send message
           ├── Click input field (template match)
           ├── Paste "see you tomorrow" (clipboard → Cmd+V)
           └── Press Enter

CONFIRM  → Verify message sent
           ├── OCR chat area → "see you tomorrow" visible ✅
           └── Done
```

<details>
<summary>📖 More examples</summary>

### "Scan my Mac for malware"

```
OBSERVE  → Screenshot → CleanMyMac X not in foreground → activate
           ├── Get main window bounds (largest window, skip status bar panels)
           └── OCR window content → identify current page state

REVISE   → Check memory for CleanMyMac X
           ├── "malware_removal" workflow known? Yes
           └── Use existing memory, skip full re-learn

NAVIGATE → Click "Malware Removal" in sidebar
           ├── Find element in window (exact match, filter by window bounds)
           └── Verify page switched (OCR confirms new page content)

ACT      → Click "Scan" button
           ├── Find "Scan" (exact match, bottom position — prevents matching "Deep Scan")
           └── Click → scan starts

POLL     → Wait for completion (event-driven, no fixed sleep)
           ├── Every 2s: screenshot → OCR check for "No threats"
           └── Target found → proceed immediately

CONFIRM  → "No threats found" ✅
```

### "Check if my GPU training is still running"

```
OBSERVE  → Screenshot → Chrome is open
           └── Identify target: JupyterLab tab

NAVIGATE → Find JupyterLab tab in browser
           ├── OCR tab bar or use bookmarks
           └── Click to switch

EXPLORE  → Multiple terminal tabs visible
           ├── Screenshot terminal area
           ├── LLM vision analysis → identify which tab has nvitop
           └── Click the correct tab

READ     → Screenshot terminal content
           ├── LLM reads GPU utilization table
           └── Report: "8 GPUs, 7 at 100% — experiment running" ✅
```

### "Kill GlobalProtect via Activity Monitor"

```
OBSERVE  → Screenshot current state
           └── Neither GlobalProtect nor Activity Monitor in foreground

ACT      → Launch both apps
           ├── open -a "GlobalProtect"
           └── open -a "Activity Monitor"

EXPLORE  → Screenshot Activity Monitor window
           ├── LLM vision → "Network tab active, search field empty at top-right"
           └── Decide: click search field first

ACT      → Search for process
           ├── Click search field (identified by explore)
           ├── Paste "GlobalProtect" (clipboard → Cmd+V, never cliclick type)
           └── Wait for filter results

VERIFY   → Process found in list → select it

ACT      → Kill process
           ├── Click stop button (X) in toolbar
           └── Confirmation dialog appears

VERIFY   → Click "Force Quit"

CONFIRM  → Screenshot → process list empty → terminated ✅
```

</details>

## 🚀 Quick Start

```bash
# 1. Clone & install
git clone https://github.com/Fzkuji/GUIClaw.git
cd GUIClaw
bash scripts/setup.sh

# 2. Grant accessibility permissions
# System Settings → Privacy & Security → Accessibility → Add Terminal / OpenClaw

# 3. Use with OpenClaw (recommended) or any LLM agent
# Add to ~/.openclaw/openclaw.json:
#   "skills": { "entries": { "gui-agent": { "enabled": true } } }
# Then just chat: "Send a message to John in WeChat"
```

## 🧠 How It Works

```
User: "Clean my Mac"
         │
         ▼
┌─────────────────┐
│ 0. OBSERVE      │ Screenshot → OCR → What app? What page? What state?
└────────┬────────┘
         ▼
┌─────────────────┐     ┌──────────────────────┐
│ In memory?      ├─No─▶│ DETECT (YOLO + OCR)  │
└───┬─────────────┘     │ Save to memory       │
    │ Yes               └──────────┬───────────┘
    ▼                              │
┌────────────┐                     │
│ Template   │◀────────────────────┘
│ Match 0.3s │
└─────┬──────┘
      ▼
┌─────────────────┐
│ 1. VERIFY       │ Is this the right element? In the right window?
└────────┬────────┘
         ▼
┌─────────────────┐
│ 2. ACT          │ Click / type / send
└────────┬────────┘
         ▼
┌─────────────────┐
│ 3. CONFIRM      │ Did it work? Right state now?
└─────────────────┘
```

### Learn Once, Match Forever

**First time** — YOLO detects everything (~4 seconds):
```
🔍 YOLO: 43 icons    📝 OCR: 34 text elements    🔗 → 24 fixed UI components saved
```

**Every time after** — instant template match (~0.3 seconds):
```
✅ search_bar_icon (202,70) conf=1.0
✅ emoji_button (354,530) conf=1.0
✅ sidebar_contacts (85,214) conf=1.0
```

## 🔍 Detection Stack

| Detector | Speed | Finds | Why |
|----------|-------|-------|-----|
| **[GPA-GUI-Detector](https://huggingface.co/Salesforce/GPA-GUI-Detector)** | 0.3s | Icons, buttons | Finds gray-on-gray icons others miss |
| **Apple Vision OCR** | 1.6s | Text (CN + EN) | Best Chinese OCR, pixel-accurate |
| **Template Match** | 0.3s | Known components | 100% accuracy after first learn |

## 📁 App Visual Memory

Each app gets its own visual memory. Different pages/workflows are learned separately.

```
memory/apps/
├── wechat/
│   ├── profile.json              # 24 named components
│   ├── icons/
│   │   ├── sidebar_contacts.png
│   │   ├── emoji_button.png
│   │   └── search_bar_icon.png
│   └── pages/
│       └── main_annotated.jpg
├── cleanmymac_x/
│   ├── icons/
│   └── pages/
│       ├── smart_scan/
│       └── malware_removal/      # Different workflow = different page
├── google_chrome/
│   ├── icons/
│   └── sites/                    # Per-website memory
│       ├── 12306_cn/
│       └── github_com/
```

## ⚠️ Safety & Protocol

Every action follows a mandatory protocol — **written into the code, not just documentation**:

| Step | What | Why |
|------|------|-----|
| **OBSERVE** | Screenshot + OCR before any action | Know what state you're in |
| **VERIFY** | Element exists? Correct window? Exact text match? | Prevent clicking wrong thing |
| **ACT** | Click / type / send | Execute |
| **CONFIRM** | Screenshot again, check state changed | Verify it worked |

**Safety rules enforced in code:**
- ✅ Verify chat recipient before sending messages (OCR header)
- ✅ Window-bounded operations (no clicking outside target app)
- ✅ Exact text matching (prevents "Scan" matching "Deep Scan")
- ✅ Largest-window detection (skips status bar panels)

## 🗂️ Project Structure

```
GUIClaw/
├── SKILL.md                 # 🧠 Agent reads this first
├── scripts/
│   ├── setup.sh             # 🔧 One-command setup
│   ├── agent.py             # 🎯 Unified entry point (observe→verify→act→confirm)
│   ├── ui_detector.py       # 🔍 Detection engine (YOLO + OCR)
│   ├── app_memory.py        # 🧠 Visual memory (learn/detect/click/verify)
│   ├── gui_agent.py         # 🖱️ Task executor
│   └── template_match.py    # 🎯 Template matching
├── actions/_actions.yaml    # 📋 Atomic operations
├── scenes/                  # 📝 Per-app workflows
├── apps/                    # 📱 App UI configs
├── docs/core.md             # 📚 Lessons learned
├── memory/                  # 🔒 Visual memory (gitignored)
└── requirements.txt
```

## 📦 Requirements

- **macOS** with Apple Silicon (M1/M2/M3/M4)
- **Accessibility permissions**: System Settings → Privacy → Accessibility
- Everything else installed by `bash scripts/setup.sh`

## 🤝 Ecosystem

| | |
|---|---|
| 🦞 **[OpenClaw](https://github.com/openclaw/openclaw)** | AI assistant framework — loads GUIClaw as a skill |
| 🔍 **[GPA-GUI-Detector](https://huggingface.co/Salesforce/GPA-GUI-Detector)** | Salesforce YOLO model for UI detection |
| 💬 **[Discord Community](https://discord.com/invite/clawd)** | Get help, share feedback |

## 📄 License

MIT

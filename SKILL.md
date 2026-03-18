---
name: gui-agent
description: "Control desktop GUI applications on macOS using visual detection, template matching, and cliclick. Use when asked to operate, click, type, or interact with any desktop application. NOT for web-only tasks (use browser tool) or simple file operations."
---

# GUI Agent Skill

You ARE the agent loop: Observe → Decide → Act → Verify.

## HARD RULES (NEVER SKIP)

1. **ALL GUI ops go through `agent.py`** — NO raw `screencapture` + `image` tool as a workaround
2. **App not in memory? → `agent.py learn` FIRST** — no exceptions, no "I'll just OCR it manually"
3. **If agent.py fails → FIX agent.py** — don't bypass the memory system
4. **Coordinates come from detection tools** (template match, OCR, YOLO) — NEVER from LLM guessing
5. **Every interaction saves to memory** — no "one-off" operations that leave nothing behind
6. **BANNED: `screencapture` + `image` tool for GUI tasks** — this bypasses visual memory, wastes tokens, saves nothing. Only allowed for debugging agent.py itself.

## Quick Reference: agent.py

```bash
source ~/gui-agent-env/bin/activate

agent.py learn --app AppName          # Learn new app (YOLO + OCR → save components)
agent.py detect --app AppName         # Detect + match known components
agent.py click --app AppName --component ButtonName  # Click a known component
agent.py list --app AppName           # List all known components
agent.py open --app AppName           # Open/activate an app
agent.py read_screen --app AppName    # Screenshot + OCR
agent.py wait_for --app AppName --component X  # Poll until component appears
agent.py workflows --app AppName      # List saved workflows
agent.py all_workflows                # List all workflows (app + meta)
agent.py cleanup --app AppName        # Remove duplicates + unlabeled
agent.py send_message --app AppName --contact "Name" --message "text"
```

## Core Protocol (every GUI task)

```
STEP -1: INTENT MATCH    → Match request to saved workflows (semantic, not string)
STEP  0: OBSERVE          → Screenshot + identify state (NEVER skip, NEVER assume)
         ↓
         App in memory?
         YES → template match (0.3s) → click
         NO  → agent.py learn → save components → then proceed
         ↓
STEP  1: VERIFY           → Correct element? Correct window? Inside bounds?
STEP  2: ACT              → Click / Type / Send (via agent.py, not raw cliclick)
STEP  3: CONFIRM          → Screenshot → expected change happened?
         NO  → back to OBSERVE
         YES → continue or REPORT
         ↓
REPORT:  ⏱ time | 📊 +tokens (before→after) | 🔧 actions taken
```

## Auto-Learn Rule

- App not in `memory/apps/<appname>/`? → `learn` automatically before operating
- New page/state in known app? → `learn --page <pagename>` to add it
- After any observation, new unlabeled icons? → identify immediately
- **Your responsibility. Don't wait for user to ask.**

## Key Principles

1. **Memory first, detect second** — template match before YOLO+OCR
2. **Relative coordinates** — never hardcode screen positions
3. **Verify before acting** — especially before sending messages
4. **Template > OCR > YOLO > LLM** — cheapest method first
5. **Paste > Type** for CJK text (LANG=en_US.UTF-8)
6. **Learn incrementally** — save new components after each interaction
7. **Window-based, not screen-based** — operate within target window only
8. **Integer coordinates only** — cliclick requires integers

## Detailed References (read when needed)

- **[Memory System](references/memory-system.md)** — Profile structure, learn flow, component filtering, cleanup rules, browser two-layer memory. Read when: learning a new app, debugging memory issues, understanding what to save/skip.

- **[Operation Protocol](references/operation-protocol.md)** — Full step-by-step protocol, safety rules, workflow save/execute, meta-workflows, pre-send verification. Read when: sending messages, saving workflows, understanding the verification chain.

- **[macOS Reference](references/macos-reference.md)** — Coordinate system, window management, cliclick commands, input methods, detection stack, setup guide. Read when: coordinates are wrong, input isn't working, setting up a new machine.

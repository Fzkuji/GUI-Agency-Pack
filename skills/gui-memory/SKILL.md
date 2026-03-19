---
name: gui-memory
description: "Visual memory system — app profiles, components, states, transitions."
---

# Memory — Visual Memory System

## Profile Structure (profile.json)

Each app has one profile containing:

```json
{
  "app": "WeChat",
  "components": {
    "chat_tab": {"type": "icon", "rel_x": 29, "rel_y": 128, "icon_file": "chat_tab.png"},
    "宋文涛": {"type": "text", "rel_x": 137, "rel_y": 156, "icon_file": "宋文涛.png"}
  },
  "states": {
    "click:chat_tab": {"visible": [...], "appeared": [...], "disappeared": [...]},
    "click:contacts_tab": {"visible": [...]}
  },
  "transitions": [
    {"from": "click:chat_tab", "click": "contacts_tab", "to": "click:contacts_tab", "count": 2},
    {"from": "click:contacts_tab", "click": "chat_tab", "to": "click:chat_tab", "count": 3}
  ]
}
```

## Components

- Saved as template images (cropped from full-screen screenshot)
- Matched via template matching on full screen (conf ≥ 0.8)
- Full-screen match + window bounds validation = no false matches from other apps
- conf < 0.8 → not on screen, don't lower threshold, re-learn instead

## States

- Identified by which components are visible (F1 score matching)
- `click:X` state = what the screen looks like after clicking component X
- Each state stores: `visible` (all components), `appeared` (new ones), `disappeared` (gone ones)

## Transitions

- Recorded automatically by `click_component`
- Each transition: `(from_state, click_component, to_state)`
- Builds a state graph for BFS navigation
- `find_path(app, from, to)` returns shortest click sequence

## Directory Structure

```
memory/apps/<appname>/
├── profile.json              # Components + states + transitions
└── components/               # Template images
    ├── chat_tab.png
    ├── search_bar.png
    └── ...
```

## CRUD Operations

```bash
# Learn (detect + save)
python3 scripts/agent.py learn --app AppName

# List components
python3 scripts/agent.py list --app AppName

# Rename unlabeled
python3 scripts/app_memory.py rename --app AppName --old unlabeled_xxx --new actual_name

# Delete (privacy, dynamic content)
python3 scripts/app_memory.py delete --app AppName --component name

# View state graph
python3 scripts/app_memory.py transitions --app AppName

# Find navigation path
python3 scripts/app_memory.py path --app AppName --component from_state --contact to_state
```

## Cleanup Rules

- Unlabeled components → identify with `image` tool → rename or delete
- Dynamic content (chat messages, timestamps) → delete to prevent bloat
- Privacy-sensitive (avatars with faces) → delete unless functionally needed
- macOS traffic light buttons → auto-injected as sys_close/sys_minimize/sys_fullscreen

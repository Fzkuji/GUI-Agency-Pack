---
name: gui-workflow
description: "State graph navigation, workflow recording and replay."
---

# Workflow — State Graph Navigation

## Core Concept

Every click records a **pending** state transition: `(from_state, click_component, to_state)`.
Pending transitions are **NOT saved to profile** until the workflow succeeds.

```
EXPLORING (trial & error) → pending transitions accumulate
  ↓ workflow succeeds
CONFIRM → transitions saved to profile permanently
  ↓ workflow fails
DISCARD → pending transitions thrown away
```

## Workflow Lifecycle

### 1. First Time (Exploring)

The agent doesn't know the path. Every click is trial and error:

```python
# Each click records a PENDING transition
click_and_record(app, "Scan", x, y)      # pending: unknown → click:Scan
click_and_record(app, "Run", x, y)        # pending: click:Scan → click:Run
click_and_record(app, "Quit_All", x, y)   # pending: click:Run → click:Quit_All

# Workflow succeeded! Commit all transitions
confirm_transitions(app)                   # → saved to profile.json

# OR workflow failed — discard everything
discard_transitions(app)                   # → nothing saved, graph stays clean
```

### 2. Save Workflow

Only after the FULL workflow succeeds end-to-end:

```python
save_workflow(app, "smart_cleanup", target_state="click:cleanup_done",
             description="Smart Scan → Run → handle Quit dialog → done")
```

### 3. Replay (Known Path)

```python
run_workflow(app, "smart_cleanup")
# Detects current state → find_path to target → execute clicks
# All clicks are already known, auto-verified, no screenshots needed
```

## CLI Commands

```bash
# View committed transitions
python3 scripts/app_memory.py transitions --app "CleanMyMac X"

# View pending (uncommitted) transitions
python3 scripts/app_memory.py pending --app "CleanMyMac X"

# Commit after success
python3 scripts/app_memory.py commit --app "CleanMyMac X"

# Discard after failure
python3 scripts/app_memory.py discard --app "CleanMyMac X"

# Find path between states
python3 scripts/app_memory.py path --app "CleanMyMac X" --component from_state --contact to_state
```

## Navigation

```python
from app_memory import find_path, identify_state_by_components, _detect_visible_components

visible = _detect_visible_components(app_name)
current, f1 = identify_state_by_components(app_name, visible)
path = find_path(app_name, current, target_state)
for click, next_state in path:
    click_component(app_name, click)
```

## Rules

1. **Never save transitions from failed/aborted workflows** — use `discard_transitions()`
2. **Only `confirm_transitions()` after full end-to-end success**
3. **First time exploring = trial and error** — expect mistakes, don't persist them
4. **Workflow = target state** — the path is computed at runtime from the graph

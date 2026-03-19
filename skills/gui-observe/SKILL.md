---
name: gui-observe
description: "Observe current screen state before any GUI action."
---

# Observe — Know Before You Act

## First time (unknown state)

1. `screenshot` → `image` tool to understand what's on screen
2. What app is frontmost? (check menu bar)
3. What page/state is the app in?
4. Any popups, dialogs blocking?

## Subsequent actions (known app)

Use detection instead of screenshot + image tool:

1. `_detect_visible_components()` → which saved components are on screen
2. `identify_state_by_components()` → which known state matches
3. If state is known → proceed with `click_component` (no screenshot needed)
4. If state is unknown → screenshot + image tool, then `learn`

## Coordinate System

- **Screen**: 1512×982 logical pixels (Retina 2x → 3024×1964 physical)
- **Templates**: saved in physical pixels (from full-screen screenshot)
- **Matching**: full-screen template match → physical center ÷ 2 = logical coords
- **Clicking**: logical coordinates via `platform_input.click_at(x, y)`
- **Window validation**: match position checked against `get_window_bounds()` to reject other apps

## State Detection

States are identified by which components are visible (F1 score matching):
```python
from app_memory import identify_state_by_components, _detect_visible_components
visible = _detect_visible_components(app_name)
state, f1 = identify_state_by_components(app_name, visible)
```

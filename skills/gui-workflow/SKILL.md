---
name: gui-workflow
description: "State graph navigation, workflow recording and replay."
---

# Workflow — State Graph Navigation

## Core Concept

Every click records a **state transition**: `(from_state, click_component, to_state)`.
Multiple clicks build a **state graph**. A workflow is a **path through the graph**.

```
click:chat_tab --宋文涛--> click:宋文涛 --my_avatar--> click:my_avatar
click:chat_tab --contacts_tab--> click:contacts_tab
click:contacts_tab --chat_tab--> click:chat_tab
click:moments --chat_tab--> click:chat_tab
```

## Navigation

To reach a target state from any starting state:

```python
from app_memory import find_path, identify_state_by_components, _detect_visible_components

# 1. Detect current state
visible = _detect_visible_components(app_name)
current, f1 = identify_state_by_components(app_name, visible)

# 2. Find path to target
path = find_path(app_name, current, target_state)
# Returns: [("component_to_click", "next_state"), ...]

# 3. Execute each step
for click, next_state in path:
    click_component(app_name, click)  # Auto-verifies + records transition
```

## Viewing the Graph

```bash
python3 scripts/app_memory.py transitions --app WeChat
# Output:
#   click:chat_tab --宋文涛--> click:宋文涛 (×3)
#   click:moments --chat_tab--> click:chat_tab (×1)

python3 scripts/app_memory.py path --app WeChat --component click:moments --contact click:宋文涛
# Output:
#   → click 'chat_tab' → click:chat_tab
#   → click '宋文涛' → click:宋文涛
```

## Building the Graph

The graph grows automatically with every `click_component` call. To explore faster:
1. Learn the app: `agent.py learn --app AppName`
2. Click through major pages/tabs (each click adds edges)
3. The more you explore, the more paths are available

## First-Time Task (No Graph Yet)

1. Screenshot + `image` tool to understand current state
2. Learn the app to get component names
3. Click step by step, using `image` tool to verify each step
4. Each click automatically builds the graph
5. Next time the same task → graph already has the path

## Intent Matching

When you receive a GUI task:
1. Identify target app + target state
2. Check if graph has a path from current state to target
3. If yes → follow the path (no screenshots needed for known transitions)
4. If no → explore manually (screenshot + image tool), building the graph as you go

## Cross-App Workflows

For tasks spanning multiple apps (copy from WeChat → paste in Chrome):
1. Execute steps in each app sequentially
2. Each app has its own state graph
3. Use clipboard/text for data passing between apps

---
name: gui-memory
description: "Visual memory system — split storage, component forgetting, state merging, transition dedup."
---

# Memory — Visual Memory System

## Storage Structure

Each app/site stores memory in **four independent files** (not one monolithic profile):

```
memory/apps/<appname>/
├── meta.json              # Metadata: detect_count, forget_threshold, img_size
├── components.json        # Component registry with activity tracking
├── states.json            # States defined by component sets
├── transitions.json       # State transitions (dict, deduped by key)
├── components/            # Template images (cropped UI elements)
└── pages/                 # Full page screenshots
```

### meta.json

```json
{
  "app": "chromium",
  "domain": "united.com",
  "detect_count": 47,
  "last_updated": "2026-03-23 15:30:00",
  "img_size": [1920, 1080],
  "forget_threshold": 15
}
```

- `detect_count`: total times `detect_all` has been called for this app/site
- `forget_threshold`: consecutive misses before a component is auto-deleted (default 15)

### components.json

```json
{
  "Travel_info": {
    "type": "text",
    "source": "ocr",
    "rel_x": 661, "rel_y": 188,
    "w": 80, "h": 20,
    "icon_file": "components/Travel_info.png",
    "label": "Travel info",
    "confidence": 0.95,
    "page": "homepage",
    "learned_at": "2026-03-23 02:20:00",
    "last_seen": "2026-03-23 15:30:00",
    "seen_count": 12,
    "consecutive_misses": 0
  }
}
```

Activity tracking fields (auto-managed, LLM does not set these):
- `last_seen`: last time this component was detected on screen
- `seen_count`: total times detected
- `consecutive_misses`: how many consecutive `detect_all` calls missed this component (resets to 0 on detection)

### states.json

```json
{
  "s_a3f2c1": {
    "name": "homepage",
    "description": "United Airlines homepage with booking form",
    "defining_components": ["nav_bar", "book_button", "Travel_info"],
    "visible_texts": ["United", "Book", "Travel info"],
    "first_seen": "2026-03-23 02:20:00",
    "last_seen": "2026-03-23 15:30:00",
    "visit_count": 5
  }
}
```

- States are defined by their `defining_components` set, not by naming convention
- State IDs are `s_` + 6-char hex hash of the component set
- Two states with Jaccard similarity > 0.85 are automatically merged

### transitions.json

```json
{
  "s_a3f2c1|click:Travel_info|s_b7d4e2": {
    "from_state": "s_a3f2c1",
    "action": "click:Travel_info",
    "to_state": "s_b7d4e2",
    "count": 3,
    "last_used": "2026-03-23 15:30:00",
    "success_rate": 1.0
  }
}
```

- Dict keyed by `from_state|action|to_state` — natural dedup
- Same operation updates `count` and `last_used` instead of creating duplicates

## Automatic Mechanisms

These run inside `learn_from_screenshot()` — the LLM just calls the function, everything below is automatic.

### Component Forgetting

Every time `learn_from_screenshot()` runs:
1. All detected components: `last_seen = now`, `seen_count += 1`, `consecutive_misses = 0`
2. All undetected components: `consecutive_misses += 1`
3. If `detect_count > forget_threshold` AND `consecutive_misses >= forget_threshold`:
   - Delete the component + its icon image
   - Remove from states' `defining_components`
   - If a state's `defining_components` becomes empty → delete the state
   - If a transition references a deleted state → delete the transition

### State Identification

After component activity update:
1. Filter detected components to stable ones (`seen_count >= 2`) → `stable_set`
2. Compare `stable_set` against each state's `defining_components` via Jaccard similarity
3. Jaccard > 0.7 → matched existing state, update `visit_count` and `last_seen`
4. All < 0.7 → create new state with `s_` + hash ID

### State Merging

After state identification:
1. Check all state pairs for Jaccard > 0.85
2. Merge: keep higher `visit_count` state, union `defining_components`
3. Update all transition references from merged state to kept state

## Components

- Saved as template images (cropped from full-screen screenshot)
- Matched via template matching on full screen (conf ≥ 0.8)
- Full-screen match + window bounds validation = no false matches from other apps
- conf < 0.8 → not on screen, don't lower threshold, re-learn instead
- Components that consistently fail to match are automatically forgotten

## Browser Apps (multiple websites)

Browsers host many websites, each with its own UI. The browser itself has memory for browser-level UI (toolbar, settings). Each website gets its own nested directory with the **same 4-file structure**:

```
memory/apps/chromium/
├── meta.json                 # Browser-level metadata
├── components.json           # Browser UI components (toolbar, etc.)
├── states.json
├── transitions.json
├── components/
├── pages/
└── sites/                    # ⭐ Each website = same structure
    ├── united.com/
    │   ├── meta.json
    │   ├── components.json
    │   ├── states.json
    │   ├── transitions.json
    │   ├── components/
    │   └── pages/
    ├── delta.com/
    │   └── ...
    └── ...
```

**Rules:**
- Every new website → create `sites/<domain>/` with the 4 files
- Domain as folder name (e.g. `united_com`, not `www.united.com/en/us`)
- Save after every task — even failures teach about the site's UI
- Components are site-specific — "Book" on united.com ≠ "Book" on delta.com

## Migration

Old `profile.json` files are automatically migrated to the new split format on first load:
- `profile.json` → split into `meta.json` + `components.json` + `states.json` + `transitions.json`
- Old file renamed to `profile.json.bak`
- Components get activity fields: `last_seen`, `seen_count`, `consecutive_misses`
- Transitions list converted to dict

## CRUD Operations

```bash
# Learn (detect + save + auto-forget + auto-state)
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

- Dynamic content (chat messages, timestamps) → auto-cleaned by `auto_cleanup_dynamic`
- Stale components → auto-forgotten after consecutive misses
- Unlabeled components → identify with `image` tool → rename or delete
- Privacy-sensitive (avatars) → delete unless functionally needed

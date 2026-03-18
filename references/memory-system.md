# Visual Memory System

## Memory Directory Structure

Each app gets its own memory:

```
memory/apps/<appname>/
├── profile.json        # Component registry + states
├── summary.json        # App overview
├── components/         # Cropped component images (PNG)
├── pages/              # Annotated screenshots
└── workflows/          # Saved workflow sequences
```

Meta-workflows: `memory/meta_workflows/`

## Profile Structure (profile.json)

```json
{
  "app": "AppName",
  "window_size": [w, h],
  "pages": {
    "main": {
      "fingerprint": { "expect_text": ["Chat", "Cowork", "Code"] },
      "regions": {
        "sidebar": { "position": "left", "stable": true, "components": ["Search"] },
        "toolbar": { "position": "top", "stable": true, "components": ["Chat_tab"] },
        "content": { "position": "center", "stable": false, "components": [] }
      },
      "transitions": { "Cmd+,": { "to": "settings", "type": "page" } }
    }
  },
  "overlays": {
    "account_menu": {
      "trigger": "profile_area",
      "parent_page": "main",
      "fingerprint": { "expect_text": ["Settings", "Log out"] },
      "components": ["Settings_link"],
      "dismiss": ["Esc", "click_outside"]
    }
  },
  "components": {
    "Search": { "type": "icon", "rel_x": 116, "rel_y": 144, "page": "main", "region": "sidebar" }
  }
}
```

## Key Concepts

| Concept | Description | Example |
|---------|------------|---------|
| **Page** | Full UI state, mutually exclusive | main, settings |
| **Region** | Area within a page | sidebar, toolbar, content |
| **Overlay** | Temporary popup over a page | account menu, context menu |
| **Fingerprint** | Text to identify current page | ["General", "Account"] → settings |
| **Transition** | What happens on click | click Usage → stays on settings |

## Page-Aware Matching

1. OCR the screen → get visible text
2. Match fingerprints → identify current page
3. Only match components belonging to that page
4. Match rate is calculated per-page, not overall

## Component Filtering Rules

Only save **stable UI elements** that look the same next session:

**SAVE** (stable):
- Sidebar elements (left ~15% of window)
- Toolbar elements (top ~12% of window)
- Footer elements (bottom ~12% of window)
- Any element with OCR text label

**SKIP** (dynamic):
- Tiny elements (< 25×25 pixels)
- Content area icons without labels
- Temporary content that changes every session

**Naming**:
- Has OCR label → use label as filename (`Search.png`)
- No label + stable region → `unlabeled_<region>.png`
- No label + content area → **SKIP**

## Learn Flow (MUST follow)

```
1. Capture window screenshot
2. Run GPA-GUI-Detector + Apple Vision OCR
3. For each detected element:
   a. Has OCR label? → use as filename
   b. No label? → _find_nearest_text initial guess
   c. Still no label? → "unlabeled_<region>_<x>_<y>"
   d. Check visual dedup (similarity > 0.92) → skip if duplicate
   e. Crop and save to components/
4. Agent MUST identify all components:
   a. Use `image` tool — batch up to 20 images per call
   b. For each: read text, describe icon, determine actual name
   c. ⚠️ PRIVACY CHECK: personal info → DELETE, do not keep
   d. Verify _find_nearest_text names (often wrong in dense UIs)
   e. Rename: app_memory.py rename --old X --new Y
5. After ALL identification + task done:
   a. Run: agent.py cleanup --app AppName
   b. Remove dynamic content (timestamps, message previews)
   c. Keep ONLY fixed UI elements
6. Result: ~20-30 named, fixed UI components per page
```

**Key rule**: `_find_nearest_text` is a HINT, not truth. Always verify by viewing the image.
**Privacy rule**: Components with personal info (names, emails, avatars) → delete, not save.

## What to KEEP vs REMOVE

**Golden rule**: Only save things that look **the same next time you open the app**.

**KEEP**: Sidebar nav icons, toolbar buttons, input controls, window controls, tab headers, logos.

**REMOVE**: Chat text/previews, timestamps, user avatars in lists, stickers, notification badges, contact names in chat list, web page content, text >15 chars in content area, profile pictures.

**Decision test**:
1. "Same place + same appearance tomorrow?" → KEEP
2. "Button I might click again?" → KEEP
3. "Something typed/sent/posted?" → REMOVE
4. "Web/feed item that scrolls away?" → REMOVE

## Post-Learn Checklist

- [ ] No `unlabeled_` files remain
- [ ] No timestamps, message previews, or chat content saved
- [ ] Each icon filename describes what it IS, not where it IS
- [ ] No duplicate icons (run `cleanup` if needed)
- [ ] ~20-30 components per page (not 60+)

## Memory Rules

1. **Filename = content**: `chat_button.png`, NOT `icon_0_170_103.png`
2. **Dedup**: similarity > 0.92 = duplicate. Keep ONE copy.
3. **Cleanup**: `agent.py cleanup --app AppName` to remove duplicates
4. **Per-app, per-page**: Each app has its own memory directory
5. **Keep fixed, clean dynamic**: buttons/icons = keep; messages/timestamps = clean

## Browser Memory (Two-Layer System)

Browsers are a special case — same app, different content per site:

```
memory/apps/google_chrome/
├── profile.json     # Browser chrome (tabs, address bar)
├── components/      # Browser UI icons
└── sites/           # Per-website memory
    ├── 12306.cn/
    │   ├── profile.json  # Site-specific elements
    │   └── components/   # Site buttons, nav
    └── google.com/
```

- **Browser chrome**: Learn once (address bar, tab controls, bookmarks)
- **Per-site**: Fixed UI (nav bars, search boxes, filters) = SAVE; dynamic content (search results, articles, ads) = DON'T SAVE

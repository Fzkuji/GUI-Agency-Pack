---
name: gui-observe
description: "Observe current screen state before any GUI action."
---

# Observe — Know Before You Act

## Three Visual Methods (see main SKILL.md for full details)

| Method | Returns | Coordinates? |
|--------|---------|-------------|
| **OCR** (`detect_text`) | Text + bounding box | ✅ YES |
| **GPA-GUI-Detector** (`detect_icons`) | UI components + bounding box | ✅ YES (no labels) |
| **image tool** | Semantic understanding | ⛔ NEVER |

## Phase 1: First encounter / unfamiliar page (DEFAULT)

1. Take screenshot
2. Run OCR (`detect_text`) → read all text + get coordinates
3. Send screenshot to image tool → understand layout and semantics (⛔ no coordinates from this)
4. Run GPA-GUI-Detector (`detect_icons`) → detect all UI components + coordinates
5. Combine all three to understand current state

## Phase 2: Familiar page (OPTIMIZATION)

1. Take screenshot (but don't send to image tool)
2. Run OCR + GPA-GUI-Detector → get text + coordinates as structured text
3. LLM reads text output directly → decide without visual analysis
4. If uncertain → fall back to Phase 1

## For known apps with saved memory

Use template matching instead of full detection:

1. `_detect_visible_components()` → which saved components are on screen
2. `identify_state_by_components()` → which known state matches
3. If state is known → proceed with `click_component` (no GPA-GUI-Detector needed)
4. If state is unknown → Phase 1 (full observation)

## Coordinate System — ImageContext

`detect_all()` returns **image pixel coordinates** (raw detection output).
Callers create an `ImageContext` to convert to screen click coordinates.
Cropping uses image pixel coords directly — **no conversion needed**.

### ImageContext (in `ui_detector.py`)

```python
from scripts.ui_detector import ImageContext

ctx = ImageContext.mac_fullscreen()      # Mac screencapture fullscreen
ctx = ImageContext.mac_window(wx, wy)    # Mac window screenshot (win pos in click-space)
ctx = ImageContext.remote()              # VM / remote / downloaded image (1:1)

# Image pixels → screen click coords
click_x, click_y = ctx.image_to_click(el["cx"], el["cy"])

# Screen click coords → image pixels (for cropping)
px_x, px_y = ctx.click_to_image(click_x, click_y)
```

### How it works

`ImageContext` knows two things:
1. **pixel_scale** — image pixels per click-space unit (from `backingScaleFactor`: Retina=2.0, else 1.0)
2. **origin** — image top-left in screen click-space (fullscreen=(0,0), window=(win_x, win_y))

| Source | Coordinates |
|--------|------------|
| detect_all output | **image pixels** |
| detect_icons / detect_text | image pixels |
| cv2 image crop | image pixels |
| gui_action.py click | click-space (use `ctx.image_to_click()`) |
| template_match raw | image pixels |

- **Mac Retina**: pixel_scale=2.0 (e.g., 3024×1964 image, 1512×982 click-space)
- **Mac non-Retina**: pixel_scale=1.0
- **Remote VMs**: pixel_scale=1.0, origin=(0,0)
- **Templates**: saved in image pixel coordinates

## State Detection

States are identified by which components are visible (F1 score matching):
```python
from app_memory import identify_state_by_components, _detect_visible_components
visible = _detect_visible_components(app_name)
state, f1 = identify_state_by_components(app_name, visible)
```

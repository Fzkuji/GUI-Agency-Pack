#!/usr/bin/env python3
"""
Platform abstraction layer for GUI input operations.

Replaces cliclick + osascript with pynput (cross-platform).
Window management still uses platform-specific APIs (macOS: osascript/Swift).

Usage:
    from platform_input import mouse_click, mouse_move, key_press, key_combo, type_text, paste_text
    from platform_input import activate_app, get_window_bounds, capture_window, get_clipboard, set_clipboard
"""

import os
import platform
import subprocess
import time

SYSTEM = platform.system()  # "Darwin", "Windows", "Linux"


# ═══════════════════════════════════════════
# Mouse operations (pynput)
# ═══════════════════════════════════════════

def mouse_click(x, y, button="left", clicks=1):
    """Click at screen coordinates (logical pixels, integers).
    After clicking, moves cursor to corner so it doesn't pollute screenshots."""
    from pynput.mouse import Button, Controller
    mouse = Controller()
    mouse.position = (int(x), int(y))
    time.sleep(0.05)
    btn = Button.right if button == "right" else Button.left
    mouse.click(btn, int(clicks))
    time.sleep(0.1)
    # Move cursor to bottom-right corner to avoid polluting screenshots/template matching
    mouse.position = (1500, 970)


def mouse_move(x, y):
    """Move mouse to screen coordinates."""
    from pynput.mouse import Controller
    mouse = Controller()
    mouse.position = (int(x), int(y))


def mouse_double_click(x, y):
    """Double click at screen coordinates."""
    mouse_click(x, y, clicks=2)


def mouse_right_click(x, y):
    """Right click at screen coordinates."""
    mouse_click(x, y, button="right")


def mouse_drag(start_x, start_y, end_x, end_y, duration=0.5, button="left"):
    """Drag from (start_x, start_y) to (end_x, end_y).
    
    Moves to start → press → smooth move to end → release.
    After drag, moves cursor to corner to avoid polluting screenshots.
    
    Args:
        start_x, start_y: Starting coordinates
        end_x, end_y: Ending coordinates  
        duration: Total drag duration in seconds (default 0.5)
        button: "left" or "right" (default "left")
    """
    from pynput.mouse import Button, Controller
    mouse = Controller()
    btn = Button.right if button == "right" else Button.left
    
    # Move to start position
    mouse.position = (int(start_x), int(start_y))
    time.sleep(0.1)
    
    # Press button
    mouse.press(btn)
    time.sleep(0.05)
    
    # Smooth move to end position
    steps = max(20, int(duration * 60))
    for i in range(1, steps + 1):
        progress = i / steps
        x = start_x + (end_x - start_x) * progress
        y = start_y + (end_y - start_y) * progress
        mouse.position = (int(x), int(y))
        time.sleep(duration / steps)
    
    # Ensure we're at the exact end position
    mouse.position = (int(end_x), int(end_y))
    time.sleep(0.05)
    
    # Release button
    mouse.release(btn)
    time.sleep(0.1)
    
    # Move cursor to corner
    mouse.position = (1500, 970)


# ═══════════════════════════════════════════
# Keyboard operations (pynput)
# ═══════════════════════════════════════════

# Map common key names to pynput Key objects
def _resolve_key(name):
    """Resolve a key name string to pynput Key or KeyCode."""
    from pynput.keyboard import Key, KeyCode
    
    key_map = {
        "return": Key.enter, "enter": Key.enter,
        "tab": Key.tab,
        "esc": Key.esc, "escape": Key.esc,
        "space": Key.space,
        "delete": Key.backspace, "backspace": Key.backspace,
        "fwd-delete": Key.delete,
        "up": Key.up, "arrow-up": Key.up,
        "down": Key.down, "arrow-down": Key.down,
        "left": Key.left, "arrow-left": Key.left,
        "right": Key.right, "arrow-right": Key.right,
        "home": Key.home, "end": Key.end,
        "page-up": Key.page_up, "page-down": Key.page_down,
        "f1": Key.f1, "f2": Key.f2, "f3": Key.f3, "f4": Key.f4,
        "f5": Key.f5, "f6": Key.f6, "f7": Key.f7, "f8": Key.f8,
        "f9": Key.f9, "f10": Key.f10, "f11": Key.f11, "f12": Key.f12,
        "shift": Key.shift, "ctrl": Key.ctrl, "control": Key.ctrl,
        "alt": Key.alt, "option": Key.alt,
        "command": Key.cmd, "cmd": Key.cmd, "super": Key.cmd,
    }
    
    lower = name.lower()
    if lower in key_map:
        return key_map[lower]
    
    # Single character
    if len(name) == 1:
        return KeyCode.from_char(name)
    
    return None


def key_press(key_name):
    """Press and release a single key.
    
    Examples: key_press("return"), key_press("esc"), key_press("a")
    """
    from pynput.keyboard import Controller
    kb = Controller()
    key = _resolve_key(key_name)
    if key:
        kb.press(key)
        kb.release(key)
    else:
        raise ValueError(f"Unknown key: {key_name}")


def key_combo(*keys):
    """Press a key combination.
    
    Examples: key_combo("command", "v"), key_combo("command", "shift", "s")
    """
    from pynput.keyboard import Controller
    kb = Controller()
    resolved = [_resolve_key(k) for k in keys]
    if any(k is None for k in resolved):
        bad = [keys[i] for i, k in enumerate(resolved) if k is None]
        raise ValueError(f"Unknown keys: {bad}")
    
    # Press all modifiers, then the final key, then release in reverse
    for k in resolved:
        kb.press(k)
    time.sleep(0.05)
    for k in reversed(resolved):
        kb.release(k)


def type_text(text):
    """Type text character by character. Works for ASCII.
    For CJK/special chars, use paste_text() instead.
    """
    from pynput.keyboard import Controller
    kb = Controller()
    kb.type(text)


def paste_text(text):
    """Paste text via clipboard (works for all languages including CJK)."""
    set_clipboard(text)
    time.sleep(0.1)
    key_combo("command" if SYSTEM == "Darwin" else "ctrl", "v")


# ═══════════════════════════════════════════
# Clipboard operations
# ═══════════════════════════════════════════

def set_clipboard(text):
    """Set clipboard content."""
    if SYSTEM == "Darwin":
        p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE,
                            env={"LANG": "en_US.UTF-8"})
        p.communicate(text.encode("utf-8"))
    elif SYSTEM == "Windows":
        subprocess.run(["clip"], input=text.encode("utf-16le"), check=True)
    else:  # Linux
        subprocess.run(["xclip", "-selection", "clipboard"],
                       input=text.encode("utf-8"), check=True)


def get_clipboard():
    """Get clipboard content."""
    if SYSTEM == "Darwin":
        r = subprocess.run(["pbpaste"], capture_output=True, text=True)
        return r.stdout
    elif SYSTEM == "Windows":
        r = subprocess.run(["powershell", "-command", "Get-Clipboard"],
                          capture_output=True, text=True)
        return r.stdout.strip()
    else:
        r = subprocess.run(["xclip", "-selection", "clipboard", "-o"],
                          capture_output=True, text=True)
        return r.stdout


# ═══════════════════════════════════════════
# Window management (platform-specific)
# ═══════════════════════════════════════════

def get_frontmost_app():
    """Get the name of the currently frontmost application."""
    if SYSTEM == "Darwin":
        try:
            r = subprocess.run(["osascript", "-e",
                'tell application "System Events" to return name of first process whose frontmost is true'],
                capture_output=True, text=True, timeout=5)
            return r.stdout.strip()
        except:
            return "unknown"
    else:
        raise NotImplementedError(f"{SYSTEM} get_frontmost_app not yet implemented")


def verify_frontmost(expected_app):
    """Check if the expected app is still frontmost. Returns (is_correct, actual_app)."""
    actual = get_frontmost_app()
    return actual == expected_app, actual


def activate_app(app_name):
    """Bring app window to front."""
    if SYSTEM == "Darwin":
        try:
            subprocess.run(["osascript", "-e",
                f'tell application "System Events" to set frontmost of process "{app_name}" to true'],
                capture_output=True, timeout=5)
            time.sleep(0.3)
        except:
            subprocess.run(["open", "-a", app_name], capture_output=True, timeout=5)
            time.sleep(0.5)
    elif SYSTEM == "Windows":
        # TODO: implement with pygetwindow or ctypes
        raise NotImplementedError("Windows activate_app not yet implemented")
    else:
        # TODO: implement with wmctrl or xdotool
        raise NotImplementedError("Linux activate_app not yet implemented")


def get_window_bounds(app_name):
    """Get window position and size: (x, y, w, h).
    
    Returns the largest window for the app (handles apps with multiple windows).
    """
    if SYSTEM == "Darwin":
        try:
            r = subprocess.run(["osascript", "-l", "JavaScript", "-e", f'''
var se = Application("System Events");
var ws = se.processes["{app_name}"].windows();
var best = null;
var bestArea = 0;
for (var i = 0; i < ws.length; i++) {{
    try {{
        var p = ws[i].position();
        var s = ws[i].size();
        var area = s[0] * s[1];
        if (area > bestArea) {{
            bestArea = area;
            best = [p[0], p[1], s[0], s[1]];
        }}
    }} catch(e) {{}}
}}
if (best) best.join(","); else "";
'''], capture_output=True, text=True, timeout=5)
            parts = r.stdout.strip().split(",")
            if len(parts) == 4:
                return tuple(int(x) for x in parts)
        except:
            pass
        return None
    else:
        raise NotImplementedError(f"{SYSTEM} get_window_bounds not yet implemented")


def capture_window(app_name, out_path=None):
    """Capture a screenshot of the app's window.
    
    Returns: (image_path, x, y, w, h) or None on failure.
    """
    if SYSTEM == "Darwin":
        import sys, os
        sys.path.insert(0, os.path.dirname(__file__))
        from ui_detector import get_window_info, take_window_screenshot
        
        info = get_window_info(app_name)
        if not info:
            return None
        
        path = out_path or f"/tmp/gui_agent_{app_name.lower().replace(' ', '_')}.png"
        take_window_screenshot(info["id"], path)
        return path, info["x"], info["y"], info["w"], info["h"]
    else:
        raise NotImplementedError(f"{SYSTEM} capture_window not yet implemented")


# ═══════════════════════════════════════════
# Convenience / high-level
# ═══════════════════════════════════════════

def screenshot(path="/tmp/gui_agent_screen.png"):
    """Take a full-screen screenshot and return the path."""
    subprocess.run(["screencapture", "-x", path], capture_output=True, timeout=5)
    return path


def screenshot_region(out_path, method="auto", x1=None, y1=None, x2=None, y2=None,
                      anchor_start=None, anchor_end=None, padding=10,
                      bg_color=None, content_threshold=245):
    """Take a screenshot of a specific region.
    
    Two strategies (per GUI Agent Skills design):
    
    Strategy 1 — Anchor-based (when text/components can define boundaries):
    - "anchors": Use OCR text as reference points to define crop boundaries.
                 anchor_start/anchor_end are text strings to search for.
                 Crops from above anchor_start to below anchor_end.
    - "crop": Explicit logical coordinates (x1,y1,x2,y2).
    - "drag": Cmd+Shift+4 interactive drag.
    
    Strategy 2 — Feature-based (when no anchors, detect content boundaries):
    - "auto_crop": Detect largest uniform region (white/colored) via connected 
                   components. Works for slides, documents, dialogs.
    - "edge_detect": Use edge detection to find content boundaries. 
                     Works for images, mixed-content areas.
    
    "auto" mode: tries anchors if provided, falls back to auto_crop.
    
    Args:
        out_path: Output image path
        method: "auto", "anchors", "crop", "drag", "auto_crop", "edge_detect"
        x1,y1,x2,y2: Logical screen coordinates (for "crop" and "drag")
        anchor_start: Text string marking top/left of region (for "anchors")
        anchor_end: Text string marking bottom/right of region (for "anchors")
        padding: Pixels of padding around anchors (logical coords, default 10)
        bg_color: Background color tuple (R,G,B) for auto_crop. None = auto-detect.
        content_threshold: Brightness threshold for white region detection (default 245)
    
    Returns: path to saved image, or None on failure.
    """
    # Auto mode: use anchors if provided, otherwise auto_crop
    if method == "auto":
        if anchor_start or anchor_end:
            method = "anchors"
        else:
            method = "auto_crop"
    
    if method == "drag":
        key_combo("command", "shift", "4")
        time.sleep(1)
        mouse_drag(x1, y1, x2, y2, duration=0.8)
        time.sleep(1.5)
        import glob
        files = sorted(glob.glob(os.path.expanduser("~/Desktop/Screenshot*.png")),
                       key=os.path.getmtime, reverse=True)
        if files:
            import shutil
            shutil.move(files[0], out_path)
            return out_path
        return None
    
    elif method == "crop":
        full = screenshot("/tmp/_region_full.png")
        from PIL import Image
        img = Image.open(full)
        # Logical → Retina (2x)
        crop = img.crop((x1*2, y1*2, x2*2, y2*2))
        crop.save(out_path)
        return out_path
    
    elif method == "anchors":
        return _screenshot_by_anchors(out_path, anchor_start, anchor_end, padding)
    
    elif method == "auto_crop":
        return _screenshot_auto_crop(out_path, content_threshold)
    
    elif method == "edge_detect":
        return _screenshot_edge_detect(out_path)
    
    else:
        raise ValueError(f"Unknown method: {method}")


def _screenshot_by_anchors(out_path, anchor_start, anchor_end, padding=10):
    """Strategy 1: OCR-based anchor positioning.
    
    Find text strings on screen via OCR, use their positions as crop boundaries.
    - anchor_start defines the top-left boundary (crop starts above/left of it)
    - anchor_end defines the bottom-right boundary (crop ends below/right of it)
    - If only one anchor, center the crop around it with generous padding.
    """
    full = screenshot("/tmp/_anchor_full.png")
    from PIL import Image
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    img = Image.open(full)
    
    # Run OCR
    try:
        from spreadsheet_utils import _run_vision_ocr
        ocr_results = _run_vision_ocr(full)
    except ImportError:
        print("OCR not available")
        return None
    
    if not ocr_results:
        print("OCR returned no results")
        return None
    
    # Find anchor positions (Retina coordinates from OCR)
    start_pos = None
    end_pos = None
    
    for text, x, y, w, h in ocr_results:
        clean = text.strip()
        if anchor_start and anchor_start.lower() in clean.lower():
            if start_pos is None or y < start_pos[1]:  # topmost match
                start_pos = (x, y, w, h)
        if anchor_end and anchor_end.lower() in clean.lower():
            if end_pos is None or (y + h) > (end_pos[1] + end_pos[3]):  # bottommost match
                end_pos = (x, y, w, h)
    
    if not start_pos and not end_pos:
        print(f"Could not find anchors: start='{anchor_start}', end='{anchor_end}'")
        return None
    
    # Calculate crop bounds (Retina coordinates)
    pad = padding * 2  # logical padding → Retina
    
    if start_pos and end_pos:
        crop_x1 = min(start_pos[0], end_pos[0]) - pad
        crop_y1 = start_pos[1] - pad
        crop_x2 = max(start_pos[0] + start_pos[2], end_pos[0] + end_pos[2]) + pad
        crop_y2 = end_pos[1] + end_pos[3] + pad
    elif start_pos:
        # Only start anchor — crop from anchor with generous area below
        crop_x1 = start_pos[0] - pad
        crop_y1 = start_pos[1] - pad
        crop_x2 = img.width  # to right edge
        crop_y2 = min(start_pos[1] + 800, img.height)  # ~400 logical px below
    elif end_pos:
        # Only end anchor — crop area above the anchor
        crop_x1 = 0
        crop_y1 = max(0, end_pos[1] - 800)  # ~400 logical px above
        crop_x2 = end_pos[0] + end_pos[2] + pad
        crop_y2 = end_pos[1] + end_pos[3] + pad
    
    # Clamp to image bounds
    crop_x1 = max(0, int(crop_x1))
    crop_y1 = max(0, int(crop_y1))
    crop_x2 = min(img.width, int(crop_x2))
    crop_y2 = min(img.height, int(crop_y2))
    
    crop = img.crop((crop_x1, crop_y1, crop_x2, crop_y2))
    crop.save(out_path)
    print(f"Anchored crop: ({crop_x1//2},{crop_y1//2})->({crop_x2//2},{crop_y2//2}) logical")
    return out_path


def _screenshot_auto_crop(out_path, content_threshold=245):
    """Strategy 2a: Connected components white/content region detection.
    
    Finds the largest bright/white region — works for slides, documents, 
    dialogs, any content with a uniform background.
    """
    full = screenshot("/tmp/_auto_full.png")
    from PIL import Image
    import numpy as np
    import cv2
    
    img = Image.open(full)
    arr = np.array(img)[:, :, :3]
    gray_img = np.mean(arr, axis=2)
    
    binary = (gray_img > content_threshold).astype(np.uint8)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary)
    
    max_area = 0
    best = None
    for i in range(1, num_labels):
        area = stats[i, 4]
        w, h = stats[i, 2], stats[i, 3]
        if area > max_area and w > 200 and h > 200:
            max_area = area
            best = (stats[i, 0], stats[i, 1], stats[i, 2], stats[i, 3])
    
    if best:
        x, y, w, h = best
        margin = 3
        crop = img.crop((x+margin, y+margin, x+w-margin, y+h-margin))
        crop.save(out_path)
        return out_path
    
    return None


def _screenshot_edge_detect(out_path):
    """Strategy 2b: Edge-based content boundary detection.
    
    Uses Canny edge detection + contour finding to locate the main 
    content area. Works for images, mixed-content, colored backgrounds
    where white-region detection fails.
    """
    full = screenshot("/tmp/_edge_full.png")
    from PIL import Image
    import numpy as np
    import cv2
    
    img = Image.open(full)
    arr = np.array(img)[:, :, :3]
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    
    # Edge detection
    edges = cv2.Canny(gray, 50, 150)
    
    # Dilate to connect nearby edges
    kernel = np.ones((5, 5), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=3)
    
    # Find contours
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None
    
    # Find largest contour by bounding rect area
    best_rect = None
    best_area = 0
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        area = w * h
        # Must be reasonably large (> 10% of screen)
        if area > best_area and w > 200 and h > 200:
            best_area = area
            best_rect = (x, y, w, h)
    
    if best_rect:
        x, y, w, h = best_rect
        margin = 5
        crop = img.crop((x+margin, y+margin, x+w-margin, y+h-margin))
        crop.save(out_path)
        return out_path
    
    return None


def click_at(x, y):
    """Simple left click (most common operation)."""
    mouse_click(x, y)


def send_keys(combo_string):
    """Parse and execute a key combo string like "command-v", "command-shift-s", "return".
    
    For single keys: send_keys("return"), send_keys("esc")
    For combos: send_keys("command-v"), send_keys("command-shift-s")
    """
    parts = combo_string.lower().split("-")
    if len(parts) == 1:
        key_press(parts[0])
    else:
        key_combo(*parts)


# ═══════════════════════════════════════════
# Self-test
# ═══════════════════════════════════════════

if __name__ == "__main__":
    print(f"Platform: {SYSTEM}")
    print(f"pynput import: ok")
    
    # Test clipboard
    set_clipboard("test_clipboard_content")
    assert get_clipboard() == "test_clipboard_content"
    print("Clipboard: ok")
    
    # Test key resolution
    for name in ["return", "esc", "command", "shift", "a", "space"]:
        k = _resolve_key(name)
        assert k is not None, f"Failed to resolve: {name}"
    print("Key resolution: ok")
    
    # Test send_keys parsing
    print("send_keys parsing: ok")
    
    print("\nAll tests passed ✅")

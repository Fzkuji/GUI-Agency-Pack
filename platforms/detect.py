#!/usr/bin/env python3
"""
Platform detection for GUI Agent Skills.
Auto-detects OS and available GUI automation tools.
Returns platform info dict and loads the correct platform guide.
"""

import platform
import shutil
import os
import subprocess


def detect_platform():
    """Detect current platform and available tools."""
    
    os_type = platform.system()  # "Darwin" | "Linux" | "Windows"
    os_release = platform.release()
    machine = platform.machine()  # "arm64" | "x86_64" | "aarch64"
    
    info = {
        "os": os_type,
        "os_name": _get_os_name(os_type),
        "release": os_release,
        "machine": machine,
        "display_server": _detect_display_server(os_type),
        "tools": {},
    }
    
    # Detect available tools
    tools = {
        # Screenshot
        "screencapture": shutil.which("screencapture"),      # macOS
        "scrot": shutil.which("scrot"),                       # Linux
        "gnome-screenshot": shutil.which("gnome-screenshot"), # Linux GNOME
        "import": shutil.which("import"),                     # Linux ImageMagick
        
        # Input automation
        "pynput": _check_python_module("pynput"),
        "pyautogui": _check_python_module("pyautogui"),
        "xdotool": shutil.which("xdotool"),                  # Linux X11
        "xclip": shutil.which("xclip"),                      # Linux clipboard
        "xsel": shutil.which("xsel"),                        # Linux clipboard alt
        "pbcopy": shutil.which("pbcopy"),                    # macOS clipboard
        "pbpaste": shutil.which("pbpaste"),                  # macOS clipboard
        
        # Window management
        "wmctrl": shutil.which("wmctrl"),                    # Linux
        "osascript": shutil.which("osascript"),              # macOS AppleScript
        
        # OCR / Detection (Python modules)
        "vision_framework": _check_apple_vision(),            # macOS Vision
        "pytesseract": _check_python_module("pytesseract"),   # Cross-platform OCR
        "easyocr": _check_python_module("easyocr"),           # Cross-platform OCR
    }
    
    info["tools"] = {k: v for k, v in tools.items() if v}
    
    # Determine recommended input method
    if os_type == "Darwin":
        info["recommended_input"] = "pynput"
        info["recommended_screenshot"] = "screencapture"
        info["recommended_clipboard"] = "pbcopy/pbpaste"
        info["recommended_ocr"] = "apple_vision"
    elif os_type == "Linux":
        if tools.get("xdotool"):
            info["recommended_input"] = "xdotool"
        elif tools.get("pyautogui"):
            info["recommended_input"] = "pyautogui"
        info["recommended_screenshot"] = "scrot" if tools.get("scrot") else "gnome-screenshot"
        info["recommended_clipboard"] = "xclip" if tools.get("xclip") else "xsel"
        info["recommended_ocr"] = "pytesseract"
    elif os_type == "Windows":
        info["recommended_input"] = "pyautogui"
        info["recommended_screenshot"] = "pyautogui"
        info["recommended_clipboard"] = "pyperclip"
        info["recommended_ocr"] = "pytesseract"
    
    # Determine platform guide file
    platform_map = {"Darwin": "macos", "Linux": "linux", "Windows": "windows"}
    info["platform_guide"] = platform_map.get(os_type, "unknown")
    
    return info


def _get_os_name(os_type):
    if os_type == "Darwin":
        return "macOS"
    elif os_type == "Linux":
        # Try to get distro name
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        return line.split("=", 1)[1].strip().strip('"')
        except:
            pass
        return "Linux"
    elif os_type == "Windows":
        return f"Windows {platform.version()}"
    return os_type


def _detect_display_server(os_type):
    if os_type == "Darwin":
        return "quartz"
    elif os_type == "Linux":
        session = os.environ.get("XDG_SESSION_TYPE", "")
        if session == "wayland":
            return "wayland"
        elif session == "x11" or os.environ.get("DISPLAY"):
            return "x11"
        return "unknown"
    elif os_type == "Windows":
        return "win32"
    return "unknown"


def _check_python_module(module_name):
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False


def _check_apple_vision():
    """Check if Apple Vision framework is available (macOS only)."""
    if platform.system() != "Darwin":
        return False
    try:
        import objc
        from Foundation import NSBundle
        vision_bundle = NSBundle.bundleWithIdentifier_("com.apple.vision")
        return vision_bundle is not None
    except:
        return False


def get_platform_guide_path():
    """Return the path to the platform-specific guide file."""
    info = detect_platform()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    guide_file = os.path.join(base_dir, f"{info['platform_guide']}.md")
    if os.path.exists(guide_file):
        return guide_file
    return None


def print_summary():
    """Print a human-readable platform summary."""
    info = detect_platform()
    print(f"Platform: {info['os_name']} ({info['machine']})")
    print(f"Display: {info['display_server']}")
    print(f"Guide: {info['platform_guide']}.md")
    print(f"\nAvailable tools:")
    for tool, available in sorted(info['tools'].items()):
        status = "✅" if available else "❌"
        print(f"  {status} {tool}: {available}")
    print(f"\nRecommended:")
    print(f"  Input: {info.get('recommended_input', '?')}")
    print(f"  Screenshot: {info.get('recommended_screenshot', '?')}")
    print(f"  Clipboard: {info.get('recommended_clipboard', '?')}")
    print(f"  OCR: {info.get('recommended_ocr', '?')}")


if __name__ == "__main__":
    import sys
    if "--json" in sys.argv:
        import json
        print(json.dumps(detect_platform(), default=str))
    else:
        print_summary()

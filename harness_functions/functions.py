"""
GUI Agent Functions — the 6 core functions for desktop automation.

Each function's docstring is the LLM prompt. Change the docstring → change the behavior.
The scripts/*.py layer handles all deterministic operations (screenshot, OCR, click, etc.).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Optional
from pydantic import BaseModel

# Add parent to path for imports
SKILL_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# Import from harness framework
sys.path.insert(0, str(SKILL_DIR.parent.parent.parent / "Documents" / "LLM Agent Harness" / "llm-agent-harness"))
from harness import function, Session


# ═══════════════════════════════════════════
# Return types
# ═══════════════════════════════════════════

class ObserveResult(BaseModel):
    """What the agent sees on screen right now."""
    app_name: str                          # frontmost app
    page_description: str                  # what's on screen
    visible_text: list[str]                # OCR results (key texts)
    interactive_elements: list[str]        # clickable things found
    state_name: Optional[str] = None       # known state from memory (if any)
    state_confidence: Optional[float] = None
    target_visible: bool = False           # is the user's target on screen?
    target_location: Optional[dict] = None # {x, y} if found
    screenshot_path: Optional[str] = None  # path to screenshot taken

class LearnResult(BaseModel):
    """Result of learning a new app's UI."""
    app_name: str
    components_found: int                  # total detected
    components_saved: int                  # new ones saved to memory
    component_names: list[str]             # what was identified
    page_name: str                         # human-readable page label
    already_known: bool = False            # was this app already in memory?

class ActResult(BaseModel):
    """Result of performing a GUI action."""
    action: str                            # what was done ("click", "type", "shortcut")
    target: str                            # what was targeted
    coordinates: Optional[dict] = None     # {x, y} where action happened
    success: bool                          # did it appear to work?
    before_state: Optional[str] = None     # state before action
    after_state: Optional[str] = None      # state after action
    screen_changed: bool = False           # did the screen change?
    error: Optional[str] = None            # error message if failed

class RememberResult(BaseModel):
    """Result of a memory operation."""
    operation: str                         # "save", "merge", "forget", "list"
    app_name: str
    details: str                           # human-readable summary

class NavigateResult(BaseModel):
    """Result of multi-step navigation."""
    start_state: str
    target_state: str
    path: list[str]                        # states traversed
    steps_taken: int
    reached_target: bool
    current_state: str                     # where we ended up

class VerifyResult(BaseModel):
    """Result of verification after an action."""
    expected: str                          # what we expected to see
    actual: str                            # what we actually see
    verified: bool                         # does actual match expected?
    evidence: str                          # why we think so
    screenshot_path: Optional[str] = None


# ═══════════════════════════════════════════
# Helper: run scripts
# ═══════════════════════════════════════════

def _run_script(script_name: str, *args) -> str:
    """Run a Python script from scripts/ and return stdout."""
    cmd = [sys.executable, str(SCRIPTS_DIR / script_name)] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(f"{script_name} failed: {result.stderr[:500]}")
    return result.stdout.strip()


def _take_screenshot() -> str:
    """Take a screenshot and return the path."""
    import tempfile
    path = Path(tempfile.mkdtemp()) / "screenshot.png"
    subprocess.run(["screencapture", "-x", str(path)], check=True, timeout=10)
    return str(path)


def _run_ocr(image_path: str) -> list[dict]:
    """Run OCR on an image, return text elements."""
    try:
        from ui_detector import detect_text
        return detect_text(image_path)
    except Exception:
        return []


def _run_detector(image_path: str) -> list[dict]:
    """Run GPA-GUI-Detector on an image, return UI elements."""
    try:
        from ui_detector import detect_icons
        return detect_icons(image_path)
    except Exception:
        return []


def _get_frontmost_app() -> str:
    """Get the name of the frontmost application."""
    try:
        r = subprocess.run(
            ["osascript", "-e",
             'tell application "System Events" to name of first process whose frontmost is true'],
            capture_output=True, text=True, timeout=5
        )
        return r.stdout.strip()
    except Exception:
        return "unknown"


# ═══════════════════════════════════════════
# Functions (docstring = LLM prompt)
# ═══════════════════════════════════════════

@function(return_type=ObserveResult)
def observe(session: Session, task: str, screenshot_path: str = None) -> ObserveResult:
    """You are observing the current screen to understand what's visible.

Your task: {task}

You will receive:
1. The frontmost app name
2. OCR text detected on screen (with coordinates)
3. UI components detected by GPA-GUI-Detector (with coordinates)
4. A screenshot for visual understanding

Based on ALL of this information, determine:
- What app is open and what page/state it's in
- What interactive elements are available
- Whether the target described in the task is visible
- If visible, where exactly it is (x, y coordinates from OCR or detector, NOT from your visual estimate)

IMPORTANT: Coordinates must come from OCR or detector results, NEVER from your visual interpretation of the screenshot."""


@function(return_type=LearnResult)
def learn(session: Session, app_name: str, screenshot_path: str = None) -> LearnResult:
    """You are learning a new app's UI for the first time.

App to learn: {app_name}

You will receive:
1. A screenshot of the app
2. All UI components detected by GPA-GUI-Detector (bounding boxes, no labels)
3. OCR text detected on screen

Your job:
- Look at each detected component in the screenshot
- Give each component a descriptive name based on what it is (e.g., "send_button", "search_bar", "contact_list")
- Filter out duplicates and non-interactive decorative elements
- Group related components if they belong together
- Identify the current page/state name (e.g., "chat_main", "settings", "login")

Name components clearly and consistently. Use snake_case. Be specific: "send_message_button" not just "button"."""


@function(return_type=ActResult)
def act(session: Session, action: str, target: str,
        text: str = None, screenshot_path: str = None) -> ActResult:
    """You are performing a GUI action on the screen.

Action to perform: {action} (click, type, shortcut, scroll)
Target: {target}
Text to type (if applicable): {text}

You will receive:
1. Current screenshot
2. OCR text with coordinates
3. Detected UI components with coordinates
4. Known components from memory (with template match results)

Your job:
1. Find the target element using OCR/detector/template match coordinates
2. Confirm you've found the right element (not a similarly-named one)
3. Report the coordinates to click and what action to take
4. After the action is executed, a new screenshot will be taken
5. Compare before/after to determine if the action succeeded

COORDINATE RULE: Use coordinates from OCR, detector, or template match ONLY.
Never estimate coordinates from the screenshot image.

If the target is not found, report success=false with a clear error message."""


@function(return_type=RememberResult)
def remember(session: Session, operation: str, app_name: str,
             details: str = None) -> RememberResult:
    """You are managing the visual memory for an app.

Operation: {operation}
App: {app_name}
Details: {details}

Available operations:
- "save": Save new components detected on the current screen
- "merge": Merge duplicate states that look the same
- "forget": Remove components that haven't been matched in 15+ attempts
- "list": List all known components and states for the app
- "rename": Rename a component to a better name

For "save": You'll receive detected components. Decide which are worth saving.
For "merge": You'll see similar states. Decide if they should be combined.
For "forget": You'll see components with low match rates. Decide what to remove.

Be conservative with forgetting — only remove things that are clearly obsolete."""


@function(return_type=NavigateResult)
def navigate(session: Session, target_state: str, app_name: str) -> NavigateResult:
    """You are navigating through an app to reach a target state.

Target state: {target_state}
App: {app_name}

You will receive:
1. Current state (from visual memory)
2. The state graph (known states and transitions between them)
3. BFS shortest path from current state to target (if one exists)

Your job:
1. If a known path exists, follow it step by step
2. At each step, verify you reached the expected state (template match or OCR)
3. If verification fails, re-observe and try an alternative path
4. If no known path exists, explore: try clicking likely elements and observe results

Verification tiers (try in order):
1. Template match against known components → fast, reliable
2. Full detection (OCR + GPA) → slower but comprehensive
3. LLM visual check → last resort, send screenshot to image tool

Report each state transition as you go."""


@function(return_type=VerifyResult)
def verify(session: Session, expected: str,
           screenshot_path: str = None) -> VerifyResult:
    """You are verifying whether a previous action succeeded.

Expected outcome: {expected}

You will receive:
1. A screenshot of the current screen
2. OCR text detected
3. Detected UI components

Your job:
- Look at the screen and determine if the expected outcome is achieved
- Provide specific evidence (what text you see, what elements are present/absent)
- Be honest: if it didn't work, say so clearly

Examples of verification:
- "login page loaded" → check if login form fields are visible
- "message sent" → check if message appears in chat
- "file saved" → check if save confirmation or file name appears
- "tab closed" → check if tab is no longer in the tab bar"""

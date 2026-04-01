"""
GUI Agent Functions — LLM-executed + deterministic functions for desktop automation.

Two levels:
    Low-level (deterministic, no LLM):
        take_screenshot, run_ocr, run_detector, detect_all,
        template_match, identify_state, click, type_text, paste,
        press_key, key_combo, get_frontmost_app, activate_app,
        learn_from_screenshot, record_transition

    High-level (hybrid: Python gathers data, LLM reasons):
        observe, learn, act, remember, navigate, verify

High-level functions call low-level functions internally.
You can also call low-level functions directly for deterministic tasks.
"""

# Low-level (deterministic)
from harness_functions.functions import (
    take_screenshot, ScreenshotResult,
    run_ocr, OCRResult,
    run_detector, DetectResult,
    detect_all, DetectAllResult,
    template_match, TemplateMatchResult,
    identify_state, StateResult,
    click,
    type_text,
    paste,
    press_key,
    key_combo,
    get_frontmost_app,
    activate_app,
    learn_from_screenshot,
    record_transition,
)

# High-level (LLM-powered)
from harness_functions.functions import (
    observe, ObserveResult,
    learn, LearnResult,
    act, ActResult,
    remember, RememberResult,
    navigate, NavigateResult,
    verify, VerifyResult,
)

__all__ = [
    # Low-level
    "take_screenshot", "ScreenshotResult",
    "run_ocr", "OCRResult",
    "run_detector", "DetectResult",
    "detect_all", "DetectAllResult",
    "template_match", "TemplateMatchResult",
    "identify_state", "StateResult",
    "click", "type_text", "paste", "press_key", "key_combo",
    "get_frontmost_app", "activate_app",
    "learn_from_screenshot", "record_transition",
    # High-level
    "observe", "ObserveResult",
    "learn", "LearnResult",
    "act", "ActResult",
    "remember", "RememberResult",
    "navigate", "NavigateResult",
    "verify", "VerifyResult",
]

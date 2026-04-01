"""
GUI Agent Functions — LLM-executed functions for desktop automation.

These functions wrap the existing scripts (app_memory, ui_detector, gui_agent, etc.)
with the Agentic Programming @function pattern. The docstring IS the prompt.

Architecture:
    @function (LLM decides how)  →  scripts/*.py (Python does the work)

    observe()   → LLM interprets screen state using OCR + detector + vision
    learn()     → LLM identifies and labels UI components
    act()       → LLM decides target, scripts execute click/type
    remember()  → LLM manages visual memory (label, merge, forget)
    navigate()  → LLM plans multi-step navigation via state graph
    verify()    → LLM checks if action succeeded

Each function takes a Session as first arg (the LLM that thinks)
and uses scripts/*.py for the deterministic operations (screenshot, OCR, click).
"""

from harness_functions.functions import (
    observe,
    learn,
    act,
    remember,
    navigate,
    verify,
    ObserveResult,
    LearnResult,
    ActResult,
    RememberResult,
    NavigateResult,
    VerifyResult,
)

__all__ = [
    "observe",
    "learn",
    "act",
    "remember",
    "navigate",
    "verify",
    "ObserveResult",
    "LearnResult",
    "ActResult",
    "RememberResult",
    "NavigateResult",
    "VerifyResult",
]

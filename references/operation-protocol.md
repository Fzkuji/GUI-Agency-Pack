# Operation Protocol

Every GUI action follows this protocol. Not suggestions — hard requirements.

## Timing & Context Reporting (MANDATORY)

Every GUI task MUST report timing and token cost.

**BEFORE starting**: `session_status` → note context size
**AFTER completing**: `session_status` → compute delta

Format: `⏱ 45.2s | 📊 +10k tokens (85k→95k) | 🔧 3 screenshots, 2 clicks, 1 learn`

No exceptions. Even when bypassing agent.py.

## Step -1: Intent Matching

Before doing anything:
1. Identify target app
2. List workflows: `python3 agent.py workflows --app AppName`
3. Match intent semantically (you are the LLM — understand meaning, not string-match)
4. If matched → load workflow, skip to Step 0
5. If no match → proceed normally, save workflow after success

## Step 0: Observe

Before ANY task:
1. Record context size (session_status)
2. Screenshot the screen
3. What app is in foreground? Is target app visible? What state?
4. Any popups/dialogs blocking?
5. ONLY after understanding state, proceed

**DO NOT skip. DO NOT assume state from last time.**

## Pre-Click Verify (every click)

1. Element actually on screen RIGHT NOW?
2. CORRECT element (not similar name in another window)?
3. Inside correct app window?
4. Any NO → DO NOT CLICK. Re-observe.

## Pre-Send Verify (before sending messages)

1. OCR chat header — correct contact/group open?
2. Message text in input field?
3. Any NO → ABORT. Do not send.

Why: Template matching "ContactName" could match a group chat, forwarded message, or another app's window. Only the chat HEADER reliably shows who you're chatting with.

## Post-Action Verify (after every action)

1. Screenshot again
2. Expected change happened?
3. In expected next state?
4. If NOT → re-observe and decide

## Workflow Execution (known workflows)

DO NOT blindly replay steps. Instead:
1. Observe current state FIRST
2. WHERE in the workflow am I now?
3. Skip steps already done
4. Execute ONLY the next needed step
5. Verify state changed after each step
6. State doesn't match any step → STOP, trigger plan

## Waiting for Async UI

When action triggers a slow process (scan, download, loading):
1. Use `wait_for`: `python3 agent.py wait_for --app AppName --component ComponentName`
2. Template match polls every 10s (~0.3s/check), 120s timeout
3. Success → returns coordinates, proceed
4. Timeout → saves screenshot, **DO NOT blind-click** — inspect and decide
5. **NEVER `sleep(60)` + blind click**

## Saving Workflows

After completing a multi-step task successfully:

1. Check if workflow already exists
2. If not → save it:
   ```python
   save_workflow("AppName", "task_name", [
       {"action": "open", "target": "AppName"},
       {"action": "click", "target": "Button"},
       {"action": "wait_for", "target": "Result", "timeout": 120},
   ], notes=["..."])
   ```
3. If exists → update if you learned something new
4. Names: snake_case, descriptive
5. Description: one-line, **max 30 words**

## Meta-Workflows (Cross-App Orchestration)

**Pure orchestration** — ONLY `call` steps. No raw actions (open/click/observe).

Rules:
1. Every step = `{"action": "call", ...}`
2. Each call specifies all params
3. Use `output_as` for inter-step data passing

```python
save_meta_workflow("name", [
    {"action": "call", "app": "Chrome", "workflow": "copy_page_content",
     "params": {"url": "..."}, "output_as": "$content"},
    {"action": "call", "app": "WeChat", "workflow": "send_message",
     "params": {"contact": "John", "content": "$content"}},
], description="...")
```

Variables: `$clipboard`, `$output`, `$param.xxx`
Max nesting: 5 levels

## Safety Rules

These exist because of real bugs that sent messages to wrong people.

1. **VERIFY BEFORE SENDING** — OCR chat header to confirm contact. Wrong → ABORT.
2. **Stay within window bounds** — Get bounds first. NEVER click outside target window.
3. **No wrong-app learning** — Click outside target window → don't save as template.
4. **Reject tiny templates** — <30×30 pixels = false matches everywhere.
5. **Template ≠ correct target** — Template match + header verify, not just one.
6. **LLM never provides coordinates** — You decide WHAT to click. Tools provide WHERE.
7. **Never send screenshots to conversation** — Internal only.

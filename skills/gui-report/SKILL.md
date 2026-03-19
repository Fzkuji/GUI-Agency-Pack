---
name: gui-report
description: "Track and report cost/performance of GUI agent tasks. Use at the START and END of every gui-agent workflow to measure duration, token consumption, operation counts, and estimated cost. Also use to view historical task cost data."
---

# GUI Task Report

Track every GUI task's cost: time, tokens, operations, and dollars.

## When to Use

- **BEFORE** any gui-agent task: call `start`
- **DURING** the task: call `tick` after each screenshot/click/learn/detect/image call
- **AFTER** the task completes: call `report` with final token counts
- **On demand**: call `history` to review past task costs

## Commands

All commands use `scripts/tracker.py` in this skill directory.

```bash
TRACKER="python3 ~/.openclaw/workspace/skills/gui-agent/skills/gui-report/scripts/tracker.py"

# 1. Start tracking (get baseline tokens from session_status first)
$TRACKER start --task "CleanMyMac cleanup" --tokens-in 3 --tokens-out 662 --cache-hits 51000

# 2. During task — increment counters as you go
$TRACKER tick screenshots
$TRACKER tick clicks
$TRACKER tick learns
$TRACKER tick image_calls
$TRACKER tick clicks -n 3    # batch increment

# 3. Optional notes
$TRACKER note "Clicked Ignore on quit dialog to protect Discord"

# 4. Final report (get final tokens from session_status)
$TRACKER report --tokens-in 50 --tokens-out 2500 --cache-hits 55000 --model opus

# 5. View history
$TRACKER history
$TRACKER history --limit 20
```

## Token Baseline

Get token counts from `session_status` tool:
- **Before task**: record `Tokens in`, `Tokens out`, and cached tokens
- **After task**: record again, tracker computes the delta

## Cost Models

| Model | Input | Output | Cached Input |
|-------|-------|--------|-------------|
| Claude Opus 4 | $15/M | $75/M | $1.875/M |
| Claude Sonnet 4.5 | $3/M | $15/M | $0.375/M |

## Output Example

```
============================================================
📊 GUI Task Report: CleanMyMac cleanup
============================================================
⏱  Duration:    3.2min
📥 Tokens in:   2.1k (new) + 4.0k (cached)
📤 Tokens out:  1.8k
💰 Est. cost:   $0.1665
🔧 Operations:  5×screenshots, 3×clicks, 1×learns, 5×image_calls
📝 Notes:
   - Clicked Ignore on quit dialog to protect Discord
============================================================
💾 Saved to logs/task_history.jsonl
```

## Integration with gui-agent

In SKILL.md STEP 6 (Report), after the timing line, add the tracker report.
The agent should:
1. Call `session_status` at task start → feed tokens to `tracker.py start`
2. Call `tick` inline with each operation
3. Call `session_status` at task end → feed tokens to `tracker.py report`

## Log Storage

Task history is saved to `skills/gui-report/logs/task_history.jsonl` (one JSON object per line).
Use `history` command to view formatted summary with cumulative cost.

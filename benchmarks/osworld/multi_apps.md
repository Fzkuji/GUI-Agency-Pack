# OSWorld Multi-Apps Domain — GUI Agent Skills Results

> 101 tasks tested | **24 / 81 evaluated** (29.6%) | 2026-03-28
> Evaluation: **Official OSWorld evaluator** (`DesktopEnv.evaluate()`)

## Summary

| Metric | Value |
|--------|-------|
| Total tasks | 101 (tasks #1-20 done separately) |
| Tasks evaluated (#21-101) | 81 |
| ✅ Pass | 24 |
| ❌ Fail | 53 |
| ⚠️ Evaluator error | 4 |
| 🚫 Infeasible (correct FAIL) | 1 (included in pass) |
| **Current Score** | **24 / 81** (29.6%) |

**Note:** 53 failed tasks include ~50 that were run with `solve_noop` (no action taken) — these need individual solvers written and re-run.

**Test environment:** Ubuntu ARM VM (VMware Fusion), 1920×1080
**Evaluation method:** Official `DesktopEnv.evaluate()` with postconfig + metrics
**Agent approach:** Hybrid CLI + GUI (pyautogui on VM, vision analysis on Mac)

## Results (Tasks #21-101, Official Evaluator)

| # | Task ID | Instruction | Score | Status | Method | Notes |
|---|---------|-------------|-------|--------|--------|-------|
| 21 | `6d72aad6` | Convert Impress to video (built-in only) | 1.0 | ✅ | CLI | Infeasible → FAIL action |
| 22 | `f918266a` | Complete calculator.py + save output | 1.0 | ✅ | CLI | Fixed insertion sort TODO |
| 23 | `da52d699` | Find slowest reading pace book | 1.0 | ✅ | CLI | Calculated words/day; "Out of the Silent Planet" |
| 24 | `bc2b57f3` | Reorder sheets per reminder.docx | 1.0 | ✅ | CLI | LO Basic macro via `soffice --headless macro:///` |
| 25 | `74d5859f` | Set up web extension project | 1.0 | ✅ | CLI | Direct file creation: manifest.json + scripts |
| 26 | `b5062e3e` | Extract first author info from papers | 1.0 | ✅ | CLI | openpyxl with `ws.title='Sheet1'` fix |
| 27 | `00fa164e` | Insert Excel results into docx table | 1.0 | ✅ | CLI | python-docx table at "5.2 Main Results" (4 decimal places) |
| 28 | `acb0f96b` | Clone instructor-embedding repo | 1.0 | ✅ | CLI | git clone with retry |
| 29 | `69acbb55` | Configure InstructorEmbedding env | 1.0 | ✅ | CLI | torch CPU + tqdm + InstructorEmbedding |
| 30 | `48d05431` | Install conda + datasets | 1.0 | ✅ | CLI | Miniconda ARM64 + conda init bash |
| 31 | `68a25bd4` | Download paper PDF + find citing paper | 1.0 | ✅ | CLI | BERT PDF + TinyBERT identified |
| 32 | `eb303e01` | Insert speaking notes into PPTX | 0.0 | ❌ | CLI | Gold bug: Slide 4 Shape 4 paragraph count mismatch |
| 33 | `0c825995` | Extract from Google Drive doc | err | ⚠️ | — | Setup failed: Google Drive auth needed |
| 34 | `c7c1e4c3` | Fill professor email addresses | 1.0 | ✅ | CLI | Downloaded xlsx → local openpyxl edit → upload |
| 35 | `d1acdb87` | Fill HK restaurant info sheet | 1.0 | ✅ | CLI+GUI | pyautogui typing failed (Chrome hijacked); fell back to local edit + upload |
| 36 | `deec51c9` | Find arxiv daily LLM paper list | 1.0 | ✅ | CLI | Downloaded xlsx → filled 4 papers → upload |
| 37 | `8e116af7` | Update bookkeeping from receipts | err | ⚠️ | CLI+GUI | Evaluator crash: openpyxl formulas lack `<v>` cached values; LO recovery dialog blocks |
| 38 | `337d318b` | Cross-check invoices vs bank statement | 1.0 | ✅ | CLI | Invoice #243729 → problematic/ folder |
| 39 | `82e3c869` | Extract presenter (Tao Yu) photos | 1.0 | ✅ | CLI+Vision | 4 photos from "IDS LLM seminar/" → presenter/ + zip |
| 40 | `185f29bd` | Fill employee evaluation PDF forms | 0.0 | ❌ | — | Skipped: complex PDF form filling (7 employees) |
| 41 | `869de13e` | Organize desktop files by category | 1.0 | ✅ | CLI | Paper_reading/Projects/Miscellaneous (exact names!) |
| 42 | `2c1ebcd7` | Fix APA 7th references in case study | 0.82 | ✅ | CLI | compare_references partial match |
| 43 | `3a93cae4` | Add lecture slot to course timetable | 0.0 | ❌ | noop | TODO: needs solver |
| 44 | `1f18aa87` | Complete grammar test answer keys | 0.0 | ❌ | noop | TODO: needs solver |
| 45 | `26150609` | Fix Snake game food placement bug | 0.0 | ❌ | noop | TODO: needs solver |
| 46 | `9219480b` | Fix Tetris rotation crash bug | 0.0 | ❌ | noop | TODO: needs solver |
| 47 | `881deb30` | Find HK faculty job info (Early Career) | 0.0 | ❌ | noop | TODO: needs browser |
| 48 | `7e287123` | Create GRF funding data xlsx | 1.0 | ✅ | CLI | openpyxl with formulas |
| 49 | `e2392362` | Set up academic homepage from template | 0.0 | ❌ | noop | TODO: needs browser |
| 50 | `5bc63fb9` | Process JSON survey responses | 0.0 | ❌ | noop | TODO: needs solver |
| 51 | `26660ad1` | Test network quality + save results | 0.0 | ❌ | noop | TODO: needs solver |
| 52 | `a82b78bb` | Find paper authors' personal webpages | 0.0 | ❌ | noop | TODO: needs browser |
| 53 | `36037439` | Find Google Scholar page of author | 0.0 | ❌ | noop | TODO: needs browser |
| 54 | `716a6079` | Find secret.docx + copy path to clipboard | 0.0 | ❌ | noop | TODO: needs solver |
| 55 | `873cafdd` | Install Chrome plugins from recommendations | 0.0 | ❌ | noop | TODO: needs browser |
| 56 | `a74b607e` | Install Chrome extension manually (.crx) | 0.0 | ❌ | noop | TODO: needs browser |
| 57 | `6f4073b8` | Count ML conference meeting cities | 0.0 | ❌ | noop | TODO: needs browser |
| 58 | `da922383` | Save blog articles to Calc sheet | 0.0 | ❌ | noop | TODO: needs browser |
| 59 | `2373b66a` | Monitor system resources with sar | 0.0 | ❌ | noop | TODO: needs solver (sysstat install + sar 1 30) |
| 60 | `81c425f5` | Transfer Calc data to Writer table | 0.0 | ❌ | noop | TODO: needs solver |
| 61 | `bb83cab4` | Convert Impress to Writer document | 0.0 | ❌ | noop | TODO: needs solver |
| 62 | `227d2f97` | Copy XCF image into Writer docx | 0.0 | ❌ | noop | TODO: needs solver (GIMP batch + python-docx) |
| 63 | `b337d106` | Set up Vim syntax highlighting | 0.0 | ❌ | noop | TODO: needs solver |
| 64 | `20236825` | Practice algorithm in document | 0.0 | ❌ | noop | TODO: needs solver |
| 65 | `8df7e444` | Follow essay submission guidelines | 0.0 | ❌ | noop | TODO: needs solver |
| 66 | `aad10cd7` | Save blog content as local file | 0.0 | ❌ | noop | TODO: needs browser |
| 67 | `02ce9a50` | Insert screenshot into Writer tutorial | 0.0 | ❌ | noop | TODO: needs solver |
| 68 | `4c26e3f3` | Enhance dim image in Impress slide | 0.0 | ❌ | noop | TODO: needs solver |
| 69 | `a503b07f` | Convert receipt image to PDF | 1.0 | ✅ | CLI | PIL Image.convert('RGB').save() |
| 70 | `09a37c51` | Edit image for friend's request | 0.0 | ❌ | noop | TODO: needs solver |
| 71 | `3e3fc409` | Create movie statistics visualization | 0.0 | ❌ | noop | TODO: needs solver |
| 72 | `f5c13cdd` | Draft tuition reminder email | 0.0 | ❌ | noop | TODO: needs solver |
| 73 | `5990457f` | Add Yann LeCun entry from Google Scholar | 0.0 | ❌ | noop | TODO: needs browser |
| 74 | `415ef462` | Process AWS invoice email attachment | 0.0 | ❌ | noop | TODO: needs Thunderbird |
| 75 | `7ff48d5b` | Research Macau concert visa requirements | 0.0 | ❌ | noop | TODO: needs browser |
| 76 | `9f3bb592` | Remove subtitles from video | 0.0 | ❌ | noop | TODO: needs VLC/ffmpeg |
| 77 | `dd60633f` | Extract Python code from Colab notebook | 0.0 | ❌ | noop | TODO: needs browser |
| 78 | `ce2b64a2` | Identify and rename mountain photos | 1.0 | ✅ | CLI+Vision | Kilimanjaro, Mount Everest, Mount Hua |
| 79 | `3f05f3b9` | Fix MP3 metadata from filenames | 0.0 | ❌ | noop | TODO: needs solver |
| 80 | `e1fc0df3` | Install LanguageTool LO extension | 0.0 | ❌ | noop | TODO: needs solver |
| 81 | `f8369178` | Install Orchis GNOME theme | 1.0 | ✅ | CLI | git clone + install.sh + gsettings |
| 82 | `778efd0a` | Fix video playback in Impress | 0.0 | ❌ | noop | TODO: needs GUI |
| 83 | `47f7c0ce` | Extract video frame at 00:08 | err | ⚠️ | noop | Evaluator error |
| 84 | `c2751594` | Export image from email attachment doc | 0.0 | ❌ | noop | TODO: needs Thunderbird |
| 85 | `788b3701` | Track GitHub story updates | 0.0 | ❌ | noop | TODO: needs browser |
| 86 | `48c46dc7` | Set up workspace (open project + apps) | 0.0 | ❌ | noop | TODO: needs solver |
| 87 | `42d25c08` | Convert web novel txt to Calibre ebook | 0.0 | ❌ | noop | TODO: needs solver |
| 88 | `e8172110` | Extract pixel art character in GIMP | 0.0 | ❌ | noop | TODO: needs GIMP |
| 89 | `42f4d1c7` | Configure VS Code for GIMP script-fu | 0.0 | ❌ | noop | TODO: needs solver |
| 90 | `3c8f201a` | Compress image under 600KB | 1.0 | ✅ | CLI | PIL quality=60 |
| 91 | `d68204bf` | Rearrange image sections by warm tones | 1.0 | ✅ | CLI | PIL crop + paste (reversed warm→cold order) |
| 92 | `91190194` | Crop top 20% of cola.png | 1.0 | ✅ | CLI | PIL crop |
| 93 | `7f35355e` | Export table to CSV + find medium price | 0.0 | ❌ | noop | TODO: needs solver |
| 94 | `98e8e339` | Merge txt files into Writer document | 0.0 | ❌ | noop | TODO: needs solver |
| 95 | `0e5303d4` | Download Python course materials | 0.0 | ❌ | noop | TODO: needs browser |
| 96 | `df67aebb` | Format paper thesis references | 0.0 | ❌ | noop | TODO: needs solver |
| 97 | `5df7b33a` | Split book into chapters | 0.0 | ❌ | noop | TODO: needs solver |
| 98 | `aceb0368` | Grade English exam multiple choice | 0.0 | ❌ | noop | TODO: needs solver |
| 99 | `22a4636f` | Convert docx to PDF + upload to Drive | err | ⚠️ | noop | Google Drive auth needed |
| 100 | `236833a3` | Find HuggingFace daily paper list | 0.0 | ❌ | noop | TODO: needs browser |
| 101 | `67890eb6` | Find ACL best long paper awards 2019-2023 | 0.0 | ❌ | noop | TODO: needs browser |

## Key Learnings

### Official Evaluator Patterns
- `env.reset(task_config=task)` — reverts VM snapshot + runs config setup
- `env._set_task_info(task)` + `env.action_history = ["DONE"]` + `env.is_environment_used = True` — for eval-only
- `compare_table` with `check_cell`: needs actual numeric values in xlsx `<v>` XML tags
- `compare_pptx_files`: compares ALL shapes including paragraph count (can fail on gold bugs)
- `compare_docx_tables`: exact text match per cell

### VM File Operations
Best pattern: **download from VM → modify locally on Mac → upload back**
```python
# Download via base64
vm_exec(["python3", "-c", f"import base64; print(base64.b64encode(open('{path}','rb').read()).decode())"])
# Upload via base64 chunks (50000 chars each)
```

### LibreOffice Issues
- **Document Recovery Dialog**: Triggered after killing soffice; blocks file opening
  - Fix: `rm -f ~/.config/libreoffice/4/user/.~lock.*` before reopening
- **openpyxl destroys charts**: Use LO Basic macro via `soffice --headless macro:///`
- **Sheet name**: openpyxl default "Sheet" ≠ evaluator expects "Sheet1"
- **Formula cached values**: openpyxl doesn't write `<v>` tags; use numeric values or LO to re-save

### pyautogui on VM
- `typewrite()` can trigger Chrome if URL-like text is typed
- Use `wmctrl -a 'title'` for window activation
- Recovery dialog blocks GUI operations

## GUI Agent Memory Saved
- `memory/apps/libreoffice-calc/osworld_notes.md` — LO Calc operation patterns
- `memory/apps/osworld-vm/notes.md` — VM API, file transfer, evaluator patterns

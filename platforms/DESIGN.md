# Dynamic Platform-Aware Skill Design

## Problem

GUI Agent Skill 需要在不同平台（macOS, Linux, Windows）上使用不同的工具（pynput vs pyautogui, screencapture vs scrot, Cmd vs Ctrl）。静态 SKILL.md 无法根据运行环境动态调整内容，导致：

1. 模型看到不适用于当前平台的工具说明 → 浪费 context + 用错工具
2. 远程操作（VM/SSH）时，host 和 target 平台可能不同
3. 每次都需要手动判断用什么工具

## Design: Code-Driven Skill Activation

### 核心思路

Skill 不再是纯文本，而是**代码驱动的**。激活 skill 时：

1. **检测阶段**：自动运行 `detect.py` 获取平台信息
2. **选择阶段**：根据检测结果选择对应的平台指南
3. **注入阶段**：只将相关内容提供给模型

### 架构

```
gui-agent/
├── SKILL.md                    # 通用流程（平台无关）
├── platforms/
│   ├── detect.py               # 平台检测脚本
│   ├── macos.md                # macOS 工具指南
│   ├── linux.md                # Linux 工具指南
│   └── windows.md              # Windows 工具指南（未来）
├── scripts/
│   ├── agent.py                # CLI 入口
│   ├── activate.py             # ⭐ 新增：skill 激活脚本
│   └── ...
```

### activate.py 的工作流程

```python
#!/usr/bin/env python3
"""
Skill activation script. 
Called when gui-agent skill is loaded.
Outputs platform-specific context for the model.
"""

from platforms.detect import detect_platform
import os

def activate():
    info = detect_platform()
    
    # Read the platform-specific guide
    guide_path = f"platforms/{info['platform_guide']}.md"
    if os.path.exists(guide_path):
        guide = open(guide_path).read()
    else:
        guide = "No platform guide available."
    
    # Output structured context
    print(f"## Current Platform: {info['os_name']} ({info['machine']})")
    print(f"## Display: {info['display_server']}")
    print(f"## Available Tools: {', '.join(info['tools'].keys())}")
    print(f"## Recommended: input={info['recommended_input']}, "
          f"screenshot={info['recommended_screenshot']}")
    print()
    print(guide)

if __name__ == "__main__":
    activate()
```

### SKILL.md 中的引用方式

```markdown
## Platform Setup (MANDATORY FIRST STEP)

Before any GUI operation, run the platform detection:

\`\`\`bash
python3 {baseDir}/scripts/activate.py
\`\`\`

This outputs:
- Current platform and available tools
- Platform-specific guide (input methods, shortcuts, clipboard, etc.)

Read the output and follow the platform-specific instructions.
Do NOT use tools from other platforms.
```

### 远程操作场景

当操作远程机器（VM/SSH）时，有两个平台需要检测：

```python
# Host (where OCR/detection runs)
host_info = detect_platform()  # e.g., macOS

# Target (where GUI operations execute)  
# Run detect.py on the remote machine
target_info = run_remote("python3 detect.py")  # e.g., Linux

# Model gets both:
# - Host platform → for OCR, detection, image analysis
# - Target platform → for input, clipboard, window management
```

### 好处

1. **零冗余**：模型只看到当前平台的工具说明
2. **自动适应**：换到新机器自动检测，不需要改 skill
3. **远程感知**：区分 host 和 target 平台
4. **可扩展**：加新平台只需要加一个 .md 文件

### 实现步骤

1. ✅ `platforms/detect.py` — 已完成
2. ✅ `platforms/macos.md` — 已完成
3. ✅ `platforms/linux.md` — 已完成
4. ⬜ `scripts/activate.py` — 将 detect 结果格式化输出
5. ⬜ SKILL.md 更新 — 加入 "Platform Setup" 作为第一步
6. ⬜ 远程平台检测 — detect.py 支持 SSH/HTTP 远程执行
7. ⬜ 测试 — 在 Mac + Linux VM 上验证完整流程

### 未来：OpenClaw 原生支持

如果 OpenClaw 框架层面支持动态 skill 加载，可以：

```yaml
# SKILL.md frontmatter
---
name: gui-agent
description: ...
activate: scripts/activate.py    # ⭐ 框架自动运行，输出注入 prompt
---
```

这样框架在加载 skill 时自动运行 activate 脚本，将输出作为 skill 内容的一部分注入到模型上下文中。模型不需要手动执行检测——框架替它做了。

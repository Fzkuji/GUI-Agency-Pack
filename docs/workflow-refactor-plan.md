# Workflow 重构规划

> 创建日期：2026-03-24
> 状态：实施中

## 核心改动

### 1. 像素对比判断变化程度

在 `app_memory.py` 新增：

```python
def assess_change(before_img_path, after_img_path):
    """用像素差异判断点击前后页面变化程度。
    
    Args:
        before_img_path: 点击前截图
        after_img_path: 点击后截图
    
    Returns:
        (change_type, change_ratio)
        change_type: "no_change" | "minor_change" | "page_change"
        change_ratio: 0.0 ~ 1.0，变化像素占比
    
    阈值：
        change_ratio < 0.01  → "no_change"（截图几乎一样）
        0.01 ~ 0.10          → "minor_change"（弹窗、toggle、局部刷新）
        > 0.10               → "page_change"（翻页、跳转）
    """
    import cv2
    import numpy as np
    
    before = cv2.imread(before_img_path)
    after = cv2.imread(after_img_path)
    
    # 如果尺寸不同，肯定是大变化
    if before.shape != after.shape:
        return "page_change", 1.0
    
    diff = cv2.absdiff(before, after)
    change_ratio = np.count_nonzero(diff > 30) / diff.size
    
    if change_ratio < 0.01:
        return "no_change", change_ratio
    elif change_ratio < 0.10:
        return "minor_change", change_ratio
    else:
        return "page_change", change_ratio
```

### 2. 集成到 record_page_transition

```python
# 在 record_page_transition 开头先判断变化
change_type, change_ratio = assess_change(before_img_path, after_img_path)

if change_type == "no_change":
    print(f"  ⚠️ No visible change after click (ratio={change_ratio:.4f})")
    return {"change_type": "no_change", "change_ratio": change_ratio}
```

transition 记录加 `change_type` 字段。

### 3. 统一状态识别

`identify_state_by_components()` 改为同时支持旧 `visible` 和新 `defining_components`：

```python
def identify_state_by_components(app_name, visible_components):
    """用组件集合匹配已知状态。
    
    同时检查 state 的 "defining_components"（新格式）和 "visible"（旧格式）。
    用 Jaccard 相似度匹配。
    """
```

### 4. workflow 执行流程

在 `run_workflow()` 里加变化验证：

```python
for action, expected_next_state in path:
    before_img = screenshot()
    click(action)
    time.sleep(0.5)
    after_img = screenshot()
    
    change_type, ratio = assess_change(before_img, after_img)
    
    if change_type == "no_change":
        # 等 1.5 秒再试
        time.sleep(1.5)
        after_img = screenshot()
        change_type, ratio = assess_change(before_img, after_img)
        
        if change_type == "no_change":
            # 重试点击
            click(action)
            time.sleep(1.0)
            after_img = screenshot()
            change_type, ratio = assess_change(before_img, after_img)
            
            if change_type == "no_change":
                return False, "Click had no effect after retry"
    
    # 验证到达预期状态
    current = identify_current_state(...)
    if current != expected_next_state:
        # 状态不对，但页面确实变了，可能走了不同路径
        # fallback 给 LLM
        return False, f"Expected {expected_next_state}, got {current}"
```

### 5. 清理死代码

从 `agent.py` 删除：
- `save_meta_workflow()` / `load_meta_workflow()` — 从未使用
- `detect_workflow_conflict()` — 空实现
- `plan_workflow()` — 读旧格式，没用

### 6. workflow 存储整合

workflow 文件从 `workflows/*.json` 散文件改为 `workflows.json` 单文件（和 meta/components/states/transitions 同级）。

### 7. 更新 gui-workflow/SKILL.md

适配新的变化检测 + 统一状态识别。

## 改动文件

- `scripts/app_memory.py` — assess_change, identify_state_by_components 改造
- `scripts/agent.py` — run_workflow 改造, 清理死代码
- `skills/gui-workflow/SKILL.md` — 文档更新

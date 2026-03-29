# gui-act 设计文档

> 最后更新：2026-03-24

## 核心原则

**每次点击是一个完整的 7 步循环，不能跳步。**

## 7 步循环的设计理由

```
DETECT → MATCH → SAVE → EXECUTE → DETECT AGAIN → DIFF → SAVE TRANSITION
```

### 为什么 SAVE 在 EXECUTE 之前（步骤 3 在步骤 4 之前）

早期设计是先点击再保存。问题：
- 点击后页面跳转，之前的组件全消失了
- 如果点击导致 app 崩溃/关闭，什么都没保存
- 失败的操作也有价值 — 至少知道了这个页面有哪些组件

现在：**先保存组件再点击**。即使点击失败，检测到的组件已经在 memory 里了。

### 为什么必须用 click_and_record / click_component

不允许 raw `click_at(x, y)` 因为：
- 没有记录是哪个组件被点击（transition 记录不了）
- 没有状态图更新（workflow 学不到路径）
- 没有前后截图对比（无法验证结果）

`click_and_record` 和 `click_component` 封装了截图 + 点击 + 验证 + 状态记录的完整流程。

## 坐标来源规则

**坐标只能来自检测结果，不能来自 LLM 猜测。**

允许的来源：
1. OCR `detect_text` 的 cx/cy
2. GPA `detect_icons` 的 cx/cy
3. 模板匹配 `match_component` 的返回坐标

不允许的来源：
- image tool 回复中的坐标描述
- 硬编码的像素位置
- 从文档/记忆中记住的坐标

为什么这么严格：
- LLM 给的坐标误差 > 50px，密集 UI 会点错
- 硬编码坐标在不同分辨率/DPI/窗口位置下全部失效
- 记忆中的坐标会因为页面布局变化而过时

## learn_from_screenshot 的角色

`learn_from_screenshot()` 不只是"学习"——它是每次操作前的**感知函数**。

调用时自动完成：
1. 检测所有组件（GPA + OCR）
2. 保存新组件到 memory
3. 更新所有组件活跃度
4. 触发遗忘机制
5. 识别/创建当前状态
6. 合并相似状态

所以 gui-act 的 "DETECT + SAVE" 步骤就是调用一次 `learn_from_screenshot()`。

## 远程 VM 操作的适配

本机 Mac 和远程 VM 的区别：
- Mac: screencapture → 检测在本地跑
- VM: 通过 HTTP API 下载截图 → 检测在 Mac 上跑 → 点击指令发回 VM

## 坐标系统 — ImageContext

`detect_all()` 返回**图片像素坐标**（原始检测输出，不做转换）。
调用者通过 `ImageContext` 将像素坐标转为屏幕点击坐标。

```python
from scripts.ui_detector import ImageContext

ctx = ImageContext.mac_fullscreen()      # Mac 全屏截图
ctx = ImageContext.mac_window(wx, wy)    # Mac 窗口截图（窗口位置）
ctx = ImageContext.remote()              # VM / 远程截图（1:1）

click_x, click_y = ctx.image_to_click(px_x, px_y)  # 像素 → 点击
px_x, px_y = ctx.click_to_image(click_x, click_y)   # 点击 → 像素
```

### ImageContext 的两个参数

1. **pixel_scale** — 图片像素 / 点击坐标的比值
   - Mac Retina: 2.0（`backingScaleFactor`）
   - Mac 非 Retina / VM: 1.0
2. **origin** — 图片左上角在屏幕中的点击坐标
   - 全屏: (0, 0)
   - 窗口截图: (window_x, window_y)

### 每个工具的坐标空间

| 工具 | 返回坐标 |
|------|---------|
| detect_icons | 图片像素 |
| detect_text | 图片像素 |
| detect_all 输出 | **图片像素** |
| template_match | 图片像素 |
| cv2 图片裁剪 | 图片像素 |
| pynput / pyautogui | 点击空间（用 `ctx.image_to_click()` 转换）|

### 为什么裁剪不会出错

- 检测返回图片像素 → 直接用来裁剪 → 坐标系一致 → 永远正确
- 旧设计的 bug：检测 → 转成点击坐标 → 裁剪时再转回像素 → 转换不对 → 错

### Legacy 兼容

旧函数 `detect_to_click()` / `click_to_detect()` 仍可用（已修正为使用 `backingScaleFactor`），
但新代码应使用 `ImageContext`。

## 操作前后验证

点击后需要验证的原因：
- 点到了错误元素（坐标偏移）
- 弹出了意外的对话框（cookie banner, 登录提示）
- 页面没反应（元素不可点击、被遮挡）
- App 切换了（点击触发了其他 app 的窗口）

验证方式现在由 workflow 的分层策略接管：Level 0 快速模板匹配 → Level 1 完整检测 → Level 2 LLM 判断。

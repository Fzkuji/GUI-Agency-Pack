# gui-observe 设计文档

> 最后更新：2026-03-24

## 核心原则

**先看再做。每个操作必须有视觉依据。**

## 三种视觉方法的分工

### 为什么需要三种方法

单一方法不够：
- OCR 看不到没有文字的图标按钮（三点菜单、关闭按钮）
- GPA 检测到位置但不知道是什么（label 始终是 null）
- image tool 能理解语义但给不了精确坐标

三者互补：
- OCR → 坐标 ✅ + 语义 ✅（文字本身就是语义）
- GPA → 坐标 ✅ + 语义 ❌（需要结合 OCR 或 image tool 识别）
- image tool → 坐标 ⛔ + 语义 ✅（理解页面结构和含义）

### 为什么 image tool 不能提供坐标

LLM 视觉模型看到的是压缩后的图片，内部没有像素级别的空间推理能力。它说"按钮在右上角"是模糊的语义描述，不是 (1200, 50) 这样的精确坐标。实测误差通常 > 50px，在密集 UI 里会点错元素。

### detect_all 统一入口

`detect_all(img_path)` 同时调用 GPA + OCR，返回合并去重的结果。

设计决策：
- **GPA 是必须的底线** — 纯 Python + YOLO，任何平台都能跑
- **OCR 是可选增强** — Mac 有 Apple Vision（最准），其他平台以后可接 Tesseract/PaddleOCR
- OCR 失败时 graceful degradation：只用 GPA 结果，不报错

## Phase 1 / Phase 2 渐进式观察

### 为什么区分两个阶段

Phase 1（全量观察）每次调用 image tool 分析截图，消耗 ~3000 token。如果对一个已经操作过 20 次的页面每次都跑 Phase 1，token 浪费严重。

Phase 2（快速观察）跳过 image tool，只用 OCR + GPA 的文字输出让 LLM 直接判断。在熟悉的页面上这就够了。

### 何时降级回 Phase 1

- OCR/GPA 输出看不懂（不认识的页面）
- 操作后结果不符合预期
- 出现弹窗、错误页面等异常

## 坐标系统 — ImageContext

`detect_all()` 返回**图片像素坐标**（原始检测结果，不做转换）。
调用者通过 `ImageContext` 将像素坐标转为屏幕点击坐标。
裁剪直接用图片像素坐标——不需要任何转换。

```python
from scripts.ui_detector import ImageContext

ctx = ImageContext.mac_fullscreen()      # Mac 全屏（pixel_scale = backingScaleFactor）
ctx = ImageContext.mac_window(wx, wy)    # Mac 窗口（含窗口偏移）
ctx = ImageContext.remote()              # VM / 远程（1:1，无偏移）

click_x, click_y = ctx.image_to_click(el["cx"], el["cy"])
```

| 工具 | 返回坐标 |
|------|---------|
| detect_icons | 图片像素 |
| detect_text | 图片像素 |
| detect_all 输出 | **图片像素** |
| template_match | 图片像素 |
| cv2 图片裁剪 | 图片像素（直接使用） |
| pynput / pyautogui | 点击空间（需 `ctx.image_to_click()` 转换）|

- **Mac Retina**：pixel_scale = 2.0（如 3024×1964 图片，1512×982 点击空间）
- **Mac 非 Retina**：pixel_scale = 1.0
- **远程 VM**：pixel_scale = 1.0, origin = (0, 0)
- pixel_scale 来自 `NSScreen.main.backingScaleFactor`（不再用图片尺寸÷屏幕尺寸计算）

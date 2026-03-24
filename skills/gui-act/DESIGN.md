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

## 坐标系统设计

**以截图为锚。所有坐标都是"截图上的像素坐标"。**

### 为什么不做转换

1. **已验证**：macOS 上 `screencapture` 输出的坐标空间和 `pynput`/`CGEvent` 使用的坐标空间一致
   - 即使在 Retina 显示器上，screencapture 输出的是与系统 UI 坐标一致的像素
   - pynput 使用的也是同一坐标空间
   - 所以检测坐标可以直接传给 `click_at`，不需要任何缩放

2. **验证方式**：在不同显示模式下（1512×982、1800×1169 等）测试，screencapture 输出的分辨率始终匹配 pynput 的坐标空间

3. **远程 VM**：VM 上截图像素和 pyautogui 坐标也是 1:1，原理相同

### 不同设备的适配策略

`ui_detector.get_screenshot_scale()` 返回截图像素和点击坐标空间的比例。
- 目前返回 1.0（已在 Mac 各种显示模式下验证）
- 如果将来某设备不匹配，这个函数可以做自动校准
- 校准方式：截图 → 比较截图尺寸和已知屏幕信息 → 计算比例

### `retina` 参数

`learn_from_screenshot` 等函数保留了 `retina` 参数（向后兼容），但它不再生效。
坐标始终按原始截图像素存储和使用。

## 远程 VM 操作的适配

本机 Mac 和远程 VM 的区别：
- Mac: screencapture → 检测在本地跑
- VM: 通过 HTTP API 下载截图 → 检测在 Mac 上跑 → 点击指令发回 VM

所有平台上坐标都是截图像素，不需要区分 Retina/非 Retina。

## 操作前后验证

点击后需要验证的原因：
- 点到了错误元素（坐标偏移）
- 弹出了意外的对话框（cookie banner, 登录提示）
- 页面没反应（元素不可点击、被遮挡）
- App 切换了（点击触发了其他 app 的窗口）

验证方式现在由 workflow 的分层策略接管：Level 0 快速模板匹配 → Level 1 完整检测 → Level 2 LLM 判断。

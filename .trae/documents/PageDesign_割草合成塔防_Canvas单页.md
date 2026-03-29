# 页面设计与交互说明（Desktop-first）

## 全局设计规范
### Layout
- 页面为垂直三段式：上“战斗区(Canvas)”、中“5x5 网格”、下“底部 UI 操作条”。
- 使用 CSS Grid/ Flex 组合：
  - 外层容器 `display:flex; flex-direction:column;` 固定整体高度（视口优先）。
  - 战斗区使用固定比例画布（如 16:9 或自适应宽度，高度占主要空间）。
  - 网格使用 `display:grid; grid-template-columns: repeat(5, 1fr);`。
  - 底部 UI 使用 `display:flex; justify-content:space-between; align-items:center;`。

### Meta Information
- title: 割草合成塔防
- description: 购买随机塔、拖拽合成升级、自动射击拦截下落敌人。
- Open Graph: 使用与 title/description 一致，image 可后续补充。

### Global Styles (Design Tokens)
- 背景色：#0B1020（深色）
- 面板色：#141B2D
- 强调色：#5AE4A8（可用于按钮/高亮）
- 危险色：#FF5A6A（失败/警告）
- 字体：系统默认 sans-serif；数值使用等宽字体（可选）
- 文字：主文字 #E6EAF2，次级 #A8B0C2
- 按钮：圆角 10px；hover 提亮；disabled 降低透明度并禁用点击
- 动效：交互反馈以 120–180ms 过渡为主（hover/按下/拖拽阴影）

---

## 页面：游戏主界面（index.html）

### Page Structure
1) 顶部：战斗区（Canvas）
2) 中部：5x5 塔网格（HTML 组件层，或 Canvas 内辅助绘制；建议 HTML 网格便于拖拽）
3) 底部：UI 操作条（购买/金币/状态/控制）

### Sections & Components

#### 1) 顶部战斗区（Canvas）
- 元素
  - 主 Canvas：绘制敌人、子弹/射线、命中效果、底线。
  - 叠层 HUD（可选 div 绝对定位）：波次/时间、当前加速等级、FPS(开发态)。
- 交互/状态
  - 自动运行：敌人生成→下落→加速。
  - 反馈：
    - 敌人受击闪烁/血条变化。
    - 击杀显示金币浮字（可选）。
  - 失败条件：敌人触底线时显示“失败遮罩层”。

#### 2) 中部 5x5 网格（塔管理区）
- 布局
  - 25 个格子等宽等高卡片；格子间距 8–10px。
  - 每格展示：塔图标/颜色块、等级角标（如 Lv.1）。
- 拖拽交互（核心）
  - 拖起：塔卡片提升层级并显示阴影；原格子显示占位态。
  - 放下规则：
    1. 目标为空格：完成移动。
    2. 目标为“同类型+同等级”：触发合成（消耗两座塔→生成高一级塔）。
    3. 其他情况：回弹到原位（或实现交换；二选一且全程一致）。
  - 合成反馈：合成瞬间缩放/闪光；新塔等级更新。
- 状态提示
  - 网格已满：购买按钮提示“无空位”。

#### 3) 底部 UI 操作条
- 左侧：金币显示
  - 文案示例：金币：123
  - 金币不足时购买按钮置灰并提示。
- 中间：主操作按钮
  - “购买随机塔”按钮：显示价格（如 20）并支持连点购买（需金币与空位）。
- 右侧：控制区
  - “暂停/继续”切换按钮
  - “重开”按钮
- 弹层/提示
  - Toast 文案（短）：金币不足、格子已满、合成成功。
  - 失败遮罩：
    - 标题：失败
    - 次级信息：到达波次/击杀数/金币（若有统计则展示；没有就仅给重开按钮）
    - 主按钮：重开

### Responsive Behavior（简述）
- Desktop-first：整体居中，最大宽度建议 960–1200px。
- 小屏时：战斗区高度优先保证可玩；网格缩放为更紧凑间距；底部 UI 允许换行或两行布局。

### 关键交互状态清单
- 按钮：default / hover / active / disabled
- 塔卡片：idle / dragging / merge-available（目标可合成高亮） / invalid-drop（抖动回弹）
- 游戏：running / paused / gameover
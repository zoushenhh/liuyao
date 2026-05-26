# 坚六爻 Web 重构设计文档

## 1. 概述

将现有 Streamlit 单体应用重构为前后端分离架构，部署到 GitHub Pages + Render。

### 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vite 5 + React 18 + React Router 6 + Tailwind CSS 3 |
| 后端 | FastAPI + Pydantic + uvicorn |
| 部署 | 前端: GitHub Pages / 后端: Render |

### 项目结构

```
apps/
  web/          # Vite React 前端
  api/          # FastAPI 后端
ichingshifa/    # 核心占卜库 (保持不变)
docs/
```

---

## 2. 页面与路由

```
/          → HomePage     (摇卦向导)
/result    → ResultPage   (卦象 + AI 解读 + 文档)
/settings  → SettingsPage (AI 配置)
```

### 2.1 首页 (HomePage)

摇卦向导式界面：
- 日期时间选择器 (DatePicker + TimePicker)
- 摇卦指南 expander (如何用硬币摇卦)
- 六爻选择器: 2 列网格 (手机) / 3 列 (桌面), 从初爻到上爻
- 问题输入 textarea
- "生成排盘" 按钮 (朱砂红, 全宽, min 48px)

### 2.2 结果页 (ResultPage)

摇卦完成后跳转到此页。顶部为固定卡片，底部为 3 个 Tab:

- **卦象 Tab**: 固定高度卡片，排盘内容在卡片内滚动
- **AI 解读 Tab**: 问题输入 + 生成按钮 + AI 结果 + 复制/下载
- **文档 Tab**: 占诀 / 古占例 / 日志 (3 个子 Tab 或列出)

顶部操作栏: 重新摇卦按钮

### 2.3 AI 配置页 (SettingsPage)

表单式页面:
- Base URL, Model, API Key (password)
- Temperature slider (0.0-1.0)
- System Prompt textarea
- User Prompt Template textarea
- 高级选项: Max Tokens, Timeout, Max Retries
- 保存 / 重置 / 返回 按钮

---

## 3. API 设计

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | /api/health | 健康检查 |
| POST | /api/cast | 生成排盘 |
| POST | /api/interpret | AI 解读 |
| POST | /api/validate-api-key | 验证 API Key 有效性 |
| GET | /api/texts | 获取文档列表 |
| GET | /api/texts/{name} | 获取指定文档内容 |

---

## 4. UI 设计规范

### 配色

- 底色: 宣纸米白 `#F7F3E8`
- 主色: 朱砂红 `#9E2A2B`
- 点缀: 鎏金 `#D4AF37`
- 文字: `#2B2B2B`

### 字体

- 标题: SimSun / 宋体 / serif
- 正文: system sans-serif

### 响应式断点

- ≤480px: 手机竖屏, 列堆叠
- 481-768px: 平板 / 手机横屏
- ≥769px: 桌面

### 交互规范

- 最小触摸区域: 44px
- 按钮: min-height 48px, 全宽(手机)
- Tab: 横向可滚动 (手机)

---

## 5. UX 改进总结

| 问题 | 原设计 | 新设计 |
|---|---|---|
| AI配置按钮重复 | 首页/结果页/Tab 内多个 | 统一到顶部右侧齿轮图标 |
| 爻选择占用空间 | 6 个竖向下拉框 | 2-3 列网格布局 |
| 排盘内容溢出 | pre code block | 自定义 Flexbox 组件 |
| 导航混乱 | 无导航栏 | 全局 sticky Header + 返回按钮 |

---

## 6. 安全

- API Key 存 localStorage, 仅发送到用户指定的后端
- 后端校验 Base URL 防 SSRF
- /api/interpret 添加 rate limiting
- 不在日志中输出 API Key 或请求体

---

## 7. 迁移策略

1. 保留 `ichingshifa/` 和 `ai_module.py` 不变
2. 新建 `apps/api/` FastAPI 后端封装现有逻辑
3. 新建 `apps/web/` Vite React 前端
4. 测试完毕后可移除 Streamlit 依赖

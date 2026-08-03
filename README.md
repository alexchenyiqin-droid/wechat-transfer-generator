# 微信转账截图生成器

像素级复刻微信转账成功页面截图，支持自定义收款方、金额、说明、时间。

基于 Playwright + Chromium 无头浏览器渲染，输出高清 PNG。

## 功能

- 网页端实时预览 + 表单编辑
- Playwright 服务端渲染，输出高清截图（2x Retina）
- 支持自定义：收款方、金额、转账说明、转账时间、收款时间

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt
playwright install chromium

# 启动截图服务
python screenshot_server.py

# 打开预览页面
open wechat-transfer-generator.html
```

## 文件说明

- `wechat-transfer-generator.html` — 前端预览和编辑界面
- `screenshot_server.py` — Flask + Playwright 截图服务

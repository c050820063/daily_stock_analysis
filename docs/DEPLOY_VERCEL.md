# 使用 Vercel 部署指南

本项目已配置 Vercel 部署支持，可以将股票分析系统的 WebUI 和 Bot Webhook 服务部署到 Vercel Serverless 环境。

## ⚠️ 重要说明

Vercel 是 Serverless 环境，与本地运行有以下区别：
1. **无后台调度**：无法运行 `main.py` 中的 `schedule` 循环任务。需要使用 Vercel Cron 或外部定时触发器。
2. **无长连接 Bot**：钉钉/飞书的 Stream 模式（长连接）无法在 Vercel 上运行。**必须使用 Webhook 模式**。
3. **执行时间限制**：普通版 Vercel 函数最长执行 10 秒（Pro 版 60 秒）。大盘复盘耗时较长，可能会超时。建议仅用于任务分发或使用异步队列（如果架构支持）。

---

## 🚀 快速部署

### 1. 准备工作
- 注册 [Vercel](https://vercel.com/) 账号
- 安装 Vercel CLI（可选，也可通过 GitHub 集成部署）: `npm i -g vercel`

### 2. 通过 GitHub 部署 (推荐)
1. 将本项目推送到 GitHub 仓库。
2. 在 Vercel 控制台点击 "Add New..." -> "Project"。
3. 导入你的 GitHub 仓库。
4. **Environment Variables**: 在配置页面添加必要的环境变量（参考 `.env` 文件），主要包括：
   - `OPENAI_API_KEY` / `GEMINI_API_KEY`: AI 分析密钥
   - `FEISHU_APP_ID`, `FEISHU_APP_SECRET`: 飞书配置 (如果使用)
   - `DINGTALK_...`: 钉钉配置 (如果使用)
   - `TAVILY_API_KEY` / `SERPAPI_API_KEY`: 搜索服务密钥
5. 点击 **Deploy**。

### 3. 配置 Bot Webhook
由于无法使用 Stream 模式，你需要配置 Bot 平台向 Vercel 发送 Webhook。

#### 飞书/Lark
1. 进入 [飞书开放平台](https://open.feishu.cn/)。
2. 在应用配置中找到 **事件订阅**。
3. 配置 **请求网址 URL** 为: `https://你的项目域名.vercel.app/bot/feishu`
4. 这里的 `Decrypt Key` 和 `Verification Token` 需要添加到 Vercel 环境变量中。

#### 钉钉
1. 在钉钉机器人设置中使用 **Outgoing 机制** 或 **企业内部机器人 Webhook**。
2. 设置回调地址为: `https://你的项目域名.vercel.app/bot/dingtalk`

---

## ⏰ 设置定时任务 (Cron Jobs)

由于没有本地调度器，我们需要利用 Vercel Cron 来触发每日分析。

1. 在项目根目录创建 `vercel.json` (项目中已包含此文件)。
   ```json
   {
     "crons": [
       {
         "path": "/analysis?type=daily",
         "schedule": "0 17 * * 1-5"
       }
     ]
   }
   ```
   *(注意：上述配置表示每天下午 5 点（UTC时间，需换算为北京时间）执行。由于 Vercel Cron 免费版限制，建议根据实际情况通过外部 Cron (如 GitHub Actions) 调用 HTTPS 接口)*

2. 或者，使用 Vercel 的 WebUI 面板手动触发，或使用 Postman 定时调用 `/analysis` 接口。

## 🛠 文件说明
- `vercel.json`: Vercel 路由配置，将所有 API 请求转发给 Python 处理函数。
- `api/index.py`: Serverless 函数入口适配器，将 Vercel 的请求桥接到项目的 `WebRequestHandler`。


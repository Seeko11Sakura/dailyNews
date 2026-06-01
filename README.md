# dailyNews

一个反算法、随机推荐内容的信息流平台。

## 项目功能简介

用户先选择感兴趣的领域。系统每天 8 点抓取当天最新资讯并生成 AI 短概览，用户打开 App 后直接查看当天简报，也可以探索新的领域并收藏内容。

## 技术架构

- 移动端：Expo + React Native，负责引导页、今日简报、探索页、收藏页和设置页。
- 后端：FastAPI，负责领域、今日简报、文章详情、抓取触发、抓取状态和单篇文章爬虫预览接口。
- 数据库：Supabase，保存文章、用户选择、阅读记录和收藏记录。
- 内容抓取：12 个兴趣领域都有来源配置，当前主流程使用网页爬虫，先从列表页找文章链接，再打开详情页提取正文、发布时间和图片。
- AI 分类：抓取后会让 AI 判断文章最适合展示在哪个领域，减少跨模块重复展示。
- AI 概览：抓取后调用兼容 OpenAI 的接口生成短概览，保存到 `articles.ai_overview`。
- 图片存储：文章入库后抓取原文图片，上传到 Supabase Storage，并把图片关系写入 `article_images`。
- 每日任务：后端启动后注册后台任务，每天 8 点自动覆盖全部来源并生成当天简报，慢来源会超时跳过。

## 本地运行方法

后端：

```powershell
cd D:\Java_program\dailyNews\dailyNews\apps\api
..\..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

移动端（Expo）：

```powershell
cd D:\Java_program\dailyNews\dailyNews\apps\mobile
npx expo start --host lan --port 8083
```

- `--host 0.0.0.0` 让后端监听所有网卡，手机可访问
- `--host lan` 让 Expo 使用局域网 IP（手机测试需要和电脑同一 WiFi）
- 端口 8001 / 8083 避免与系统其他服务冲突
- 前端 API 地址可用 `EXPO_PUBLIC_API_BASE_URL` 覆盖；不设置时默认连接本地局域网后端。

图片存储相关环境变量：

```text
ARTICLE_IMAGE_BUCKET=article-images
ARTICLE_IMAGE_MAX_PER_ARTICLE=1
ARTICLE_IMAGE_MAX_BYTES=5242880
ARTICLE_IMAGE_CRAWL_ENABLED=false
SOURCE_FETCH_CONCURRENCY=4
SOURCE_FETCH_TIMEOUT_SECONDS=60
SOURCE_ARTICLE_LIMIT=10
DAILY_DIGEST_TIER=
DAILY_IMAGE_BACKFILL_LIMIT=30
```

- 正式采集会默认打开原文页补全文、标题、发布时间和图片，让 AI 概览基于原文生成。
- `ARTICLE_IMAGE_CRAWL_ENABLED=false` 只影响旧的补图兜底逻辑；正式采集已有详情页图片时会直接使用。
- `DAILY_IMAGE_BACKFILL_LIMIT` 控制每日任务后最多给多少篇无图文章补封面。

## 部署方法和命令

推荐部署方式：

- 前端 Web：Cloudflare Pages
- 后端 API：Render Web Service
- 每日 8 点任务：Render Cron Job
- 数据库和图片：Supabase

Render 部署：

```text
Blueprint 文件：render.yaml
后端根目录：apps/api
启动命令：uvicorn app.main:app --host 0.0.0.0 --port $PORT
定时任务：每天 00:00 UTC，即北京时间 8 点
```

Render 需要在控制台补充这些环境变量：

```text
SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY
SUPABASE_ANON_KEY
AI_API_KEY
```

Cloudflare Pages 部署：

```text
构建命令：pnpm --filter @dailynews/mobile build:web
输出目录：apps/mobile/dist
环境变量：EXPO_PUBLIC_API_BASE_URL=https://你的-render-后端地址
```

App 打包：

```powershell
cd D:\Java_program\dailyNews\dailyNews\apps\mobile
npx eas build --profile preview --platform android
```

`preview` 会生成 Android APK，适合先安装测试；`production` 会生成 Android App Bundle，适合后续上架。

数据库需要执行：

```sql
apps/api/app/core/migrations/20260529_add_article_images.sql
apps/api/app/core/migrations/20260529_add_article_classification.sql
```

## 测试方法和常用命令

```powershell
pnpm --filter @dailynews/mobile test
pnpm --filter @dailynews/shared test
```

后端测试：

```powershell
cd D:\Java_program\dailyNews\dailyNews\apps\api
pytest
```

前端 Web 构建：

```powershell
pnpm --filter @dailynews/mobile build:web
```

手动生成当天简报：

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8001/digest/generate" -Method Post
```

查看每日任务状态：

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8001/digest/job/status"
```

补齐当天文章封面：

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8001/images/backfill" -Method Post -ContentType "application/json" -Body '{"domain_id":"technology","date":"2026-05-30","limit":10}'
```

试抓单篇文章：

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8001/crawl/article" -Method Post -ContentType "application/json" -Body '{"url":"https://example.com/news/1"}'
```

试跑一个新网站来源：

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8001/sources/trial" -Method Post -ContentType "application/json" -Body '{"url":"https://example.com","domain_id":"technology","limit":5}'
```

## 搜索记录

暂无外部搜索记录。

## 已完成功能列表

- 引导页领域选择
- 今日简报信息流
- 阅读详情弹窗
- 探索页抽卡
- 收藏页和设置页
- 网页爬虫抓取
- URL 去重和标题折叠
- Supabase 文章读取
- AI 短概览入库
- AI 二次分类入库
- 抓取候选文章质量过滤
- 每天 8 点自动生成当天简报
- 单篇文章标题、正文和图片地址爬虫预览
- 新网站来源试跑接口
- 文章图片上传 Supabase Storage 并保存图片记录
- 已入库文章封面图补齐
- 每日抓取后自动补齐当天文章封面
- 今日页按文章发布时间筛选当天内容
- 全领域手动抓取和网页兜底识别
- 无图文章默认封面占位，避免卡片布局空缺
- Cloudflare Pages + Render + EAS 打包配置

## 待办事项

- 给历史文章补生成 `ai_overview`
- 在 Render 和 Cloudflare 控制台填入正式环境变量并创建服务

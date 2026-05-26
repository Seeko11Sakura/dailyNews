# dailyNews

一个反算法、随机推荐内容的信息流平台。

## 项目功能简介

用户先选择感兴趣的领域，然后每天查看按领域整理的短资讯卡片，也可以探索新的领域并收藏内容。

## 技术架构

- 移动端：Expo + React Native，负责引导页、今日简报、探索页、收藏页和设置页。
- 后端：FastAPI，负责领域、今日简报、文章详情、抓取触发和抓取状态接口。
- 数据库：Supabase，保存文章、用户选择、阅读记录和收藏记录。
- 内容抓取：RSS 和网页抓取两种方式，抓到后去重并写入 Supabase。
- AI 概览：抓取后调用兼容 OpenAI 的接口生成短概览，保存到 `articles.ai_overview`。

## 本地运行方法

后端：

```powershell
cd D:\Java_program\dailyNews\dailyNews\apps\api
..\..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

移动端：

```powershell
cd D:\Java_program\dailyNews\dailyNews
pnpm --filter @dailynews/mobile start
```

## 部署方法和命令

当前没有完整部署脚本，先按本地方式分别启动后端和移动端。

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

## 搜索记录

暂无外部搜索记录。

## 已完成功能列表

- 引导页领域选择
- 今日简报信息流
- 阅读详情弹窗
- 探索页抽卡
- 收藏页和设置页
- RSS/网页抓取
- URL 去重和标题折叠
- Supabase 文章读取
- AI 短概览入库

## 待办事项

- 在 Supabase 执行 `apps/api/app/core/migrations/20260526_add_ai_overview.sql`
- 给历史文章补生成 `ai_overview`

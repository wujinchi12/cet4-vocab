# CET-4 词汇学习 — 部署指南

## 前置条件
- GitHub 账号
- Vercel 账号 (https://vercel.com)
- Railway 账号 (https://railway.app)

## 步骤 1: 推送代码到 GitHub

```bash
# 在项目根目录 cet4-vocab/
git remote add origin https://github.com/你的用户名/cet4-vocab.git
git push -u origin master
```

## 步骤 2: 部署后端到 Railway

1. 打开 https://railway.app，点击 "New Project" → "Deploy from GitHub repo"
2. 选择 `cet4-vocab` 仓库
3. Railway 会自动检测 Python 项目 (runtime.txt → Python 3.12)
4. 设置环境变量 (Settings → Variables):
   - `SECRET_KEY`: 一个随机字符串 (建议用 `openssl rand -hex 32` 生成)
   - `DATABASE_URL`: `sqlite:///./cet4_vocab.db` (如需持久化，挂载 Volume 后改为 `sqlite:////data/cet4_vocab.db`)
   - `CORS_ORIGINS`: `https://你的vercel域名.vercel.app`
5. 设置 Start Command: `cd backend && gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT`
6. 点击 Deploy
7. 记下 Railway 分配的域名 (如 `cet4-vocab-api.up.railway.app`)

## 步骤 3: 部署前端到 Vercel

1. 打开 https://vercel.com，点击 "Add New..." → "Project"
2. 选择 `cet4-vocab` 仓库
3. 配置:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. 设置环境变量 (Settings → Environment Variables):
   - `VITE_API_BASE`: `https://你的railway域名/api` (例如 `https://cet4-vocab-api.up.railway.app/api`)
5. 点击 Deploy
6. 记下 Vercel 分配的域名 (如 `cet4-vocab.vercel.app`)

## 步骤 4: 更新 CORS 和重新部署

1. 在 Railway 环境变量中更新 `CORS_ORIGINS` 为你的 Vercel 域名
2. 重新部署 Railway (或等待自动重启)
3. 在 Vercel 中重新部署以确认配置

## 步骤 5: 数据库初始化

部署完成后，Railway 后端会自动创建数据库表。如需导入词汇数据:

```bash
# 在 Railway 终端中 (或本地连接 Railway 数据库后)
cd backend
python scripts/seed_words.py
```

注意: 首次部署时如果数据库文件不存在，`Base.metadata.create_all()` 会自动创建表结构。词汇数据需要手动导入或用 seed_words.py 脚本。

## 可选: 自定义域名

- Vercel: Settings → Domains → 添加你的域名
- Railway: Settings → Networking → Public Networking → Custom Domain

## 可选: 持久化 SQLite 数据库 (Railway)

Railway 的免费实例会定期重启，文件系统不持久。建议:
1. 在 Railway 中挂载 Volume (Settings → Volumes)，挂载到 `/data`
2. 将 `DATABASE_URL` 改为 `sqlite:////data/cet4_vocab.db`
3. 或使用 Railway 的 PostgreSQL 插件，更新 `DATABASE_URL` 为 PostgreSQL 连接串

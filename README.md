# MergeTowerDefense

一个 Canvas 单页塔防原型（前端 `index.html` + 后端 `FastAPI`）。

## 运行环境

- Python 3.10+（推荐）
- Node.js（可选，用于本地起静态页面服务）

## 启动后端（API）

后端用于提供配置与存档接口：

- `GET /api/config`
- `POST /api/save`
- `GET /api/load/{user_id}`

安装依赖并启动：

```bash
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000
```

启动后可访问：

- http://127.0.0.1:8000/api/health
- http://127.0.0.1:8000/api/config

## 启动前端（页面）

前端是单文件页面 `index.html`。页面默认会请求 `http://127.0.0.1:8000` 的后端接口（见 `index.html` 内 `API_BASE` 常量）。

推荐用本地静态服务器打开（避免浏览器对本地文件/跨域的一些限制）：

### 方式 A：用 Python 起静态服务

```bash
python -m http.server 5173
```

然后打开：

- http://127.0.0.1:5173/

### 方式 B：用 Node.js 起静态服务

```bash
node -e "const http=require('http');const fs=require('fs');const path=require('path');const root=process.cwd();http.createServer((req,res)=>{let p=req.url.split('?')[0];if(p==='/'||p==='/index.html')p='/index.html';const fp=path.join(root,p);fs.readFile(fp,(err,data)=>{if(err){res.statusCode=404;res.end('not found');return;}res.setHeader('Content-Type',fp.endsWith('.html')?'text/html; charset=utf-8':'text/plain; charset=utf-8');res.end(data);});}).listen(5173,'127.0.0.1',()=>console.log('http://127.0.0.1:5173/'));setInterval(()=>{},1<<30);"
```

## 常见问题

- 页面提示 “配置加载失败，使用本地默认值”：说明后端没有启动，或 `API_BASE` 指向的地址不可达。
- 想改后端地址：直接修改 `index.html` 中的 `API_BASE`。


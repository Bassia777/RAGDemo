# RAGDemo

一个用于逐层学习 Wiki RAG 的本地透明实现。

## 当前阶段

当前只实现：手动 SSO 登录、保存本地浏览器会话、抓取一个白名单 Wiki 页面。

## 环境准备

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e '.[dev]'
playwright install chromium
cp config/example.yaml config/local.yaml
```

编辑 `config/local.yaml`，填写真实 Wiki 域名和允许抓取的路径前缀。不要提交该文件。

## 登录与抓取一个页面

先登录并保存本地会话：

```bash
source .venv/bin/activate
ragdemo --config config/local.yaml login
```

复制一个允许的 Wiki 页面 URL，然后执行：

```bash
wiki_page_url="$(pbpaste)"
ragdemo --config config/local.yaml fetch "$wiki_page_url"
```

`config/local.yaml`、`secrets/`、`data/` 和真实 URL 清单都属于本地数据，不提交到 Git。

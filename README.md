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

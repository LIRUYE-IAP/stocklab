# StockLab Visual Prototype

面向个人投资者的 A 股研究与交易辅助平台。项目已加入可配置行情后端：iFinD QuantAPI 为盘中主源，Tushare 为具备相应权限时的历史/降级数据源，Mock 为明确标记的演示模式。Technical、Behavior、市场统计和回测仍含演示研究数据。

## 启动前端

```bash
pnpm install
pnpm dev
```

构建验证：

```bash
pnpm build
```

演示账户：`demo` / `demo1234`，也可在登录页直接点击“进入演示账户”。

## 启动数据后端

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

默认没有凭据时返回明确标记的演示数据。历史数据通过 Tushare 同步到数据库；实时行情通过 iFinD 进入 Redis/Memory Cache，再由 WebSocket 推送。所有 Token 只放在 `backend/.env`，不要使用 `VITE_` 前缀，也不要提交到版本库。

正式数据库与缓存可用：

```bash
docker compose up -d
```

当前开发模式也支持 SQLite + 内存 Cache。真实联调的配置、同步命令和验收顺序见 [docs/REAL_DATA_RUNBOOK.md](docs/REAL_DATA_RUNBOOK.md)。

后端检查：

```bash
set PYTHONPATH=backend
python -m pytest backend/tests -q
```

详细数据边界和接口见 [docs/REALTIME_DATA.md](docs/REALTIME_DATA.md)。

## 量化实验室

访问 `/quant` 可体验完整的虚拟量化交易流程。该模块只进行 Paper Trading，不连接券商或真实资金；当前订单、成交和绩效均为演示数据。实现范围与正式化接入点见 [docs/QUANT_LAB.md](docs/QUANT_LAB.md)。

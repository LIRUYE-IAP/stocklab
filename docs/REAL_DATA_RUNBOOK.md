# StockLab 真实数据联调手册

## 1. 凭据放在哪里

复制 `backend/.env.example` 为 `backend/.env`，只在本机填写：

```dotenv
DATA_MODE=hybrid
HISTORY_PROVIDER=tushare
REALTIME_PROVIDER=ifind
TUSHARE_TOKEN=你的_Tushare_Token
IFIND_REFRESH_TOKEN=你的_iFinD_Refresh_Token
IFIND_ACCESS_TOKEN=
```

不要把 Token 写进 Vue、截图、聊天、日志或 Git。`backend/.env` 已被 `.gitignore` 忽略。通常只需要长期保存 refresh token，access token 由服务端管理；如果账号只提供临时 access token，也可填入对应项。

## 2. 数据库和缓存

正式推荐：

```powershell
docker compose up -d
```

它会启动 PostgreSQL 与 Redis。当前开发机没有检测到 Docker，因此工程默认还能使用 `backend/stocklab.db` 和内存 Quote Cache 做代码验证；这不等价于正式部署。

如使用容器，将 `.env` 保持为：

```dotenv
DATABASE_URL=postgresql+psycopg://stocklab:stocklab_local_only@127.0.0.1:5432/stocklab
QUOTE_CACHE_BACKEND=redis
REDIS_URL=redis://127.0.0.1:6379/0
```

## 3. 安装并启动

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

另开终端：

```powershell
pnpm install
pnpm dev
```

## 4. 小范围历史数据联调

严格从铜陵有色和最近 30 个交易日开始：

```powershell
python scripts/sync_stock_basic.py
python scripts/sync_trade_calendar.py --start 20260801 --end 20260909
python scripts/backfill_market_data.py SZ.000630 --start 20260801 --end 20260909
python scripts/check_data_health.py
```

然后检查：

```text
http://127.0.0.1:8000/api/v1/stocks/search?q=000630
http://127.0.0.1:8000/api/v1/stocks/SZ.000630/daily?adjust=qfq
http://127.0.0.1:5173/stock/SZ.000630
```

## 5. 实时行情联调

```powershell
python scripts/test_realtime_provider.py SZ.000630
```

再打开设置页确认 iFinD、Redis 和最近行情时间。iFinD 指标名和权限必须以你的账号“超级命令”返回为准；默认仅请求已经确认的 `open,high,low,latest`，未返回的字段显示为空。

## 6. 验收顺序

1. 铜陵有色基础资料入库。
2. raw/qfq/hfq 日 K 可读。
3. MA/MACD/RSI/价格位置生成。
4. iFinD 单只 Quote 成功。
5. Redis 出现 `quote:SZ.000630` 且 TTL 为 120 秒。
6. WebSocket 推送价格，断线后按 1/2/5/10/30 秒退避重连。
7. 自选与持仓只订阅可见股票。
8. Quant Lab 使用候选池、持仓和待成交订单行情驱动虚拟成交。

在这八步通过前，不扩到全市场，也不声称真实数据已经接通。

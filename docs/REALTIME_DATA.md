# StockLab 真实数据层

更新日期：2026-09-09。

## 当前结论

工程已经完成真实数据接入的代码通路，但本机尚未配置 Tushare 或 iFinD 凭据，所以当前运行状态仍是明确标记的 Mock。测试通过表示映射、存储、API 和 WebSocket 契约可用，不代表第三方账号已经联调成功。

```text
Tushare → HistoryMarketProvider → 校验/标准化 → PostgreSQL/SQLite → REST → Vue
iFinD   → RealtimeMarketProvider → Redis/Memory → REST/WebSocket → Vue
实时 Quote → Strategy Universe → Risk Engine → Paper Broker（仅虚拟交易）
```

前端不接触供应商 Token，也不会直接请求第三方接口。

## 已实现

- Provider 抽象、统一代码 `SH.600000` / `SZ.000630` / `BJ.xxxxxx`。
- Tushare：股票基础信息、交易日历、日线、Daily Basic、复权因子、每日涨跌停、历史名称/ST 状态。
- 原始日线、每日估值、复权因子、涨跌停、ST、数据任务、数据状态和质量错误表。
- 日线幂等写入、OHLC/非负量额校验、有限指数退避。
- raw/qfq/hfq K 线 API，以及 MA、MACD、RSI、Technical Score、价格位置的日级计算。
- iFinD access/refresh token 管理、实时 Quote 映射、Memory/Redis 缓存、REST 与 WebSocket。
- 行情新鲜度与 PRE_MARKET/OPEN/LUNCH_BREAK/CLOSED/STALE/OFFLINE 状态。
- 数据健康页只显示配置状态和数据统计，不暴露 Token。

## 单位规则

StockLab 内部统一使用：成交量 `share`、成交额/市值 `CNY`。Tushare 日线 `vol` 的供应商单位为手、`amount` 为千元，因此入库时分别乘以 100 和 1,000；`daily_basic` 的股本和市值字段按万元/万股口径转换。Tushare `rt_min` 的分钟成交量和成交额已是股/元，不重复换算。

参考：

- [Tushare 日线](https://tushare.pro/document/2?doc_id=27)
- [Tushare Daily Basic](https://tushare.pro/document/2?doc_id=32)
- [Tushare rt_min](https://tushare.pro/document/2?doc_id=374)
- [同花顺 QuantAPI 产品手册](https://quantapi.10jqka.com.cn/gwstatic/static/ds_web/quantapi-web/help-center/manual.html)
- [iFinD HTTP 部署与 Token](https://quantapi.10jqka.com.cn/gwstatic/static/ds_web/quantapi-web/help-center/deploy.html)

## API

```text
GET /api/v1/health
GET /api/v1/settings/data
GET /api/v1/stocks/search?q=铜陵
GET /api/v1/stocks/SZ.000630
GET /api/v1/stocks/SZ.000630/daily?adjust=qfq
GET /api/v1/realtime/status
GET /api/v1/realtime/quotes?symbols=SZ.000630
GET /api/v1/realtime/quotes/SZ.000630
WS  /api/v1/ws/quotes
```

WebSocket 支持 `subscribe`、`unsubscribe` 和 `ping`。批量实时接口最多 100 只股票。

## 明确边界

- 正式 Technical Score 是 EOD 值；盘中 Quote 不冒充正式技术评分。
- 历史数据由同步任务落库，用户打开页面时不会临时向 Tushare 下载。
- Quant Lab 永远是虚拟资金与模拟成交；即使使用真实行情也不连接券商。
- Market、Behavior、Backtest、Review 中尚未迁移的数据继续明确显示演示标识。
- 真实模式缺字段时返回空值或配置错误，不用 Mock 数字伪装真实结果。

完整配置和联调步骤见 `docs/REAL_DATA_RUNBOOK.md`。

# StockLab Quant Lab（虚拟量化交易）

## 边界

Quant Lab 只实现 Paper Trading。它没有券商连接、真实账户、真实资金或真实下单能力。页面、订单、成交、净值和绩效目前全部明确标记为演示数据。

## 用户流程

```text
StockLab Strategy
→ 创建 LIVE_PAPER Strategy Instance
→ MockRealtimeMarketProvider / Realtime Service
→ Condition Engine
→ Signal Engine
→ Risk Engine
→ Paper Broker
→ Paper Exchange Simulator
→ Paper Portfolio
→ Performance / Logs
```

任何订单必须经过 Condition Engine 和 Risk Engine。AI 后续只能解释、总结和生成策略草稿，不能绕过规则链直接创建订单。

## 当前已实现

- 一级导航 `/quant` 与十个内部视图。
- 创建十万元或自定义初始资金的虚拟账户。
- 策略实例状态：READY、RUNNING、PAUSED、STOPPED、RISK_HALTED。
- 定时演示行情推进、可解释信号、风险检查、虚拟市价单、滑点和佣金。
- Paper Orders、Paper Trades、Paper Positions、虚拟现金和净值联动。
- 最大单股仓位、总仓位、持仓数、单笔金额、止损止盈、最大回撤与 Kill Switch 参数。
- 可撤销 PENDING 订单。
- Strategy NAV、Demo Benchmark、回撤、月度收益和运行日志。
- 策略页、选股页和回测页进入量化实验室的入口。

## 当前演示限制

- 模拟状态保存在浏览器内存，刷新页面会恢复到预置演示快照。
- MockRealtimeMarketProvider 只推进当前演示股票与净值。
- 订单撮合仅实现演示级市场单成交与预置限价待成交。
- 年化收益、胜率等绩效指标中的部分值是固定 Mock 样本。
- 没有数据库持久化和后端常驻策略调度器。

## 正式化接入点

正式版本应在后端建立独立 Quant Worker，并持久化：

- `quant_strategies`
- `strategy_instances`
- `strategy_signals`
- `paper_accounts`
- `paper_orders`
- `paper_trades`
- `paper_positions`
- `paper_daily_snapshots`
- `risk_events`
- `quant_run_logs`

行情统一从 Realtime Market Service 进入，iFinD、Tushare 或 Mock 仅是可替换 Provider；策略、风控、撮合和 UI 不依赖特定供应商。

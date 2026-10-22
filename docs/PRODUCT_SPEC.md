# StockLab 统一产品规格 V1.0

## 1. 产品定位

StockLab 是面向个人投资者的股票研究与交易辅助平台，不是荐股、喊单或自动交易工具。产品以“可解释、数据可靠、个人股票研究终端”为最高原则，帮助用户完成市场观察、股票发现、技术诊断、历史股性研究、自选跟踪、持仓管理、交易复盘与策略验证。

产品语言：**用数据发现机会，用统计验证判断，用策略管理交易。**

## 2. 核心用户流程

注册/登录 → 查看今日市场 → 从扫描、板块或条件选股发现股票 → 打开个股研究页 → 分别理解技术状态、历史股性与价格位置 → 加入自选/建立预警 → 记录买卖与持仓 → 按 Trade Episode 复盘 → 用 Signal Backtest 验证策略 → 在 Quant Lab 用真实或演示行情进行 Paper Trading 验证。

## 3. 页面信息架构

- 账户：登录、注册、用户设置。
- 工作台：首页、通知中心、全局股票搜索。
- 市场研究：市场、板块热力/轮动、异动雷达。
- 股票研究：个股详情、行情 K 线、技术分析、历史位置、涨停基因。
- 发现与跟踪：条件选股、策略、自选、预警。
- 交易研究：持仓、交易流水、交易复盘、策略回测、量化实验室（仅虚拟盘）。

主路由：`/dashboard`、`/market`、`/screener`、`/radar`、`/watchlist`、`/portfolio`、`/strategies`、`/quant`、`/alerts`、`/review`、`/backtest`、`/settings`、`/stock/:symbol`。

## 4. 核心模块

Account Engine、Market Engine、Price Limit Engine、Behavior Engine、Technical Engine、Position Engine、Screener Engine、Watchlist & Alert Engine、Portfolio & Transaction Engine、Trade Review Engine、Backtest Engine、Quant Lab / Paper Trading Engine，以及后续 AI Research Layer。

## 5. Technical Score

Technical Score 表示股票“当前”的技术状态，不能与历史股性或价格位置合并成神秘综合分。由趋势、动能、量能和风险四个可解释维度构成，典型输入包括 MA 排列与斜率、MACD、RSI/KDJ、BOLL、ATR、量比、阶段涨跌幅等。指标默认基于前复权价格计算；评分规则与版本应可配置、可追溯。

页面同时展示积极信号与风险信号，统一使用“趋势偏强、技术状态较强、短期风险增加”等中性研究语言，禁止“必涨、稳赚、强烈买入”。

## 6. Behavior Score

Behavior Score 描述股票历史活跃度与涨停后行为，包括半年/一年/两年涨停次数、最大连板、距最近涨停天数、炸板、一字板、封板成功率，以及涨停后 T+1/T+3/T+5/T+10/T+20 的平均收益、中位收益、上涨概率和样本量。

事实层拆为 `limit_events`，连续事件层为 `limit_streaks`，滚动派生层为 `stock_behavior_stats`。无涨跌幅限制日不纳入涨停统计；日线不能伪造盘中开板次数。

## 7. Price Percentile / Position

Price Position 独立回答“当前位置高不高”，展示半年、一年、三年价格分位、距 60 日/52 周高低点距离，并使用最低—当前—最高位置条。价格位置与技术强弱没有必然等价关系，必须独立呈现。

## 8. Screener

通过 Field Registry 暴露业务字段而非数据库列。支持行情、成交、技术、位置、股性和基本面条件，支持 AND/OR 与嵌套条件组；V1 默认使用 AND。每次筛选保留 `as_of_date`，以支持历史日期和 Point-in-Time 回测。结果必须提供“为什么入选”的逐条件解释，并可加入自选、设置预警、保存策略或打开个股研究页。

预设：历史活跃低位转强、沉寂股重新激活、低位放量、趋势突破、缩量回踩、基本面过滤。

## 9. Watchlist

自选不是简单收藏夹，而是个人研究工作台。用户可建立默认自选、准备买入、重点观察和自定义分组；一只股票可属于多个分组。保存加入来源、加入原因、计划买入价、止损价、目标价、优先级、备注与笔记时间轴，并突出“今天发生了什么变化”。

## 10. Alert

支持价格高于/低于、Technical Score 上穿阈值、MACD 金叉、跌破 MA20/MA60、突破 60 日高点、成交量放大、策略新增标的等。状态包括启用、停用、已触发；触发需要永久记录并进入通知中心。

## 11. Portfolio

允许一个用户拥有实盘记录账户与模拟账户。交易流水是事实核心，每笔 BUY/SELL/DEPOSIT/WITHDRAW/ADJUST 都永久保留；当前持仓是可重算缓存。展示总资产、现金、仓位、今日/累计盈亏、最大回撤、净值曲线、持仓与行业分布。交易记录包含价格、数量、费用、策略、原因与备注。

## 12. Trade Review

复盘以 Trade Episode 而非单笔买卖为单位：同一账户与股票从持仓 0 变为正数开始，经过加仓/减仓，到再次归零结束。记录加权入场/退出价、自然日与交易日持有时间、已实现收益、MFE、MAE、入场/退出快照、策略与原因。聚合层展示胜率、盈亏比、Profit Factor、收益分布及按策略、持有周期、入场 Technical、Price Position、行业的表现。

## 13. Backtest

V1 优先 Signal Backtest：某历史日满足条件即生成信号，不模拟复杂资金与撮合。支持 T+1/T+3/T+5/T+10/T+20/T+60 的样本数、上涨概率、平均收益与中位收益。策略条件必须保存快照与版本，并坚持 Point-in-Time Data，避免前视偏差与幸存者偏差。V2 再扩展 Portfolio Backtest。

## 14. Account System

每个账户拥有隔离的自选、策略、笔记、预警、持仓、复盘和回测。生产架构采用 FastAPI + PostgreSQL + Redis，密码使用 Argon2 Hash，JWT 身份认证。本轮前端原型使用 `demo / demo1234` 的 Mock 登录，并明确标记 Demo 数据。

## 14.1 Quant Lab / Paper Trading

量化实验室只允许虚拟量化交易，禁止连接真实券商或真实资金。核心链路为：Realtime Market Service → Condition Engine → Signal Engine → Risk Engine → Paper Broker → Paper Exchange Simulator → Paper Portfolio → Performance / Logs。任何订单都必须经过可解释策略和风险检查，AI 不得绕过该链路直接下单。

页面包含总览、我的策略、实时模拟、虚拟账户、当前持仓、订单、成交、风险、绩效和运行日志。策略实例支持 READY、RUNNING、PAUSED、STOPPED、ERROR、RISK_HALTED；风控至少覆盖单股/总仓位、持仓数量、单笔金额、止损止盈、单日亏损、策略最大回撤、冷却时间与 Kill Switch。手工持仓与 Paper Account 必须逻辑隔离。

## 15. 后续 AI Research Layer

AI 层只能基于可追溯事实与派生结果做解释、摘要、自然语言选股、复盘归因和研究助手，不可生成无法追溯的行情事实，也不使用“荐股、稳赚、准确预测”等语言。任何 AI 结论都需要展示数据时间、依据与不确定性。

## 16. 数据事实层与派生层

事实层保存原始且可追溯的数据：股票身份、曾用名、交易日历、未复权 OHLCV、每日估值与换手、复权因子、数据源给出的涨跌停价、ST 状态、交易流水。派生层保存可重算结果：前/后复权序列、技术指标、信号、评分、价格分位、涨停行为统计、持仓快照、Trade Episode、回测统计。

技术指标使用前复权序列；涨跌停判断必须使用原始价格和当日实际规则/事实。事实层与派生层不混表，派生结果记录算法/规则版本与计算时间。

## 17. V1 / V2 / V3 优先级

### V1 — 可运行研究闭环

账户原型、完整 App Shell、Dashboard、市场、搜索、个股详情、K 线、三大评分、选股与解释、自选分组、预警、持仓、Trade Episode 复盘、Signal Backtest，以及可交互的 Quant Lab Paper Trading 原型。数据可为明确标记的 Mock，但全部主要交互必须工作。

### V2 — 真实数据与增强研究

接入 FastAPI 行情层；盘中实时行情优先使用同花顺 iFinD QuantAPI，Tushare 负责历史研究与具备权限时的降级，Mock 仅用于显式演示模式。后续完善 PostgreSQL/Redis、Quant Worker 与 Paper 数据持久化、数据质量任务、真实预警、板块/概念多对多、财务快照、Portfolio Backtest、券商流水导入与响应式布局。量化实验室仍只做虚拟盘。

### V3 — 个性化与 AI

自然语言选股、研究摘要、相似走势、用户交易画像、策略失效监控、多策略组合与更完整的 AI Research Layer；所有输出继续遵守可解释、可追溯和非荐股边界。

## 视觉与数据边界

桌面端优先（1440px，兼容 1200px），左侧约 220px、顶部约 62px。中性浅色为主，轻边框与紧凑表格；A 股语义上涨红、下跌绿，但红绿只用于涨跌、盈亏和信号。所有本轮行情、评分、持仓、回测均标注“演示数据 · 非实时行情”。

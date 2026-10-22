# StockLab：接入 iFinD QuantAPI 实时行情，保留 Tushare 与 Mock 的 Codex 完整执行指令

> 本文件是交给 Codex 的实施任务书。编写于 2026-09-07，基于「股票分析网站灵感」对话最新实时行情设计及当前项目代码。文件存在不代表真实行情已经接通。
>
> 复制以下正文，或者让 Codex 读取本文件后直接执行。

---

你正在维护 StockLab，项目位于 Windows 的 `D:\A股可视化网页`。请直接在现有工程上实现真实行情接入，安装依赖、运行服务并完成验证。保留已有 Vue 页面和视觉设计，不重新创建另一个演示站点。

目标：iFinD QuantAPI 提供盘中行情，Tushare 提供历史研究数据与具备权限时的降级数据，Mock 提供明确隔离的演示模式。实现完整的“数据源 → 后端 → 缓存 → WebSocket → 页面”链路。

## 1. 先核对当前工程，避免只改接口但页面继续显示假数据

先读 AGENTS.md（若有）、README、docs/PRODUCT_SPEC.md、package.json、src/api、src/services、src/stores、src/types、src/mock 和相关页面。

目前已知：
- 技术栈为 Vue 3、TypeScript、Vite、Element Plus、ECharts、Pinia、Vue Router；项目已有 pnpm 锁文件，沿用 pnpm。
- src/api/client.ts 只是 mode='mock' 的配置占位。
- StockService、MarketService 直接返回本地 Mock；多个页面也直接导入 Mock。
- Stock 同时承载身份、价格、评分、历史 K 线，缺少数据来源和行情时间。
- K 线是合成序列，个股页 MACD 为演示公式，回测为固定结果。
- 当前工程未提供可用 FastAPI 实时后端，不能假设后端已存在。
- AppHeader 的全局搜索、Dashboard、Market、StockDetail、Watchlist、Radar、Screener、Portfolio 都有直接读取 Mock 的路径；不要漏掉表格中的现价列。
- findStock 查无结果时会回退第一只股票；持仓的添加交易目前只追加流水，不重算数量与成本。
- 当前 .gitignore 未明确排除 .env；必须在创建任何真实凭据文件前补齐忽略规则。

用 rg 找全 Mock 的直接引用、固定行情日期、固定指数、持仓估值与收益计算。迁移范围内的数据入口统一经过 service/store。演示数据仅允许在 Mock Provider、演示业务状态或测试 fixture 中使用。保留已有未提交修改。

## 2. 明确本次范围

本次必须实现：
1. 可运行 FastAPI 后端与健康检查。
2. iFinD HTTP 鉴权、批量行情获取、标准化与错误处理。
3. Tushare 历史数据适配与按能力降级；独立 Mock Provider。
4. Redis 最新行情缓存；本地单进程可显式使用内存缓存。
5. REST 首屏快照与 WebSocket 按需订阅。
6. 首页指数、个股、自选和持仓的行情更新及状态显示。
7. 个股分时/分钟数据接口与图表，有权限时显示真实数据，无权限时显示原因。
8. 设置页数据连接状态、脱敏诊断、用量控制、测试及启动文档。

正式 Technical、Behavior、Price Position、选股、复盘与回测仍以日终研究数据为依据。尚未完成的真实算法保持“演示结果”或“未计算”状态，并注明数据日期。不能因最新价接通就宣称所有模块已真实化。

本轮不扩展完整生产账户体系、券商下单或整个回测引擎重写。

## 3. 技术架构与目录

后端建议使用 Python、FastAPI、httpx.AsyncClient、Pydantic Settings、redis.asyncio、pytest；如仓库已有兼容后端则延续。

行情获取是后端对 QuantAPI HTTP 的定时批量请求；WebSocket 是 StockLab 自己向浏览器推送的连接，不能假设供应商提供了相同的流式接口。

建议新增：
- backend/app/main.py
- backend/app/core/config.py
- backend/app/core/logging.py
- backend/app/providers/base.py
- backend/app/providers/ifind.py
- backend/app/providers/ifind_auth.py
- backend/app/providers/tushare.py
- backend/app/providers/mock.py
- backend/app/services/quote_service.py
- backend/app/services/history_service.py
- backend/app/realtime/collector.py
- backend/app/realtime/cache.py
- backend/app/realtime/subscriptions.py
- backend/app/realtime/calendar.py
- backend/app/api/realtime.py
- backend/app/schemas/market.py
- backend/tests/
- backend/.env.example
- docs/REALTIME_DATA.md

前端新增或扩展：
- src/types/market.ts
- src/api/client.ts
- src/services/realtimeService.ts
- src/stores/quotes.ts
- src/composables/useQuoteSubscription.ts
- src/components/QuoteStatus.vue

新增 HTTP/WS 的 Vite 代理，保留现有路由与 UI。核对根目录 vite.config.ts 与可能存在的 vite.config.js，避免实际生效配置与修改文件不一致。真实历史事实需要持久化；已有数据库则复用，没有则提供独立的数据存储适配与可启动配置，勿将完整 PostgreSQL 建库变成实时最小链路的前置障碍。

检查 tsconfig.node.json 的 include 和 emit 行为，统一 Vite 配置来源并避免构建重新生成歧义文件；确认文件是否为生成物后再整理，保留用户配置。

## 4. iFinD 官方接口与鉴权

实施时再次核对官方文档，并将字段名、单位、样例和核对日期写入 docs/REALTIME_DATA.md。

优先使用 HTTP API；本方案不需要安装 SDK 或用账户密码调用 SDK 登录。

鉴权：
- 服务端读取 IFIND_REFRESH_TOKEN。
- 调用 POST https://quantapi.51ifind.com/api/v1/get_access_token。
- 请求头包含 Content-Type: application/json 和 refresh_token。
- 校验响应，再取得 data.access_token；缓存 access token，避免每次行情请求重新取 token。
- 行情请求通过 access_token 请求头传递凭据。
- 失效时合并并发刷新请求，并最多重试一次原业务请求。
- 有效期以响应信息与当时官方规则为依据；“获取当前有效 token”不能被当成必然延长有效期。
- 不自动轮换 refresh token，也不默认调用强制更新 access token 的操作，避免使其他会话的凭据失效。
- 权限不足、账号到期、IP 限制与 token 失效要区分处理，不能全部反复刷新 token。

以上鉴权形式见[官方 HTTP 示例](https://quantapi.10jqka.com.cn/gwstatic/static/ds_web/quantapi-web/example.html)；生命周期与更新影响见[官方部署说明](https://quantapi.10jqka.com.cn/gwstatic/static/ds_web/quantapi-web/help-center/deploy.html)。

实时报价：
- POST https://quantapi.51ifind.com/api/v1/real_time_quotation
- JSON 请求体先使用已确认的最小指标集合：
  {"codes":"000630.SZ,002155.SZ","indicators":"open,high,low,latest"}
- 通过官方超级命令/产品手册确认昨收、累计成交量、累计成交额、行情时间、涨跌幅等字段后，再完善字段映射；不猜字段名、单位、指数代码或权限。
- 不能只因 HTTP 200 就当成功，还要检查业务错误、返回标的、指标数组与时间。
- 解析必须按证券代码对应，不能假定返回顺序等于请求顺序。
- 对缺失标的、null、停牌、空结果、部分成功、异常 HTML/JSON、超时、限流、权限和配额错误分别处理。
- 批次大小、字段集、超时、重试、限流可配置，使用连接池和有限退避。

实时端点及最小指标来自[官方实时行情说明](https://quantapi.10jqka.com.cn/gwstatic/static/ds_web/quantapi-web/help-center/manual.html)。

## 5. 标准化模型与数值语义

不要继续用一个必填数值的 Stock 表示所有数据。分出 StockIdentity、Quote、MinuteBar、DailyBar、ResearchSnapshot；生成前后端一致的类型契约。

Quote 至少包括：
- symbol、instrument_type、name（可空）
- price、pre_close、change、change_pct
- open、high、low、volume、amount
- source：ifind / tushare / mock
- granularity：snapshot / minute / eod / demo
- trade_time（供应商行情时间，可空）、received_at（服务端接收时间）
- trading_date、market_status、is_stale、is_demo
- availability、fallback_reason、quality_flags
- currency、price_unit、volume_unit、amount_unit

要求：
- 内部继续使用 SZ.000630；供应商使用 000630.SZ。使用显式双向映射和证券基础资料，区分股票与指数；000001.SH 与 000001.SZ 不是同一个证券。
- 时间包含时区，交易日判断使用 Asia/Shanghai。供应商没有行情时间时不得用“服务器刚收到的时间”伪装。
- 股票价格统一人民币元，成交量统一股，成交额统一元；指数价格单位为点，指数成交量语义另行核实。
- change = price - pre_close；change_pct 为百分数，例如 3.17 表示 3.17%。优先验证供应商涨跌参考价口径，不能用复权图表上一根收盘价代替除权日昨收参考价。
- 无值用 null，不用 0、随机数、别的股票或 Mock 补齐；避免空值参与 toFixed 和除法。
- 原始盘口价格不复权；历史图表明确前复权/后复权/不复权口径。不同日期或来源的补充字段需要单独标注，不能拼出一条貌似完整的同时间行情。
- 保留精度，在显示层格式化；持仓金额使用 Decimal 或一致的金额精度规则。

## 6. Provider 与 fallback 策略

分别定义 RealtimeMarketProvider 与 HistoricalMarketProvider，并暴露支持的能力。每条返回记录携带真实来源、时间与粒度。

实现三个运行模式：
- mock：仅使用演示数据，整页及图表明确显示“演示行情”。
- ifind：使用 iFinD 与允许的真实降级链路；无凭据显示“未配置”，不能无声切回 Mock。
- auto：已配置 iFinD 则尝试它；没有主源则按能力选择真实 Tushare；均未配置且明确开启演示允许项时，整个会话进入演示模式并显示持续提示。

真实模式运行中 iFinD 故障：
1. 保留同标的最后一条有效 iFinD 缓存，并如实显示行情时间、连接故障和新鲜度；缓存来源不能改写为新的实时数据。
2. 若该缓存已不适合当前用途且 Tushare 已开通对应分钟权限，则尝试 Tushare 分钟数据，明确显示“分钟级降级”。
3. 无分钟能力但有 Tushare 日线，则显示最近已完成交易日收盘数据与日期，标为“收盘数据”。
4. 都不可用则显示缺失/暂不可用；既有过期值只能作为最后已知值保留。
5. 用户显式进入演示模式后才使用 Mock；演示数据与真实数据、缓存 key、图表序列、预警状态必须隔离。

重要约束：
- Tushare 日线不是实时快照。分钟接口的 open/high/low/vol/amount 也不是当日累计字段；只有当日完整分钟历史齐备、覆盖检查通过时才可聚合当日数据。
- 普通 Tushare Token 不等于拥有实时分钟权限。根据配置及实际能力检查启用 rt_min / rt_min_daily。
- 依据字段粒度与时间选择降级，不能对整批部分失败标的一刀切，也不能将一条记录拆成不兼容的数据源字段。
- 恢复 iFinD 后使用有界探测和稳定期切回，避免来回切换；历史记录保持原来源。
- Mock、过期行情和故障期间跨源跳变不能触发正式价格预警。切源后重建条件基线。
- 任一价格字段缺失，不应使整页、其他标的或 WebSocket 崩溃。

Tushare 分钟能力与单位见[rt_min 文档](https://tushare.pro/document/2?doc_id=374)及[rt_min_daily 文档](https://tushare.pro/document/2?doc_id=457)。

## 7. Redis、订阅、交易时段和额度

按可见页面按需获取：
- 首页：四个指数，以及实际展示的自选摘要。
- 个股：当前打开的一只；理论目标间隔 2–3 秒。
- 自选/持仓：当前可见的标的；理论目标间隔 3–5 秒。
- 搜索主要读取证券目录，不逐键触发实时订阅。
- 市场广度、板块等使用有明确覆盖范围的聚合快照及日期，不能从十只演示股外推全市场。

刷新频率只是目标，必须受账号权限、实际额度与可见订阅预算约束。低额度时主动放慢并在设置页显示有效频率。

实现：
- 多页面、多连接订阅去重与引用计数，同一股票字段集共用后端采集。
- 关闭页面、路由跳转、断连与长时间后台隐藏及时释放订阅。
- 价格预警如需后台监控，应由明确启用的预警任务登记独立订阅并计入用量。
- 基于真实交易日历和时段处理午休、节假日、收盘、集合竞价与停牌。交易日历不可用时显示未知，不把单纯周一至周五当作权威交易日历。
- 休市时降低/停止轮询，展示最后交易时间及“已休市”；连接状态、新鲜度和市场状态分别判断。停牌或无成交不简单等价于网络断线。
- Redis key 包含运行模式、来源、证券身份；例如 quote:live:ifind:SZ.000630。最新缓存 TTL 可设 120 秒，另存最后有效值用于明确的过期展示。TTL 不等同于实时新鲜度阈值。
- 多 worker 采用共享缓存、分布式采集协调与 Pub/Sub，避免每个 worker 重复消耗上游额度。内存模式只支持单进程且明确提示。
- 按供应商返回的用量字段记录请求消耗；本地估算与供应商权威配额要区分。展示本地会话/日累计估算、缓存命中率和实际刷新间隔。
- 预算未配置时使用保守有限请求与明显的用量估算，不默认全天高频运行。
- 不把“数据条数”当成请求次数；不把对话中的免费套餐或额度永久写死。用“标的数 × 字段数 × 更新次数”预估，按实际计费口径校正。

同花顺计量和并发约束以[官方 FAQ](https://quantapi.10jqka.com.cn/gwstatic/static/ds_web/quantapi-web/help-center/faq.html)及该账号当前权限为准。

## 8. REST 与 WebSocket 契约

至少提供：
- GET /api/v1/health
- GET /api/v1/realtime/status
- GET /api/v1/realtime/quotes?symbols=SZ.000630,SZ.002155
- GET /api/v1/realtime/quotes/{symbol}
- GET /api/v1/realtime/minutes/{symbol}?date=YYYY-MM-DD
- GET /api/v1/stocks/search?q=铜陵
- GET /api/v1/stocks/{symbol}/history
- WebSocket /api/v1/ws/quotes

支持 subscribe / unsubscribe：
{"action":"subscribe","symbols":["SZ.000630","SZ.002155"]}

服务器返回 ack、snapshot、quote、status、error、heartbeat 等明确消息类型。quote 附事件序号或版本。限制单连接标的数、消息大小与订阅频率；处理部分成功、慢客户端、过期连接、重连、重复消息、乱序消息及重新订阅。

前端从同一个缓存/行情服务拿 REST 初值并接收增量；浏览器 WebSocket 失败时可以有限频率轮询自家 REST，该请求仍经过后端缓存及额度控制。REST 可用不等于上游实时正常。

默认仅本机访问，校验 Origin、符号和请求参数；已有账户鉴权则沿用。不要通过公开代理暴露凭据或无限制查询权限。

## 9. 前端实际接线

- 建立统一 quotes Pinia store，REST 与 WS 更新同一份状态；由订阅 composable 管理生命周期。
- 改造 DashboardView、StockDetailView、WatchlistView、PortfolioView 及市场行情相关展示，移除这些实时字段的直接 Mock 读取。
- 统一格式化空值、单位、红涨绿跌及价格精度。
- 每个行情区域显示“iFinD 行情 / 分钟级降级 / 收盘数据 / 演示行情”、行情时间和连接状态；首页不能用一个“实时”徽标覆盖仍为 Mock 的板块数据。
- StockDetail 用当前 symbol 拉取，未知代码显示明确空状态，不能默认显示铜陵有色。
- 页面有数据但不新鲜时显示“最后已知价格”，不能只把 received_at 更新一下延长“实时”标签。
- 价格局部刷新，历史日 K 和正式评分不每几秒重新加载；保留 ECharts 缩放与用户选中的周期。
- SettingsView 增加数据源状态、是否配置、可用能力、降级原因、最后成功时间、实际刷新间隔和用量估算。连接检测按钮应只做小范围有限测试，不能显示或提交真实密钥。
- 价格变化后，持仓市值与浮盈亏跟随更新；使用持仓数量和实际平均成本，保留现金。示例持仓即便使用真实价格估值也必须标“模拟持仓按真实行情估值”。
- 行情接入不改写历史成交价；当前交易记录尚未驱动持仓重算时，应明确提示记账能力边界，不能让用户以为新增流水已自动更新账户。
- 当日盈亏若缺少昨日持仓、当日资金与交易流，显示不可计算或明确的持仓价格变动指标，不能冒充完整账户当日收益。
- 保留整体布局和 1200px / 1440px 桌面体验。

## 10. 历史图表、分时与研究结果

- 历史日线通过 Tushare 或已验证权限的 iFinD 历史接口获取，记录来源、区间、复权方式、交易日期与缺口。
- 当历史数据可用时，以统一口径计算 MA5/10/20/60、标准 MACD 和 RSI；记录参数、初始化与暖机要求，删除真实模式中的演示 MACD 公式。
- 日、周、月切换必须实际改变数据粒度；聚合遵守交易日历与成交量求和语义。
- 当前未收盘日 K 若显示，应单独标识未完成，不写成正式历史事实。
- 分时/分钟 OHLCV 从受支持接口获取；单纯间隔采样最新价无法还原完整成交、高低点和成交量，不用采样序列伪造正式分钟 K 线。
- 无历史权限时保留真实当前价并显示“历史行情暂不可用”，不把合成 K 线接在真实价格下面而隐藏其性质。
- Behavior、价格分位、市场情绪与回测若尚无真实计算，仅保留明确演示区或未计算状态；不能沿用固定高分并标成真实分析。
- 所有研究结果保留 as_of_date、source、是否演示、算法版本；实时最新价不覆盖历史回测入场快照。

## 11. 配置与本地启动

创建 backend/.env.example，至少包括以下变量，值仅为应用配置示例，并非供应商默认额度：

STOCKLAB_MARKET_MODE=auto
STOCKLAB_ALLOW_DEMO=true
IFIND_BASE_URL=https://quantapi.51ifind.com/api/v1
IFIND_REFRESH_TOKEN=
TUSHARE_TOKEN=
TUSHARE_REALTIME_ENABLED=false
REALTIME_FALLBACK_ORDER=last_good,tushare_minute,tushare_eod,unavailable
QUOTE_CACHE_BACKEND=memory
REDIS_URL=redis://127.0.0.1:6379/0
QUOTE_DETAIL_INTERVAL_SECONDS=3
QUOTE_LIST_INTERVAL_SECONDS=5
QUOTE_STALE_AFTER_SECONDS=30
QUOTE_CACHE_TTL_SECONDS=120
IFIND_MAX_QPS=2
IFIND_DAILY_CELL_BUDGET=
QUOTE_TIMEZONE=Asia/Shanghai

STOCKLAB_ALLOW_DEMO 只允许明确的初始演示选择或显式模式切换，不能使 live 故障静默混入 Mock。QUOTE_STALE_AFTER_SECONDS 要根据行情粒度、时段与有效刷新频率调整。

提供 backend/.env 配置说明和 .gitignore。凭据不得使用 VITE_ 前缀，不写入前端 bundle、localStorage、URL、日志、截图、测试 fixture 或版本库。诊断只报告配置状态与脱敏错误；保留已有环境文件，不输出其内容。

缺少凭据时继续完成代码、Mock 链路、错误场景与自动化测试；最后报告“真实接入待凭据验证”，并指出应在本机填写的变量。不要以等待 Token 为由停止实现。

提供 README 启动步骤、后端依赖文件、单进程内存开发方式和可选 Redis 启动方式；有需要再提供 Docker Compose。不要强制用户先安装整套生产基础设施才能运行。

## 12. 验证与验收

编写有实际价值的测试并执行，至少覆盖：
- symbol 双向转换、股票/指数区分、未知代码、单位换算、空值和涨跌计算。
- 官方格式的脱敏契约 fixture：多标的、返回乱序、部分缺失、空数组、HTTP 200 业务失败。
- Token 缓存、并发单次刷新、过期重试上限、权限错误不重复刷新、日志无密钥。
- iFinD 成功、断线、缓存新鲜/过期、Tushare 有/无分钟权限、日终降级、无任何真实数据、显式演示与主源恢复。
- 交易日、周末、节假日、午休、停牌，接收时间与交易时间不能混淆。
- 引用计数、跨连接去重、后台释放、重连重订阅、乱序丢弃、慢客户端和限流。
- 演示与真实数据的缓存、图表和预警隔离。
- 真实价格变化推动持仓估值，现金与成本不被覆盖。
- 历史/分钟字段语义、复权状态、真实模式禁止合成历史兜底。

执行后端测试、pnpm typecheck、pnpm build，并在浏览器验证首页、搜索、个股、自选、持仓、设置页，检查控制台与 1200/1440px 布局。

有有效凭据且用户已授权此接入时，执行小批量真实 smoke test，不做全天持续或全市场拉取。至少核对：
- 同一证券、相近行情时间的价格与官方响应一致；
- 接口原始单位、标准化结果与页面单位一致；
- market time 与 received_at 正确区分；
- 故障降级和恢复有可见状态；
- 无权限字段保持空值而不是伪造。

没有凭据时，真实 smoke test 必须标“未执行/待验证”，fixture 测试通过不能写成真实 API 联调通过。

## 13. 完成交付

同步更新 README、docs/PRODUCT_SPEC.md 中的数据源描述以及 docs/REALTIME_DATA.md。交付说明包括：
- 修改了哪些文件、哪些页面接入了行情 store。
- iFinD / Tushare / Mock 的实际可用范围与降级行为。
- 如何启动、如何配置本地凭据、如何查看行情时间及来源。
- 执行的测试与实际结果，明确区分 Mock/契约测试和真实 smoke test。
- 尚未取得权限的字段、尚为 Mock 的研究模块，以及当前边界。
- 当前有效刷新频率与预算策略。

请直接实现并验证。不要仅输出代码片段、用假结果宣称接通或重复撰写大篇产品方案。完成不依赖凭据的全部工作，再报告仅凭据或权限所阻塞的真实验证项。

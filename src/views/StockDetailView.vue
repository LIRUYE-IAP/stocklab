<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import type { EChartsOption } from 'echarts'
import { Bell, CirclePlus, Star, StarFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import EChart from '@/components/charts/EChart.vue'
import ScoreCard from '@/components/ScoreCard.vue'
import SignalTag from '@/components/SignalTag.vue'
import PositionBar from '@/components/PositionBar.vue'
import QuoteStatus from '@/components/QuoteStatus.vue'
import { findStock } from '@/mock/stocks'
import { HistoryService } from '@/services/historyService'
import type { DailyPrice, Stock } from '@/types'
import type { StockProfile } from '@/types/history'
import { useWatchlistStore } from '@/stores/watchlist'
import { useAlertsStore } from '@/stores/alerts'
import { usePortfolioStore } from '@/stores/portfolio'
import { useQuoteSubscription } from '@/composables/useQuoteSubscription'

const route = useRoute()
const watchlist = useWatchlistStore()
const alerts = useAlertsStore()
const portfolio = usePortfolioStore()
const activeTab = ref('analysis')
const period = ref('日')
const adjust = ref('前复权')
const alertDialog = ref(false)
const tradeDialog = ref(false)
const alertForm = reactive({ type: '价格低于', value: 5.50 })
const tradeForm = reactive({ date: '2026-08-30', price: 5.86, quantity: 1000, strategy: '历史活跃低位转强', reason: '技术状态转强，等待确认后分批建仓' })
const routeSymbol = computed(() => String(route.params.symbol))
const baseStock = computed(() => findStock(routeSymbol.value))
const profile = ref<StockProfile | null>(null)
const historicalBars = ref<DailyPrice[]>([])
const historicalSource = ref<string | null>(null)
const historicalDate = ref<string | null>(null)
const historyError = ref<string | null>(null)
const quotes = useQuoteSubscription(computed(() => [routeSymbol.value]))
const stock = computed(() => {
  const liveProfile = profile.value
  const fallback: Stock | undefined = baseStock.value || (liveProfile ? {
    symbol: liveProfile.symbol, code: liveProfile.code, name: liveProfile.name, exchange: liveProfile.exchange as Stock['exchange'], board: liveProfile.board,
    industry: liveProfile.industry || '未分类', price: liveProfile.close || 0, change: 0, changePct: 0, open: liveProfile.close || 0, high: liveProfile.close || 0, low: liveProfile.close || 0, preClose: liveProfile.close || 0,
    volume: 0, amount: 0, turnover: liveProfile.turnover_rate || 0, pe: liveProfile.pe_ttm || 0, pb: liveProfile.pb || 0, marketCap: (liveProfile.market_cap || 0) / 100_000_000,
    technicalScore: Number(liveProfile.technical?.technical_score || 0), behaviorScore: 0, pricePercentile: Number(liveProfile.position?.price_percentile_1y || 0), signals: [], risks: ['Behavior Engine 数据尚未就绪'], limitUpsYear: 0, maxStreak: 0, recentLimitUp: '—', kline: historicalBars.value,
  } : undefined)
  if (!fallback) return undefined
  const quote = quotes.quote(fallback.symbol)
  return { ...fallback,
    name: liveProfile?.name || fallback.name, industry: liveProfile?.industry || fallback.industry,
    kline: historicalBars.value.length ? historicalBars.value : fallback.kline,
    turnover: liveProfile?.turnover_rate ?? fallback.turnover, pe: liveProfile?.pe_ttm ?? fallback.pe, pb: liveProfile?.pb ?? fallback.pb,
    marketCap: liveProfile?.market_cap != null ? liveProfile.market_cap / 100_000_000 : fallback.marketCap,
    technicalScore: Number(liveProfile?.technical?.technical_score ?? fallback.technicalScore), pricePercentile: Number(liveProfile?.position?.price_percentile_1y ?? fallback.pricePercentile),
    price: quote ? quote.price : (liveProfile?.close ?? fallback.price), change: quote ? quote.change : fallback.change,
    changePct: quote ? quote.changePct : fallback.changePct, open: quote ? quote.open : fallback.open,
    high: quote ? quote.high : fallback.high, low: quote ? quote.low : fallback.low,
    preClose: quote ? quote.preClose : fallback.preClose, volume: quote ? quote.volume : fallback.volume,
    amount: quote ? quote.amount : fallback.amount, quote }
})

async function loadHistorical() {
  profile.value = null; historicalBars.value = []; historicalSource.value = null; historicalDate.value = null; historyError.value = null
  const adjustMode = adjust.value === '前复权' ? 'qfq' : adjust.value === '后复权' ? 'hfq' : 'raw'
  try {
    const [nextProfile, history] = await Promise.all([HistoryService.stock(routeSymbol.value), HistoryService.daily(routeSymbol.value, adjustMode)])
    profile.value = nextProfile
    historicalBars.value = history.bars.filter((row) => row.open != null && row.high != null && row.low != null && row.close != null).map((row) => ({ date: row.date, open: row.open!, high: row.high!, low: row.low!, close: row.close!, volume: (row.volume_shares || 0) / 100 }))
    historicalSource.value = history.source; historicalDate.value = history.latest_trade_date
  } catch (error) {
    historyError.value = error instanceof Error ? error.message : '历史数据库不可用'
  }
}

watch([routeSymbol, adjust], loadHistorical, { immediate: true })

watch(stock, (current) => { if (current?.price != null) { tradeForm.price = current.price; alertForm.value = +(current.price * .95).toFixed(2) } }, { immediate: true })

const ma = (days: number) => (stock.value?.kline || []).map((_, index, rows) => {
  if (index < days - 1) return '-'
  return +(rows.slice(index - days + 1, index + 1).reduce((sum, row) => sum + row.close, 0) / days).toFixed(2)
})

const klineOption = computed<EChartsOption>(() => {
  const rows = stock.value?.kline || []
  const dates = rows.map((row) => row.date)
  const candle = rows.map((row) => [row.open, row.close, row.low, row.high])
  const macd = rows.map((row, i) => +((row.close - row.open) * (1.3 + Math.sin(i / 5))).toFixed(3))
  return {
    animation: false,
    legend: { top: 4, left: 10, data: ['MA5', 'MA10', 'MA20', 'MA60'], textStyle: { color: '#7e8492', fontSize: 9 }, itemWidth: 13, itemHeight: 2 },
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross', lineStyle: { color: '#9da2ad', type: 'dashed' } }, textStyle: { fontSize: 11 } },
    axisPointer: { link: [{ xAxisIndex: 'all' }], label: { backgroundColor: '#555b68' } },
    grid: [
      { left: 52, right: 16, top: 34, height: '54%' },
      { left: 52, right: 16, top: '65%', height: '12%' },
      { left: 52, right: 16, top: '81%', height: '12%' },
    ],
    xAxis: [
      { type: 'category', data: dates, boundaryGap: true, axisLine: { lineStyle: { color: '#dfe1e6' } }, axisLabel: { show: false }, axisTick: { show: false }, min: 'dataMin', max: 'dataMax' },
      { type: 'category', gridIndex: 1, data: dates, boundaryGap: true, axisLine: { lineStyle: { color: '#dfe1e6' } }, axisLabel: { show: false }, axisTick: { show: false }, min: 'dataMin', max: 'dataMax' },
      { type: 'category', gridIndex: 2, data: dates, boundaryGap: true, axisLine: { lineStyle: { color: '#dfe1e6' } }, axisLabel: { color: '#8a909e', fontSize: 9, interval: 14 }, axisTick: { show: false }, min: 'dataMin', max: 'dataMax' },
    ],
    yAxis: [
      { scale: true, position: 'right', axisLine: { show: false }, axisTick: { show: false }, splitLine: { lineStyle: { color: '#eef0f3' } }, axisLabel: { color: '#8a909e', fontSize: 9 } },
      { gridIndex: 1, scale: true, position: 'right', splitNumber: 2, axisLine: { show: false }, axisTick: { show: false }, splitLine: { show: false }, axisLabel: { color: '#8a909e', fontSize: 8 } },
      { gridIndex: 2, scale: true, position: 'right', splitNumber: 2, axisLine: { show: false }, axisTick: { show: false }, splitLine: { lineStyle: { color: '#f1f2f5' } }, axisLabel: { color: '#8a909e', fontSize: 8 } },
    ],
    dataZoom: [{ type: 'inside', xAxisIndex: [0, 1, 2], start: 20, end: 100 }, { show: true, xAxisIndex: [0, 1, 2], type: 'slider', bottom: 0, height: 14, borderColor: 'transparent', backgroundColor: '#f1f2f5', fillerColor: 'rgba(85,85,201,.12)', handleStyle: { color: '#7777d8' }, textStyle: { fontSize: 0 } }],
    series: [
      { name: 'K线', type: 'candlestick', data: candle, itemStyle: { color: '#d74444', color0: '#15966f', borderColor: '#d74444', borderColor0: '#15966f' } },
      { name: 'MA5', type: 'line', data: ma(5), showSymbol: false, smooth: true, lineStyle: { width: 1.1, color: '#d69532' } },
      { name: 'MA10', type: 'line', data: ma(10), showSymbol: false, smooth: true, lineStyle: { width: 1.1, color: '#5a8fd4' } },
      { name: 'MA20', type: 'line', data: ma(20), showSymbol: false, smooth: true, lineStyle: { width: 1.1, color: '#7b60c5' } },
      { name: 'MA60', type: 'line', data: ma(60), showSymbol: false, smooth: true, lineStyle: { width: 1.1, color: '#777d88' } },
      { name: '成交量', type: 'bar', xAxisIndex: 1, yAxisIndex: 1, data: rows.map((row) => ({ value: row.volume, itemStyle: { color: row.close >= row.open ? 'rgba(215,68,68,.58)' : 'rgba(21,150,111,.58)' } })) },
      { name: 'MACD', type: 'bar', xAxisIndex: 2, yAxisIndex: 2, data: macd.map((value) => ({ value, itemStyle: { color: value >= 0 ? 'rgba(215,68,68,.65)' : 'rgba(21,150,111,.65)' } })) },
    ],
  }
})

const behaviorHorizon = [
  { label: 'T+1', win: 64, avg: 1.8, median: 1.1, samples: 8 },
  { label: 'T+3', win: 67, avg: 3.9, median: 2.4, samples: 8 },
  { label: 'T+5', win: 69, avg: 6.8, median: 4.2, samples: 8 },
  { label: 'T+10', win: 66, avg: 8.1, median: 5.7, samples: 7 },
  { label: 'T+20', win: 71, avg: 12.4, median: 7.9, samples: 7 },
]

const formatValue = (value: number | null, digits = 2) => value == null ? '—' : value.toFixed(digits)
const formatPct = (value: number | null) => value == null ? '—' : `${value > 0 ? '+' : ''}${value.toFixed(2)}%`
const formatVolume = (value: number | null) => value == null ? '—' : stock.value?.quote ? `${(value / 10_000).toLocaleString('zh-CN', { maximumFractionDigits: 1 })}万股` : `${value}万手`
const formatAmount = (value: number | null) => value == null ? '—' : stock.value?.quote ? `${(value / 100_000_000).toFixed(2)}亿元` : `${value}亿元`

function toggleWatch() {
  if (!stock.value) return
  const existed = watchlist.contains(stock.value.symbol)
  watchlist.toggle(stock.value.symbol)
  ElMessage.success(existed ? '已从自选移除' : '已加入默认自选')
}
function saveAlert() {
  if (!stock.value) return
  alerts.add({ symbol: stock.value.symbol, stockName: stock.value.name, type: alertForm.type, detail: `${alertForm.value}`, enabled: true, status: '启用', updatedAt: '刚刚' })
  alertDialog.value = false
  ElMessage.success('演示预警已创建')
}
function saveTrade() {
  if (!stock.value) return
  portfolio.addTransaction({ date: tradeForm.date, symbol: stock.value.symbol, stockName: stock.value.name, side: '买入', price: tradeForm.price, quantity: tradeForm.quantity, strategy: tradeForm.strategy, reason: tradeForm.reason })
  tradeDialog.value = false
  ElMessage.success('演示买入记录已保存')
}
</script>

<template>
  <template v-if="stock">
  <PageHeader eyebrow="Stock research" :title="`${stock.name} ${stock.code}`" :description="`${stock.exchange} · ${stock.board} · ${stock.industry} · ${stock.quote && !stock.quote.isDemo ? '行情服务' : '演示行情'}`">
    <button class="btn" :class="{ soft: watchlist.contains(stock.symbol) }" @click="toggleWatch"><component :is="watchlist.contains(stock.symbol) ? StarFilled : Star" />{{ watchlist.contains(stock.symbol) ? '已在自选' : '加入自选' }}</button>
    <button class="btn" @click="alertDialog = true"><Bell />设置预警</button>
    <button class="btn primary" @click="tradeDialog = true"><CirclePlus />记录买入</button>
  </PageHeader>
  <div class="demo-banner"><span><b>{{ historicalSource ? 'DATABASE HISTORY' : stock.quote && !stock.quote.isDemo ? 'LIVE QUOTE + DEMO RESEARCH' : 'DEMO / MOCK' }}</b>　{{ historicalSource ? `历史K线来自 ${historicalSource}，最新完整交易日 ${historicalDate || '—'}；Behavior 数据仍可能为演示。` : '历史数据库尚无该股票数据，K线、评分和涨停统计使用演示数据。' }}</span><QuoteStatus :quote="stock.quote" :connection="quotes.connection" /></div>

  <section class="panel stock-quote">
    <div class="quote-primary"><span>当前价</span><div><strong :class="stock.changePct == null ? '' : stock.changePct >= 0 ? 'positive' : 'negative'">{{ formatValue(stock.price) }}</strong><em :class="stock.changePct == null ? '' : stock.changePct >= 0 ? 'positive' : 'negative'">{{ stock.change != null && stock.change > 0 ? '+' : '' }}{{ formatValue(stock.change) }}　{{ formatPct(stock.changePct) }}</em></div></div>
    <div v-for="item in [
      ['今开', formatValue(stock.open)], ['最高', formatValue(stock.high)], ['最低', formatValue(stock.low)], ['昨收', formatValue(stock.preClose)],
      ['成交量', formatVolume(stock.volume)], ['成交额', formatAmount(stock.amount)], ['换手率', `${stock.turnover}%`], ['PE(TTM)', stock.pe.toFixed(1)], ['PB', stock.pb.toFixed(2)], ['总市值', `${stock.marketCap}亿元`],
    ]" :key="String(item[0])" class="quote-item"><span>{{ item[0] }}</span><strong>{{ item[1] }}</strong></div>
  </section>

  <div class="stock-score-grid section-gap">
    <ScoreCard label="Technical Score" :score="stock.technicalScore" :status="stock.technicalScore >= 80 ? '较强' : '中性'" description="当前技术状态：趋势、动能、量能与风险。" color="#5555c9" />
    <ScoreCard label="Behavior Score" :score="stock.behaviorScore" :status="stock.behaviorScore >= 75 ? '历史活跃' : '一般'" description="历史涨停、封板与后续持续性统计。" color="#c4792a" />
    <ScoreCard label="Price Position" :score="stock.pricePercentile" :status="stock.pricePercentile <= 35 ? '中低位' : stock.pricePercentile >= 70 ? '偏高位' : '中位区'" description="一年价格分位，独立于技术强弱。" color="#3976d8" />
    <section class="panel quick-signals"><div class="panel-head"><h2>当前状态</h2></div><div class="panel-body"><div class="signal-group"><span>积极</span><div><SignalTag v-for="signal in stock.signals.slice(0, 3)" :key="signal" :text="signal" tone="positive" /></div></div><div class="signal-group"><span>风险</span><div><SignalTag v-for="risk in stock.risks" :key="risk" :text="risk" tone="warning" /></div></div></div></section>
  </div>

  <section class="panel section-gap">
    <div class="panel-head chart-toolbar"><div><h2>价格与技术指标</h2><p>{{ historicalSource ? '数据库日K' : '演示日K' }} · 成交量 · MA · MACD</p></div><div class="chart-controls"><div class="segmented"><button v-for="item in ['日','周','月']" :key="item" :class="{ active: period === item }" @click="period = item">{{ item }}</button></div><select v-model="adjust"><option>前复权</option><option>不复权</option><option>后复权</option></select></div></div>
    <div class="chart-panel"><EChart :option="klineOption" height="475px" /></div>
  </section>

  <section class="panel section-gap detail-tabs">
    <div class="tabs-nav"><button v-for="tab in [{id:'analysis',name:'技术分析'},{id:'behavior',name:'涨停基因'},{id:'position',name:'历史位置'}]" :key="tab.id" :class="{ active: activeTab === tab.id }" @click="activeTab = tab.id">{{ tab.name }}</button></div>
    <div v-if="activeTab === 'analysis'" class="tab-content analysis-grid">
      <div><h3>技术状态拆解</h3><div class="factor-list"><div v-for="factor in [{name:'趋势',score:92,text:'MA5 > MA10 > MA20，MA20向上'},{name:'动能',score:78,text:'MACD 零轴上方，柱体扩张'},{name:'量能',score:84,text:'成交量约为20日均量 1.7 倍'},{name:'风险',score:66,text:'短期涨幅偏大，RSI 接近高位'}]" :key="factor.name" class="factor-row"><strong>{{ factor.name }}</strong><div class="factor-track"><i :style="{width:`${factor.score}%`}" /></div><span>{{ factor.score }}</span><p>{{ factor.text }}</p></div></div></div>
      <div class="tech-summary"><span>研究摘要</span><strong>趋势偏强，量能配合，短期风险有所增加。</strong><p>当前演示数据中，股价站上 MA60，MA20 斜率向上且 MACD 位于零轴上方。价格并非高分位，但短线涨幅扩张，继续观察回踩时的量价表现。</p><div><SignalTag text="技术状态较强" tone="info" /><SignalTag text="不构成买入建议" tone="neutral" /></div></div>
    </div>
    <div v-else-if="activeTab === 'behavior'" class="tab-content">
      <div class="gene-metrics"><div v-for="item in [['近半年涨停','4次'],['近一年涨停',`${stock.limitUpsYear}次`],['近两年涨停','17次'],['最大连板',`${stock.maxStreak}板`],['最近涨停',stock.recentLimitUp],['炸板次数','5次'],['一字涨停','2次'],['封板成功率','72%']]" :key="String(item[0])"><span>{{ item[0] }}</span><strong>{{ item[1] }}</strong></div></div>
      <div class="gene-grid section-gap"><div><h3>涨停后历史统计</h3><table class="data-table"><thead><tr><th>周期</th><th class="num">样本</th><th class="num">上涨概率</th><th class="num">平均收益</th><th class="num">中位收益</th></tr></thead><tbody><tr v-for="row in behaviorHorizon" :key="row.label"><td><strong>{{ row.label }}</strong></td><td class="num">{{ row.samples }}</td><td class="num">{{ row.win }}%</td><td class="num positive">+{{ row.avg }}%</td><td class="num positive">+{{ row.median }}%</td></tr></tbody></table></div><div><h3>涨停时间轴</h3><div class="timeline"><div v-for="event in [{date:'2026-07-18',title:'涨停收盘',note:'放量封板 · 换手 8.6%'},{date:'2026-03-06',title:'触板未封',note:'盘中触及涨停 · 收盘 +6.2%'},{date:'2025-12-22',title:'2 连板',note:'一字涨停后 T 字板'},{date:'2025-10-09',title:'涨停收盘',note:'低位首次放量'}]" :key="event.date"><i /><div><span>{{ event.date }}</span><strong>{{ event.title }}</strong><p>{{ event.note }}</p></div></div></div></div></div>
    </div>
    <div v-else class="tab-content position-grid">
      <div><h3>多周期价格分位</h3><div class="position-cards"><div><span>半年价格分位</span><strong>41%</strong><PositionBar :value="41" min-label="半年最低" max-label="半年最高" /></div><div><span>一年价格分位</span><strong>{{ stock.pricePercentile }}%</strong><PositionBar :value="stock.pricePercentile" /></div><div><span>三年价格分位</span><strong>36%</strong><PositionBar :value="36" min-label="三年最低" max-label="三年最高" /></div></div></div>
      <div class="distance-panel"><h3>关键距离</h3><div v-for="item in [['距离60日高点','-8.4%'],['距离52周高点','-14.7%'],['距离52周低点','+39.2%'],['近一年波动区间','3.91 — 6.87']]" :key="String(item[0])"><span>{{ item[0] }}</span><strong>{{ item[1] }}</strong></div></div>
    </div>
  </section>

  <el-dialog v-model="alertDialog" title="新建演示预警" width="430px">
    <div class="form-field"><label>股票</label><input :value="`${stock.name} ${stock.code}`" disabled /></div>
    <div class="grid-2"><div class="form-field"><label>预警类型</label><select v-model="alertForm.type"><option>价格低于</option><option>价格高于</option><option>Technical 上穿</option><option>跌破 MA20</option></select></div><div class="form-field"><label>阈值</label><input v-model.number="alertForm.value" type="number" step="0.01" /></div></div>
    <template #footer><button class="btn" @click="alertDialog = false">取消</button><button class="btn primary" @click="saveAlert">保存预警</button></template>
  </el-dialog>

  <el-dialog v-model="tradeDialog" title="记录买入" width="520px">
    <div class="grid-3"><div class="form-field"><label>日期</label><input v-model="tradeForm.date" type="date" /></div><div class="form-field"><label>价格</label><input v-model.number="tradeForm.price" type="number" step="0.01" /></div><div class="form-field"><label>数量（股）</label><input v-model.number="tradeForm.quantity" type="number" step="100" /></div></div>
    <div class="form-field"><label>关联策略</label><select v-model="tradeForm.strategy"><option>历史活跃低位转强</option><option>低位放量</option><option>趋势突破</option><option>手工研究</option></select></div>
    <div class="form-field"><label>买入原因</label><textarea v-model="tradeForm.reason" /></div>
    <template #footer><button class="btn" @click="tradeDialog = false">取消</button><button class="btn primary" @click="saveTrade">保存交易</button></template>
  </el-dialog>
  </template>
  <section v-else class="panel empty-stock"><strong>未找到股票 {{ routeSymbol }}</strong><p>请从搜索、自选或选股结果打开有效证券代码。</p></section>
</template>

<style scoped>
.stock-quote { display: grid; grid-template-columns: 1.4fr repeat(5, .62fr); overflow: hidden; }
.quote-primary { grid-row: span 2; padding: 16px 18px; border-right: 1px solid var(--border); }
.quote-primary > span { color: var(--text-3); font-size: 10px; }
.quote-primary > div { display: flex; align-items: baseline; gap: 12px; margin-top: 8px; }
.quote-primary strong { font: 700 32px var(--mono); letter-spacing: -1.5px; }
.quote-primary em { font: 600 12px var(--mono); }
.quote-item { min-height: 48px; padding: 10px 12px; border-right: 1px solid var(--border); border-bottom: 1px solid var(--border); }
.empty-stock { padding: 48px; text-align: center; }.empty-stock p { margin-top: 8px; color: var(--text-3); }
.quote-item:nth-last-child(-n+5) { border-bottom: 0; }
.quote-item span, .quote-item strong { display: block; }
.quote-item span { color: var(--text-3); font-size: 9px; }
.quote-item strong { margin-top: 5px; font: 600 11px var(--mono); }
.stock-score-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)) minmax(260px, 1.1fr); gap: 12px; }
.quick-signals .panel-body { padding-top: 11px; }
.signal-group { display: grid; grid-template-columns: 34px 1fr; gap: 7px; align-items: start; }
.signal-group + .signal-group { margin-top: 10px; }
.signal-group > span { color: var(--text-3); font-size: 10px; line-height: 22px; }
.chart-toolbar { min-height: 54px; }
.chart-controls { display: flex; align-items: center; gap: 8px; }
.chart-controls select { height: 33px; padding: 0 8px; border: 1px solid var(--border); border-radius: 7px; background: #fff; color: var(--text-2); font-size: 11px; }
.tabs-nav { display: flex; gap: 4px; min-height: 46px; align-items: flex-end; padding: 0 14px; border-bottom: 1px solid var(--border); }
.tabs-nav button { height: 46px; padding: 0 15px; border: 0; border-bottom: 2px solid transparent; background: transparent; color: var(--text-3); font-size: 12px; cursor: pointer; }
.tabs-nav button.active { color: var(--brand); border-color: var(--brand); font-weight: 650; }
.tab-content { padding: 18px; }
.tab-content h3 { margin-bottom: 14px; font-size: 13px; }
.analysis-grid { display: grid; grid-template-columns: 1.4fr .8fr; gap: 22px; }
.factor-row { display: grid; grid-template-columns: 44px minmax(100px, .55fr) 34px 1.4fr; gap: 10px; align-items: center; min-height: 42px; border-bottom: 1px solid #eef0f3; }
.factor-row strong { font-size: 11px; }
.factor-row span { font: 600 11px var(--mono); color: var(--brand); }
.factor-row p { color: var(--text-2); font-size: 10px; }
.factor-track { height: 5px; border-radius: 5px; background: #eceef2; overflow: hidden; }
.factor-track i { display: block; height: 100%; border-radius: 5px; background: var(--brand); }
.tech-summary { padding: 16px; border-radius: 9px; background: #f6f6fb; }
.tech-summary > span { color: var(--text-3); font-size: 10px; }
.tech-summary > strong { display: block; margin-top: 10px; font-size: 14px; line-height: 1.5; }
.tech-summary > p { margin: 10px 0 14px; color: var(--text-2); font-size: 11px; line-height: 1.75; }
.gene-metrics { display: grid; grid-template-columns: repeat(8, 1fr); border: 1px solid var(--border); border-radius: 8px; }
.gene-metrics > div { padding: 12px; border-right: 1px solid var(--border); }
.gene-metrics > div:last-child { border-right: 0; }
.gene-metrics span, .gene-metrics strong { display: block; }
.gene-metrics span { color: var(--text-3); font-size: 9px; }
.gene-metrics strong { margin-top: 7px; font: 600 14px var(--mono); }
.gene-grid { display: grid; grid-template-columns: 1.15fr .85fr; gap: 22px; }
.timeline { border-left: 1px solid var(--border-strong); margin-left: 4px; }
.timeline > div { position: relative; padding: 0 0 14px 18px; }
.timeline i { position: absolute; left: -4px; top: 4px; width: 7px; height: 7px; border: 2px solid #fff; border-radius: 50%; background: var(--brand); box-shadow: 0 0 0 1px var(--brand); }
.timeline span { color: var(--text-3); font: 9px var(--mono); }
.timeline strong { display: block; margin-top: 2px; font-size: 11px; }
.timeline p { margin-top: 3px; color: var(--text-3); font-size: 9px; }
.position-grid { display: grid; grid-template-columns: 1.5fr .7fr; gap: 22px; }
.position-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.position-cards > div { padding: 14px; border: 1px solid var(--border); border-radius: 8px; }
.position-cards span { color: var(--text-3); font-size: 10px; }
.position-cards > div > strong { display: block; margin-top: 7px; font: 650 22px var(--mono); }
.distance-panel > div { display: flex; align-items: center; justify-content: space-between; min-height: 38px; border-bottom: 1px solid #eef0f3; }
.distance-panel span { color: var(--text-2); font-size: 10px; }
.distance-panel strong { font: 600 11px var(--mono); }
@media (max-width: 1280px) { .stock-score-grid { grid-template-columns: repeat(3, 1fr); } .quick-signals { grid-column: 1 / -1; } .gene-metrics { grid-template-columns: repeat(4, 1fr); } .gene-metrics > div:nth-child(4) { border-right: 0; } .gene-metrics > div:nth-child(-n+4) { border-bottom: 1px solid var(--border); } }
</style>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import type { EChartsOption } from 'echarts'
import { ArrowRight, Refresh } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import EChart from '@/components/charts/EChart.vue'
import SignalTag from '@/components/SignalTag.vue'
import QuoteStatus from '@/components/QuoteStatus.vue'
import { breadth, changes, indices, scanCards, sectors, sentiment, stocks } from '@/mock'
import { useWatchlistStore } from '@/stores/watchlist'
import { useQuoteSubscription } from '@/composables/useQuoteSubscription'

const router = useRouter()
const watchlist = useWatchlistStore()
const indexSymbols = ['SH.000001', 'SZ.399001', 'SZ.399006', 'SH.000688']
const quoteSymbols = computed(() => [...indexSymbols, ...watchlist.items.slice(0, 5).map(item => item.symbol)])
const quotes = useQuoteSubscription(quoteSymbols)
const displayIndices = computed(() => indices.map((index, position) => {
  const quote = quotes.quote(indexSymbols[position]!)
  return { ...index, value: quote?.price == null ? (quote ? '—' : index.value) : quote.price.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }), change: quote ? quote.changePct : index.change, quote }
}))
const watchStocks = computed(() => watchlist.items.map((item) => {
  const stock = stocks.find((candidate) => candidate.symbol === item.symbol)
  if (!stock) return null
  const quote = quotes.quote(stock.symbol)
  return { ...stock, price: quote ? quote.price : stock.price, change: quote ? quote.change : stock.change, changePct: quote ? quote.changePct : stock.changePct, quote }
}).filter(Boolean).slice(0, 5))
const hasLiveSource = computed(() => ['ifind', 'tushare', 'cache'].includes(quotes.provider?.activeSource || ''))
const formatPrice = (value: number | null) => value == null ? '—' : value.toFixed(2)
const formatPct = (value: number | null) => value == null ? '—' : `${value > 0 ? '+' : ''}${value.toFixed(2)}%`

const sentimentOption = computed<EChartsOption>(() => ({
  animationDuration: 500,
  grid: { top: 9, right: 4, bottom: 18, left: 4 },
  xAxis: { type: 'category', boundaryGap: false, data: sentiment.trend.map((_, i) => i + 1), axisLine: { show: false }, axisTick: { show: false }, axisLabel: { show: false } },
  yAxis: { type: 'value', min: 30, max: 90, show: false },
  tooltip: { trigger: 'axis', valueFormatter: (value) => `${value}` },
  series: [{ type: 'line', data: sentiment.trend, showSymbol: false, smooth: .35, lineStyle: { color: '#5555c9', width: 2 }, areaStyle: { color: 'rgba(85,85,201,.10)' } }],
}))

const sparkPath = (values: number[]) => {
  const min = Math.min(...values); const max = Math.max(...values); const span = max - min || 1
  return values.map((value, i) => `${(i / (values.length - 1)) * 86 + 1},${35 - ((value - min) / span) * 31}`).join(' ')
}
</script>

<template>
  <PageHeader title="今日工作台" description="市场脉络、个人关注与策略变化，集中在一处。">
    <button class="btn" @click="quotes.fetchQuotes()"><Refresh />刷新行情</button>
  </PageHeader>
  <div class="demo-banner"><span><b>{{ hasLiveSource ? 'MARKET DATA' : 'DEMO / MOCK' }}</b>　指数与自选价格来自行情服务；广度、板块与评分仍为演示研究数据。</span><QuoteStatus :quote="watchStocks[0]?.quote" :connection="quotes.connection" /></div>

  <section class="index-strip">
    <button v-for="index in displayIndices" :key="index.code" class="index-card plain-button" @click="router.push('/market')">
      <div><span>{{ index.name }} · {{ index.code }}</span><strong>{{ index.value }}</strong><em :class="index.change == null ? '' : index.change >= 0 ? 'positive' : 'negative'">{{ formatPct(index.change) }}</em></div>
      <svg v-if="!index.quote || index.quote.isDemo" class="spark" viewBox="0 0 88 38" preserveAspectRatio="none"><polyline fill="none" :stroke="index.change != null && index.change >= 0 ? '#d74444' : '#15966f'" stroke-width="1.7" :points="sparkPath(index.points)" /></svg>
    </button>
  </section>

  <section class="panel section-gap">
    <div class="breadth-line">
      <div class="breadth-item"><span>上涨家数</span><strong class="positive">{{ breadth.rise.toLocaleString() }}</strong></div>
      <div class="breadth-item"><span>下跌家数</span><strong class="negative">{{ breadth.fall.toLocaleString() }}</strong></div>
      <div class="breadth-item"><span>平盘</span><strong>{{ breadth.flat }}</strong></div>
      <div class="breadth-item"><span>涨停</span><strong class="positive">{{ breadth.limitUp }}</strong></div>
      <div class="breadth-item"><span>跌停</span><strong class="negative">{{ breadth.limitDown }}</strong></div>
      <div class="breadth-item"><span>两市成交额</span><strong>{{ breadth.amount }}</strong></div>
    </div>
  </section>

  <div class="dashboard-grid section-gap">
    <div class="stack">
      <section class="panel">
        <div class="panel-head"><div><h2>市场情绪</h2><p>基于演示市场广度与活跃度的 0–100 指标</p></div><span class="chart-legend-note">近 20 个交易日</span></div>
        <div class="panel-body emotion-wrap"><div><div class="emotion-value"><strong>{{ sentiment.value }}</strong><span>/ 100</span></div><div class="emotion-level">{{ sentiment.level }}</div></div><EChart :option="sentimentOption" height="92px" /></div>
      </section>

      <section class="panel">
        <div class="panel-head"><div><h2>今日扫描</h2><p>系统规则在全市场发现的新信号</p></div><button class="text-button" @click="router.push('/radar')">查看雷达 <ArrowRight /></button></div>
        <div class="panel-body scan-grid">
          <button v-for="scan in scanCards" :key="scan.name" class="scan-card plain-button" @click="router.push('/screener')"><span>{{ scan.name }}</span><strong>{{ scan.count }}</strong><small>较昨日 {{ scan.delta }}</small></button>
        </div>
      </section>

      <section class="panel">
        <div class="panel-head"><div><h2>我的自选</h2><p>{{ watchlist.items.length }} 只股票 · 按关注优先级</p></div><button class="text-button" @click="router.push('/watchlist')">管理自选 <ArrowRight /></button></div>
        <div class="data-table-wrap"><table class="data-table"><thead><tr><th>股票</th><th class="num">现价</th><th class="num">涨跌</th><th class="num">Technical</th><th class="num">Behavior</th><th class="num">价格分位</th><th>主要信号</th></tr></thead><tbody><tr v-for="stock in watchStocks" :key="stock!.symbol" @click="router.push(`/stock/${stock!.symbol}`)"><td><div class="stock-cell"><span class="stock-round">{{ stock!.name[0] }}</span><span><strong>{{ stock!.name }}</strong><small>{{ stock!.code }}</small></span></div></td><td class="num">{{ formatPrice(stock!.price) }}</td><td class="num" :class="stock!.changePct == null ? '' : stock!.changePct >= 0 ? 'positive' : 'negative'">{{ formatPct(stock!.changePct) }}</td><td class="num"><span class="score-number">{{ stock!.technicalScore }}</span></td><td class="num">{{ stock!.behaviorScore }}</td><td class="num">{{ stock!.pricePercentile }}%</td><td><SignalTag :text="stock!.signals[0]" tone="info" /></td></tr></tbody></table></div>
      </section>
    </div>

    <div class="stack">
      <section class="panel">
        <div class="panel-head"><div><h2>今日变化</h2><p>与你的自选、持仓和策略相关</p></div></div>
        <div class="change-list"><div v-for="item in changes" :key="item.label" class="change-row"><i :style="{ background: item.color }" /><span>{{ item.label }}<small>{{ item.note }}</small></span><strong>{{ item.value }}</strong></div></div>
      </section>
      <section class="panel">
        <div class="panel-head"><div><h2>热门板块</h2><p>多周期强度与当前阶段</p></div><button class="text-button" @click="router.push('/market')">全部</button></div>
        <div class="panel-body sector-list"><div v-for="sector in sectors.slice(0, 6)" :key="sector.name" class="sector-row"><strong>{{ sector.name }}</strong><span :class="sector.change >= 0 ? 'positive' : 'negative'">{{ sector.change > 0 ? '+' : '' }}{{ sector.change }}%</span><span>{{ sector.return5 > 0 ? '+' : '' }}{{ sector.return5 }}%</span><span>{{ sector.strength }}</span><em class="stage">{{ sector.stage }}</em></div></div>
      </section>
      <section class="panel">
        <div class="panel-head"><div><h2>研究提示</h2><p>来自当前 Demo 数据状态</p></div></div>
        <div class="panel-body research-note"><strong>市场活跃度偏高</strong><p>上涨家数占比约 69.5%，机器人与存储芯片进入高强度区。自选中 3 只股票技术状态转强，同时 2 只持仓出现新的风险信号。</p><button class="btn soft" @click="router.push('/screener')">打开条件选股</button></div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.plain-button { border: 0; background: transparent; text-align: left; cursor: pointer; }
.index-card.plain-button { background: #fff; }
.panel-head .text-button { display: inline-flex; align-items: center; gap: 4px; }
.panel-head .text-button svg { width: 11px; }
.research-note strong { font-size: 13px; }
.research-note p { margin-top: 8px; color: var(--text-2); font-size: 11px; line-height: 1.7; }
.research-note .btn { margin-top: 12px; }
</style>

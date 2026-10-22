<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import type { EChartsOption } from 'echarts'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import MetricCard from '@/components/MetricCard.vue'
import SignalTag from '@/components/SignalTag.vue'
import EChart from '@/components/charts/EChart.vue'
import { navSeries } from '@/mock/portfolio'
import { stocks } from '@/mock/stocks'
import { usePortfolioStore } from '@/stores/portfolio'
import QuoteStatus from '@/components/QuoteStatus.vue'
import { useQuoteSubscription } from '@/composables/useQuoteSubscription'

const store = usePortfolioStore()
const account = ref('模拟策略账户')
const active = ref('当前持仓')
const dialog = ref(false)
const form = reactive({ symbol: 'SZ.000630', date: '2026-08-30', side: '买入' as '买入' | '卖出', price: 5.86, quantity: 1000, strategy: '手工研究', reason: '按交易计划记录' })
const symbols = computed(() => store.currentPositions.map(item => item.symbol))
const quotes = useQuoteSubscription(symbols)
const valuedPositions = computed(() => store.currentPositions.map(item => {
  const quote = quotes.quote(item.symbol)
  const price = quote ? quote.price : item.price
  const marketValue = price == null ? null : Math.round(price * item.quantity)
  const pnl = price == null ? null : Math.round((price - item.avgCost) * item.quantity)
  return { ...item, price, marketValue, pnl, returnPct: price == null ? null : +((price / item.avgCost - 1) * 100).toFixed(2), quote }
}))
const totalMarket = computed(() => valuedPositions.value.reduce((sum, item) => sum + (item.marketValue ?? 0), 0))
const totalPnl = computed(() => valuedPositions.value.reduce((sum, item) => sum + (item.pnl ?? 0), 0))
const cash = 126842
const totalAssets = computed(() => totalMarket.value + cash)
const industryData = computed(() => Object.entries(valuedPositions.value.reduce<Record<string, number>>((map, item) => { map[item.industry] = (map[item.industry] || 0) + (item.marketValue ?? 0); return map }, {})).map(([name, value]) => ({ name, value })))
const formatMoney = (value: number | null) => value == null ? '—' : `¥${value.toLocaleString()}`
const formatPrice = (value: number | null) => value == null ? '—' : value.toFixed(2)
const formatPct = (value: number | null) => value == null ? '—' : `${value > 0 ? '+' : ''}${value.toFixed(2)}%`
const navOption = computed<EChartsOption>(() => ({
  grid: { top: 15, right: 18, bottom: 26, left: 46 }, tooltip: { trigger: 'axis', valueFormatter: (value) => `${value}` },
  xAxis: { type: 'category', boundaryGap: false, data: navSeries.map((_, i) => `08/${String(i + 1).padStart(2, '0')}`), axisTick: { show: false }, axisLine: { lineStyle: { color: '#dfe1e6' } }, axisLabel: { color: '#8a909e', fontSize: 9, interval: 4 } },
  yAxis: { type: 'value', min: 95, max: 128, axisLine: { show: false }, axisTick: { show: false }, splitLine: { lineStyle: { color: '#eef0f3' } }, axisLabel: { color: '#8a909e', fontSize: 9 } },
  series: [{ type: 'line', data: navSeries, smooth: .3, showSymbol: false, lineStyle: { width: 2, color: '#5555c9' }, areaStyle: { color: 'rgba(85,85,201,.09)' } }],
}))
const allocationOption = computed<EChartsOption>(() => ({
  tooltip: { trigger: 'item', formatter: '{b}<br/>{d}%' }, legend: { bottom: 2, itemWidth: 9, itemHeight: 9, textStyle: { color: '#6f7582', fontSize: 9 } },
  series: [{ type: 'pie', radius: ['53%', '73%'], center: ['50%', '42%'], avoidLabelOverlap: true, label: { show: false }, emphasis: { label: { show: false } }, itemStyle: { borderColor: '#fff', borderWidth: 2 }, color: ['#5555c9','#c4792a','#3976d8','#8998a6'], data: industryData.value }],
}))
function addTransaction() {
  const stock = stocks.find((item) => item.symbol === form.symbol)!
  store.addTransaction({ ...form, stockName: stock.name })
  dialog.value = false; ElMessage.success('演示交易已添加')
}
</script>

<template>
  <PageHeader title="持仓" description="查看资产、仓位、风险与完整交易流水。">
    <select v-model="account" class="page-select"><option>模拟策略账户</option><option>长期观察账户</option></select>
    <button class="btn primary" @click="dialog = true"><Plus />添加交易</button>
  </PageHeader>
  <div class="demo-banner"><span><b>PAPER ACCOUNT</b>　数量、成本与流水为演示记录；市值和浮盈亏按当前行情重新估值。</span><QuoteStatus :quote="valuedPositions[0]?.quote" :connection="quotes.connection" /></div>

  <div class="portfolio-metrics">
    <MetricCard label="总资产" :value="`¥${totalAssets.toLocaleString()}`" change="+1.21% 今日" tone="positive" hint="市值 + 现金" />
    <MetricCard label="今日盈亏" value="+¥5,486" change="+1.36%" tone="positive" hint="截至演示收盘" />
    <MetricCard label="累计盈亏" :value="`${totalPnl >= 0 ? '+' : ''}¥${totalPnl.toLocaleString()}`" change="+7.4%" tone="positive" hint="不含历史已清仓交易" />
    <MetricCard label="最大回撤" value="-8.6%" change="近 12 个月" tone="negative" hint="按每日账户净值" />
    <MetricCard label="现金 / 仓位" :value="`¥${cash.toLocaleString()}`" change="76.3% 仓位" tone="neutral" hint="可用现金 23.7%" />
  </div>

  <div class="portfolio-charts section-gap">
    <section class="panel"><div class="panel-head"><div><h2>账户净值曲线</h2><p>基准 100 · 近 20 个演示交易日</p></div><span class="chart-legend-note">最新 124.6</span></div><div class="chart-panel"><EChart :option="navOption" height="280px" /></div></section>
    <section class="panel"><div class="panel-head"><div><h2>行业分布</h2><p>按当前持仓市值</p></div></div><div class="chart-panel"><EChart :option="allocationOption" height="280px" /></div></section>
  </div>

  <section class="panel section-gap">
    <div class="portfolio-tabs"><div class="segmented"><button v-for="item in ['当前持仓','交易记录']" :key="item" :class="{ active: active === item }" @click="active = item">{{ item }}</button></div><span>{{ active === '当前持仓' ? `${store.currentPositions.length} 只持仓` : `${store.history.length} 笔交易` }}</span></div>
    <div v-if="active === '当前持仓'" class="data-table-wrap"><table class="data-table"><thead><tr><th>股票</th><th class="num">数量</th><th class="num">平均成本</th><th class="num">当前价</th><th class="num">市值</th><th class="num">浮盈亏</th><th class="num">收益率</th><th class="num">仓位</th><th class="num">Technical</th><th>风险信号</th></tr></thead><tbody><tr v-for="position in valuedPositions" :key="position.symbol"><td><div class="stock-cell"><span class="stock-round">{{ position.stockName[0] }}</span><span><strong>{{ position.stockName }}</strong><small>{{ position.symbol }}</small></span></div></td><td class="num">{{ position.quantity.toLocaleString() }}</td><td class="num">{{ position.avgCost.toFixed(2) }}</td><td class="num">{{ formatPrice(position.price) }}</td><td class="num">{{ formatMoney(position.marketValue) }}</td><td class="num" :class="position.pnl == null ? '' : position.pnl >= 0 ? 'positive' : 'negative'">{{ position.pnl != null && position.pnl >= 0 ? '+' : '' }}{{ formatMoney(position.pnl) }}</td><td class="num" :class="position.returnPct == null ? '' : position.returnPct >= 0 ? 'positive' : 'negative'">{{ formatPct(position.returnPct) }}</td><td class="num">{{ position.weight }}%</td><td class="num"><span class="score-number">{{ position.technicalScore }}</span></td><td><SignalTag :text="position.risk" tone="warning" /></td></tr></tbody></table></div>
    <div v-else class="data-table-wrap"><table class="data-table"><thead><tr><th>日期</th><th>股票</th><th>方向</th><th class="num">价格</th><th class="num">数量</th><th class="num">金额</th><th>策略</th><th>原因</th></tr></thead><tbody><tr v-for="transaction in store.history" :key="transaction.id"><td class="mono muted">{{ transaction.date }}</td><td><strong>{{ transaction.stockName }}</strong><small class="stock-code-inline">{{ transaction.symbol }}</small></td><td><SignalTag :text="transaction.side" :tone="transaction.side === '买入' ? 'positive' : 'negative'" /></td><td class="num">{{ transaction.price.toFixed(2) }}</td><td class="num">{{ transaction.quantity.toLocaleString() }}</td><td class="num">¥{{ transaction.amount.toLocaleString() }}</td><td>{{ transaction.strategy }}</td><td class="reason-cell">{{ transaction.reason }}</td></tr></tbody></table></div>
  </section>

  <el-dialog v-model="dialog" title="添加演示交易" width="570px"><div class="grid-3"><div class="form-field"><label>股票</label><select v-model="form.symbol"><option v-for="stock in stocks" :key="stock.symbol" :value="stock.symbol">{{ stock.name }}</option></select></div><div class="form-field"><label>日期</label><input v-model="form.date" type="date" /></div><div class="form-field"><label>方向</label><select v-model="form.side"><option>买入</option><option>卖出</option></select></div></div><div class="grid-2"><div class="form-field"><label>价格</label><input v-model.number="form.price" type="number" step="0.01" /></div><div class="form-field"><label>数量（股）</label><input v-model.number="form.quantity" type="number" step="100" /></div></div><div class="form-field"><label>关联策略</label><input v-model="form.strategy" /></div><div class="form-field"><label>交易原因</label><textarea v-model="form.reason" /></div><template #footer><button class="btn" @click="dialog = false">取消</button><button class="btn primary" @click="addTransaction">保存交易</button></template></el-dialog>
</template>

<style scoped>
.page-select { height: 34px; padding: 0 10px; border: 1px solid var(--border-strong); border-radius: 7px; background: #fff; color: var(--text-2); font-size: 11px; }
.portfolio-metrics { display: grid; grid-template-columns: 1.15fr repeat(4, 1fr); gap: 10px; }
.portfolio-charts { display: grid; grid-template-columns: 1.55fr .65fr; gap: 14px; }
.portfolio-tabs { min-height: 52px; display: flex; align-items: center; justify-content: space-between; padding: 0 14px; border-bottom: 1px solid var(--border); }.portfolio-tabs > span { color: var(--text-3); font-size: 10px; }
.stock-code-inline { margin-left: 6px; color: var(--text-3); font: 8px var(--mono); }.reason-cell { max-width: 240px; overflow: hidden; text-overflow: ellipsis; }.data-table tbody tr { cursor: default; }
</style>

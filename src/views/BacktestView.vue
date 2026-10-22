<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { EChartsOption } from 'echarts'
import { VideoPlay } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import MetricCard from '@/components/MetricCard.vue'
import EChart from '@/components/charts/EChart.vue'
import SignalTag from '@/components/SignalTag.vue'
import { annualBacktest, horizonStats, strategies } from '@/mock/strategies'
import { BacktestService } from '@/services/backtestService'

const route = useRoute()
const router = useRouter()
const form = reactive({ strategy: Number(route.query.strategy) || 1, start: '2023-01-01', end: '2026-08-30', mode: 'FIRST_ENTRY' })
const loading = ref(false)
const progress = ref(100)
const hasResult = ref(true)
const periodOption = computed<EChartsOption>(() => ({
  grid: { top: 20, right: 18, bottom: 30, left: 48 }, tooltip: { trigger: 'axis' }, legend: { top: 0, data: ['平均收益','中位收益'], textStyle: { color: '#777d88', fontSize: 9 }, itemWidth: 12, itemHeight: 7 }, xAxis: { type: 'category', data: horizonStats.map((row) => row.horizon), axisTick: { show: false }, axisLine: { lineStyle: { color: '#dfe1e6' } }, axisLabel: { color: '#6f7582', fontSize: 9 } }, yAxis: { type: 'value', axisLine: { show: false }, axisTick: { show: false }, splitLine: { lineStyle: { color: '#eef0f3' } }, axisLabel: { formatter: '{value}%', color: '#8a909e', fontSize: 8 } }, series: [{ name: '平均收益', type: 'bar', data: horizonStats.map((row) => row.avg), barWidth: 14, itemStyle: { color: '#6262cf', borderRadius: [3,3,0,0] } }, { name: '中位收益', type: 'line', data: horizonStats.map((row) => row.median), smooth: true, symbolSize: 5, lineStyle: { color: '#c4792a', width: 1.7 }, itemStyle: { color: '#c4792a' } }],
}))
const annualOption = computed<EChartsOption>(() => ({
  grid: { top: 15, right: 22, bottom: 28, left: 42 }, tooltip: { trigger: 'axis' }, xAxis: { type: 'category', data: annualBacktest.map((row) => row.year), axisTick: { show: false }, axisLine: { lineStyle: { color: '#dfe1e6' } }, axisLabel: { color: '#6f7582', fontSize: 9 } }, yAxis: { type: 'value', axisLine: { show: false }, axisTick: { show: false }, splitLine: { lineStyle: { color: '#eef0f3' } }, axisLabel: { formatter: '{value}%', color: '#8a909e', fontSize: 8 } }, series: [{ type: 'bar', barWidth: '42%', data: annualBacktest.map((row) => ({ value: row.avg, itemStyle: { color: '#6262cf', borderRadius: [3,3,0,0] } })), label: { show: true, position: 'top', formatter: '{c}%', color: '#535866', fontSize: 8 } }],
}))
const groupOption = computed<EChartsOption>(() => ({
  grid: { top: 10, right: 30, bottom: 22, left: 105 }, tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } }, xAxis: { type: 'value', axisLine: { show: false }, axisTick: { show: false }, splitLine: { lineStyle: { color: '#eef0f3' } }, axisLabel: { formatter: '{value}%', color: '#8a909e', fontSize: 8 } }, yAxis: { type: 'category', data: ['Technical <60','60–70','70–80','80–90','≥90'], axisTick: { show: false }, axisLine: { show: false }, axisLabel: { color: '#6f7582', fontSize: 8 } }, series: [{ type: 'bar', barWidth: 10, data: [1.2,3.8,6.4,9.1,8.3], itemStyle: { color: '#6262cf', borderRadius: [0,3,3,0] }, label: { show: true, position: 'right', formatter: '{c}%', color: '#535866', fontSize: 8 } }],
}))
const signalRows = [
  { date: '2026-08-18', stock: '铜陵有色', code: '000630', score: 78, percentile: 24, t5: 6.2, t20: 11.8, max: 15.4, drawdown: -3.1 },
  { date: '2026-07-09', stock: '湖南白银', code: '002716', score: 84, percentile: 29, t5: 8.7, t20: 16.3, max: 22.1, drawdown: -4.8 },
  { date: '2026-06-18', stock: '中科曙光', code: '603019', score: 81, percentile: 31, t5: 4.3, t20: 12.6, max: 18.7, drawdown: -5.1 },
  { date: '2026-05-22', stock: '科大讯飞', code: '002230', score: 72, percentile: 34, t5: -2.8, t20: -6.1, max: 3.2, drawdown: -9.4 },
]
async function run() { loading.value = true; progress.value = 18; hasResult.value = false; const timer = window.setInterval(() => progress.value = Math.min(92, progress.value + 16), 120); await BacktestService.run(); window.clearInterval(timer); progress.value = 100; loading.value = false; hasResult.value = true; ElMessage.success('Demo Signal Backtest 已完成') }
</script>

<template>
  <PageHeader title="策略回测" description="回到历史日期，验证选股信号后续表现，不模拟复杂资金撮合。"><SignalTag text="Signal Backtest" tone="info" /><button class="btn" @click="router.push({ path: '/quant', query: { strategy: form.strategy } })">使用该策略启动模拟</button></PageHeader>
  <div class="demo-banner"><span><b>DEMO / MOCK</b>　回测结果为固定演示样本，用于展示指标和交互。</span><span>Point-in-Time 概念原型</span></div>
  <section class="panel backtest-config"><div class="config-fields"><div class="form-field"><label>策略</label><select v-model="form.strategy"><option v-for="strategy in strategies" :key="strategy.id" :value="strategy.id">{{ strategy.name }}</option></select></div><div class="form-field"><label>开始日期</label><input v-model="form.start" type="date" /></div><div class="form-field"><label>结束日期</label><input v-model="form.end" type="date" /></div><div class="form-field"><label>信号模式</label><select v-model="form.mode"><option>FIRST_ENTRY</option><option>EVERY_SIGNAL</option></select></div><button class="btn primary run-button" :disabled="loading" @click="run"><VideoPlay />{{ loading ? `运行中 ${progress}%` : '运行 Demo 回测' }}</button></div><div v-if="loading" class="progress-track"><i :style="{ width: `${progress}%` }" /></div></section>
  <template v-if="hasResult">
    <div class="backtest-metrics section-gap"><MetricCard label="总信号数" value="486" change="3.7 年" tone="neutral" hint="去重前信号" /><MetricCard label="涉及股票" value="172" hint="演示股票集合" /><MetricCard label="T+5 上涨概率" value="61.3%" change="样本 461" tone="positive" /><MetricCard label="T+5 平均收益" value="+3.8%" change="中位 +1.9%" tone="positive" /><MetricCard label="T+20 上涨概率" value="58.7%" change="样本 402" tone="positive" /><MetricCard label="T+20 平均收益" value="+7.2%" change="中位 +3.4%" tone="positive" /></div>
    <div class="backtest-charts section-gap"><section class="panel span-2"><div class="panel-head"><div><h2>不同持有周期收益</h2><p>平均收益与中位收益</p></div></div><div class="chart-panel"><EChart :option="periodOption" height="270px" /></div></section><section class="panel"><div class="panel-head"><div><h2>年度表现</h2><p>年度信号平均收益</p></div></div><div class="chart-panel"><EChart :option="annualOption" height="270px" /></div></section><section class="panel"><div class="panel-head"><div><h2>按 Technical Score 分组</h2><p>入场评分与 T+20 平均收益</p></div></div><div class="chart-panel"><EChart :option="groupOption" height="270px" /></div></section></div>
    <section class="panel section-gap"><div class="panel-head"><div><h2>周期统计</h2><p>样本量、上涨概率、平均与中位收益</p></div><span class="chart-legend-note">策略版本 v1.3 快照</span></div><div class="data-table-wrap"><table class="data-table"><thead><tr><th>持有周期</th><th class="num">有效样本</th><th class="num">上涨概率</th><th class="num">平均收益</th><th class="num">中位收益</th></tr></thead><tbody><tr v-for="row in horizonStats" :key="row.horizon"><td><strong>{{ row.horizon }}</strong></td><td class="num">{{ row.samples }}</td><td class="num">{{ row.winRate }}%</td><td class="num positive">+{{ row.avg }}%</td><td class="num positive">+{{ row.median }}%</td></tr></tbody></table></div></section>
    <section class="panel section-gap"><div class="panel-head"><div><h2>历史信号</h2><p>点击后可进一步查看当时的入选解释</p></div></div><div class="data-table-wrap"><table class="data-table"><thead><tr><th>信号日期</th><th>股票</th><th class="num">入场 Technical</th><th class="num">价格分位</th><th class="num">T+5</th><th class="num">T+20</th><th class="num">最大上涨</th><th class="num">最大回撤</th><th>当时入选</th></tr></thead><tbody><tr v-for="row in signalRows" :key="row.date + row.code"><td class="mono muted">{{ row.date }}</td><td><strong>{{ row.stock }}</strong><small class="stock-code-inline">{{ row.code }}</small></td><td class="num">{{ row.score }}</td><td class="num">{{ row.percentile }}%</td><td class="num" :class="row.t5 >= 0 ? 'positive' : 'negative'">{{ row.t5 > 0 ? '+' : '' }}{{ row.t5 }}%</td><td class="num" :class="row.t20 >= 0 ? 'positive' : 'negative'">{{ row.t20 > 0 ? '+' : '' }}{{ row.t20 }}%</td><td class="num positive">+{{ row.max }}%</td><td class="num negative">{{ row.drawdown }}%</td><td><SignalTag text="全部条件通过" tone="positive" /></td></tr></tbody></table></div></section>
  </template>
</template>

<style scoped>
.backtest-config { padding: 14px; }.config-fields { display: grid; grid-template-columns: 1.35fr repeat(3, 1fr) auto; gap: 10px; align-items: end; }.config-fields .form-field { margin: 0; }.run-button { height: 40px; }.progress-track { height: 3px; margin-top: 13px; overflow: hidden; border-radius: 3px; background: #eceef2; }.progress-track i { display: block; height: 100%; background: var(--brand); transition: width .15s; }
.backtest-metrics { display: grid; grid-template-columns: repeat(6, 1fr); gap: 9px; }.backtest-metrics :deep(.metric-row strong) { font-size: 19px; }
.backtest-charts { display: grid; grid-template-columns: 1.25fr .75fr; gap: 14px; }.span-2 { grid-row: span 2; }.stock-code-inline { margin-left: 6px; color: var(--text-3); font: 8px var(--mono); }
</style>

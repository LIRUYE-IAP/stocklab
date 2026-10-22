<script setup lang="ts">
import { computed } from 'vue'
import type { EChartsOption } from 'echarts'
import PageHeader from '@/components/PageHeader.vue'
import MetricCard from '@/components/MetricCard.vue'
import EChart from '@/components/charts/EChart.vue'
import { breadth, marketDistribution, sectors } from '@/mock'

const distributionOption = computed<EChartsOption>(() => ({
  grid: { top: 14, right: 14, bottom: 32, left: 42 },
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, valueFormatter: (value) => `${value} 只` },
  xAxis: { type: 'category', data: marketDistribution.map((item) => item.range), axisTick: { show: false }, axisLine: { lineStyle: { color: '#dfe1e6' } }, axisLabel: { color: '#8a909e', fontSize: 9 } },
  yAxis: { type: 'value', axisLine: { show: false }, axisTick: { show: false }, splitLine: { lineStyle: { color: '#eef0f3' } }, axisLabel: { color: '#8a909e', fontSize: 9 } },
  series: [{ type: 'bar', barWidth: '68%', data: marketDistribution.map((item, i) => ({ value: item.value, itemStyle: { color: i < 5 ? '#6ab79f' : '#dc7070', borderRadius: [3, 3, 0, 0] } })) }],
}))

const rotationOption = computed<EChartsOption>(() => ({
  grid: { top: 24, right: 25, bottom: 40, left: 48 },
  tooltip: { formatter: (params: any) => `<b>${params.data.name}</b><br/>20日 ${params.value[0]}%<br/>5日 ${params.value[1]}%<br/>成交额 ${params.value[2]} 亿` },
  xAxis: { name: '20日收益', nameTextStyle: { color: '#8a909e', fontSize: 9 }, type: 'value', axisLine: { lineStyle: { color: '#cfd2d9' } }, splitLine: { lineStyle: { color: '#eef0f3' } }, axisLabel: { formatter: '{value}%', color: '#8a909e', fontSize: 9 } },
  yAxis: { name: '5日收益', nameTextStyle: { color: '#8a909e', fontSize: 9 }, type: 'value', axisLine: { lineStyle: { color: '#cfd2d9' } }, splitLine: { lineStyle: { color: '#eef0f3' } }, axisLabel: { formatter: '{value}%', color: '#8a909e', fontSize: 9 } },
  series: [{
    type: 'scatter',
    symbolSize: (value: number[]) => Math.max(18, Math.sqrt(value[2] ?? 0) * .8),
    data: sectors.map((sector) => ({ name: sector.name, value: [sector.return20, sector.return5, sector.amount], itemStyle: { color: sector.return5 >= 0 ? '#6262cf' : '#73ad9a', opacity: .78 } })),
    label: { show: true, formatter: '{b}', position: 'top', color: '#535866', fontSize: 9 },
  }],
  graphic: [
    { type: 'text', left: '62%', top: 28, style: { text: '主升', fill: '#b2b5bf', fontSize: 10 } },
    { type: 'text', left: '17%', top: 28, style: { text: '新启动', fill: '#b2b5bf', fontSize: 10 } },
    { type: 'text', left: '16%', bottom: 46, style: { text: '弱势', fill: '#b2b5bf', fontSize: 10 } },
    { type: 'text', left: '64%', bottom: 46, style: { text: '退潮', fill: '#b2b5bf', fontSize: 10 } },
  ],
}))

const heatmapOption = computed<EChartsOption>(() => ({
  tooltip: { formatter: (p: any) => `${p.name}<br/>今日 ${p.value}%` },
  series: [{
    type: 'treemap', roam: false, nodeClick: false, breadcrumb: { show: false },
    data: sectors.map((sector) => ({ name: `${sector.name}\n${sector.change > 0 ? '+' : ''}${sector.change}%`, value: Math.max(250, sector.amount), change: sector.change, itemStyle: { color: sector.change >= 0 ? `rgba(202, 62, 62, ${Math.min(.9, .35 + sector.change / 9)})` : `rgba(22, 140, 105, ${Math.min(.9, .35 + Math.abs(sector.change) / 7)})`, borderColor: '#fff', borderWidth: 2, gapWidth: 2 } })),
    label: { show: true, color: '#fff', fontSize: 11, lineHeight: 17, fontWeight: 600 },
  }],
}))
</script>

<template>
  <PageHeader title="市场" description="从市场广度、板块强度与轮动位置理解当日结构。">
    <div class="segmented"><button class="active">今日</button><button>本周</button><button>本月</button></div>
  </PageHeader>
  <div class="demo-banner"><span><b>DEMO / MOCK</b>　市场数据为演示快照，不代表当前真实行情。</span><span>收盘快照 · 2026-08-30</span></div>

  <div class="grid-4">
    <MetricCard label="上涨占比" value="69.5%" change="较昨日 +8.2pct" tone="positive" hint="3,618 / 5,206" />
    <MetricCard label="涨跌比" value="2.44" change="偏强" tone="positive" hint="上涨家数 ÷ 下跌家数" />
    <MetricCard label="涨停 / 跌停" value="76 / 9" change="封板率 71%" tone="neutral" hint="按演示价格限制规则" />
    <MetricCard label="两市成交额" value="1.60万亿" change="+11.8%" tone="positive" hint="较前一交易日" />
  </div>

  <div class="grid-2 section-gap market-top">
    <section class="panel"><div class="panel-head"><div><h2>涨跌幅分布</h2><p>全市场股票按当日涨跌幅区间</p></div><span class="chart-legend-note">共 {{ (breadth.rise + breadth.fall + breadth.flat).toLocaleString() }} 只</span></div><div class="chart-panel"><EChart :option="distributionOption" height="292px" /></div></section>
    <section class="panel"><div class="panel-head"><div><h2>板块轮动</h2><p>X：20日收益 · Y：5日收益 · 气泡：成交额</p></div></div><div class="chart-panel"><EChart :option="rotationOption" height="292px" /></div></section>
  </div>

  <div class="market-bottom section-gap">
    <section class="panel"><div class="panel-head"><div><h2>市场热力图</h2><p>面积代表演示成交额，颜色代表当日涨跌</p></div></div><div class="chart-panel"><EChart :option="heatmapOption" height="335px" /></div></section>
    <section class="panel"><div class="panel-head"><div><h2>板块强度榜</h2><p>今日、多周期与阶段状态</p></div></div><div class="data-table-wrap"><table class="data-table"><thead><tr><th>#</th><th>板块</th><th class="num">今日</th><th class="num">5日</th><th class="num">20日</th><th class="num">强度</th><th>阶段</th></tr></thead><tbody><tr v-for="(sector, index) in sectors" :key="sector.name"><td class="mono muted">{{ String(index + 1).padStart(2, '0') }}</td><td><strong>{{ sector.name }}</strong></td><td class="num" :class="sector.change >= 0 ? 'positive' : 'negative'">{{ sector.change > 0 ? '+' : '' }}{{ sector.change }}%</td><td class="num" :class="sector.return5 >= 0 ? 'positive' : 'negative'">{{ sector.return5 > 0 ? '+' : '' }}{{ sector.return5 }}%</td><td class="num" :class="sector.return20 >= 0 ? 'positive' : 'negative'">{{ sector.return20 > 0 ? '+' : '' }}{{ sector.return20 }}%</td><td class="num"><span class="strength"><i :style="{ width: `${sector.strength}%` }" /></span>{{ sector.strength }}</td><td><span class="stage-pill">{{ sector.stage }}</span></td></tr></tbody></table></div></section>
  </div>
</template>

<style scoped>
.market-bottom { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(500px, .9fr); gap: 14px; }
.strength { display: inline-block; width: 36px; height: 4px; margin-right: 7px; border-radius: 4px; background: #eceef2; vertical-align: middle; }
.strength i { display: block; height: 100%; border-radius: 4px; background: var(--brand); }
.stage-pill { padding: 2px 7px; border-radius: 5px; background: var(--surface-hover); font-size: 9px; }
@media (max-width: 1280px) { .market-bottom { grid-template-columns: 1fr; } }
</style>

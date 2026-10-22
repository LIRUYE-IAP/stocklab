<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Aim, Warning } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import SignalTag from '@/components/SignalTag.vue'
import { stocks } from '@/mock/stocks'
import { useWatchlistStore } from '@/stores/watchlist'
import { positions } from '@/mock/portfolio'

const router = useRouter()
const watchlist = useWatchlistStore()
const scope = ref('全市场')
const filtered = computed(() => scope.value === '我的自选' ? stocks.filter((stock) => watchlist.contains(stock.symbol)) : scope.value === '我的持仓' ? stocks.filter((stock) => positions.some((position) => position.symbol === stock.symbol)) : stocks)
const groups = computed(() => [
  { title: '强势', tone: 'positive', note: '放量突破 · 创新高 · 均线多头', rows: filtered.value.filter((stock) => stock.technicalScore >= 76).slice(0, 5) },
  { title: '潜在启动', tone: 'info', note: '底部放量 · 低位高换手 · 缩量回踩', rows: filtered.value.filter((stock) => stock.pricePercentile <= 55 && stock.technicalScore >= 55).slice(0, 5) },
  { title: '风险', tone: 'warning', note: '高位放量 · 跌破均线 · RSI 过热', rows: filtered.value.filter((stock) => stock.risks.length > 0).sort((a, b) => a.technicalScore - b.technicalScore).slice(0, 5) },
])
</script>

<template>
  <PageHeader title="异动雷达" description="把全市场、自选和持仓中的状态变化按研究目的分组。">
    <div class="segmented"><button v-for="item in ['全市场','我的自选','我的持仓']" :key="item" :class="{ active: scope === item }" @click="scope = item">{{ item }}</button></div>
  </PageHeader>
  <div class="demo-banner"><span><b>DEMO / MOCK</b>　雷达信号来自演示规则计算，不是实时盘中预警。</span><span>今日共发现 87 条变化</span></div>

  <div class="radar-summary panel">
    <div><Aim /><span><strong>{{ groups[0]?.rows.length ?? 0 }}</strong> 强势信号</span></div>
    <div><i class="launch-dot" /><span><strong>{{ groups[1]?.rows.length ?? 0 }}</strong> 潜在启动</span></div>
    <div><Warning /><span><strong>{{ groups[2]?.rows.length ?? 0 }}</strong> 风险信号</span></div>
    <p>范围：{{ scope }} · 演示股票 {{ filtered.length }} 只</p>
  </div>

  <div class="radar-grid section-gap">
    <section v-for="group in groups" :key="group.title" class="panel radar-column">
      <div class="panel-head"><div><h2>{{ group.title }}</h2><p>{{ group.note }}</p></div><span class="count-pill">{{ group.rows.length }}</span></div>
      <div class="radar-list">
        <button v-for="stock in group.rows" :key="stock.symbol" @click="router.push(`/stock/${stock.symbol}`)">
          <div class="stock-cell"><span class="stock-round">{{ stock.name[0] }}</span><span><strong>{{ stock.name }}</strong><small>{{ stock.code }} · {{ stock.industry }}</small></span></div>
          <div class="radar-value"><strong :class="stock.changePct >= 0 ? 'positive' : 'negative'">{{ stock.changePct > 0 ? '+' : '' }}{{ stock.changePct }}%</strong><small>Technical {{ stock.technicalScore }}</small></div>
          <div class="radar-tags"><SignalTag :text="group.title === '风险' ? stock.risks[0] : stock.signals[0]" :tone="group.tone as any" /><span>查看研究 →</span></div>
        </button>
        <div v-if="!group.rows.length" class="empty-state">当前范围暂无此类信号</div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.radar-summary { min-height: 64px; display: flex; align-items: center; gap: 28px; padding: 0 16px; }
.radar-summary > div { display: flex; align-items: center; gap: 8px; }
.radar-summary svg, .launch-dot { width: 16px; height: 16px; color: var(--brand); }
.launch-dot { display: block; border: 4px solid var(--blue-soft); border-radius: 50%; background: var(--blue); }
.radar-summary span { color: var(--text-2); font-size: 11px; }
.radar-summary strong { margin-right: 3px; color: var(--text); font: 650 15px var(--mono); }
.radar-summary p { margin-left: auto; color: var(--text-3); font-size: 10px; }
.radar-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.count-pill { min-width: 24px; height: 20px; display: grid; place-items: center; border-radius: 10px; background: var(--surface-hover); color: var(--text-2); font: 10px var(--mono); }
.radar-list { padding: 6px; }
.radar-list > button { width: 100%; display: grid; grid-template-columns: 1fr auto; gap: 8px; padding: 10px 8px; border: 0; border-bottom: 1px solid #eef0f3; background: transparent; text-align: left; cursor: pointer; }
.radar-list > button:last-child { border-bottom: 0; }
.radar-list > button:hover { border-radius: 7px; background: var(--surface-hover); }
.radar-value { text-align: right; }
.radar-value strong { display: block; font: 600 11px var(--mono); }
.radar-value small { display: block; margin-top: 4px; color: var(--text-3); font: 9px var(--mono); }
.radar-tags { grid-column: 1 / -1; display: flex; justify-content: space-between; align-items: center; padding-left: 38px; }
.radar-tags > span { color: var(--text-3); font-size: 9px; }
</style>

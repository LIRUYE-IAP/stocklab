<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Delete, Plus, Star, VideoPlay } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import SignalTag from '@/components/SignalTag.vue'
import { stocks } from '@/mock/stocks'
import { ScreenerService } from '@/services/screenerService'
import { useWatchlistStore } from '@/stores/watchlist'
import type { ScreenerCondition, Stock } from '@/types'

const router = useRouter()
const watchlist = useWatchlistStore()
const running = ref(false)
const ran = ref(true)
const whyStock = ref<Stock | null>(null)
const activeCategory = ref('全部')
const conditions = ref<ScreenerCondition[]>([
  { id: 'turnover', field: 'turnover', label: '换手率', operator: '>=', value: 3, suffix: '%' },
  { id: 'limitUpsYear', field: 'limitUpsYear', label: '近一年涨停', operator: '>=', value: 5, suffix: '次' },
  { id: 'pricePercentile', field: 'pricePercentile', label: '一年价格分位', operator: '<=', value: 35, suffix: '%' },
  { id: 'technicalScore', field: 'technicalScore', label: 'Technical Score', operator: '>=', value: 70 },
])
const results = ref<Stock[]>([stocks[0]!])

const library: Array<ScreenerCondition & { category: string; description: string }> = [
  { id: 'turnover', field: 'turnover', label: '换手率', operator: '>=', value: 3, suffix: '%', category: '成交', description: '当日成交活跃度' },
  { id: 'technicalScore', field: 'technicalScore', label: 'Technical Score', operator: '>=', value: 70, category: '技术', description: '当前技术状态评分' },
  { id: 'behaviorScore', field: 'behaviorScore', label: 'Behavior Score', operator: '>=', value: 70, category: '股性', description: '历史涨停活跃度' },
  { id: 'pricePercentile', field: 'pricePercentile', label: '一年价格分位', operator: '<=', value: 35, suffix: '%', category: '位置', description: '当前价在一年区间的位置' },
  { id: 'limitUpsYear', field: 'limitUpsYear', label: '近一年涨停', operator: '>=', value: 5, suffix: '次', category: '股性', description: '近一年涨停收盘次数' },
  { id: 'pe', field: 'pe', label: 'PE(TTM)', operator: '>=', value: 10, category: '基本面', description: '滚动市盈率' },
]
const presets = [
  { name: '历史活跃低位转强', note: '股性 + 位置 + 技术', ids: ['turnover','limitUpsYear','pricePercentile','technicalScore','behaviorScore'] },
  { name: '沉寂股重新激活', note: '低位 + 换手回升', ids: ['turnover','pricePercentile','technicalScore'] },
  { name: '低位放量', note: '位置 + 成交', ids: ['turnover','pricePercentile'] },
  { name: '趋势突破', note: '高技术强度', ids: ['technicalScore','turnover'] },
  { name: '缩量回踩', note: '趋势中的回撤', ids: ['technicalScore','pricePercentile'] },
  { name: '基本面过滤', note: '估值 + 盈利', ids: ['pe','technicalScore'] },
]
const categories = ['全部', '成交', '技术', '位置', '股性', '基本面']
const filteredLibrary = computed(() => activeCategory.value === '全部' ? library : library.filter((item) => item.category === activeCategory.value))

function addCondition(item: ScreenerCondition) {
  if (conditions.value.some((condition) => condition.id === item.id)) return ElMessage.info('该条件已添加')
  conditions.value.push({ id: item.id, field: item.field, label: item.label, operator: item.operator, value: item.value, suffix: item.suffix })
}
function usePreset(preset: (typeof presets)[number]) {
  conditions.value = preset.ids.map((id) => {
    const source = library.find((item) => item.id === id)!
    return { id: source.id, field: source.field, label: source.label, operator: source.operator, value: source.value, suffix: source.suffix }
  })
  run()
  ElMessage.success(`已应用「${preset.name}」`)
}
async function run() {
  running.value = true
  await new Promise((resolve) => setTimeout(resolve, 350))
  results.value = await ScreenerService.run(conditions.value)
  running.value = false
  ran.value = true
}
function clear() { conditions.value = []; results.value = stocks; ran.value = false }
function addWatch(stock: Stock) {
  watchlist.addToGroup(stock.symbol)
  ElMessage.success(`${stock.name} 已加入默认自选`)
}
function displayValue(stock: Stock, condition: ScreenerCondition) {
  return stock[condition.field] as number
}
</script>

<template>
  <PageHeader title="条件选股" description="用可解释的条件，从演示 A 股池中找到值得继续研究的股票。">
    <button class="btn" @click="ElMessage.success('已保存为「我的演示策略」')">保存策略</button>
    <button class="btn" @click="router.push({ path: '/quant', query: { strategy: 1 } })">加入量化实验室</button>
    <button class="btn primary" :disabled="running" @click="run"><VideoPlay />{{ running ? '筛选中…' : '运行筛选' }}</button>
  </PageHeader>
  <div class="demo-banner"><span><b>DEMO / MOCK</b>　当前股票池共 {{ stocks.length }} 只演示股票，筛选结果不代表真实市场。</span><span>逻辑模式：全部 AND</span></div>

  <div class="screener-layout">
    <aside class="screener-sidebar stack">
      <section class="panel condition-library">
        <div class="panel-head"><div><h2>条件库</h2><p>点击条件加入编辑器</p></div></div>
        <div class="category-tabs"><button v-for="category in categories" :key="category" :class="{ active: activeCategory === category }" @click="activeCategory = category">{{ category }}</button></div>
        <div class="library-list"><button v-for="item in filteredLibrary" :key="item.id" @click="addCondition(item)"><span><strong>{{ item.label }}</strong><small>{{ item.description }}</small></span><Plus /></button></div>
      </section>
      <section class="panel preset-panel"><div class="panel-head"><div><h2>预设策略</h2><p>一键载入，可继续修改</p></div></div><div class="preset-list"><button v-for="preset in presets" :key="preset.name" @click="usePreset(preset)"><span><strong>{{ preset.name }}</strong><small>{{ preset.note }}</small></span><em>使用</em></button></div></section>
    </aside>

    <div class="screener-main stack">
      <section class="panel condition-editor">
        <div class="panel-head"><div><h2>条件编辑器</h2><p>{{ conditions.length }} 个条件 · 同时满足</p></div><button class="text-button" @click="clear">清空</button></div>
        <div v-if="conditions.length" class="condition-list">
          <div v-for="(condition, index) in conditions" :key="condition.id" class="condition-row"><span class="logic-badge">{{ index === 0 ? '当' : '且' }}</span><strong>{{ condition.label }}</strong><select v-model="condition.operator"><option>&gt;=</option><option>&lt;=</option><option>&gt;</option></select><div class="condition-value"><input v-model.number="condition.value" type="number" /><span>{{ condition.suffix }}</span></div><button title="删除条件" @click="conditions.splice(index, 1)"><Delete /></button></div>
        </div>
        <div v-else class="empty-state">从左侧条件库添加条件，或直接使用预设策略。</div>
        <div class="condition-actions"><div class="chips"><SignalTag v-for="condition in conditions" :key="condition.id" :text="`${condition.label} ${condition.operator} ${condition.value}${condition.suffix || ''}`" tone="info" /></div><div><button class="btn" @click="clear">重置</button><button class="btn primary" :disabled="running" @click="run">{{ running ? '计算中…' : '运行筛选' }}</button></div></div>
      </section>

      <section class="panel result-panel">
        <div class="panel-head"><div><h2>筛选结果</h2><p v-if="ran">共找到 {{ results.length }} 只 · 按 Technical Score 排序</p><p v-else>尚未运行最新条件</p></div><span class="result-time">演示快照 2026-08-30</span></div>
        <div class="data-table-wrap"><table class="data-table result-table"><thead><tr><th>股票</th><th class="num">现价</th><th class="num">涨跌</th><th class="num">Technical</th><th class="num">Behavior</th><th class="num">价格分位</th><th class="num">换手率</th><th class="num">PE</th><th>主要信号</th><th>操作</th></tr></thead><tbody><tr v-for="stock in results" :key="stock.symbol"><td @click="router.push(`/stock/${stock.symbol}`)"><div class="stock-cell"><span class="stock-round">{{ stock.name[0] }}</span><span><strong>{{ stock.name }}</strong><small>{{ stock.code }}</small></span></div></td><td class="num">{{ stock.price.toFixed(2) }}</td><td class="num" :class="stock.changePct >= 0 ? 'positive' : 'negative'">{{ stock.changePct > 0 ? '+' : '' }}{{ stock.changePct }}%</td><td class="num"><span class="score-number">{{ stock.technicalScore }}</span></td><td class="num">{{ stock.behaviorScore }}</td><td class="num">{{ stock.pricePercentile }}%</td><td class="num">{{ stock.turnover }}%</td><td class="num">{{ stock.pe }}</td><td><SignalTag :text="stock.signals[0]" tone="positive" /></td><td><div class="row-actions"><button @click.stop="whyStock = stock">为什么入选</button><button :class="{ active: watchlist.contains(stock.symbol) }" @click.stop="addWatch(stock)"><Star />{{ watchlist.contains(stock.symbol) ? '已自选' : '自选' }}</button></div></td></tr><tr v-if="!results.length"><td colspan="10"><div class="empty-state">没有股票同时满足当前条件。可以放宽阈值后重新运行。</div></td></tr></tbody></table></div>
      </section>
    </div>
  </div>

  <el-dialog v-model="whyStock" :title="`${whyStock?.name || ''} · 为什么入选`" width="480px">
    <p class="why-intro">截至演示日期，这只股票满足当前 AND 条件：</p>
    <div v-if="whyStock" class="why-list"><div v-for="condition in conditions" :key="condition.id"><span>{{ condition.label }}</span><strong>{{ displayValue(whyStock, condition) }}{{ condition.suffix }} {{ condition.operator }} {{ condition.value }}{{ condition.suffix }}</strong><em>✓</em></div></div>
    <template #footer><button class="btn" @click="whyStock = null">关闭</button><button class="btn primary" @click="router.push(`/stock/${whyStock?.symbol}`)">查看分析</button></template>
  </el-dialog>
</template>

<style scoped>
.screener-layout { display: grid; grid-template-columns: 258px minmax(0, 1fr); gap: 14px; align-items: start; }
.screener-sidebar { position: sticky; top: 76px; }
.category-tabs { display: grid; grid-template-columns: repeat(3, 1fr); gap: 5px; padding: 10px 10px 3px; }
.category-tabs button { height: 27px; border: 1px solid transparent; border-radius: 5px; background: var(--surface-soft); color: var(--text-3); font-size: 9px; cursor: pointer; }
.category-tabs button.active { background: var(--brand-soft); border-color: #ddddfa; color: var(--brand); font-weight: 600; }
.library-list { padding: 7px; }
.library-list button { width: 100%; min-height: 50px; display: flex; align-items: center; justify-content: space-between; padding: 8px 9px; border: 0; border-bottom: 1px solid #eef0f3; background: transparent; text-align: left; cursor: pointer; }
.library-list button:hover { background: var(--surface-hover); border-radius: 6px; }
.library-list strong, .library-list small { display: block; }
.library-list strong { font-size: 11px; }
.library-list small { margin-top: 3px; color: var(--text-3); font-size: 9px; }
.library-list svg { width: 13px; color: var(--brand); }
.preset-list { padding: 7px; }
.preset-list button { width: 100%; min-height: 48px; display: flex; justify-content: space-between; align-items: center; padding: 7px 9px; border: 0; border-bottom: 1px solid #eef0f3; background: transparent; text-align: left; cursor: pointer; }
.preset-list button:hover { background: var(--surface-hover); border-radius: 6px; }
.preset-list strong, .preset-list small { display: block; }
.preset-list strong { font-size: 10px; }
.preset-list small { margin-top: 3px; color: var(--text-3); font-size: 8px; }
.preset-list em { color: var(--brand); font: normal 9px var(--font); }
.condition-list { padding: 8px 14px 3px; }
.condition-row { display: grid; grid-template-columns: 30px 170px 70px 150px 30px; gap: 9px; align-items: center; min-height: 46px; border-bottom: 1px solid #eef0f3; }
.logic-badge { width: 24px; height: 22px; display: grid; place-items: center; border-radius: 5px; background: var(--brand-soft); color: var(--brand); font-size: 9px; font-weight: 650; }
.condition-row strong { font-size: 11px; }
.condition-row select, .condition-row input { height: 30px; padding: 0 8px; border: 1px solid var(--border); border-radius: 6px; background: #fff; color: var(--text-2); font-size: 11px; }
.condition-value { position: relative; }
.condition-value input { width: 100%; padding-right: 32px; font-family: var(--mono); }
.condition-value span { position: absolute; top: 8px; right: 9px; color: var(--text-3); font-size: 9px; }
.condition-row > button { width: 28px; height: 28px; border: 0; border-radius: 5px; background: transparent; color: var(--text-3); cursor: pointer; }
.condition-row > button:hover { background: var(--positive-soft); color: var(--positive); }
.condition-actions { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 12px 14px; border-top: 1px solid var(--border); background: #fafbfc; }
.condition-actions > div:last-child { display: flex; gap: 7px; }
.chips { min-width: 0; overflow: hidden; white-space: nowrap; }
.result-time { color: var(--text-3); font-size: 9px; }
.result-table { min-width: 880px; }
.result-table tbody tr { cursor: default; }
.result-table td:first-child { cursor: pointer; }
.row-actions { display: flex; gap: 4px; }
.row-actions button { height: 25px; display: inline-flex; align-items: center; gap: 3px; padding: 0 6px; border: 1px solid var(--border); border-radius: 5px; background: #fff; color: var(--text-2); font-size: 9px; cursor: pointer; }
.row-actions button:hover, .row-actions button.active { border-color: #ccccf4; background: var(--brand-soft); color: var(--brand); }
.row-actions svg { width: 10px; }
.why-intro { margin-bottom: 10px; color: var(--text-2); font-size: 11px; }
.why-list { border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
.why-list > div { display: grid; grid-template-columns: 1fr 1.2fr 20px; gap: 8px; align-items: center; min-height: 42px; padding: 0 11px; border-bottom: 1px solid #eef0f3; }
.why-list > div:last-child { border-bottom: 0; }
.why-list span { color: var(--text-2); font-size: 10px; }
.why-list strong { font: 600 10px var(--mono); }
.why-list em { color: var(--negative); font: normal 13px var(--font); }
</style>

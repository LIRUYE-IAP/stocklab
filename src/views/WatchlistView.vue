<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Delete, FolderAdd, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import SignalTag from '@/components/SignalTag.vue'
import PositionBar from '@/components/PositionBar.vue'
import QuoteStatus from '@/components/QuoteStatus.vue'
import { stocks } from '@/mock/stocks'
import { useWatchlistStore, type WatchItem } from '@/stores/watchlist'
import { useQuoteSubscription } from '@/composables/useQuoteSubscription'

const store = useWatchlistStore()
const router = useRouter()
const group = ref('全部')
const addGroupDialog = ref(false)
const newGroup = ref('')
const selected = ref<WatchItem | null>(null)
const edit = reactive({ plannedBuy: 0, stopLoss: 0, target: 0, priority: '中', note: '' })
const symbols = computed(() => store.items.map(item => item.symbol))
const quotes = useQuoteSubscription(symbols)
const rows = computed(() => store.items.filter((item) => group.value === '全部' || item.group === group.value).map((item) => {
  const stock = stocks.find((candidate) => candidate.symbol === item.symbol)
  if (!stock) return null
  const quote = quotes.quote(stock.symbol)
  return { ...item, stock: { ...stock, price: quote ? quote.price : stock.price, changePct: quote ? quote.changePct : stock.changePct }, quote }
}).filter((row): row is NonNullable<typeof row> => Boolean(row)))
const detailStock = computed(() => selected.value ? rows.value.find(row => row.symbol === selected.value!.symbol)?.stock : undefined)
const hasLiveSource = computed(() => ['ifind', 'tushare', 'cache'].includes(quotes.provider?.activeSource || ''))
const formatPrice = (value: number | null) => value == null ? '—' : value.toFixed(2)
const formatPct = (value: number | null) => value == null ? '—' : `${value > 0 ? '+' : ''}${value.toFixed(2)}%`
const groupCount = (name: string) => name === '全部' ? store.items.length : store.items.filter((item) => item.group === name).length

watch(selected, (item) => {
  if (!item) return
  edit.plannedBuy = item.plannedBuy || 0; edit.stopLoss = item.stopLoss || 0; edit.target = item.target || 0; edit.priority = item.priority; edit.note = item.note
})
function createGroup() {
  if (!newGroup.value.trim()) return
  store.addGroup(newGroup.value.trim()); group.value = newGroup.value.trim(); newGroup.value = ''; addGroupDialog.value = false; ElMessage.success('自选分组已创建')
}
function saveDetail() {
  if (!selected.value) return
  const actual = store.items.find((item) => item.symbol === selected.value!.symbol)
  if (actual) { actual.plannedBuy = edit.plannedBuy; actual.stopLoss = edit.stopLoss; actual.target = edit.target; actual.priority = edit.priority as WatchItem['priority']; actual.note = edit.note }
  selected.value = null; ElMessage.success('研究计划已更新')
}
function remove(symbol: string) { store.toggle(symbol); if (selected.value?.symbol === symbol) selected.value = null; ElMessage.success('已从自选移除') }
</script>

<template>
  <PageHeader title="我的自选" description="按研究阶段组织股票，跟踪信号、计划价格与笔记。">
    <button class="btn" @click="addGroupDialog = true"><FolderAdd />新建分组</button>
    <button class="btn primary" @click="router.push('/screener')"><Plus />从选股器添加</button>
  </PageHeader>
  <div class="demo-banner"><span><b>{{ hasLiveSource ? 'LIVE QUOTES' : 'DEMO / MOCK' }}</b>　自选计划为本地演示记录，现价通过统一行情服务更新。</span><QuoteStatus :quote="rows[0]?.quote" :connection="quotes.connection" /></div>

  <div class="watch-layout">
    <aside class="panel group-panel">
      <div class="panel-head"><h2>自选分组</h2></div>
      <div class="group-list"><button v-for="item in store.groups" :key="item" :class="{ active: group === item }" @click="group = item"><span>{{ item }}</span><em>{{ groupCount(item) }}</em></button></div>
      <div class="group-foot"><button @click="addGroupDialog = true"><Plus />新增分组</button></div>
    </aside>
    <section class="panel watch-table-panel">
      <div class="panel-head"><div><h2>{{ group }}</h2><p>{{ rows.length }} 只 · 点击行打开研究计划</p></div><div class="segmented"><button class="active">紧凑</button><button>卡片</button></div></div>
      <div class="data-table-wrap"><table class="data-table watch-table"><thead><tr><th>股票</th><th class="num">现价</th><th class="num">涨跌</th><th class="num">Technical</th><th class="num">Behavior</th><th class="num">价格分位</th><th>主要信号</th><th>预警</th><th>优先级</th><th>操作</th></tr></thead><tbody><tr v-for="row in rows" :key="row.symbol" @click="selected = row"><td><div class="stock-cell"><span class="stock-round">{{ row.stock.name[0] }}</span><span><strong>{{ row.stock.name }}</strong><small>{{ row.stock.code }} · {{ row.group }}</small></span></div></td><td class="num">{{ formatPrice(row.stock.price) }}</td><td class="num" :class="row.stock.changePct == null ? '' : row.stock.changePct >= 0 ? 'positive' : 'negative'">{{ formatPct(row.stock.changePct) }}</td><td class="num"><span class="score-number">{{ row.stock.technicalScore }}</span></td><td class="num">{{ row.stock.behaviorScore }}</td><td class="num">{{ row.stock.pricePercentile }}%</td><td><SignalTag :text="row.stock.signals[0]" tone="info" /></td><td><span class="alert-dot active" />启用</td><td><span class="priority" :class="row.priority">{{ row.priority }}</span></td><td><button class="table-icon" title="移除" @click.stop="remove(row.symbol)"><Delete /></button></td></tr></tbody></table></div>
    </section>
  </div>

  <el-drawer v-model="selected" size="430px" direction="rtl" :with-header="false">
    <div v-if="selected" class="watch-drawer">
      <div class="drawer-head"><div class="stock-round">{{ detailStock?.name[0] }}</div><div><h2>{{ detailStock?.name }}</h2><p>{{ selected.symbol }} · {{ selected.group }}</p></div><button class="text-button" @click="router.push(`/stock/${selected!.symbol}`)">打开个股</button></div>
      <div class="drawer-score"><div><span>Technical</span><strong>{{ detailStock?.technicalScore }}</strong></div><div><span>Behavior</span><strong>{{ detailStock?.behaviorScore }}</strong></div><div><span>价格分位</span><strong>{{ detailStock?.pricePercentile }}%</strong></div></div>
      <PositionBar :value="detailStock?.pricePercentile || 0" />
      <div class="drawer-section"><h3>交易计划</h3><div class="grid-3"><div class="form-field"><label>计划买入价</label><input v-model.number="edit.plannedBuy" type="number" step="0.01" /></div><div class="form-field"><label>止损价</label><input v-model.number="edit.stopLoss" type="number" step="0.01" /></div><div class="form-field"><label>目标价</label><input v-model.number="edit.target" type="number" step="0.01" /></div></div><div class="form-field"><label>优先级</label><select v-model="edit.priority"><option>高</option><option>中</option><option>低</option></select></div></div>
      <div class="drawer-section"><h3>研究笔记</h3><div class="note-item"><span>2026-08-28</span><p>{{ selected.note }}</p></div><div class="form-field"><label>更新笔记</label><textarea v-model="edit.note" /></div></div>
      <div class="drawer-actions"><button class="btn danger" @click="remove(selected.symbol)">移除自选</button><button class="btn primary" @click="saveDetail">保存计划</button></div>
    </div>
  </el-drawer>

  <el-dialog v-model="addGroupDialog" title="新建自选分组" width="390px"><div class="form-field"><label>分组名称</label><input v-model="newGroup" placeholder="例如：有色、机器人、等待回踩" @keyup.enter="createGroup" /></div><template #footer><button class="btn" @click="addGroupDialog = false">取消</button><button class="btn primary" @click="createGroup">创建</button></template></el-dialog>
</template>

<style scoped>
.watch-layout { display: grid; grid-template-columns: 210px minmax(0, 1fr); gap: 14px; align-items: start; }
.group-panel { position: sticky; top: 76px; }
.group-list { padding: 8px; }
.group-list button { width: 100%; height: 38px; display: flex; align-items: center; justify-content: space-between; padding: 0 10px; border: 0; border-radius: 6px; background: transparent; color: var(--text-2); font-size: 11px; cursor: pointer; }
.group-list button:hover { background: var(--surface-hover); }
.group-list button.active { background: var(--brand-soft); color: var(--brand); font-weight: 650; }
.group-list em { min-width: 22px; padding: 2px 5px; border-radius: 9px; background: rgba(255,255,255,.65); color: var(--text-3); font: normal 9px var(--mono); }
.group-foot { padding: 8px; border-top: 1px solid var(--border); }
.group-foot button { width: 100%; height: 34px; display: flex; align-items: center; gap: 7px; padding: 0 10px; border: 0; background: transparent; color: var(--brand); font-size: 10px; cursor: pointer; }
.watch-table { min-width: 940px; }
.alert-dot { display: inline-block; width: 6px; height: 6px; margin-right: 5px; border-radius: 50%; background: #b6bac5; }
.alert-dot.active { background: var(--negative); }
.priority { padding: 2px 7px; border-radius: 5px; background: #f1f2f5; font-size: 9px; }
.priority.高 { background: var(--positive-soft); color: var(--positive); }.priority.中 { background: var(--warning-soft); color: var(--warning); }
.table-icon { width: 26px; height: 26px; display: grid; place-items: center; border: 0; border-radius: 5px; background: transparent; color: var(--text-3); cursor: pointer; }.table-icon:hover { background: var(--positive-soft); color: var(--positive); }.table-icon svg { width: 12px; }
.watch-drawer { min-height: calc(100vh - 40px); display: flex; flex-direction: column; padding: 4px 3px; }
.drawer-head { display: grid; grid-template-columns: 38px 1fr auto; gap: 10px; align-items: center; padding-bottom: 16px; border-bottom: 1px solid var(--border); }.drawer-head .stock-round { width: 38px; height: 38px; }.drawer-head h2 { font-size: 16px; }.drawer-head p { margin-top: 3px; color: var(--text-3); font: 9px var(--mono); }
.drawer-score { display: grid; grid-template-columns: repeat(3, 1fr); margin: 16px 0 8px; border: 1px solid var(--border); border-radius: 8px; }.drawer-score > div { padding: 11px; border-right: 1px solid var(--border); }.drawer-score > div:last-child { border-right: 0; }.drawer-score span, .drawer-score strong { display: block; }.drawer-score span { color: var(--text-3); font-size: 9px; }.drawer-score strong { margin-top: 6px; font: 650 17px var(--mono); }
.drawer-section { margin-top: 20px; }.drawer-section h3 { margin-bottom: 12px; font-size: 12px; }.note-item { padding: 11px; margin-bottom: 12px; border-left: 2px solid var(--brand); background: var(--surface-soft); }.note-item span { color: var(--text-3); font: 9px var(--mono); }.note-item p { margin-top: 6px; color: var(--text-2); font-size: 11px; line-height: 1.6; }
.drawer-actions { display: flex; justify-content: space-between; margin-top: auto; padding-top: 18px; border-top: 1px solid var(--border); }
</style>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { Bell, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import SignalTag from '@/components/SignalTag.vue'
import { stocks } from '@/mock/stocks'
import { useAlertsStore } from '@/stores/alerts'

const store = useAlertsStore()
const tab = ref('我的预警')
const dialog = ref(false)
const form = reactive({ symbol: 'SZ.000630', type: '价格低于', detail: '5.50' })
const rows = computed(() => tab.value === '历史触发' ? store.rules.filter((rule) => rule.status === '已触发') : store.rules)
function create() {
  const stock = stocks.find((item) => item.symbol === form.symbol)!
  store.add({ symbol: form.symbol, stockName: stock.name, type: form.type, detail: form.detail, enabled: true, status: '启用', updatedAt: '刚刚' })
  dialog.value = false; ElMessage.success('演示预警已创建')
}
</script>

<template>
  <PageHeader title="预警中心" description="持续监控价格、技术状态和策略新增标的。"><button class="btn primary" @click="dialog = true"><Plus />新建预警</button></PageHeader>
  <div class="demo-banner"><span><b>DEMO / MOCK</b>　预警不会发送真实通知，开关与新建交互在当前会话生效。</span><span>{{ store.rules.filter(r => r.enabled).length }} 条启用</span></div>
  <section class="panel">
    <div class="alerts-toolbar"><div class="segmented"><button v-for="item in ['我的预警','历史触发']" :key="item" :class="{ active: tab === item }" @click="tab = item">{{ item }}</button></div><span>最近更新优先</span></div>
    <div class="data-table-wrap"><table class="data-table"><thead><tr><th>股票</th><th>预警类型</th><th>条件</th><th>状态</th><th>最近更新</th><th class="num">启用</th></tr></thead><tbody><tr v-for="rule in rows" :key="rule.id"><td><div class="stock-cell"><span class="stock-round">{{ rule.stockName[0] }}</span><span><strong>{{ rule.stockName }}</strong><small>{{ rule.symbol }}</small></span></div></td><td>{{ rule.type }}</td><td class="mono">{{ rule.detail }}</td><td><SignalTag :text="rule.status" :tone="rule.status === '已触发' ? 'warning' : rule.enabled ? 'positive' : 'neutral'" /></td><td class="muted">{{ rule.updatedAt }}</td><td class="num"><el-switch :model-value="rule.enabled" size="small" style="--el-switch-on-color:#5555c9" @change="store.toggle(rule.id)" /></td></tr></tbody></table></div>
  </section>
  <section class="panel section-gap alert-types"><div class="panel-head"><div><h2>可用预警类型</h2><p>当前原型已覆盖的监控能力</p></div></div><div class="alert-type-grid"><div v-for="item in [['价格','高于 / 低于指定价格'],['Technical Score','上穿 80 或跌破阈值'],['技术信号','MACD 金叉、跌破 MA20/MA60'],['突破','突破 60 日高点'],['成交量','高于 20 日均量指定倍数'],['策略','每日新增符合条件的股票']]" :key="String(item[0])"><Bell /><span><strong>{{ item[0] }}</strong><small>{{ item[1] }}</small></span></div></div></section>

  <el-dialog v-model="dialog" title="新建演示预警" width="460px"><div class="form-field"><label>股票</label><select v-model="form.symbol"><option v-for="stock in stocks" :key="stock.symbol" :value="stock.symbol">{{ stock.name }} · {{ stock.code }}</option></select></div><div class="grid-2"><div class="form-field"><label>类型</label><select v-model="form.type"><option>价格低于</option><option>价格高于</option><option>Technical Score 上穿</option><option>MACD 金叉</option><option>跌破 MA20</option><option>成交量放大</option></select></div><div class="form-field"><label>条件 / 阈值</label><input v-model="form.detail" /></div></div><template #footer><button class="btn" @click="dialog = false">取消</button><button class="btn primary" @click="create">创建预警</button></template></el-dialog>
</template>

<style scoped>
.alerts-toolbar { min-height: 52px; display: flex; align-items: center; justify-content: space-between; padding: 0 14px; border-bottom: 1px solid var(--border); }.alerts-toolbar > span { color: var(--text-3); font-size: 10px; }
.alert-type-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0; }.alert-type-grid > div { min-height: 72px; display: flex; align-items: center; gap: 11px; padding: 14px; border-right: 1px solid var(--border); border-bottom: 1px solid var(--border); }.alert-type-grid > div:nth-child(3n) { border-right: 0; }.alert-type-grid > div:nth-last-child(-n+3) { border-bottom: 0; }.alert-type-grid svg { width: 16px; color: var(--brand); }.alert-type-grid strong, .alert-type-grid small { display: block; }.alert-type-grid strong { font-size: 11px; }.alert-type-grid small { margin-top: 4px; color: var(--text-3); font-size: 9px; }
</style>

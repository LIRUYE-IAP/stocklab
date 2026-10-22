<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import SignalTag from '@/components/SignalTag.vue'
import { HistoryService } from '@/services/historyService'
import { useQuotesStore } from '@/stores/quotes'
import type { DataHealthStatus } from '@/types/history'

const quotes = useQuotesStore()
const dataHealth = ref<DataHealthStatus | null>(null)
const dataHealthError = ref<string | null>(null)
const tab = ref('数据源状态')
const prefs = reactive({ start: '首页工作台', density: '紧凑', adjustment: '前复权', notifications: true, risk: true })

async function refreshDataStatus() {
  await quotes.refreshStatus()
  try { dataHealth.value = await HistoryService.status(); dataHealthError.value = null }
  catch (error) { dataHealthError.value = error instanceof Error ? error.message : '数据健康接口不可用' }
}
onMounted(refreshDataStatus)
</script>

<template>
  <PageHeader title="设置" description="管理研究偏好、数据连接和演示账户信息。"><button class="btn primary" @click="ElMessage.success('演示设置已保存')">保存设置</button></PageHeader>
  <div class="settings-layout">
    <aside class="panel settings-nav"><button v-for="item in ['数据源状态','个人偏好','行情与图表','通知设置','账户与安全','关于 StockLab']" :key="item" :class="{ active: tab === item }" @click="tab = item">{{ item }}</button></aside>
    <section class="panel settings-content">
      <div class="panel-head"><div><h2>{{ tab }}</h2><p>行情凭据仅由本机后端读取，前端只显示脱敏状态</p></div><button v-if="tab === '数据源状态'" class="btn" @click="refreshDataStatus">检测连接</button></div>
      <div v-if="tab === '数据源状态'" class="settings-form">
        <div v-if="quotes.provider" class="source-grid">
          <div><span>数据模式</span><strong>{{ quotes.provider.dataMode }}</strong></div><div><span>当前实时来源</span><strong>{{ quotes.provider.activeSource }}</strong></div>
          <div><span>历史 Provider</span><strong>{{ dataHealth?.historical_provider.name || quotes.provider.historyProvider }}</strong></div><div><span>实时 Provider</span><strong>{{ dataHealth?.realtime_provider.name || quotes.provider.realtimeProvider }}</strong></div>
          <div><span>iFinD</span><SignalTag :text="quotes.provider.ifindConfigured ? '已配置' : '未配置'" :tone="quotes.provider.ifindConfigured ? 'positive' : 'neutral'" /></div><div><span>Tushare</span><SignalTag :text="quotes.provider.tushareConfigured ? '已配置' : '未配置'" :tone="quotes.provider.tushareConfigured ? 'positive' : 'neutral'" /></div>
          <div><span>Redis</span><strong>{{ dataHealth?.redis.active_backend || quotes.provider.cacheBackend }}</strong></div><div><span>数据库</span><strong>{{ dataHealth?.database.engine || '未连接' }}</strong></div>
        </div>
        <div v-else class="settings-placeholder"><strong>行情后端未连接</strong><p>{{ quotes.error || '请启动 FastAPI 后端后重新检测。' }}</p></div>
        <div class="setting-row"><div><strong>数据能力</strong><p>{{ quotes.provider?.capabilities.join(' · ') || '暂无' }}</p></div></div>
        <div v-if="dataHealth?.datasets.length" class="dataset-health"><div v-for="item in dataHealth.datasets" :key="item.dataset"><span>{{ item.dataset }}</span><SignalTag :text="item.status" :tone="item.status === 'SUCCESS' ? 'positive' : item.status === 'PARTIAL' ? 'warning' : 'negative'" /><strong>{{ item.latest_trade_date || '—' }}</strong><small>{{ item.record_count }} 条</small></div></div>
        <div v-else class="settings-placeholder data-empty"><strong>尚无真实历史数据</strong><p>{{ dataHealthError || '请配置 TUSHARE_TOKEN 后依次运行股票基础、交易日历和铜陵有色 30 日同步。' }}</p></div>
        <div v-if="quotes.provider?.lastError" class="source-error">{{ quotes.provider.lastError }}</div>
        <p class="credential-note">在 backend/.env 中配置 TUSHARE_TOKEN 与 IFIND_REFRESH_TOKEN。这里只显示是否配置，绝不返回或记录 Token 内容。</p>
      </div>
      <div v-else-if="tab === '个人偏好'" class="settings-form"><div class="form-field"><label>登录后默认页面</label><select v-model="prefs.start"><option>首页工作台</option><option>我的自选</option><option>持仓</option></select></div><div class="form-field"><label>表格密度</label><select v-model="prefs.density"><option>紧凑</option><option>舒适</option></select></div><div class="setting-row"><div><strong>风险信号优先展示</strong><p>在自选和持仓列表中将风险变化放在前面。</p></div><el-switch v-model="prefs.risk" style="--el-switch-on-color:#5555c9" /></div></div>
      <div v-else-if="tab === '行情与图表'" class="settings-form"><div class="form-field"><label>默认复权方式</label><select v-model="prefs.adjustment"><option>前复权</option><option>不复权</option><option>后复权</option></select></div><div class="setting-row"><div><strong>A 股颜色习惯</strong><p>上涨使用红色，下跌使用绿色。</p></div><SignalTag text="上涨红 · 下跌绿" tone="info" /></div></div>
      <div v-else-if="tab === '通知设置'" class="settings-form"><div class="setting-row"><div><strong>站内通知</strong><p>预警触发后显示在顶部通知中心。</p></div><el-switch v-model="prefs.notifications" style="--el-switch-on-color:#5555c9" /></div><div class="setting-row"><div><strong>每日策略摘要</strong><p>收盘后汇总策略新增与移除标的。</p></div><el-switch :model-value="true" style="--el-switch-on-color:#5555c9" /></div></div>
      <div v-else class="settings-form"><div class="settings-placeholder"><strong>{{ tab }}</strong><p>该模块在生产后端接入后开放。当前原型不会保存真实账户凭据或发送外部通知。</p></div></div>
    </section>
  </div>
</template>

<style scoped>
.settings-layout { display: grid; grid-template-columns: 210px minmax(0, 820px); gap: 14px; }.settings-nav { padding: 8px; }.settings-nav button { width: 100%; height: 39px; display: block; padding: 0 10px; border: 0; border-radius: 6px; background: transparent; color: var(--text-2); font-size: 11px; text-align: left; cursor: pointer; }.settings-nav button:hover { background: var(--surface-hover); }.settings-nav button.active { background: var(--brand-soft); color: var(--brand); font-weight: 650; }.settings-form { padding: 18px; }.settings-form > .form-field { max-width: 340px; }.setting-row { min-height: 62px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border); }.setting-row strong { font-size: 11px; }.setting-row p { margin-top: 4px; color: var(--text-3); font-size: 9px; }.settings-placeholder { padding: 18px; border-radius: 8px; background: var(--surface-soft); }.settings-placeholder strong { font-size: 12px; }.settings-placeholder p { margin-top: 8px; color: var(--text-2); font-size: 10px; line-height: 1.7; }.source-grid { display:grid; grid-template-columns:repeat(2,1fr); border:1px solid var(--border); border-radius:8px; }.source-grid > div { display:flex; justify-content:space-between; align-items:center; min-height:48px; padding:0 12px; border-bottom:1px solid var(--border); }.source-grid > div:nth-child(odd) { border-right:1px solid var(--border); }.source-grid > div:nth-last-child(-n+2) { border-bottom:0; }.source-grid span { color:var(--text-3); font-size:10px; }.source-grid strong { font:600 11px var(--mono); }.credential-note,.source-error { margin-top:14px; padding:10px; border-radius:7px; font-size:10px; line-height:1.6; }.credential-note { background:var(--surface-soft); color:var(--text-2); }.source-error { background:var(--negative-soft); color:var(--negative); }.data-empty { margin-top:14px; }.dataset-health { margin-top:14px; border:1px solid var(--border); border-radius:8px; overflow:hidden; }.dataset-health > div { display:grid; grid-template-columns:1.2fr 90px 100px 70px; gap:10px; align-items:center; min-height:42px; padding:0 11px; border-bottom:1px solid var(--border); }.dataset-health > div:last-child { border:0; }.dataset-health span { font:600 9px var(--mono); }.dataset-health strong,.dataset-health small { color:var(--text-3); font:9px var(--mono); text-align:right; }
</style>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { CopyDocument, Cpu, Delete, Edit, Plus, VideoPlay } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import SignalTag from '@/components/SignalTag.vue'
import { useStrategiesStore } from '@/stores/strategies'

const store = useStrategiesStore()
const router = useRouter()
const tab = ref('全部')
const editDialog = ref(false)
const editingId = ref<number | null>(null)
const form = reactive({ name: '', description: '' })
const filtered = computed(() => tab.value === '全部' ? store.list : store.list.filter((item) => item.kind === tab.value))
function run(name: string) { ElMessage.success(`「${name}」已运行：演示结果已更新`) }
function edit(id: number) { const item = store.list.find((row) => row.id === id)!; editingId.value = id; form.name = item.name; form.description = item.description; editDialog.value = true }
function save() { const item = store.list.find((row) => row.id === editingId.value); if (item) { item.name = form.name; item.description = form.description }; editDialog.value = false; ElMessage.success('策略已保存') }
async function remove(id: number) { await ElMessageBox.confirm('删除这个演示策略？', '确认删除', { type: 'warning' }); store.remove(id); ElMessage.success('策略已删除') }
</script>

<template>
  <PageHeader title="策略" description="保存、运行和比较你的选股逻辑，条件始终保持可解释。"><button class="btn primary" @click="router.push('/screener')"><Plus />新建策略</button></PageHeader>
  <div class="demo-banner"><span><b>DEMO / MOCK</b>　策略匹配数量和运行时间均为演示结果。</span><span>{{ store.list.length }} 个策略</span></div>
  <div class="strategy-toolbar panel"><div class="segmented"><button v-for="item in ['全部','系统策略','我的策略']" :key="item" :class="{ active: tab === item }" @click="tab = item">{{ item }}</button></div><div><span>今日运行 4 次</span><span>最新匹配 126 只</span></div></div>
  <div class="strategy-grid section-gap">
    <article v-for="strategy in filtered" :key="strategy.id" class="panel strategy-card">
      <div class="strategy-card-head"><SignalTag :text="strategy.kind" :tone="strategy.kind === '系统策略' ? 'info' : 'neutral'" /><button class="icon-mini" @click="edit(strategy.id)"><Edit /></button></div>
      <h2>{{ strategy.name }}</h2><p>{{ strategy.description }}</p>
      <div class="strategy-tags"><SignalTag v-for="tag in strategy.tags" :key="tag" :text="tag" /></div>
      <div class="strategy-meta"><div><span>条件数</span><strong>{{ strategy.conditionCount }}</strong></div><div><span>最新匹配</span><strong>{{ strategy.matches }}</strong></div><div><span>上次运行</span><strong>{{ strategy.lastRun }}</strong></div></div>
      <div class="strategy-actions"><button class="btn soft" @click="run(strategy.name)"><VideoPlay />运行</button><button class="btn" @click="edit(strategy.id)"><Edit />编辑</button><button class="btn" @click="store.copy(strategy.id); ElMessage.success('已复制到我的策略')"><CopyDocument />复制</button><button class="btn" @click="router.push({ path: '/backtest', query: { strategy: strategy.id } })">回测</button><button class="btn" @click="router.push({ path: '/quant', query: { strategy: strategy.id } })"><Cpu />模拟</button><button v-if="strategy.kind === '我的策略'" class="icon-mini danger-text" @click="remove(strategy.id)"><Delete /></button></div>
    </article>
  </div>
  <el-dialog v-model="editDialog" title="编辑演示策略" width="520px"><div class="form-field"><label>策略名称</label><input v-model="form.name" /></div><div class="form-field"><label>说明</label><textarea v-model="form.description" /></div><div class="strategy-condition-preview"><span>条件结构预览</span><code>Technical ≥ 70 AND Behavior ≥ 70 AND Price Percentile ≤ 35%</code><small>完整条件编辑可在条件选股页进行。</small></div><template #footer><button class="btn" @click="editDialog = false">取消</button><button class="btn primary" @click="save">保存策略</button></template></el-dialog>
</template>

<style scoped>
.strategy-toolbar { min-height: 56px; display: flex; align-items: center; justify-content: space-between; padding: 0 14px; }.strategy-toolbar > div:last-child { display: flex; gap: 22px; color: var(--text-3); font-size: 10px; }
.strategy-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }.strategy-card { padding: 15px; }.strategy-card-head { display: flex; justify-content: space-between; align-items: center; }.strategy-card h2 { margin-top: 14px; font-size: 15px; }.strategy-card > p { min-height: 42px; margin-top: 7px; color: var(--text-2); font-size: 10px; line-height: 1.6; }.strategy-tags { min-height: 49px; padding: 11px 0; border-bottom: 1px solid var(--border); }.strategy-meta { display: grid; grid-template-columns: .6fr .75fr 1.2fr; gap: 8px; padding: 12px 0; }.strategy-meta span, .strategy-meta strong { display: block; }.strategy-meta span { color: var(--text-3); font-size: 8px; }.strategy-meta strong { margin-top: 5px; font: 600 10px var(--mono); }.strategy-actions { display: flex; align-items: center; gap: 5px; }.strategy-actions .btn { min-height: 30px; padding: 0 9px; font-size: 9px; }.icon-mini { width: 27px; height: 27px; display: grid; place-items: center; border: 0; border-radius: 5px; background: transparent; color: var(--text-3); cursor: pointer; }.icon-mini:hover { background: var(--surface-hover); color: var(--brand); }.icon-mini svg { width: 12px; }.danger-text { margin-left: auto; }.danger-text:hover { background: var(--positive-soft); color: var(--positive); }
.strategy-condition-preview { padding: 12px; border-radius: 8px; background: var(--surface-soft); }.strategy-condition-preview span, .strategy-condition-preview code, .strategy-condition-preview small { display: block; }.strategy-condition-preview span { color: var(--text-3); font-size: 9px; }.strategy-condition-preview code { margin-top: 8px; color: var(--brand-dark); font-size: 10px; }.strategy-condition-preview small { margin-top: 8px; color: var(--text-3); font-size: 9px; }
</style>

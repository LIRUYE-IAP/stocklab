<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Bell, Search, Star } from '@element-plus/icons-vue'
import { stocks } from '@/mock/stocks'
import { StockService } from '@/services/stockService'
import type { StockSearchResult } from '@/types/history'
import { useAlertsStore } from '@/stores/alerts'
import { useAuthStore } from '@/stores/auth'
import { useQuoteSubscription } from '@/composables/useQuoteSubscription'

const router = useRouter()
const auth = useAuthStore()
const alerts = useAlertsStore()
const query = ref('')
const focused = ref(false)
const results = ref<StockSearchResult[]>(stocks.slice(0, 4).map((stock) => ({ ...stock, source: 'mock', is_demo: true })))
const searching = ref(false)
let searchTimer: number | undefined
watch(query, (value) => {
  window.clearTimeout(searchTimer)
  if (!value.trim()) { results.value = stocks.slice(0, 4).map((stock) => ({ ...stock, source: 'mock', is_demo: true })); return }
  searching.value = true
  searchTimer = window.setTimeout(async () => { results.value = (await StockService.search(value)).slice(0, 10); searching.value = false }, 180)
})
onBeforeUnmount(() => window.clearTimeout(searchTimer))
const quotes = useQuoteSubscription(computed(() => focused.value ? results.value.map(stock => stock.symbol) : []))
const displayResults = computed(() => results.value.map(stock => {
  const quote = quotes.quote(stock.symbol)
  return { ...stock, changePct: quote ? quote.changePct : null }
}))
const formatPct = (value: number | null) => value == null ? '—' : `${value > 0 ? '+' : ''}${value.toFixed(2)}%`
const unread = computed(() => alerts.notices.filter((item) => !item.read).length)

function openStock(symbol: string) {
  focused.value = false
  query.value = ''
  router.push(`/stock/${symbol}`)
}
function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <header class="app-header">
    <div class="global-search" :class="{ focused }">
      <Search class="search-icon" />
      <input v-model="query" placeholder="搜索股票代码 / 名称" @focus="focused = true" @keydown.esc="focused = false" />
      <kbd>⌘ K</kbd>
      <div v-if="focused" class="search-results">
        <div class="search-caption">{{ searching ? '正在查询 StockLab 数据库…' : query ? '搜索结果' : '常用股票（演示）' }}</div>
        <button v-for="stock in displayResults" :key="stock.symbol" @mousedown.prevent="openStock(stock.symbol)">
          <span class="stock-round">{{ stock.name.slice(0, 1) }}</span>
          <span><strong>{{ stock.name }}</strong><small>{{ stock.code }} · {{ stock.exchange }}</small></span>
          <em :class="stock.changePct == null ? '' : stock.changePct >= 0 ? 'positive' : 'negative'">{{ formatPct(stock.changePct) }}</em>
        </button>
        <div v-if="!results.length && !searching" class="search-empty">StockLab 数据库中没有匹配股票</div>
      </div>
    </div>
    <div class="header-actions">
      <button class="icon-button" title="打开自选" @click="router.push('/watchlist')"><Star /></button>
      <el-popover placement="bottom-end" :width="360" trigger="click" popper-class="notification-popover">
        <template #reference>
          <button class="icon-button notification-button" title="通知"><Bell /><span v-if="unread" class="badge">{{ unread }}</span></button>
        </template>
        <div class="notification-head"><strong>通知中心</strong><button @click="alerts.markAllRead">全部已读</button></div>
        <div class="notice-list">
          <div v-for="notice in alerts.notices" :key="notice.id" class="notice-item" :class="{ unread: !notice.read }">
            <i :class="notice.tone" /><div><p>{{ notice.title }}</p><span>{{ notice.time }} · 演示数据</span></div>
          </div>
        </div>
      </el-popover>
      <el-dropdown trigger="click" @command="(command: string) => command === 'logout' ? logout() : router.push('/settings')">
        <button class="user-menu"><span>{{ auth.user?.initials }}</span><div><strong>{{ auth.user?.name }}</strong><small>Demo 账户</small></div></button>
        <template #dropdown><el-dropdown-menu><el-dropdown-item command="settings">账户设置</el-dropdown-item><el-dropdown-item command="logout" divided>退出登录</el-dropdown-item></el-dropdown-menu></template>
      </el-dropdown>
    </div>
  </header>
</template>

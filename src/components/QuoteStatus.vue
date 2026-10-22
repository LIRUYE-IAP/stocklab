<script setup lang="ts">
import { computed } from 'vue'
import type { RealtimeQuote } from '@/types/market'

const props = defineProps<{ quote?: RealtimeQuote; connection?: string; compact?: boolean }>()
const label = computed(() => {
  if (!props.quote) return props.connection === 'connected' ? '等待行情' : '行情未连接'
  if (props.quote.isDemo) return '演示行情'
  if (props.quote.marketStatus === 'OFFLINE') return '连接中断'
  if (props.quote.marketStatus === 'STALE' || props.quote.isStale) return '数据延迟'
  if (props.quote.marketStatus === 'LUNCH_BREAK') return '午间休市'
  if (props.quote.marketStatus === 'CLOSED' || props.quote.marketStatus === 'closed') return '已收盘'
  if (props.quote.marketStatus === 'PRE_MARKET') return '盘前'
  if (props.quote.source === 'cache') return props.quote.isStale ? '最后已知价格' : '缓存行情'
  if (props.quote.granularity === 'eod') return '收盘数据'
  if (props.quote.source === 'tushare') return 'Tushare 分钟'
  return 'iFinD 实时'
})
const time = computed(() => props.quote?.tradeTime || props.quote?.tradingDate || '')
</script>

<template>
  <span class="quote-status" :class="{ demo: quote?.isDemo, stale: quote?.isStale, compact }">
    <i />{{ label }}<small v-if="time">{{ new Date(time).toLocaleString('zh-CN', { hour12: false }) }}</small>
  </span>
</template>

<style scoped>
.quote-status { display:inline-flex; align-items:center; gap:6px; color:var(--text-2); font-size:10px; }.quote-status i { width:6px; height:6px; border-radius:50%; background:#1a9a70; }.quote-status small { color:var(--text-3); font:9px var(--mono); }.quote-status.demo i { background:#c58a22; }.quote-status.stale i { background:#d35b50; }.quote-status.compact small { display:none; }
</style>

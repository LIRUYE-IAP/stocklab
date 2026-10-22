import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export interface WatchItem {
  symbol: string
  group: string
  note: string
  priority: '高' | '中' | '低'
  plannedBuy?: number
  stopLoss?: number
  target?: number
}

const defaultItems: WatchItem[] = [
  { symbol: 'SZ.000630', group: '重点观察', note: '等待缩量回踩 MA20，不追高。', priority: '高', plannedBuy: 5.52, stopLoss: 5.18, target: 6.42 },
  { symbol: 'SZ.002155', group: '准备买入', note: '黄金板块强势，等待回踩确认。', priority: '高', plannedBuy: 22.8, stopLoss: 21.9, target: 27.5 },
  { symbol: 'SZ.002716', group: '默认自选', note: '历史股性活跃，观察量能。', priority: '中', plannedBuy: 4.55, stopLoss: 4.31, target: 5.35 },
  { symbol: 'SH.603019', group: '重点观察', note: '突破后波动加大，等下一次确认。', priority: '中', plannedBuy: 74.2, stopLoss: 70.8, target: 86 },
  { symbol: 'SZ.300750', group: '默认自选', note: '中线跟踪，暂不加仓。', priority: '低', plannedBuy: 298, stopLoss: 284, target: 348 },
]

export const useWatchlistStore = defineStore('watchlist', () => {
  const items = ref<WatchItem[]>(defaultItems)
  const groups = ref(['全部', '默认自选', '准备买入', '重点观察'])
  const symbols = computed(() => items.value.map((item) => item.symbol))

  function contains(symbol: string) {
    return symbols.value.includes(symbol)
  }
  function toggle(symbol: string) {
    const index = items.value.findIndex((item) => item.symbol === symbol)
    if (index >= 0) items.value.splice(index, 1)
    else items.value.unshift({ symbol, group: '默认自选', note: '从个股研究页加入。', priority: '中' })
  }
  function addToGroup(symbol: string, group = '默认自选') {
    const item = items.value.find((row) => row.symbol === symbol)
    if (item) item.group = group
    else items.value.push({ symbol, group, note: '从筛选结果加入。', priority: '中' })
  }
  function addGroup(name: string) {
    if (name && !groups.value.includes(name)) groups.value.push(name)
  }
  function updateNote(symbol: string, note: string) {
    const item = items.value.find((row) => row.symbol === symbol)
    if (item) item.note = note
  }

  return { items, groups, symbols, contains, toggle, addToGroup, addGroup, updateNote }
})

import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { RealtimeService, normalizeQuote, normalizeStatus } from '@/services/realtimeService'
import type { ProviderStatus, RealtimeQuote } from '@/types/market'

export const useQuotesStore = defineStore('quotes', () => {
  const quotes = ref<Record<string, RealtimeQuote>>({})
  const provider = ref<ProviderStatus | null>(null)
  const connection = ref<'idle' | 'connecting' | 'connected' | 'disconnected'>('idle')
  const error = ref<string | null>(null)
  const refs = new Map<string, number>()
  let socket: WebSocket | null = null
  let reconnectTimer: number | undefined
  let reconnectAttempt = 0

  const activeSymbols = () => [...refs.entries()].filter(([, count]) => count > 0).map(([symbol]) => symbol)
  const isDemo = computed(() => provider.value?.activeSource === 'mock' || Object.values(quotes.value).some(q => q.isDemo))

  function apply(rows: RealtimeQuote[]) {
    for (const quote of rows) {
      const current = quotes.value[quote.symbol]
      if (!current || Date.parse(quote.receivedAt) >= Date.parse(current.receivedAt)) quotes.value[quote.symbol] = quote
    }
  }
  async function fetchQuotes(symbols = activeSymbols()) {
    if (!symbols.length) return
    try {
      const result = await RealtimeService.quotes(symbols)
      apply(result.quotes); provider.value = result.status; error.value = null
    } catch (cause) {
      error.value = cause instanceof Error ? cause.message : '行情服务不可用'
    }
  }
  function send(action: 'subscribe' | 'unsubscribe', symbols: string[]) {
    if (socket?.readyState === WebSocket.OPEN && symbols.length) socket.send(JSON.stringify({ action, symbols }))
  }
  function connect() {
    if (socket && (socket.readyState === WebSocket.CONNECTING || socket.readyState === WebSocket.OPEN)) return
    connection.value = 'connecting'
    socket = new WebSocket(RealtimeService.socketUrl())
    socket.onopen = () => { connection.value = 'connected'; reconnectAttempt = 0; send('subscribe', activeSymbols()) }
    socket.onmessage = (event) => {
      const message = JSON.parse(event.data)
      if (Array.isArray(message.quotes)) apply(message.quotes.map(normalizeQuote))
      if (message.status) provider.value = normalizeStatus(message.status)
    }
    socket.onerror = () => { error.value = '实时连接异常' }
    socket.onclose = () => {
      connection.value = 'disconnected'; socket = null
      if (activeSymbols().length) {
        const delays = [1000, 2000, 5000, 10000, 30000]
        const delay = delays[Math.min(reconnectAttempt, delays.length - 1)]!
        reconnectAttempt += 1; connection.value = 'connecting'
        reconnectTimer = window.setTimeout(connect, delay)
      }
    }
  }
  function subscribe(symbols: string[]) {
    const unique = [...new Set(symbols.filter(Boolean))]
    unique.forEach(symbol => refs.set(symbol, (refs.get(symbol) || 0) + 1))
    void fetchQuotes(unique); connect(); send('subscribe', unique)
    return () => {
      const removed: string[] = []
      unique.forEach(symbol => { const next = Math.max(0, (refs.get(symbol) || 1) - 1); refs.set(symbol, next); if (!next) removed.push(symbol) })
      send('unsubscribe', removed)
      if (!activeSymbols().length && reconnectTimer) window.clearTimeout(reconnectTimer)
    }
  }
  function quote(symbol: string) { return quotes.value[symbol] }
  async function refreshStatus() {
    try { provider.value = await RealtimeService.status(); error.value = null } catch (cause) { error.value = cause instanceof Error ? cause.message : '行情服务不可用' }
  }
  return { quotes, provider, connection, error, isDemo, quote, subscribe, fetchQuotes, refreshStatus }
})

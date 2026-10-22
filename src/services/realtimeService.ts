import { apiFetch, apiWebSocketUrl } from '@/api/client'
import type { ProviderStatus, RealtimeQuote } from '@/types/market'

type RawQuote = Record<string, unknown>
type RawStatus = Record<string, unknown>

const n = (value: unknown) => typeof value === 'number' ? value : value == null ? null : Number(value)
const s = (value: unknown) => value == null ? null : String(value)

export function normalizeQuote(raw: RawQuote): RealtimeQuote {
  return {
    symbol: String(raw.symbol), name: s(raw.name), price: n(raw.price), preClose: n(raw.pre_close),
    change: n(raw.change), changePct: n(raw.change_pct), open: n(raw.open), high: n(raw.high), low: n(raw.low),
    volume: n(raw.volume), amount: n(raw.amount), source: String(raw.source) as RealtimeQuote['source'],
    granularity: String(raw.granularity) as RealtimeQuote['granularity'], tradeTime: s(raw.trade_time),
    receivedAt: String(raw.received_at), tradingDate: s(raw.trading_date),
    marketStatus: String(raw.market_status) as RealtimeQuote['marketStatus'], isStale: Boolean(raw.is_stale),
    isDemo: Boolean(raw.is_demo), availability: String(raw.availability) as RealtimeQuote['availability'],
    fallbackReason: s(raw.fallback_reason), qualityFlags: Array.isArray(raw.quality_flags) ? raw.quality_flags.map(String) : [],
  }
}

export function normalizeStatus(raw: RawStatus): ProviderStatus {
  return {
    dataMode: String(raw.data_mode || 'mock'), historyProvider: String(raw.history_provider || 'tushare'), realtimeProvider: String(raw.realtime_provider || 'ifind'),
    configuredMode: String(raw.configured_mode), activeSource: String(raw.active_source),
    ifindConfigured: Boolean(raw.ifind_configured), tushareConfigured: Boolean(raw.tushare_configured),
    tushareRealtimeEnabled: Boolean(raw.tushare_realtime_enabled), cacheBackend: String(raw.cache_backend),
    allowDemo: Boolean(raw.allow_demo), lastSuccessAt: s(raw.last_success_at), lastError: s(raw.last_error),
    capabilities: Array.isArray(raw.capabilities) ? raw.capabilities.map(String) : [], databaseConfigured: Boolean(raw.database_configured),
  }
}

export const RealtimeService = {
  async quotes(symbols: string[]) {
    const response = await apiFetch<{ quotes: RawQuote[]; status: RawStatus }>(`/realtime/quotes?symbols=${encodeURIComponent(symbols.join(','))}`)
    return { quotes: response.quotes.map(normalizeQuote), status: normalizeStatus(response.status) }
  },
  async status() { return normalizeStatus(await apiFetch<RawStatus>('/realtime/status')) },
  socketUrl: () => apiWebSocketUrl('/ws/quotes'),
}

export type QuoteSource = 'ifind' | 'tushare' | 'mock' | 'cache' | 'unavailable'
export type QuoteGranularity = 'snapshot' | 'minute' | 'eod' | 'demo' | 'unknown'

export interface RealtimeQuote {
  symbol: string
  name: string | null
  price: number | null
  preClose: number | null
  change: number | null
  changePct: number | null
  open: number | null
  high: number | null
  low: number | null
  volume: number | null
  amount: number | null
  source: QuoteSource
  granularity: QuoteGranularity
  tradeTime: string | null
  receivedAt: string
  tradingDate: string | null
  marketStatus: 'PRE_MARKET' | 'OPEN' | 'LUNCH_BREAK' | 'CLOSED' | 'STALE' | 'OFFLINE' | 'UNKNOWN' | 'open' | 'closed' | 'delayed' | 'unknown'
  isStale: boolean
  isDemo: boolean
  availability: 'available' | 'partial' | 'unavailable'
  fallbackReason: string | null
  qualityFlags: string[]
}

export interface ProviderStatus {
  dataMode: string
  historyProvider: string
  realtimeProvider: string
  configuredMode: string
  activeSource: string
  ifindConfigured: boolean
  tushareConfigured: boolean
  tushareRealtimeEnabled: boolean
  cacheBackend: string
  allowDemo: boolean
  lastSuccessAt: string | null
  lastError: string | null
  capabilities: string[]
  databaseConfigured: boolean
}

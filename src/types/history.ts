export interface StockSearchResult {
  symbol: string
  code: string
  name: string
  exchange: string
  board: string
  industry: string | null
  list_status?: string
  source: string
  is_demo: boolean
}

export interface HistoricalBar {
  date: string
  open: number | null
  high: number | null
  low: number | null
  close: number | null
  pre_close: number | null
  pct_change: number | null
  volume_shares: number | null
  amount_cny: number | null
  source: string
}

export interface StockProfile {
  symbol: string
  code: string
  name: string
  exchange: string
  board: string
  industry: string | null
  area: string | null
  list_date: string | null
  list_status: string
  latest_trade_date: string | null
  close: number | null
  market_cap: number | null
  pe_ttm: number | null
  pb: number | null
  turnover_rate: number | null
  technical: Record<string, number | string | null> | null
  position: Record<string, number | string | null> | null
  source: string
  is_demo: boolean
}

export interface DataHealthStatus {
  data_mode: string
  historical_provider: { name: string; configured: boolean }
  realtime_provider: { name: string; configured: boolean; active_source: string; last_quote_at: string | null }
  redis: { configured: boolean; active_backend: string }
  database: { configured: boolean; engine: string }
  datasets: Array<{ dataset: string; latest_trade_date: string | null; status: string; record_count: number; updated_at: string; detail: string | null }>
}

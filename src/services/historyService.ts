import { apiFetch } from '@/api/client'
import type { DataHealthStatus, HistoricalBar, StockProfile, StockSearchResult } from '@/types/history'

export const HistoryService = {
  search(query: string) { return apiFetch<StockSearchResult[]>(`/stocks/search?q=${encodeURIComponent(query)}`) },
  stock(symbol: string) { return apiFetch<StockProfile>(`/stocks/${encodeURIComponent(symbol)}`) },
  daily(symbol: string, adjust: 'raw' | 'qfq' | 'hfq' = 'qfq') {
    return apiFetch<{ symbol: string; adjust: string; bars: HistoricalBar[]; latest_trade_date: string | null; source: string; is_demo: boolean }>(`/stocks/${encodeURIComponent(symbol)}/daily?adjust=${adjust}`)
  },
  status() { return apiFetch<DataHealthStatus>('/settings/data') },
}

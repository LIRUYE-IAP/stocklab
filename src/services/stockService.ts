import { findStock, stocks } from '@/mock/stocks'
import { HistoryService } from '@/services/historyService'

export const StockService = {
  async search(query: string) {
    const keyword = query.trim().toLowerCase()
    if (!keyword) return []
    try { return await HistoryService.search(keyword) }
    catch { return stocks.filter((stock) => stock.code.includes(keyword) || stock.name.toLowerCase().includes(keyword) || stock.symbol.toLowerCase().includes(keyword)).map((stock) => ({ ...stock, source: 'mock', is_demo: true })) }
  },
  async get(symbol: string) {
    return findStock(symbol)
  },
}

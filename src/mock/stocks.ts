import type { DailyPrice, Stock } from '@/types'

const createKline = (base: number, seed: number): DailyPrice[] => {
  const rows: DailyPrice[] = []
  let close = base
  const start = new Date('2026-04-01T00:00:00')
  for (let i = 0; i < 96; i += 1) {
    const day = new Date(start)
    day.setDate(start.getDate() + i)
    if (day.getDay() === 0 || day.getDay() === 6) continue
    const wave = Math.sin((i + seed) / 5) * 0.018 + Math.cos((i + seed) / 11) * 0.012
    const drift = (seed % 3 === 0 ? 0.0015 : 0.0005) + ((i * seed) % 7 - 3) * 0.0007
    const open = close * (1 + Math.sin(i + seed) * 0.006)
    close = Math.max(2, close * (1 + wave * 0.34 + drift))
    const high = Math.max(open, close) * (1.009 + ((i + seed) % 4) * 0.002)
    const low = Math.min(open, close) * (0.992 - ((i + seed) % 3) * 0.001)
    rows.push({
      date: `${day.getMonth() + 1}/${day.getDate()}`,
      open: +open.toFixed(2),
      close: +close.toFixed(2),
      low: +low.toFixed(2),
      high: +high.toFixed(2),
      volume: Math.round(35 + Math.abs(Math.sin(i / 4 + seed)) * 65 + (i % 9) * 4),
    })
  }
  return rows
}

const rawStocks: Omit<Stock, 'kline'>[] = [
  { symbol: 'SZ.000630', code: '000630', name: '铜陵有色', exchange: 'SZ', board: '主板', industry: '有色金属', price: 5.86, change: 0.18, changePct: 3.17, open: 5.66, high: 5.92, low: 5.61, preClose: 5.68, volume: 421.8, amount: 24.6, turnover: 5.8, pe: 18.6, pb: 1.72, marketCap: 752, technicalScore: 82, behaviorScore: 86, pricePercentile: 27, signals: ['放量突破', 'MA20向上', 'MACD金叉'], risks: ['短期涨幅偏大'], limitUpsYear: 8, maxStreak: 2, recentLimitUp: '43天前' },
  { symbol: 'SZ.002155', code: '002155', name: '湖南黄金', exchange: 'SZ', board: '主板', industry: '贵金属', price: 24.31, change: 0.88, changePct: 3.76, open: 23.46, high: 24.55, low: 23.31, preClose: 23.43, volume: 92.4, amount: 22.1, turnover: 7.2, pe: 31.4, pb: 4.08, marketCap: 292, technicalScore: 88, behaviorScore: 79, pricePercentile: 63, signals: ['趋势突破', '均线多头'], risks: ['接近60日高点'], limitUpsYear: 5, maxStreak: 2, recentLimitUp: '71天前' },
  { symbol: 'SZ.002716', code: '002716', name: '湖南白银', exchange: 'SZ', board: '主板', industry: '贵金属', price: 4.72, change: -0.06, changePct: -1.26, open: 4.81, high: 4.84, low: 4.68, preClose: 4.78, volume: 176.3, amount: 8.4, turnover: 4.1, pe: 45.2, pb: 3.19, marketCap: 132, technicalScore: 64, behaviorScore: 91, pricePercentile: 42, signals: ['历史活跃', '缩量回踩'], risks: ['跌破MA10'], limitUpsYear: 12, maxStreak: 3, recentLimitUp: '18天前' },
  { symbol: 'SH.688256', code: '688256', name: '寒武纪', exchange: 'SH', board: '科创板', industry: '半导体', price: 623.8, change: 14.5, changePct: 2.38, open: 607.2, high: 629.9, low: 601.8, preClose: 609.3, volume: 10.7, amount: 66.2, turnover: 2.6, pe: 128.4, pb: 21.3, marketCap: 2604, technicalScore: 76, behaviorScore: 68, pricePercentile: 81, signals: ['站上MA20', '动能回升'], risks: ['高位波动', '估值偏高'], limitUpsYear: 2, maxStreak: 1, recentLimitUp: '156天前' },
  { symbol: 'SZ.300750', code: '300750', name: '宁德时代', exchange: 'SZ', board: '创业板', industry: '电池', price: 312.45, change: 2.41, changePct: 0.78, open: 309.2, high: 315.1, low: 307.6, preClose: 310.04, volume: 28.6, amount: 89.2, turnover: 1.4, pe: 27.8, pb: 5.6, marketCap: 13790, technicalScore: 72, behaviorScore: 52, pricePercentile: 58, signals: ['MA20向上', '缩量整理'], risks: ['量能不足'], limitUpsYear: 0, maxStreak: 0, recentLimitUp: '—' },
  { symbol: 'SH.603019', code: '603019', name: '中科曙光', exchange: 'SH', board: '主板', industry: '计算机设备', price: 78.62, change: 4.39, changePct: 5.91, open: 74.8, high: 79.2, low: 73.95, preClose: 74.23, volume: 86.2, amount: 66.9, turnover: 6.3, pe: 52.1, pb: 6.2, marketCap: 1150, technicalScore: 91, behaviorScore: 84, pricePercentile: 74, signals: ['放量突破', '创新高', '均线多头'], risks: ['RSI偏高'], limitUpsYear: 6, maxStreak: 2, recentLimitUp: '28天前' },
  { symbol: 'SZ.000858', code: '000858', name: '五粮液', exchange: 'SZ', board: '主板', industry: '白酒', price: 136.28, change: -1.43, changePct: -1.04, open: 138.1, high: 138.8, low: 135.6, preClose: 137.71, volume: 31.7, amount: 43.3, turnover: 0.8, pe: 19.4, pb: 4.1, marketCap: 5289, technicalScore: 43, behaviorScore: 31, pricePercentile: 18, signals: ['低位整理'], risks: ['跌破MA60', '趋势偏弱'], limitUpsYear: 0, maxStreak: 0, recentLimitUp: '—' },
  { symbol: 'SH.601899', code: '601899', name: '紫金矿业', exchange: 'SH', board: '主板', industry: '有色金属', price: 28.76, change: 0.52, changePct: 1.84, open: 28.31, high: 29.02, low: 28.11, preClose: 28.24, volume: 135.6, amount: 38.7, turnover: 0.7, pe: 20.9, pb: 4.7, marketCap: 7564, technicalScore: 79, behaviorScore: 61, pricePercentile: 69, signals: ['趋势偏强', 'MA20向上'], risks: ['接近前高'], limitUpsYear: 1, maxStreak: 1, recentLimitUp: '248天前' },
  { symbol: 'SZ.002230', code: '002230', name: '科大讯飞', exchange: 'SZ', board: '主板', industry: '软件服务', price: 58.43, change: -1.12, changePct: -1.88, open: 59.61, high: 60.02, low: 58.18, preClose: 59.55, volume: 63.4, amount: 37.2, turnover: 2.9, pe: 96.5, pb: 8.2, marketCap: 1351, technicalScore: 55, behaviorScore: 73, pricePercentile: 47, signals: ['平台整理'], risks: ['跌破MA20', '动能转弱'], limitUpsYear: 4, maxStreak: 1, recentLimitUp: '96天前' },
  { symbol: 'SH.600036', code: '600036', name: '招商银行', exchange: 'SH', board: '主板', industry: '银行', price: 43.86, change: 0.09, changePct: 0.21, open: 43.72, high: 44.1, low: 43.51, preClose: 43.77, volume: 54.8, amount: 24.0, turnover: 0.3, pe: 7.5, pb: 1.02, marketCap: 11061, technicalScore: 68, behaviorScore: 22, pricePercentile: 54, signals: ['趋势稳定'], risks: ['动能一般'], limitUpsYear: 0, maxStreak: 0, recentLimitUp: '—' },
]

export const stocks: Stock[] = rawStocks.map((stock, index) => ({
  ...stock,
  kline: createKline(stock.price * (0.86 + (index % 3) * 0.05), index + 2),
}))

export const findStock = (symbolOrCode: string): Stock | undefined =>
  stocks.find((stock) => stock.symbol === symbolOrCode || stock.code === symbolOrCode)

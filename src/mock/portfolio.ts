import type { Position, TradeEpisode, Transaction } from '@/types'

export const positions: Position[] = [
  { symbol: 'SZ.000630', stockName: '铜陵有色', industry: '有色金属', quantity: 22000, avgCost: 5.21, price: 5.86, marketValue: 128920, pnl: 14300, returnPct: 12.48, weight: 31.6, technicalScore: 82, risk: '短期涨幅偏大' },
  { symbol: 'SZ.002155', stockName: '湖南黄金', industry: '贵金属', quantity: 3800, avgCost: 22.84, price: 24.31, marketValue: 92378, pnl: 5586, returnPct: 6.44, weight: 22.7, technicalScore: 88, risk: '接近60日高点' },
  { symbol: 'SZ.300750', stockName: '宁德时代', industry: '电池', quantity: 300, avgCost: 326.2, price: 312.45, marketValue: 93735, pnl: -4125, returnPct: -4.22, weight: 23, technicalScore: 72, risk: '量能不足' },
  { symbol: 'SZ.000858', stockName: '五粮液', industry: '白酒', quantity: 680, avgCost: 148.6, price: 136.28, marketValue: 92670, pnl: -8378, returnPct: -8.29, weight: 22.7, technicalScore: 43, risk: '跌破MA60' },
]

export const transactions: Transaction[] = [
  { id: 1, date: '2026-08-28', symbol: 'SZ.000630', stockName: '铜陵有色', side: '买入', price: 5.62, quantity: 6000, amount: 33720, strategy: '历史活跃低位转强', reason: '突破平台后回踩确认' },
  { id: 2, date: '2026-08-21', symbol: 'SZ.002155', stockName: '湖南黄金', side: '买入', price: 23.18, quantity: 1200, amount: 27816, strategy: '趋势突破', reason: 'MA20向上且量能配合' },
  { id: 3, date: '2026-08-14', symbol: 'SH.603019', stockName: '中科曙光', side: '卖出', price: 73.42, quantity: 900, amount: 66078, strategy: '低位放量', reason: '达到计划目标位' },
  { id: 4, date: '2026-08-06', symbol: 'SZ.000858', stockName: '五粮液', side: '买入', price: 141.2, quantity: 280, amount: 39536, strategy: '缩量回踩', reason: '价格进入计划区间' },
]

export const navSeries = [100, 101.2, 100.4, 102.1, 104.8, 103.9, 106.2, 108.9, 110.1, 109.3, 112.8, 114.2, 113.5, 116.8, 118.3, 117.4, 120.6, 119.8, 122.7, 124.6]

export const episodes: TradeEpisode[] = [
  { id: 1, symbol: 'SH.603019', stockName: '中科曙光', industry: '计算机设备', openDate: '2026-06-18', closeDate: '2026-08-14', holdingDays: 42, returnPct: 18.6, pnl: 12740, mfe: 23.8, mae: -5.1, entryTechnical: 78, entryBehavior: 82, entryPercentile: 31, strategy: '低位放量', exitReason: '达到计划目标位', reviewStatus: '已复盘' },
  { id: 2, symbol: 'SH.601899', stockName: '紫金矿业', industry: '有色金属', openDate: '2026-03-09', closeDate: '2026-05-22', holdingDays: 52, returnPct: 12.4, pnl: 8960, mfe: 17.1, mae: -3.8, entryTechnical: 73, entryBehavior: 58, entryPercentile: 42, strategy: '趋势突破', exitReason: '趋势转弱', reviewStatus: '已复盘' },
  { id: 3, symbol: 'SZ.002230', stockName: '科大讯飞', industry: '软件服务', openDate: '2026-02-12', closeDate: '2026-03-03', holdingDays: 13, returnPct: -7.2, pnl: -4860, mfe: 4.2, mae: -9.8, entryTechnical: 69, entryBehavior: 75, entryPercentile: 55, strategy: '历史活跃低位转强', exitReason: '跌破止损位', reviewStatus: '待复盘' },
  { id: 4, symbol: 'SZ.002716', stockName: '湖南白银', industry: '贵金属', openDate: '2025-11-21', closeDate: '2026-01-16', holdingDays: 39, returnPct: 26.8, pnl: 18350, mfe: 34.6, mae: -6.4, entryTechnical: 84, entryBehavior: 91, entryPercentile: 24, strategy: '历史活跃低位转强', exitReason: '分批止盈完成', reviewStatus: '已复盘' },
]

export const cumulativeReturns = [0, 2.4, 1.1, 5.8, 9.4, 7.9, 14.8, 18.2, 15.5, 22.6, 27.1, 25.8, 33.4, 38.7]

import type { Strategy } from '@/types'

export const strategies: Strategy[] = [
  { id: 1, name: '历史活跃低位转强', description: '历史股性活跃，处于中低价格分位，并出现技术转强信号。', kind: '系统策略', conditionCount: 6, lastRun: '今日 15:18', matches: 14, tags: ['Behavior ≥70', '分位 ≤35%', 'Technical ≥70'] },
  { id: 2, name: '沉寂股重新激活', description: '较长时间无明显行情后，换手与动能同步回升。', kind: '系统策略', conditionCount: 5, lastRun: '今日 15:18', matches: 9, tags: ['量比 ≥1.5', 'MACD金叉'] },
  { id: 3, name: '低位放量', description: '一年价格分位较低且成交量显著高于20日均量。', kind: '系统策略', conditionCount: 4, lastRun: '今日 15:18', matches: 23, tags: ['分位 ≤30%', '量比 ≥1.8'] },
  { id: 4, name: '趋势突破', description: '均线多头、放量突破平台且趋势评分较高。', kind: '系统策略', conditionCount: 5, lastRun: '今日 15:18', matches: 31, tags: ['MA20向上', '创新高'] },
  { id: 5, name: '缩量回踩', description: '上升趋势中的缩量回踩，靠近MA20但尚未破位。', kind: '我的策略', conditionCount: 7, lastRun: '昨日 18:02', matches: 42, tags: ['趋势偏强', '缩量', '靠近MA20'] },
  { id: 6, name: '基本面过滤', description: '盈利为正、估值处于合理区间并具备基础技术强度。', kind: '我的策略', conditionCount: 5, lastRun: '2026-08-28', matches: 126, tags: ['净利润 >0', 'PE 10–30'] },
]

export const horizonStats = [
  { horizon: 'T+1', samples: 486, winRate: 54.3, avg: 0.8, median: 0.4 },
  { horizon: 'T+3', samples: 472, winRate: 58.7, avg: 2.1, median: 1.2 },
  { horizon: 'T+5', samples: 461, winRate: 61.3, avg: 3.8, median: 1.9 },
  { horizon: 'T+10', samples: 438, winRate: 60.5, avg: 5.2, median: 2.7 },
  { horizon: 'T+20', samples: 402, winRate: 58.7, avg: 7.2, median: 3.4 },
  { horizon: 'T+60', samples: 318, winRate: 55.9, avg: 10.6, median: 4.8 },
]

export const annualBacktest = [
  { year: '2023', signals: 128, avg: 5.1, winRate: 56.2 },
  { year: '2024', signals: 143, avg: 7.8, winRate: 60.1 },
  { year: '2025', signals: 154, avg: 8.6, winRate: 62.4 },
  { year: '2026 YTD', signals: 61, avg: 6.9, winRate: 59.0 },
]

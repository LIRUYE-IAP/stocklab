import type { AlertRule } from '@/types'

export const alertRules: AlertRule[] = [
  { id: 1, symbol: 'SZ.000630', stockName: '铜陵有色', type: 'Technical Score', detail: '上穿 80', enabled: true, status: '已触发', updatedAt: '今日 14:36' },
  { id: 2, symbol: 'SZ.002155', stockName: '湖南黄金', type: '价格', detail: '低于 ¥22.80', enabled: true, status: '启用', updatedAt: '今日 09:31' },
  { id: 3, symbol: 'SZ.002230', stockName: '科大讯飞', type: '技术信号', detail: '跌破 MA20', enabled: true, status: '已触发', updatedAt: '今日 10:42' },
  { id: 4, symbol: 'SH.688256', stockName: '寒武纪', type: '成交量', detail: '大于 MA20 × 1.8', enabled: false, status: '停用', updatedAt: '昨日 15:05' },
  { id: 5, symbol: 'SH.603019', stockName: '中科曙光', type: '价格', detail: '突破 60 日高点', enabled: true, status: '启用', updatedAt: '2026-08-28' },
]

export const notifications = [
  { id: 1, title: '铜陵有色 Technical Score 从 76 升至 82', time: '14:36', read: false, tone: 'positive' },
  { id: 2, title: '科大讯飞跌破 MA20', time: '10:42', read: false, tone: 'negative' },
  { id: 3, title: '历史活跃低位转强今日新增 4 只', time: '09:45', read: false, tone: 'info' },
  { id: 4, title: '湖南黄金接近计划买入价', time: '昨日', read: true, tone: 'warning' },
]

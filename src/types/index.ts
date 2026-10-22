export type Trend = 'up' | 'down' | 'flat'
export type SignalTone = 'positive' | 'negative' | 'warning' | 'neutral' | 'info'

export interface DailyPrice {
  date: string
  open: number
  close: number
  low: number
  high: number
  volume: number
}

export interface Stock {
  symbol: string
  code: string
  name: string
  exchange: 'SH' | 'SZ' | 'BJ'
  board: string
  industry: string
  price: number
  change: number
  changePct: number
  open: number
  high: number
  low: number
  preClose: number
  volume: number
  amount: number
  turnover: number
  pe: number
  pb: number
  marketCap: number
  technicalScore: number
  behaviorScore: number
  pricePercentile: number
  signals: string[]
  risks: string[]
  limitUpsYear: number
  maxStreak: number
  recentLimitUp: string
  kline: DailyPrice[]
}

export interface Sector {
  name: string
  change: number
  return5: number
  return20: number
  amount: number
  strength: number
  stage: '启动' | '加速' | '高潮' | '分歧' | '退潮' | '企稳'
}

export interface ScreenerCondition {
  id: string
  field: 'technicalScore' | 'behaviorScore' | 'pricePercentile' | 'turnover' | 'pe' | 'limitUpsYear'
  label: string
  operator: '>=' | '<=' | '>'
  value: number
  suffix?: string
}

export interface AlertRule {
  id: number
  symbol: string
  stockName: string
  type: string
  detail: string
  enabled: boolean
  status: '启用' | '停用' | '已触发'
  updatedAt: string
}

export interface Position {
  symbol: string
  stockName: string
  industry: string
  quantity: number
  avgCost: number
  price: number
  marketValue: number
  pnl: number
  returnPct: number
  weight: number
  technicalScore: number
  risk: string
}

export interface Transaction {
  id: number
  date: string
  symbol: string
  stockName: string
  side: '买入' | '卖出'
  price: number
  quantity: number
  amount: number
  strategy: string
  reason: string
}

export interface Strategy {
  id: number
  name: string
  description: string
  kind: '系统策略' | '我的策略'
  conditionCount: number
  lastRun: string
  matches: number
  tags: string[]
}

export interface TradeEpisode {
  id: number
  symbol: string
  stockName: string
  industry: string
  openDate: string
  closeDate: string
  holdingDays: number
  returnPct: number
  pnl: number
  mfe: number
  mae: number
  entryTechnical: number
  entryBehavior: number
  entryPercentile: number
  strategy: string
  exitReason: string
  reviewStatus: '待复盘' | '已复盘'
}

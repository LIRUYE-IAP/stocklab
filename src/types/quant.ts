export type QuantRunStatus = 'DRAFT' | 'READY' | 'RUNNING' | 'PAUSED' | 'STOPPED' | 'ERROR' | 'RISK_HALTED'
export type PaperOrderStatus = 'NEW' | 'PENDING' | 'PARTIALLY_FILLED' | 'FILLED' | 'CANCELLED' | 'REJECTED'
export type PaperOrderSide = 'BUY' | 'SELL'
export type PaperOrderType = 'MARKET' | 'LIMIT'
export type QuantLogLevel = 'INFO' | 'SIGNAL' | 'ORDER' | 'TRADE' | 'RISK' | 'ERROR'

export interface QuantConfig {
  strategyId: number
  accountName: string
  initialCash: number
  maxPositions: number
  maxSingleWeight: number
  maxTotalWeight: number
  maxOrderAmount: number
  stopLoss: number
  takeProfit: number
  maxDailyLoss: number
  maxDrawdown: number
  cooldownMinutes: number
  slippageBps: number
  commissionRate: number
  minimumCommission: number
  taxRate: number
  timeframe: string
}

export interface StrategyInstance {
  id: string
  strategyId: number
  strategyName: string
  accountName: string
  mode: 'LIVE_PAPER'
  status: QuantRunStatus
  createdAt: string
  startedAt?: string
  config: QuantConfig
}

export interface PaperPosition {
  symbol: string
  stockName: string
  quantity: number
  available: number
  avgCost: number
  price: number
  marketValue: number
  pnl: number
  returnPct: number
  weight: number
  technicalScore: number
  behaviorScore: number
  signal: string
}

export interface PaperOrder {
  id: string
  time: string
  symbol: string
  stockName: string
  side: PaperOrderSide
  type: PaperOrderType
  limitPrice: number | null
  quantity: number
  status: PaperOrderStatus
  filledQuantity: number
  strategyName: string
  reason: string
}

export interface PaperTrade {
  id: string
  time: string
  symbol: string
  stockName: string
  side: PaperOrderSide
  price: number
  quantity: number
  amount: number
  fee: number
  slippage: number
  strategyName: string
  marketDataSource?: string
  marketQuoteTime?: string | null
  simulationVersion?: string
}

export interface StrategySignal {
  id: string
  time: string
  symbol: string
  stockName: string
  type: 'BUY' | 'SELL' | 'HOLD'
  reason: string[]
  technicalScore: number
  behaviorScore: number
  volumeRatio: number
  status: 'DETECTED' | 'RISK_PASSED' | 'RISK_REJECTED' | 'ORDERED'
}

export interface RiskEvent {
  id: string
  time: string
  severity: 'INFO' | 'WARNING' | 'HALT'
  rule: string
  detail: string
  action: string
}

export interface QuantRunLog {
  id: string
  time: string
  level: QuantLogLevel
  message: string
  detail?: string
}

export interface NavPoint {
  time: string
  strategy: number
  benchmark: number
  drawdown: number
}

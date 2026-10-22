import type { NavPoint, PaperOrder, PaperPosition, PaperTrade, QuantRunLog, RiskEvent, StrategySignal } from '@/types/quant'

export const demoNav: NavPoint[] = Array.from({ length: 42 }, (_, index) => {
  const strategy = 1 + index * 0.0021 + Math.sin(index / 3.2) * 0.012 - Math.cos(index / 8) * 0.006
  const benchmark = 1 + index * 0.0009 + Math.sin(index / 5) * 0.008
  return {
    time: index < 30 ? `08/${String(index + 1).padStart(2, '0')}` : `09/${String(index - 29).padStart(2, '0')}`,
    strategy: +strategy.toFixed(4),
    benchmark: +benchmark.toFixed(4),
    drawdown: +((strategy / Math.max(1, strategy + Math.max(0, Math.sin(index / 4)) * 0.018) - 1) * 100).toFixed(2),
  }
})

export const demoPositions: PaperPosition[] = [
  { symbol: 'SZ.000630', stockName: '铜陵有色', quantity: 2600, available: 2600, avgCost: 5.62, price: 5.86, marketValue: 15236, pnl: 624, returnPct: 4.27, weight: 14.3, technicalScore: 82, behaviorScore: 86, signal: '继续持有' },
  { symbol: 'SH.603019', stockName: '中科曙光', quantity: 200, available: 200, avgCost: 74.18, price: 78.62, marketValue: 15724, pnl: 888, returnPct: 5.99, weight: 14.8, technicalScore: 91, behaviorScore: 84, signal: '趋势偏强' },
]

export const demoSignals: StrategySignal[] = [
  { id: 'SIG-0908-003', time: '14:31:00', symbol: 'SH.603019', stockName: '中科曙光', type: 'BUY', reason: ['Technical 84 → 91', '放量突破平台', 'Volume Ratio 1.82'], technicalScore: 91, behaviorScore: 84, volumeRatio: 1.82, status: 'ORDERED' },
  { id: 'SIG-0908-002', time: '14:27:00', symbol: 'SZ.000630', stockName: '铜陵有色', type: 'HOLD', reason: ['MA20 向上', 'Behavior Score 86'], technicalScore: 82, behaviorScore: 86, volumeRatio: 1.46, status: 'DETECTED' },
  { id: 'SIG-0908-001', time: '14:16:00', symbol: 'SZ.002155', stockName: '湖南黄金', type: 'BUY', reason: ['单股仓位将超过 20%'], technicalScore: 88, behaviorScore: 79, volumeRatio: 1.67, status: 'RISK_REJECTED' },
]

export const demoOrders: PaperOrder[] = [
  { id: 'PO-20260908-003', time: '14:31:00', symbol: 'SH.603019', stockName: '中科曙光', side: 'BUY', type: 'MARKET', limitPrice: null, quantity: 200, status: 'FILLED', filledQuantity: 200, strategyName: '历史活跃低位转强', reason: '信号通过风控，模拟市价成交' },
  { id: 'PO-20260908-002', time: '14:25:00', symbol: 'SZ.002716', stockName: '湖南白银', side: 'BUY', type: 'LIMIT', limitPrice: 4.66, quantity: 3000, status: 'PENDING', filledQuantity: 0, strategyName: '历史活跃低位转强', reason: '市场价尚未触及委托价' },
  { id: 'PO-20260908-001', time: '14:16:00', symbol: 'SZ.002155', stockName: '湖南黄金', side: 'BUY', type: 'MARKET', limitPrice: null, quantity: 900, status: 'REJECTED', filledQuantity: 0, strategyName: '历史活跃低位转强', reason: '风控拒绝：预计单股仓位 21.4% > 20%' },
]

export const demoTrades: PaperTrade[] = [
  { id: 'PT-20260908-002', time: '14:31:00', symbol: 'SH.603019', stockName: '中科曙光', side: 'BUY', price: 74.18, quantity: 200, amount: 14836, fee: 5, slippage: 1.48, strategyName: '历史活跃低位转强' },
  { id: 'PT-20260906-001', time: '10:08:00', symbol: 'SZ.000630', stockName: '铜陵有色', side: 'BUY', price: 5.62, quantity: 2600, amount: 14612, fee: 5, slippage: 1.46, strategyName: '历史活跃低位转强' },
]

export const demoRiskEvents: RiskEvent[] = [
  { id: 'RISK-003', time: '14:16:00', severity: 'WARNING', rule: '最大单股仓位', detail: '湖南黄金预计仓位 21.4%，阈值为 20%', action: '拒绝创建订单' },
  { id: 'RISK-002', time: '13:42:00', severity: 'INFO', rule: '重复交易冷却', detail: '铜陵有色距上次交易 34 分钟', action: '通过' },
  { id: 'RISK-001', time: '09:30:00', severity: 'INFO', rule: '策略最大回撤', detail: '当前回撤 -2.18%，阈值 -12%', action: '通过' },
]

export const demoLogs: QuantRunLog[] = [
  { id: 'L9', time: '14:31:01', level: 'TRADE', message: '模拟成交完成', detail: '中科曙光 200股 @ 74.18，费用 ¥5.00' },
  { id: 'L8', time: '14:31:00', level: 'ORDER', message: 'BUY 订单已创建', detail: 'PO-20260908-003 · MARKET · 200股' },
  { id: 'L7', time: '14:30:59', level: 'RISK', message: '风险检查通过', detail: '预计单股仓位 14.2%，总仓位 29.1%' },
  { id: 'L6', time: '14:30:58', level: 'SIGNAL', message: '中科曙光产生 BUY 信号', detail: 'Technical 91 · Behavior 84 · 量比 1.82' },
  { id: 'L5', time: '14:30:04', level: 'INFO', message: '17 只股票通过筛选', detail: '3 个 BUY 信号进入风险检查' },
  { id: 'L4', time: '14:30:03', level: 'INFO', message: '股票池扫描完成', detail: '5342 只股票 · 耗时 2.8s（演示）' },
  { id: 'L3', time: '14:30:00', level: 'INFO', message: 'Strategy Scan Started', detail: '历史活跃低位转强 v1.3' },
  { id: 'L2', time: '09:30:00', level: 'INFO', message: 'Paper Exchange Simulator 已就绪', detail: '只允许虚拟委托，不连接券商' },
  { id: 'L1', time: '09:29:58', level: 'INFO', message: '策略实例启动', detail: 'LIVE_PAPER · 1分钟周期' },
]

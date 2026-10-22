import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { stocks } from '@/mock/stocks'
import { strategies } from '@/mock/strategies'
import { demoLogs, demoNav, demoOrders, demoPositions, demoRiskEvents, demoSignals, demoTrades } from '@/mock/quant'
import type { NavPoint, PaperOrder, PaperPosition, PaperTrade, QuantConfig, QuantRunLog, QuantRunStatus, RiskEvent, StrategyInstance, StrategySignal } from '@/types/quant'
import type { RealtimeQuote } from '@/types/market'

const now = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })
const makeId = (prefix: string) => `${prefix}-${Date.now()}-${Math.floor(Math.random() * 100)}`

const defaultConfig: QuantConfig = {
  strategyId: 1, accountName: '10万低位转强策略', initialCash: 100000, maxPositions: 5,
  maxSingleWeight: 20, maxTotalWeight: 80, maxOrderAmount: 20000, stopLoss: 8,
  takeProfit: 20, maxDailyLoss: 4, maxDrawdown: 12, cooldownMinutes: 30,
  slippageBps: 10, commissionRate: 0.0003, minimumCommission: 5, taxRate: 0.0005, timeframe: '1分钟',
}

export const useQuantStore = defineStore('quant', () => {
  const config = ref<QuantConfig>({ ...defaultConfig })
  const status = ref<QuantRunStatus>('RUNNING')
  const instance = ref<StrategyInstance>({ id: 'QI-20260908-001', strategyId: 1, strategyName: strategies[0]!.name, accountName: defaultConfig.accountName, mode: 'LIVE_PAPER', status: 'RUNNING', createdAt: '2026-09-01 09:25:00', startedAt: '2026-09-01 09:29:58', config: { ...defaultConfig } })
  const initialCash = ref(100000)
  const cash = ref(72184)
  const positions = ref<PaperPosition[]>(demoPositions.map((row) => ({ ...row })))
  const orders = ref<PaperOrder[]>(demoOrders.map((row) => ({ ...row })))
  const trades = ref<PaperTrade[]>(demoTrades.map((row) => ({ ...row })))
  const signals = ref<StrategySignal[]>(demoSignals.map((row) => ({ ...row, reason: [...row.reason] })))
  const riskEvents = ref<RiskEvent[]>(demoRiskEvents.map((row) => ({ ...row })))
  const logs = ref<QuantRunLog[]>(demoLogs.map((row) => ({ ...row })))
  const nav = ref<NavPoint[]>(demoNav.map((row) => ({ ...row })))
  const tickCount = ref(0)

  const marketValue = computed(() => positions.value.reduce((sum, item) => sum + item.marketValue, 0))
  const totalAssets = computed(() => cash.value + marketValue.value)
  const cumulativeReturn = computed(() => (totalAssets.value / initialCash.value - 1) * 100)
  const todayReturn = computed(() => 1.36 + Math.sin(tickCount.value / 2) * 0.08)
  const maxDrawdown = computed(() => Math.min(...nav.value.map((row) => row.drawdown), -0.01))
  const pendingOrders = computed(() => orders.value.filter((row) => row.status === 'PENDING' || row.status === 'NEW').length)
  const todaySignalCount = computed(() => signals.value.length)
  const totalWeight = computed(() => totalAssets.value ? marketValue.value / totalAssets.value * 100 : 0)

  function addLog(level: QuantRunLog['level'], message: string, detail?: string) {
    logs.value.unshift({ id: makeId('L'), time: now(), level, message, detail })
  }

  function setStatus(next: QuantRunStatus) {
    status.value = next
    instance.value.status = next
  }

  function createInstance(next: QuantConfig) {
    config.value = { ...next }
    const strategy = strategies.find((row) => row.id === next.strategyId) || strategies[0]!
    initialCash.value = next.initialCash
    cash.value = next.initialCash
    positions.value = []
    orders.value = []
    trades.value = []
    signals.value = []
    riskEvents.value = []
    logs.value = []
    nav.value = [{ time: now(), strategy: 1, benchmark: 1, drawdown: 0 }]
    tickCount.value = 0
    instance.value = { id: makeId('QI'), strategyId: strategy.id, strategyName: strategy.name, accountName: next.accountName, mode: 'LIVE_PAPER', status: 'READY', createdAt: new Date().toLocaleString('zh-CN'), config: { ...next } }
    setStatus('READY')
    addLog('INFO', 'Strategy Instance 已创建', `${strategy.name} · ¥${next.initialCash.toLocaleString()} · LIVE_PAPER`)
  }

  function start() {
    if (status.value === 'RISK_HALTED') return
    setStatus('RUNNING')
    instance.value.startedAt ||= new Date().toLocaleString('zh-CN')
    addLog('INFO', '策略实例开始运行', `${instance.value.strategyName} · ${config.value.timeframe}`)
  }

  function pause() { if (status.value === 'RUNNING') { setStatus('PAUSED'); addLog('INFO', '策略实例已暂停', '停止扫描与新开仓，已有虚拟持仓保留') } }
  function stop() { if (status.value !== 'STOPPED') { setStatus('STOPPED'); addLog('INFO', '策略实例已停止', '不会再生成新信号和模拟订单') } }

  function reset() {
    cash.value = config.value.initialCash
    initialCash.value = config.value.initialCash
    positions.value = []; orders.value = []; trades.value = []; signals.value = []; riskEvents.value = []
    nav.value = [{ time: now(), strategy: 1, benchmark: 1, drawdown: 0 }]
    logs.value = []; tickCount.value = 0; setStatus('READY')
    addLog('INFO', '虚拟账户已重置', `现金恢复至 ¥${initialCash.value.toLocaleString()}`)
  }

  function cancelOrder(id: string) {
    const order = orders.value.find((row) => row.id === id)
    if (!order || !['NEW', 'PENDING', 'PARTIALLY_FILLED'].includes(order.status)) return false
    order.status = 'CANCELLED'; order.reason = '用户手动撤销'
    addLog('ORDER', '虚拟订单已撤销', `${order.stockName} · ${order.quantity}股`)
    return true
  }

  function rejectSignal(stock: typeof stocks[number], detail: string) {
    const signal: StrategySignal = { id: makeId('SIG'), time: now(), symbol: stock.symbol, stockName: stock.name, type: 'BUY', reason: [detail], technicalScore: stock.technicalScore, behaviorScore: stock.behaviorScore, volumeRatio: +(1.2 + Math.random()).toFixed(2), status: 'RISK_REJECTED' }
    signals.value.unshift(signal)
    riskEvents.value.unshift({ id: makeId('RISK'), time: now(), severity: 'WARNING', rule: '组合风险约束', detail, action: '拒绝创建订单' })
    addLog('RISK', `${stock.name} 未通过风险检查`, detail)
  }

  function executeBuy(stock: typeof stocks[number], quote?: RealtimeQuote) {
    if (!quote || quote.price == null || quote.availability === 'unavailable') return rejectSignal(stock, '行情缺失，Paper Broker 禁止模拟成交')
    if (quote.isStale) return rejectSignal(stock, `行情已过期（${quote.tradeTime || quote.receivedAt}），订单保持未创建`)
    const marketPrice = quote.price
    const maxAmount = Math.min(totalAssets.value * config.value.maxSingleWeight / 100, config.value.maxOrderAmount, cash.value * 0.9)
    const quantity = Math.floor(maxAmount / marketPrice / 100) * 100
    if (quantity < 100) return rejectSignal(stock, '可用现金不足以完成一手模拟交易')
    if (!positions.value.some((row) => row.symbol === stock.symbol) && positions.value.length >= config.value.maxPositions) return rejectSignal(stock, `持仓数量已达到上限 ${config.value.maxPositions} 只`)
    if (totalWeight.value >= config.value.maxTotalWeight) return rejectSignal(stock, `总仓位 ${totalWeight.value.toFixed(1)}% 已达到上限 ${config.value.maxTotalWeight}%`)
    const signal: StrategySignal = { id: makeId('SIG'), time: now(), symbol: stock.symbol, stockName: stock.name, type: 'BUY', reason: [`Technical Score ${stock.technicalScore}`, stock.signals[0] || '条件满足', `Volume Ratio ${(1.5 + tickCount.value * .07).toFixed(2)}`], technicalScore: stock.technicalScore, behaviorScore: stock.behaviorScore, volumeRatio: +(1.5 + tickCount.value * .07).toFixed(2), status: 'ORDERED' }
    signals.value.unshift(signal); addLog('SIGNAL', `${stock.name} 产生 BUY 信号`, signal.reason.join(' · ')); addLog('RISK', `${stock.name} 通过风险检查`, '仓位、金额、回撤与冷却时间均通过')
    const fillPrice = +(marketPrice * (1 + config.value.slippageBps / 10000)).toFixed(2)
    const amount = fillPrice * quantity
    const fee = Math.max(config.value.minimumCommission, amount * config.value.commissionRate)
    const order: PaperOrder = { id: makeId('PO'), time: now(), symbol: stock.symbol, stockName: stock.name, side: 'BUY', type: 'MARKET', limitPrice: null, quantity, status: 'FILLED', filledQuantity: quantity, strategyName: instance.value.strategyName, reason: '信号与风控均通过，Paper Exchange 模拟成交' }
    orders.value.unshift(order); addLog('ORDER', 'BUY 模拟订单已创建', `${stock.name} · MARKET · ${quantity}股`)
    const trade: PaperTrade = { id: makeId('PT'), time: now(), symbol: stock.symbol, stockName: stock.name, side: 'BUY', price: fillPrice, quantity, amount, fee, slippage: +(amount * config.value.slippageBps / 10000).toFixed(2), strategyName: instance.value.strategyName, marketDataSource: quote.source, marketQuoteTime: quote.tradeTime || quote.receivedAt, simulationVersion: 'paper-v1' }
    trades.value.unshift(trade); cash.value -= amount + fee
    const existing = positions.value.find((row) => row.symbol === stock.symbol)
    if (existing) {
      const totalQty = existing.quantity + quantity
      existing.avgCost = +((existing.avgCost * existing.quantity + amount + fee) / totalQty).toFixed(2)
      existing.quantity = totalQty; existing.available += quantity
    } else {
      positions.value.push({ symbol: stock.symbol, stockName: stock.name, quantity, available: quantity, avgCost: +(amount + fee) / quantity, price: marketPrice, marketValue: marketPrice * quantity, pnl: marketPrice * quantity - amount - fee, returnPct: 0, weight: 0, technicalScore: stock.technicalScore, behaviorScore: stock.behaviorScore, signal: '新建仓' })
    }
    addLog('TRADE', 'Paper Trade 模拟成交', `${stock.name} ${quantity}股 @ ${fillPrice.toFixed(2)}，费用 ¥${fee.toFixed(2)}`)
  }

  function tick(marketQuotes: Record<string, RealtimeQuote> = {}, forceSignal = false) {
    if (status.value !== 'RUNNING') return
    tickCount.value += 1
    positions.value.forEach((position, index) => {
      const movement = Math.sin((tickCount.value + index) / 2.2) * .0016 + .0003
      const quote = marketQuotes[position.symbol]
      position.price = quote?.price != null && quote.availability !== 'unavailable' ? quote.price : +(position.price * (1 + movement)).toFixed(2)
      position.marketValue = +(position.price * position.quantity).toFixed(2)
      position.pnl = +(position.marketValue - position.avgCost * position.quantity).toFixed(2)
      position.returnPct = +((position.price / position.avgCost - 1) * 100).toFixed(2)
    })
    positions.value.forEach((position) => { position.weight = totalAssets.value ? +(position.marketValue / totalAssets.value * 100).toFixed(1) : 0 })
    const previous = nav.value[nav.value.length - 1] || { strategy: 1, benchmark: 1, drawdown: 0 }
    const strategyNav = +(totalAssets.value / initialCash.value).toFixed(4)
    const peak = Math.max(...nav.value.map((row) => row.strategy), strategyNav)
    nav.value.push({ time: now(), strategy: strategyNav, benchmark: +(previous.benchmark * (1 + Math.sin(tickCount.value) * .0003)).toFixed(4), drawdown: +((strategyNav / peak - 1) * 100).toFixed(2) })
    if (nav.value.length > 80) nav.value.shift()
    if (Math.abs(maxDrawdown.value) >= config.value.maxDrawdown) {
      setStatus('RISK_HALTED'); riskEvents.value.unshift({ id: makeId('RISK'), time: now(), severity: 'HALT', rule: 'Kill Switch', detail: `策略回撤 ${maxDrawdown.value.toFixed(2)}% 达到阈值 -${config.value.maxDrawdown}%`, action: '停止所有新开仓' }); addLog('RISK', 'Risk Halted', 'Kill Switch 已停止新开仓'); return
    }
    if (forceSignal || tickCount.value % 3 === 0) {
      addLog('INFO', 'Strategy Scan Started', '演示股票池正在按 Condition Engine 扫描')
      const candidates = stocks.filter((stock) => stock.technicalScore >= 70 && stock.behaviorScore >= 60)
      const target = candidates[tickCount.value % candidates.length]!
      if (positions.value.some((row) => row.symbol === target.symbol)) {
        signals.value.unshift({ id: makeId('SIG'), time: now(), symbol: target.symbol, stockName: target.name, type: 'HOLD', reason: ['已有虚拟持仓', '退出条件未触发'], technicalScore: target.technicalScore, behaviorScore: target.behaviorScore, volumeRatio: 1.38, status: 'DETECTED' })
        addLog('SIGNAL', `${target.name} 保持 HOLD`, '已有持仓，未重复下单')
      } else executeBuy(target, marketQuotes[target.symbol])
    }
  }

  return { config, status, instance, initialCash, cash, positions, orders, trades, signals, riskEvents, logs, nav, marketValue, totalAssets, cumulativeReturn, todayReturn, maxDrawdown, pendingOrders, todaySignalCount, totalWeight, createInstance, start, pause, stop, reset, cancelOrder, tick }
})

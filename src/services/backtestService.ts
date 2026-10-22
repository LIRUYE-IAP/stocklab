import { annualBacktest, horizonStats } from '@/mock/strategies'

export const BacktestService = {
  async run() {
    await new Promise((resolve) => setTimeout(resolve, 650))
    return { horizons: horizonStats, annual: annualBacktest, totalSignals: 486, stocks: 172, source: 'DEMO / MOCK' }
  },
}

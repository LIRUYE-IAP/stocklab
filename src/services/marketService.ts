import { breadth, indices, sectors, sentiment } from '@/mock/market'

export const MarketService = {
  async getOverview() { return { indices, breadth, sectors, sentiment, source: 'DEMO / MOCK' } },
}

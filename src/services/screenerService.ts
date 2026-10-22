import { stocks } from '@/mock/stocks'
import type { ScreenerCondition, Stock } from '@/types'

const matches = (stock: Stock, condition: ScreenerCondition) => {
  const current = stock[condition.field] as number
  if (condition.operator === '>=') return current >= condition.value
  if (condition.operator === '<=') return current <= condition.value
  return current > condition.value
}

export const ScreenerService = {
  async run(conditions: ScreenerCondition[]) {
    return conditions.length ? stocks.filter((stock) => conditions.every((condition) => matches(stock, condition))) : stocks
  },
}

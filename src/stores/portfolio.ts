import { defineStore } from 'pinia'
import { ref } from 'vue'
import { positions, transactions } from '@/mock/portfolio'
import type { Transaction } from '@/types'

export const usePortfolioStore = defineStore('portfolio', () => {
  const currentPositions = ref(positions.map((item) => ({ ...item })))
  const history = ref(transactions.map((item) => ({ ...item })))
  function addTransaction(transaction: Omit<Transaction, 'id' | 'amount'>) {
    history.value.unshift({ ...transaction, id: Date.now(), amount: transaction.price * transaction.quantity })
  }
  return { currentPositions, history, addTransaction }
})

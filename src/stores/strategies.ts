import { defineStore } from 'pinia'
import { ref } from 'vue'
import { strategies } from '@/mock/strategies'

export const useStrategiesStore = defineStore('strategies', () => {
  const list = ref(strategies.map((item) => ({ ...item })))
  function copy(id: number) {
    const source = list.value.find((item) => item.id === id)
    if (source) list.value.push({ ...source, id: Date.now(), name: `${source.name} · 副本`, kind: '我的策略' })
  }
  function remove(id: number) {
    const index = list.value.findIndex((item) => item.id === id)
    if (index >= 0) list.value.splice(index, 1)
  }
  return { list, copy, remove }
})

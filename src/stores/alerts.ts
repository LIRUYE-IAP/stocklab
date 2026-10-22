import { defineStore } from 'pinia'
import { ref } from 'vue'
import { alertRules, notifications } from '@/mock/alerts'

export const useAlertsStore = defineStore('alerts', () => {
  const rules = ref(alertRules.map((rule) => ({ ...rule })))
  const notices = ref(notifications.map((notice) => ({ ...notice })))
  function toggle(id: number) {
    const rule = rules.value.find((item) => item.id === id)
    if (!rule) return
    rule.enabled = !rule.enabled
    rule.status = rule.enabled ? '启用' : '停用'
  }
  function add(rule: Omit<(typeof rules.value)[number], 'id'>) {
    rules.value.unshift({ ...rule, id: Date.now() })
  }
  function markAllRead() {
    notices.value.forEach((notice) => { notice.read = true })
  }
  return { rules, notices, toggle, add, markAllRead }
})

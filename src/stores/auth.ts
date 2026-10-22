import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<{ name: string; initials: string } | null>(
    sessionStorage.getItem('stocklab-demo-auth') ? { name: '演示用户', initials: 'DE' } : null,
  )
  const isAuthenticated = computed(() => Boolean(user.value))

  function login(account: string, password: string) {
    if ((account === 'demo' || account.includes('@')) && password.length >= 6) {
      user.value = { name: account === 'demo' ? '演示用户' : (account.split('@')[0] ?? account), initials: account.slice(0, 2).toUpperCase() }
      sessionStorage.setItem('stocklab-demo-auth', '1')
      return true
    }
    return false
  }

  function demoLogin() {
    user.value = { name: '演示用户', initials: 'DE' }
    sessionStorage.setItem('stocklab-demo-auth', '1')
  }

  function logout() {
    user.value = null
    sessionStorage.removeItem('stocklab-demo-auth')
  }

  return { user, isAuthenticated, login, demoLogin, logout }
})

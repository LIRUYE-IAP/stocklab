import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppLayout from '@/layouts/AppLayout.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: () => import('@/views/LoginView.vue'), meta: { public: true } },
    { path: '/register', component: () => import('@/views/RegisterView.vue'), meta: { public: true } },
    {
      path: '/',
      component: AppLayout,
      redirect: '/dashboard',
      children: [
        { path: 'dashboard', component: () => import('@/views/DashboardView.vue'), meta: { title: '首页' } },
        { path: 'market', component: () => import('@/views/MarketView.vue'), meta: { title: '市场' } },
        { path: 'screener', component: () => import('@/views/ScreenerView.vue'), meta: { title: '条件选股' } },
        { path: 'radar', component: () => import('@/views/RadarView.vue'), meta: { title: '异动雷达' } },
        { path: 'watchlist', component: () => import('@/views/WatchlistView.vue'), meta: { title: '自选' } },
        { path: 'portfolio', component: () => import('@/views/PortfolioView.vue'), meta: { title: '持仓' } },
        { path: 'strategies', component: () => import('@/views/StrategiesView.vue'), meta: { title: '策略' } },
        { path: 'quant', component: () => import('@/views/QuantLabView.vue'), meta: { title: '量化实验室' } },
        { path: 'alerts', component: () => import('@/views/AlertsView.vue'), meta: { title: '预警' } },
        { path: 'review', component: () => import('@/views/ReviewView.vue'), meta: { title: '交易复盘' } },
        { path: 'backtest', component: () => import('@/views/BacktestView.vue'), meta: { title: '策略回测' } },
        { path: 'settings', component: () => import('@/views/SettingsView.vue'), meta: { title: '设置' } },
        { path: 'stock/:symbol', component: () => import('@/views/StockDetailView.vue'), meta: { title: '个股研究' } },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isAuthenticated) return '/login'
  if (to.meta.public && auth.isAuthenticated) return '/dashboard'
  return true
})

export default router

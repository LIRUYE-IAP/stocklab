<script setup lang="ts">
import {
  Aim, Bell, CollectionTag, DataAnalysis, DataLine, Grid, House, Menu as MenuIcon,
  PieChart, Setting, Star, TrendCharts, Wallet, Cpu,
} from '@element-plus/icons-vue'

const items = [
  { label: '首页', path: '/dashboard', icon: House },
  { label: '市场', path: '/market', icon: DataLine },
  { label: '选股', path: '/screener', icon: Grid },
  { label: '异动雷达', path: '/radar', icon: Aim },
  { label: '自选', path: '/watchlist', icon: Star },
  { label: '持仓', path: '/portfolio', icon: Wallet },
  { label: '策略', path: '/strategies', icon: CollectionTag },
  { label: '量化实验室', path: '/quant', icon: Cpu },
  { label: '预警', path: '/alerts', icon: Bell },
  { label: '交易复盘', path: '/review', icon: PieChart },
  { label: '策略回测', path: '/backtest', icon: TrendCharts },
  { label: '设置', path: '/settings', icon: Setting },
]
</script>

<template>
  <aside class="sidebar">
    <div class="brand">
      <div class="brand-mark"><DataAnalysis /></div>
      <div><strong>StockLab</strong><span>研究工作台</span></div>
    </div>
    <nav class="sidebar-nav" aria-label="主导航">
      <RouterLink v-for="item in items" :key="item.path" :to="item.path" class="nav-item">
        <component :is="item.icon" /><span>{{ item.label }}</span>
      </RouterLink>
    </nav>
    <div class="sidebar-foot">
      <MenuIcon />
      <div><span>研究终端</span><small>Visual Prototype</small></div>
    </div>
  </aside>
</template>

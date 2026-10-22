<template>
  <div class="app-shell">
    <AppSidebar />
    <div class="app-main">
      <AppHeader />
      <main class="page-content"><RouterView /></main>
      <footer class="app-footer"><span>StockLab Market Workspace</span><span>{{ footerText }} · 研究辅助工具</span></footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import AppSidebar from '@/components/AppSidebar.vue'
import AppHeader from '@/components/AppHeader.vue'
import { computed } from 'vue'
import { useQuotesStore } from '@/stores/quotes'

const quotes = useQuotesStore()
const footerText = computed(() => quotes.provider?.activeSource === 'ifind' ? 'iFinD 行情' : quotes.provider?.activeSource === 'tushare' ? 'Tushare 数据' : '演示行情')
</script>

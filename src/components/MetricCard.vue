<script setup lang="ts">
defineProps<{ label: string; value: string | number; change?: string; tone?: 'positive' | 'negative' | 'neutral'; hint?: string }>()
</script>

<template>
  <div class="metric-card">
    <span class="metric-label">{{ label }}</span>
    <div class="metric-row"><strong>{{ value }}</strong><em v-if="change" :class="tone">{{ change }}</em></div>
    <small v-if="hint">{{ hint }}</small>
  </div>
</template>

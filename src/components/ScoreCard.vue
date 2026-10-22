<script setup lang="ts">
const props = defineProps<{ label: string; score: number; status: string; description: string; color?: string }>()
</script>

<template>
  <div class="score-card">
    <div class="score-top"><span>{{ label }}</span><span class="score-status">{{ status }}</span></div>
    <div class="score-main"><strong :style="{ color: color || '#5555c9' }">{{ score }}</strong><small>/ 100</small></div>
    <div class="score-track"><i :style="{ width: `${score}%`, background: color || '#5555c9' }" /></div>
    <p>{{ description }}</p>
  </div>
</template>

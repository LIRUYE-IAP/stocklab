<script setup lang="ts">
defineProps<{ value: number; minLabel?: string; maxLabel?: string }>()
</script>
<template>
  <div class="position-wrap">
    <div class="position-labels"><span>{{ minLabel || '一年最低' }}</span><strong>当前 {{ value }}%</strong><span>{{ maxLabel || '一年最高' }}</span></div>
    <div class="position-bar"><i :style="{ left: `${Math.min(98, Math.max(2, value))}%` }"><b /></i></div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ text?: string; tone?: 'positive' | 'negative' | 'warning' | 'neutral' | 'info' }>(), { tone: 'neutral', text: '状态稳定' })
</script>
<template><span class="signal-tag" :class="tone">{{ text }}</span></template>

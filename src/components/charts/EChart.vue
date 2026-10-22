<script setup lang="ts">
import * as echarts from 'echarts'
import { onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue'
import type { EChartsOption } from 'echarts'

const props = withDefaults(defineProps<{ option: EChartsOption; height?: string }>(), { height: '280px' })
const root = ref<HTMLDivElement>()
const chart = shallowRef<echarts.ECharts>()
let observer: ResizeObserver | undefined

onMounted(() => {
  if (!root.value) return
  chart.value = echarts.init(root.value, undefined, { renderer: 'canvas' })
  chart.value.setOption(props.option)
  observer = new ResizeObserver(() => chart.value?.resize())
  observer.observe(root.value)
})

watch(() => props.option, (option) => chart.value?.setOption(option, true), { deep: true })
onBeforeUnmount(() => { observer?.disconnect(); chart.value?.dispose() })
</script>

<template><div ref="root" class="echart" :style="{ height }" /></template>

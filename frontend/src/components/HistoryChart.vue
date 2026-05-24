<script setup>
import { computed } from 'vue'

const props = defineProps({ history: Array })

const chartData = computed(() => props.history.slice(0, 10).reverse())

function barColor(score) {
  if (score >= 80) return 'var(--success)'
  if (score >= 60) return 'var(--warning)'
  return 'var(--danger)'
}
</script>

<template>
  <div class="chart card">
    <h3>测验记录</h3>
    <div v-if="chartData.length === 0" class="empty">暂无测验记录</div>
    <div v-else class="bars">
      <div v-for="q in chartData" :key="q.id" class="bar-col">
        <div class="bar-value">{{ Math.round(q.score_percent) }}%</div>
        <div class="bar-track">
          <div
            class="bar-fill"
            :style="{ height: q.score_percent + '%', background: barColor(q.score_percent) }"
          />
        </div>
        <div class="bar-label">{{ q.quiz_type === 'choice' ? '选择' : q.quiz_type === 'fill' ? '填空' : '配对' }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chart { padding: 20px; }
h3 { margin-bottom: 16px; }
.empty { color: var(--text-secondary); font-size: 14px; }
.bars { display: flex; align-items: flex-end; gap: 12px; height: 160px; }
.bar-col { flex: 1; display: flex; flex-direction: column; align-items: center; }
.bar-value { font-size: 12px; color: var(--text-secondary); margin-bottom: 4px; }
.bar-track { flex: 1; width: 100%; background: var(--border); border-radius: 4px 4px 0 0; position: relative; }
.bar-fill { position: absolute; bottom: 0; width: 100%; border-radius: 4px 4px 0 0; transition: height 0.3s; }
.bar-label { font-size: 11px; color: var(--text-secondary); margin-top: 4px; }
</style>

<script setup>
import { computed } from 'vue'

const props = defineProps({ history: Array })

const chartData = computed(() => props.history.slice(0, 20).reverse())

const quizTotal = computed(() => props.history.length)
const quizAvg = computed(() => {
  if (!props.history.length) return 0
  const sum = props.history.reduce((s, q) => s + q.score_percent, 0)
  return Math.round(sum / props.history.length)
})

function typeLabel(type) {
  const map = { choice: '选择', fill: '填空', match: '配对', listening: '听音' }
  return map[type] || type || ''
}

function barColor(score) {
  if (score >= 80) return 'var(--success)'
  if (score >= 60) return 'var(--warning)'
  return 'var(--danger)'
}
</script>

<template>
  <div class="chart card">
    <h3>测验记录</h3>

    <div class="quiz-summary" v-if="quizTotal > 0">
      <div class="sum-item">
        <span class="sum-value">{{ quizTotal }}</span>
        <span class="sum-label">累计测验</span>
      </div>
      <div class="sum-item">
        <span class="sum-value" :class="quizAvg >= 80 ? 'high' : quizAvg >= 60 ? 'mid' : 'low'">{{ quizAvg }}%</span>
        <span class="sum-label">平均分</span>
      </div>
    </div>

    <div v-if="chartData.length === 0" class="empty">暂无测验记录</div>
    <div v-else class="bars-wrap">
      <div class="bars">
        <div v-for="q in chartData" :key="q.id" class="bar-col">
          <div class="bar-value">{{ Math.round(q.score_percent) }}%</div>
          <div class="bar-track">
            <div
              class="bar-fill"
              :style="{ height: Math.max(q.score_percent, 4) + '%', background: barColor(q.score_percent) }"
            />
          </div>
          <div class="bar-label">{{ typeLabel(q.quiz_type) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chart { padding: 20px; }
h3 { margin-bottom: 12px; }
.empty { color: var(--text-secondary); font-size: 14px; padding: 20px 0; text-align: center; }

.quiz-summary { display: flex; gap: 24px; margin-bottom: 16px; }
.sum-item { text-align: center; }
.sum-value { font-size: 22px; font-weight: 700; }
.sum-value.high { color: var(--success); }
.sum-value.mid { color: var(--warning); }
.sum-value.low { color: var(--danger); }
.sum-label { font-size: 12px; color: var(--text-secondary); display: block; }

.bars-wrap { overflow-x: auto; padding-bottom: 4px; }
.bars { display: flex; align-items: flex-end; gap: 10px; height: 150px; min-width: fit-content; }
.bar-col { flex: 0 0 36px; display: flex; flex-direction: column; align-items: center; min-width: 36px; }
.bar-value { font-size: 11px; color: var(--text-secondary); margin-bottom: 3px; }
.bar-track { width: 100%; flex: 1; background: rgba(255,255,255,0.04); border-radius: 4px 4px 0 0; position: relative; }
.bar-fill { position: absolute; bottom: 0; width: 100%; border-radius: 4px 4px 0 0; transition: height 0.3s; }
.bar-label { font-size: 11px; color: var(--text-secondary); margin-top: 4px; white-space: nowrap; }
</style>

<script setup>
import { computed } from 'vue'

const props = defineProps({ stats: Object, quizTotal: Number, quizAvg: Number })

const quizAvgClass = computed(() => {
  const v = props.quizAvg || 0
  if (v >= 80) return 'high'
  if (v >= 60) return 'mid'
  return 'low'
})
</script>

<template>
  <div class="stats-grid">
    <div class="stat-card card">
      <div class="stat-value">{{ stats.total_words || 0 }}</div>
      <div class="stat-label">已学单词</div>
    </div>
    <div class="stat-card card">
      <div class="stat-value new">{{ stats.new_count || 0 }}</div>
      <div class="stat-label">新词</div>
    </div>
    <div class="stat-card card">
      <div class="stat-value learning">{{ stats.learning_count || 0 }}</div>
      <div class="stat-label">学习中</div>
    </div>
    <div class="stat-card card">
      <div class="stat-value mastered">{{ stats.mastered_count || 0 }}</div>
      <div class="stat-label">已掌握</div>
    </div>
    <div class="stat-card card">
      <div class="stat-value">{{ quizTotal || 0 }}</div>
      <div class="stat-label">累计测验</div>
    </div>
    <div class="stat-card card">
      <div class="stat-value" :class="quizAvgClass">{{ quizAvg || 0 }}%</div>
      <div class="stat-label">平均分</div>
    </div>
  </div>
</template>

<style scoped>
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.stat-card { text-align: center; padding: 18px 12px; }
.stat-value { font-size: 26px; font-weight: 700; }
.stat-value.new { color: var(--text-secondary); }
.stat-value.learning { color: var(--warning); }
.stat-value.mastered { color: var(--success); }
.stat-value.high { color: var(--success); }
.stat-value.mid { color: var(--warning); }
.stat-value.low { color: var(--danger); }
.stat-label { font-size: 12px; color: var(--text-secondary); margin-top: 2px; }
@media (max-width: 480px) { .stats-grid { grid-template-columns: repeat(3, 1fr); } }
</style>

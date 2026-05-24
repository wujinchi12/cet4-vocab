<script setup>
defineProps({ stats: Object })
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
  </div>
</template>

<style scoped>
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.stat-card { text-align: center; padding: 20px; }
.stat-value { font-size: 28px; font-weight: 700; }
.stat-value.new { color: var(--text-secondary); }
.stat-value.learning { color: var(--warning); }
.stat-value.mastered { color: var(--success); }
.stat-label { font-size: 13px; color: var(--text-secondary); margin-top: 4px; }
@media (max-width: 480px) { .stats-grid { grid-template-columns: repeat(2, 1fr); } }
</style>

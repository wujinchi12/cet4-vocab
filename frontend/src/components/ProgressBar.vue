<script setup>
defineProps({ current: Number, total: Number })
</script>

<template>
  <div class="progress-bar">
    <div class="bar-track">
      <div class="bar-fill" :style="{ width: ((current / total) * 100) + '%' }" />
    </div>
    <span>{{ current }} / {{ total }}</span>
  </div>
</template>

<style scoped>
.progress-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 16px 0;
}
.bar-track {
  flex: 1;
  height: 6px;
  background: var(--border);
  border-radius: 3px;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  background: var(--primary);
  border-radius: 3px;
  transition: width 0.3s;
}
span { font-size: 14px; color: var(--text-secondary); min-width: 48px; text-align: right; }
</style>

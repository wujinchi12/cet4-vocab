<script setup>
defineProps({
  word: { type: Object, required: true }
})
</script>

<template>
  <div class="word-card">
    <div class="english">{{ word.english }}</div>
    <div class="chinese">{{ word.chinese }}</div>
  </div>
</template>

<style scoped>
.word-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  border-bottom: 1px solid var(--border);
  transition: background 0.1s;
}
.word-card:hover { background: rgba(255,255,255,0.06); }
.english { font-weight: 600; font-size: 16px; color: var(--primary); }
.chinese { font-size: 15px; color: var(--text-secondary); }
</style>

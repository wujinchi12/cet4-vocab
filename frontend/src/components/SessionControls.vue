<script setup>
defineEmits(['know', 'dontKnow', 'end'])
</script>

<template>
  <div class="controls">
    <button class="btn-danger" @click="$emit('dontKnow')">不认识</button>
    <button class="btn-outline" @click="$emit('end')">结束</button>
    <button class="btn-success" @click="$emit('know')">认识</button>
  </div>
</template>

<style scoped>
.controls {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
}
.controls button { min-width: 100px; padding: 12px 24px; font-size: 16px; }
</style>

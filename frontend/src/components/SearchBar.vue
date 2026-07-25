<script setup>
import { ref, watch } from 'vue'

const emit = defineEmits(['search'])
const query = ref('')

let timer = null
watch(query, (val) => {
  clearTimeout(timer)
  timer = setTimeout(() => emit('search', val), 300)
})
</script>

<template>
  <input
    v-model="query"
    placeholder="搜索单词或中文释义..."
    class="search-input"
  />
</template>

<style scoped>
.search-input {
  width: 100%;
  padding: 12px 16px;
  font-size: 16px;
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--text);
  outline: none;
  transition: border-color 0.2s, background 0.2s;
}
.search-input::placeholder { color: var(--text-secondary); }
.search-input:focus { border-color: var(--primary); background: rgba(255,255,255,0.06); }
</style>

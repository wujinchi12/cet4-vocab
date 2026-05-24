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
}
</style>

<script setup>
import { ref, onMounted } from 'vue'
import { getWords } from '../api'
import SearchBar from '../components/SearchBar.vue'
import WordCard from '../components/WordCard.vue'

const words = ref([])
const total = ref(0)
const page = ref(1)
const size = 25
const search = ref('')
const loading = ref(false)

async function loadWords() {
  loading.value = true
  try {
    const { data } = await getWords({ page: page.value, size, search: search.value })
    words.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

function onSearch(val) {
  search.value = val
  page.value = 1
  loadWords()
}

function nextPage() {
  if (page.value * size < total.value) {
    page.value++
    loadWords()
  }
}

function prevPage() {
  if (page.value > 1) {
    page.value--
    loadWords()
  }
}

onMounted(loadWords)
</script>

<template>
  <div>
    <h2>词汇表</h2>
    <SearchBar @search="onSearch" style="margin: 16px 0" />
    <div class="card word-list">
      <WordCard v-for="w in words" :key="w.id" :word="w" />
      <div v-if="loading" class="loading">加载中...</div>
    </div>
    <div class="pagination" v-if="total > size">
      <button class="btn-outline" @click="prevPage" :disabled="page <= 1">上一页</button>
      <span>{{ page }} / {{ Math.ceil(total / size) }}</span>
      <button class="btn-outline" @click="nextPage" :disabled="page * size >= total">下一页</button>
    </div>
  </div>
</template>

<style scoped>
h2 { margin-bottom: 8px; }
.word-list { padding: 0; overflow: hidden; }
.loading { text-align: center; padding: 20px; color: var(--text-secondary); }
.pagination { display: flex; align-items: center; justify-content: center; gap: 16px; margin-top: 20px; }
</style>

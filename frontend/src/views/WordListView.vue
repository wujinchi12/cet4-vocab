<script setup>
import { ref, onMounted, computed } from 'vue'
import { getWords } from '../api'
import SearchBar from '../components/SearchBar.vue'
import WordCard from '../components/WordCard.vue'

const words = ref([])
const total = ref(0)
const page = ref(1)
const size = 25
const search = ref('')
const loading = ref(false)

const totalPages = computed(() => Math.ceil(total.value / size))

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

function goPage(p) {
  page.value = p
  loadWords()
}

onMounted(loadWords)
</script>

<template>
  <div class="word-list-page">
    <header class="page-header">
      <h2>词汇表</h2>
      <span class="word-count" v-if="total > 0">共 {{ total }} 个单词</span>
    </header>

    <div class="search-card card">
      <SearchBar @search="onSearch" />
    </div>

    <div class="word-list card">
      <template v-if="loading">
        <div class="loading">加载中...</div>
      </template>
      <template v-else-if="words.length === 0">
        <div class="empty">没有找到匹配的单词</div>
      </template>
      <template v-else>
        <WordCard v-for="w in words" :key="w.id" :word="w" :show-speak="true" />
      </template>
    </div>

    <div class="pagination" v-if="totalPages > 1">
      <button class="btn-outline" :disabled="page <= 1" @click="goPage(1)">首页</button>
      <button class="btn-outline" :disabled="page <= 1" @click="goPage(page - 1)">上一页</button>
      <span class="page-info">{{ page }} / {{ totalPages }}</span>
      <button class="btn-outline" :disabled="page >= totalPages" @click="goPage(page + 1)">下一页</button>
      <button class="btn-outline" :disabled="page >= totalPages" @click="goPage(totalPages)">末页</button>
    </div>
  </div>
</template>

<style scoped>
.page-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 16px;
}
.page-header h2 { font-size: 1.5rem; }
.word-count { font-size: 0.9rem; color: var(--text-secondary); }

.search-card {
  margin-bottom: 16px;
  padding: 12px 16px;
}

.word-list {
  padding: 0;
  overflow: hidden;
}
.loading, .empty {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 20px;
}
.page-info {
  padding: 0 12px;
  font-size: 0.9rem;
  color: var(--text-secondary);
  min-width: 60px;
  text-align: center;
}
</style>

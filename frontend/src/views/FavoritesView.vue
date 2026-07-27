<script setup>
import { ref, onMounted, computed } from 'vue'
import { getFavorites, removeFavorite, clearFavorites } from '../api'
import WordCard from '../components/WordCard.vue'

const items = ref([])
const total = ref(0)
const page = ref(1)
const size = 20
const loading = ref(false)
const showConfirmClear = ref(false)

const totalPages = computed(() => Math.ceil(total.value / size))

async function fetchData() {
  loading.value = true
  try {
    const { data } = await getFavorites({ page: page.value, size })
    items.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

async function removeOne(wordId) {
  await removeFavorite(wordId)
  items.value = items.value.filter(it => it.word_id !== wordId)
  total.value--
}

async function clearAll() {
  await clearFavorites()
  items.value = []
  total.value = 0
  showConfirmClear.value = false
}

function goPage(p) {
  if (p < 1 || p > totalPages.value) return
  page.value = p
  fetchData()
}

onMounted(fetchData)
</script>

<template>
  <div class="favorites-page">
    <header class="page-header">
      <h2>收藏库</h2>
      <span class="fav-count" v-if="total > 0">共 {{ total }} 个单词</span>
    </header>

    <div class="toolbar" v-if="total > 0">
      <button class="btn-outline btn-danger-text" @click="showConfirmClear = true">清空收藏库</button>
    </div>

    <div class="confirm-overlay" v-if="showConfirmClear" @click.self="showConfirmClear = false">
      <div class="confirm-card card">
        <p>确定要清空所有收藏吗？此操作不可撤销。</p>
        <div class="confirm-btns">
          <button class="btn-outline" @click="showConfirmClear = false">取消</button>
          <button class="btn-danger" @click="clearAll">确认清空</button>
        </div>
      </div>
    </div>

    <div class="word-list card">
      <template v-if="loading">
        <div class="loading">加载中...</div>
      </template>
      <template v-else-if="items.length === 0">
        <div class="empty">
          <p>还没有收藏的单词</p>
          <router-link to="/words" class="btn-primary">浏览词汇表</router-link>
        </div>
      </template>
      <template v-else>
        <div v-for="item in items" :key="item.id" class="fav-row">
          <WordCard :word="item" :show-speak="true" :show-pos="true" />
          <button class="remove-btn" @click="removeOne(item.word_id)" title="取消收藏">&times;</button>
        </div>
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
  display: flex; align-items: baseline; justify-content: space-between;
  margin-bottom: 16px;
}
.page-header h2 { font-size: 1.5rem; }
.fav-count { font-size: 0.9rem; color: var(--text-secondary); }

.toolbar { margin-bottom: 12px; }
.btn-danger-text { color: #ef4444; border-color: rgba(239,68,68,0.3); }
.btn-danger-text:hover { background: rgba(239,68,68,0.1); }

.confirm-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5);
  display: flex; align-items: center; justify-content: center; z-index: 100;
}
.confirm-card { max-width: 360px; text-align: center; padding: 24px; }
.confirm-card p { margin-bottom: 20px; }
.confirm-btns { display: flex; gap: 12px; justify-content: center; }
.btn-danger {
  background: #ef4444; color: #fff; border: none; padding: 8px 20px;
  border-radius: var(--radius); cursor: pointer; font-size: 14px;
}

.word-list { padding: 0; overflow: hidden; }
.loading, .empty { text-align: center; padding: 40px 20px; color: var(--text-secondary); }
.empty p { margin-bottom: 16px; }

.fav-row { display: flex; align-items: center; }
.fav-row .word-card { flex: 1; }
.remove-btn {
  width: 32px; height: 32px; border: none; background: none;
  color: var(--text-secondary); font-size: 20px; cursor: pointer;
  flex-shrink: 0; margin-right: 8px; border-radius: 50%; transition: all 0.15s;
}
.remove-btn:hover { color: #ef4444; background: rgba(239,68,68,0.1); }

.pagination { display: flex; align-items: center; justify-content: center; gap: 8px; margin-top: 20px; }
.page-info { padding: 0 12px; font-size: 0.9rem; color: var(--text-secondary); min-width: 60px; text-align: center; }
</style>

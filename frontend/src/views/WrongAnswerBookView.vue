<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { getWrongAnswers, removeWrongAnswer, clearWrongAnswers } from '../api'
import WordCard from '../components/WordCard.vue'

const items = ref([])
const total = ref(0)
const page = ref(1)
const size = 20
const loading = ref(false)
const searchQuery = ref('')
const showConfirmClear = ref(false)

const totalPages = computed(() => Math.ceil(total.value / size) || 1)

let searchTimer = null
watch(searchQuery, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { page.value = 1; fetchData() }, 300)
})

async function fetchData() {
  loading.value = true
  try {
    const params = { page: page.value, size }
    if (searchQuery.value) params.search = searchQuery.value
    const { data } = await getWrongAnswers(params)
    items.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

async function removeOne(wordId) {
  await removeWrongAnswer(wordId)
  items.value = items.value.filter(it => it.word_id !== wordId)
  total.value--
}

async function clearAll() {
  await clearWrongAnswers()
  items.value = []
  total.value = 0
  showConfirmClear.value = false
}

function goPage(p) {
  if (p >= 1 && p <= totalPages.value) {
    page.value = p
    fetchData()
  }
}

onMounted(fetchData)
</script>

<template>
  <div class="wrong-book">
    <div class="header">
      <h2>错题本</h2>
      <span class="count" v-if="total">共 {{ total }} 道错题</span>
    </div>

    <input
      v-model="searchQuery"
      placeholder="搜索错题..."
      class="search-input"
    />

    <div class="toolbar" v-if="total > 0">
      <button class="btn-danger btn-sm" @click="showConfirmClear = true">清空错题本</button>
    </div>

    <div v-if="showConfirmClear" class="confirm-overlay">
      <div class="confirm-dialog card">
        <p>确定要清空所有错题吗？</p>
        <div class="confirm-actions">
          <button class="btn-outline" @click="showConfirmClear = false">取消</button>
          <button class="btn-danger" @click="clearAll">确定清空</button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else-if="items.length === 0" class="empty card">
      <p>还没有错题记录</p>
      <p class="hint">做测验时答错的题目可以加入错题本，方便复习</p>
    </div>

    <div v-else class="wrong-list">
      <div v-for="item in items" :key="item.id" class="wrong-item card">
        <div class="item-header">
          <WordCard :word="{ english: item.english, chinese: item.chinese }" :showSpeak="true" />
          <button class="btn-icon remove-btn" @click="removeOne(item.word_id)" title="已掌握，移除">&#10005;</button>
        </div>
        <div class="answer-info">
          <div class="wrong-answer">
            <span class="label">你的回答</span>
            <span class="value error">{{ item.user_answer || '(空)' }}</span>
          </div>
          <div class="correct-answer">
            <span class="label">正确答案</span>
            <span class="value success">{{ item.correct_answer }}</span>
          </div>
          <div class="meta">
            <span class="quiz-type">{{ item.quiz_type === 'choice' ? '选择题' : item.quiz_type === 'fill' ? '填空题' : item.quiz_type === 'match' ? '配对题' : item.quiz_type || '' }}</span>
            <span class="time">{{ new Date(item.created_at).toLocaleDateString() }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="pagination" v-if="totalPages > 1">
      <button :disabled="page <= 1" @click="goPage(page - 1)">上一页</button>
      <span>{{ page }} / {{ totalPages }}</span>
      <button :disabled="page >= totalPages" @click="goPage(page + 1)">下一页</button>
    </div>
  </div>
</template>

<style scoped>
.wrong-book { max-width: 700px; margin: 0 auto; }
.search-input {
  width: 100%; padding: 10px 14px; font-size: 14px;
  background: rgba(255,255,255,0.04); border: 1px solid var(--border);
  border-radius: var(--radius); color: var(--text); outline: none;
  transition: border-color 0.2s; margin-bottom: 12px; box-sizing: border-box;
}
.search-input::placeholder { color: var(--text-secondary); }
.search-input:focus { border-color: var(--primary); }
.header { display: flex; align-items: baseline; gap: 12px; margin-bottom: 16px; }
.header h2 { margin: 0; }
.count { color: var(--text-secondary); font-size: 14px; }
.toolbar { display: flex; justify-content: flex-end; margin: 12px 0; }
.empty { text-align: center; padding: 48px; }
.empty .hint { color: var(--text-secondary); font-size: 14px; margin-top: 8px; }
.loading { text-align: center; padding: 32px; color: var(--text-secondary); }

.wrong-item { margin-bottom: 12px; padding: 16px; }
.item-header { display: flex; align-items: flex-start; justify-content: space-between; }
.remove-btn {
  font-size: 16px; color: var(--text-secondary); cursor: pointer;
  background: none; border: none; padding: 4px 8px; border-radius: 4px;
  transition: color 0.2s, background 0.2s;
}
.remove-btn:hover { color: var(--danger); background: rgba(248,113,113,0.1); }

.answer-info { margin-top: 12px; display: flex; flex-wrap: wrap; gap: 16px; font-size: 14px; }
.label { color: var(--text-secondary); margin-right: 6px; }
.value { font-weight: 500; }
.value.error { color: var(--danger); }
.value.success { color: var(--success); }
.meta { display: flex; gap: 12px; color: var(--text-secondary); font-size: 12px; margin-left: auto; align-items: center; }

.pagination { display: flex; justify-content: center; align-items: center; gap: 16px; margin-top: 24px; }
.pagination button { padding: 6px 16px; }
.pagination button:disabled { opacity: 0.4; cursor: default; }

.confirm-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 100; }
.confirm-dialog { padding: 24px 32px; text-align: center; max-width: 360px; }
.confirm-dialog p { margin-bottom: 20px; font-size: 16px; }
.confirm-actions { display: flex; gap: 12px; justify-content: center; }
</style>

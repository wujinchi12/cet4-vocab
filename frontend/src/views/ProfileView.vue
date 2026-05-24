<script setup>
import { ref, onMounted } from 'vue'
import { getProgressSummary, getQuizHistory, getWeakestWords } from '../api'
import { useAuthStore } from '../stores/auth'
import StatsOverview from '../components/StatsOverview.vue'
import HistoryChart from '../components/HistoryChart.vue'
import WordCard from '../components/WordCard.vue'

const auth = useAuthStore()
const stats = ref({})
const history = ref([])
const weakest = ref([])

onMounted(async () => {
  const [s, h, w] = await Promise.all([
    getProgressSummary(),
    getQuizHistory(),
    getWeakestWords(10),
  ])
  stats.value = s.data
  history.value = h.data
  weakest.value = w.data.map(item => ({
    id: item.word_id,
    english: item.english,
    chinese: item.chinese
  }))
})
</script>

<template>
  <div>
    <h2>我的学习进度</h2>
    <p class="username">用户: {{ auth.user?.username }}</p>

    <StatsOverview :stats="stats" style="margin: 20px 0" />
    <HistoryChart :history="history" style="margin: 20px 0" />

    <div class="card weakest-section" v-if="weakest.length > 0">
      <h3>薄弱词汇</h3>
      <WordCard v-for="w in weakest" :key="w.id" :word="w" />
    </div>
  </div>
</template>

<style scoped>
h2 { margin-bottom: 4px; }
.username { color: var(--text-secondary); font-size: 14px; }
.weakest-section { margin-top: 20px; padding: 0; overflow: hidden; }
.weakest-section h3 { padding: 16px 20px 8px; }
</style>

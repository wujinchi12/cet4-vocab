<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { getProgressSummary, getQuizHistory, getWeakestWords } from '../api'
import { useAuthStore } from '../stores/auth'
import { useLevel } from '../composables/useLevel'
import StatsOverview from '../components/StatsOverview.vue'
import HistoryChart from '../components/HistoryChart.vue'
import WordCard from '../components/WordCard.vue'

const auth = useAuthStore()
const { level } = useLevel()
const stats = ref(null)
const history = ref(null)
const weakest = ref(null)
const error = ref('')

const quizTotal = computed(() => history.value?.length || 0)
const quizAvg = computed(() => {
  if (!history.value?.length) return 0
  const sum = history.value.reduce((s, q) => s + q.score_percent, 0)
  return Math.round(sum / history.value.length)
})

async function load() {
  try {
    const [s, h, w] = await Promise.all([
      getProgressSummary(),
      getQuizHistory(),
      getWeakestWords({ limit: 10, level: level.value }),
    ])
    stats.value = s.data
    history.value = h.data
    weakest.value = w.data.map(item => ({
      id: item.word_id,
      english: item.english,
      chinese: item.chinese
    }))
  } catch (e) {
    error.value = '加载失败，请刷新重试'
  }
}

onMounted(load)

watch(level, load)
</script>

<template>
  <div class="profile-page">
    <h2>我的学习进度</h2>
    <p class="username" v-if="auth.user?.username">用户: {{ auth.user.username }}</p>

    <div class="quick-links">
      <router-link to="/wrong-answers" class="quick-link card">
        <span class="quick-title">错题本</span>
        <span class="quick-desc">复习答错的题目</span>
      </router-link>
      <router-link to="/favorites" class="quick-link card">
        <span class="quick-title">收藏库</span>
        <span class="quick-desc">已收藏的单词</span>
      </router-link>
      <router-link to="/leaderboard" class="quick-link card">
        <span class="quick-title">排行榜</span>
        <span class="quick-desc">查看学习排行</span>
      </router-link>
    </div>

    <div v-if="error" class="error-msg">{{ error }}</div>

    <template v-else>
      <StatsOverview :stats="stats || {}" :quiz-total="quizTotal" :quiz-avg="quizAvg" style="margin: 20px 0" />

      <div v-if="history">
        <HistoryChart :history="history" style="margin: 20px 0" />
      </div>

      <div class="card weakest-section" v-if="weakest && weakest.length > 0">
        <h3>薄弱词汇</h3>
        <WordCard v-for="w in weakest" :key="w.id" :word="w" :showSpeak="true" />
      </div>
      <div class="card empty-card" v-else-if="weakest && weakest.length === 0">
        <p>暂无薄弱词汇</p>
        <p class="hint">多做测验和闪卡复习，系统会帮你追踪薄弱点</p>
      </div>
    </template>
  </div>
</template>

<style scoped>
.profile-page { max-width: 700px; margin: 0 auto; }
h2 { margin-bottom: 4px; }
.username { color: var(--text-secondary); font-size: 14px; margin-bottom: 8px; }
.quick-links {
  display: grid; grid-template-columns: 1fr 1fr; gap: 12px;
  margin: 12px 0 20px;
}
.quick-link {
  display: flex; flex-direction: column; gap: 4px;
  padding: 16px; text-decoration: none; color: var(--text);
  transition: border-color 0.15s, background 0.15s;
}
.quick-link:hover { border-color: var(--primary); background: rgba(99, 102, 241, 0.08); }
.quick-link:nth-child(3) { grid-column: 1 / -1; }
.quick-title { font-size: 15px; font-weight: 600; }
.quick-desc { font-size: 12px; color: var(--text-secondary); }
.error-msg { color: var(--danger); padding: 20px; text-align: center; }
.weakest-section { margin-top: 20px; padding: 0; overflow: hidden; }
.weakest-section h3 { padding: 16px 20px 8px; }
.empty-card { text-align: center; padding: 40px 20px; margin-top: 20px; }
.empty-card .hint { color: var(--text-secondary); font-size: 13px; margin-top: 6px; }
</style>

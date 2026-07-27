<script setup>
import { ref, reactive, computed, onBeforeUnmount, watch } from 'vue'
import { getExamPapers, getExamPaper, submitExam, getExamHistory } from '../api'
import ExamSection from '../components/ExamSection.vue'

const step = ref('select')
const papers = ref([])
const history = ref([])
const selectedPaper = ref(null)
const paperDetail = ref(null)
const answers = reactive({})
const timeSpent = ref(0)
const timeLimit = ref(120)
const submitted = ref(false)
const result = ref(null)
const loading = ref(false)

let timerInterval = null

const remainingSeconds = computed(() => Math.max(0, timeLimit.value * 60 - timeSpent.value))
const formattedTime = computed(() => {
  const m = Math.floor(remainingSeconds.value / 60)
  const s = remainingSeconds.value % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})
const timeWarning = computed(() => remainingSeconds.value < 300)

const unansweredCount = computed(() => {
  if (!paperDetail.value) return 0
  const gradable = paperDetail.value.questions.filter(q => q.question_type !== 'writing')
  return gradable.filter(q => !answers[q.id] || !answers[q.id].trim()).length
})

const sections = computed(() => {
  if (!paperDetail.value) return []
  const qs = paperDetail.value.questions
  const groups = []
  const order = ['vocab', 'cloze', 'reading', 'writing']
  const labels = {
    vocab: 'Section A: 词汇选择 (30题)',
    cloze: 'Section B: 完形填空 (10题)',
    reading: 'Section C: 阅读理解 (10题)',
    writing: 'Section D: 作文 (1题)',
  }
  for (const t of order) {
    const items = qs.filter(q => q.question_type === t)
    if (items.length > 0) {
      groups.push({ type: t, title: labels[t], questions: items })
    }
  }
  return groups
})

async function loadPapers() {
  try {
    const [pRes, hRes] = await Promise.all([
      getExamPapers(),
      getExamHistory().catch(() => ({ data: [] })),
    ])
    papers.value = pRes.data
    history.value = hRes.data
  } catch (e) {
    console.error('Failed to load exam data', e)
  }
}

async function selectPaper(paper) {
  loading.value = true
  try {
    const res = await getExamPaper(paper.id)
    paperDetail.value = res.data
    selectedPaper.value = paper
    timeLimit.value = paper.time_limit || 120
    timeSpent.value = 0
    submitted.value = false
    result.value = null
    // Clear answers
    for (const k of Object.keys(answers)) delete answers[k]
    step.value = 'exam'
    startTimer()
  } catch (e) {
    console.error('Failed to load paper', e)
  } finally {
    loading.value = false
  }
}

function startTimer() {
  clearInterval(timerInterval)
  timerInterval = setInterval(() => {
    timeSpent.value++
    if (timeSpent.value >= timeLimit.value * 60) {
      handleSubmit()
    }
  }, 1000)
}

function stopTimer() {
  clearInterval(timerInterval)
}

function updateAnswer({ question_id, answer }) {
  answers[question_id] = answer
}

async function handleSubmit() {
  if (submitted.value) return
  stopTimer()

  if (unansweredCount.value > 0 && timeSpent.value < timeLimit.value * 60) {
    if (!confirm(`还有 ${unansweredCount.value} 道题未作答，确定要提交吗？`)) {
      startTimer()
      return
    }
  }

  loading.value = true
  try {
    const answerList = []
    for (const q of paperDetail.value.questions) {
      if (q.question_type !== 'writing') {
        answerList.push({
          question_id: q.id,
          answer: answers[q.id] || '',
        })
      }
    }
    const res = await submitExam({
      paper_id: selectedPaper.value.id,
      answers: answerList,
      time_spent: timeSpent.value,
    })
    result.value = res.data
    submitted.value = true
    step.value = 'result'
  } catch (e) {
    console.error('Submit failed', e)
    alert('提交失败，请重试')
    startTimer()
  } finally {
    loading.value = false
  }
}

function backToSelect() {
  stopTimer()
  step.value = 'select'
  loadPapers()
}

onBeforeUnmount(() => stopTimer())
</script>

<template>
  <div class="exam-view">
    <h2>真题测试</h2>

    <!-- Step 1: Paper Selection -->
    <div v-if="step === 'select'">
      <p class="subtitle">选择一套真题试卷开始模拟测试</p>

      <div v-if="history.length > 0" class="history-card">
        <h4>最近记录</h4>
        <div class="history-list">
          <div v-for="h in history.slice(0, 5)" :key="h.id" class="history-row">
            <span class="h-title">{{ h.paper_title }}</span>
            <span class="h-score" :class="{ good: h.score >= 60, bad: h.score < 60 }">{{ h.score }}分</span>
            <span class="h-meta">{{ h.correct_count }}/{{ h.total_questions }} · {{ new Date(h.completed_at).toLocaleDateString() }}</span>
          </div>
        </div>
      </div>

      <div class="paper-grid">
        <div
          v-for="p in papers"
          :key="p.id"
          class="paper-card"
          @click="selectPaper(p)"
        >
          <div class="paper-year">{{ p.year }}</div>
          <div class="paper-title">{{ p.title }}</div>
          <div class="paper-meta">
            <span>{{ p.question_count }} 题</span>
            <span>{{ p.time_limit }} 分钟</span>
          </div>
          <div v-if="p.description" class="paper-desc">{{ p.description }}</div>
        </div>
      </div>

      <div v-if="papers.length === 0 && !loading" class="empty-state">
        暂无可用试卷
      </div>
    </div>

    <!-- Step 2: Taking the Exam -->
    <div v-else-if="step === 'exam' && paperDetail">
      <div class="exam-header">
        <div>
          <h3>{{ paperDetail.title }}</h3>
        </div>
        <div class="timer" :class="{ warning: timeWarning }">
          <span class="timer-icon">&#9202;</span>
          <span class="timer-text">{{ formattedTime }}</span>
        </div>
      </div>

      <div class="progress-bar">
        <div
          class="progress-fill"
          :style="{ width: (timeSpent / (timeLimit * 60) * 100) + '%' }"
        ></div>
      </div>

      <ExamSection
        v-for="sec in sections"
        :key="sec.type"
        :section-title="sec.title"
        :questions="sec.questions"
        :answers="answers"
        :submitted="submitted"
        @update:answer="updateAnswer"
      />

      <div class="submit-bar">
        <button class="btn-outline" @click="backToSelect">返回选择</button>
        <span class="unanswered" v-if="unansweredCount > 0">
          {{ unansweredCount }} 题未作答
        </span>
        <button class="btn-primary" :disabled="loading" @click="handleSubmit">
          {{ loading ? '提交中...' : '提交答案' }}
        </button>
      </div>
    </div>

    <!-- Step 3: Result -->
    <div v-else-if="step === 'result' && result">
      <div class="result-card">
        <div class="score-circle" :class="{ good: result.score_percent >= 60, bad: result.score_percent < 60 }">
          <div class="score-number">{{ Math.round(result.score_percent) }}</div>
          <div class="score-label">得分</div>
        </div>
        <div class="result-stats">
          <div class="stat">
            <span class="stat-num">{{ result.total_questions }}</span>
            <span class="stat-label">总题数</span>
          </div>
          <div class="stat correct-stat">
            <span class="stat-num">{{ result.correct_count }}</span>
            <span class="stat-label">正确</span>
          </div>
          <div class="stat wrong-stat">
            <span class="stat-num">{{ result.wrong_count }}</span>
            <span class="stat-label">错误</span>
          </div>
          <div class="stat">
            <span class="stat-num">{{ formattedTime }}</span>
            <span class="stat-label">用时</span>
          </div>
        </div>
      </div>

      <div class="result-actions">
        <button class="btn-outline" @click="backToSelect">返回列表</button>
        <button class="btn-primary" @click="selectPaper(selectedPaper)">重新做题</button>
      </div>

      <!-- Review per-question results -->
      <div class="review-section">
        <h4>答题回顾</h4>
        <div v-for="r in result.results" :key="r.question_id" class="review-item" :class="{ correct: r.is_correct, wrong: !r.is_correct }">
          <div class="review-q">
            <span class="review-status">{{ r.is_correct ? '✓' : '✗' }}</span>
            <span class="review-text">{{ r.question_text }}</span>
            <span class="review-type-badge">{{ r.question_type === 'vocab' ? '词汇' : r.question_type === 'cloze' ? '完形' : '阅读' }}</span>
          </div>
          <div class="review-answers">
            <span v-if="r.your_answer">你的答案: <strong :class="{ correct: r.is_correct, wrong: !r.is_correct }">{{ r.your_answer }}</strong></span>
            <span v-else class="no-answer">未作答</span>
            <span v-if="!r.is_correct"> | 正确答案: <strong class="correct-text">{{ r.correct_answer }}</strong></span>
          </div>
          <div v-if="r.english" class="review-word">
            相关单词: <strong>{{ r.english }}</strong> — {{ r.chinese }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.exam-view {
  max-width: 800px;
  margin: 0 auto;
}
h2 { margin-bottom: 8px; }

.subtitle {
  color: var(--text-secondary);
  margin-bottom: 24px;
}

/* History */
.history-card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
}
.history-card h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: var(--text-secondary);
}
.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.history-row {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 13px;
}
.h-title { flex: 1; font-weight: 500; }
.h-score { font-weight: 700; min-width: 45px; }
.h-score.good { color: #4caf50; }
.h-score.bad { color: #f44336; }
.h-meta { color: var(--text-secondary); }

/* Paper grid */
.paper-grid {
  display: grid;
  gap: 16px;
}
.paper-card {
  background: var(--card-bg);
  border: 2px solid var(--border);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: border-color 0.2s, transform 0.15s;
}
.paper-card:hover {
  border-color: var(--primary);
  transform: translateY(-2px);
}
.paper-year {
  font-size: 28px;
  font-weight: 800;
  color: var(--primary);
}
.paper-title {
  font-size: 16px;
  font-weight: 600;
  margin: 4px 0 8px;
}
.paper-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: var(--text-secondary);
}
.paper-desc {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 8px;
}

/* Exam header */
.exam-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  position: sticky;
  top: 56px;
  background: var(--bg);
  z-index: 10;
  padding: 8px 0;
}
.exam-header h3 { margin: 0; font-size: 16px; }
.timer {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 20px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  padding: 6px 14px;
  border-radius: 8px;
  background: var(--card-bg);
  border: 1px solid var(--border);
}
.timer.warning {
  color: #f44336;
  border-color: #f44336;
  animation: pulse 1s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.progress-bar {
  height: 4px;
  background: var(--border);
  border-radius: 2px;
  margin-bottom: 24px;
  position: sticky;
  top: 108px;
  z-index: 9;
}
.progress-fill {
  height: 100%;
  background: var(--primary);
  border-radius: 2px;
  transition: width 1s linear;
}

/* Submit bar */
.submit-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 0;
  border-top: 1px solid var(--border);
  margin-top: 24px;
}
.unanswered {
  font-size: 13px;
  color: #ff9800;
}

/* Result */
.result-card {
  display: flex;
  align-items: center;
  gap: 32px;
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 32px;
  margin-bottom: 24px;
}
.score-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 4px solid;
  flex-shrink: 0;
}
.score-circle.good { border-color: #4caf50; color: #4caf50; }
.score-circle.bad { border-color: #f44336; color: #f44336; }
.score-number { font-size: 36px; font-weight: 800; line-height: 1; }
.score-label { font-size: 14px; margin-top: 2px; }
.result-stats {
  display: flex;
  gap: 24px;
}
.stat {
  text-align: center;
}
.stat-num { display: block; font-size: 24px; font-weight: 700; }
.stat-label { font-size: 12px; color: var(--text-secondary); }
.correct-stat .stat-num { color: #4caf50; }
.wrong-stat .stat-num { color: #f44336; }

.result-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 32px;
}

/* Review */
.review-section {
  margin-top: 24px;
}
.review-section h4 {
  margin: 0 0 16px 0;
}
.review-item {
  padding: 10px 12px;
  margin-bottom: 6px;
  border-radius: 6px;
  border: 1px solid var(--border);
  font-size: 14px;
}
.review-item.correct { border-left: 4px solid #4caf50; }
.review-item.wrong { border-left: 4px solid #f44336; }
.review-q {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}
.review-status {
  font-weight: 700;
  font-size: 16px;
  flex-shrink: 0;
}
.review-item.correct .review-status { color: #4caf50; }
.review-item.wrong .review-status { color: #f44336; }
.review-text { flex: 1; }
.review-type-badge {
  font-size: 11px;
  background: var(--bg);
  padding: 1px 6px;
  border-radius: 3px;
  flex-shrink: 0;
}
.review-answers {
  margin-top: 6px;
  font-size: 13px;
  padding-left: 24px;
  color: var(--text-secondary);
}
.review-answers strong.correct { color: #4caf50; }
.review-answers strong.wrong { color: #f44336; }
.review-answers .correct-text { color: #4caf50; }
.review-answers .no-answer { color: #ff9800; font-style: italic; }
.review-word {
  margin-top: 4px;
  font-size: 12px;
  padding-left: 24px;
  color: var(--text-secondary);
}

.empty-state {
  text-align: center;
  padding: 48px;
  color: var(--text-secondary);
}
</style>

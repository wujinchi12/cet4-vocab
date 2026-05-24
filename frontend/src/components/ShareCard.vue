<script setup>
import { ref, computed } from 'vue'
import html2canvas from 'html2canvas'

const props = defineProps({
  result: { type: Object, required: true },
  quizTypeName: { type: String, default: '' },
})

const cardRef = ref(null)
const loading = ref(false)

const score = computed(() => Math.round(props.result.score_percent))
const grade = computed(() => {
  if (score.value >= 90) return '优秀'
  if (score.value >= 80) return '良好'
  if (score.value >= 60) return '及格'
  return '加油'
})

const today = computed(() => {
  const d = new Date()
  return `${d.getFullYear()}/${d.getMonth() + 1}/${d.getDate()}`
})

async function downloadImage() {
  if (!cardRef.value) return
  loading.value = true
  const canvas = await html2canvas(cardRef.value, {
    scale: 2,
    backgroundColor: '#ffffff',
  })
  const link = document.createElement('a')
  link.download = `CET4-quiz-${score.value}.png`
  link.href = canvas.toDataURL('image/png')
  link.click()
  loading.value = false
}

defineExpose({ downloadImage })
</script>

<template>
  <div class="share-card-wrapper">
    <!-- Hidden card rendered for screenshot -->
    <div ref="cardRef" class="share-card">
      <div class="card-bg">
        <div class="card-header">
          <span class="logo-text">CET-4 词汇学习</span>
          <span class="author">吴瑾赤</span>
        </div>

        <div class="score-section">
          <div class="score-circle" :class="grade === '优秀' ? 'great' : grade === '良好' ? 'good' : 'normal'">
            <span class="score-num">{{ score }}</span>
            <span class="score-unit">分</span>
          </div>
          <div class="grade-text">{{ grade }}</div>
        </div>

        <div class="stats-row">
          <div class="stat-item">
            <span class="stat-num">{{ result.total_questions }}</span>
            <span class="stat-label">总题数</span>
          </div>
          <div class="stat-item">
            <span class="stat-num correct">{{ result.correct_count }}</span>
            <span class="stat-label">正确</span>
          </div>
          <div class="stat-item">
            <span class="stat-num wrong">{{ result.wrong_count }}</span>
            <span class="stat-label">错误</span>
          </div>
        </div>

        <div class="card-footer">
          <span>{{ quizTypeName }} &middot; {{ today }}</span>
        </div>
      </div>
    </div>

    <!-- Visible download button -->
    <button class="btn-primary share-btn" @click="downloadImage" :disabled="loading">
      {{ loading ? '生成中...' : '分享成绩' }}
    </button>
  </div>
</template>

<style scoped>
.share-card-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.share-card {
  position: fixed;
  left: -9999px;
  top: 0;
  width: 375px;
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.card-bg {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 32px 24px;
  color: white;
  text-align: center;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.logo-text {
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 1px;
}

.author {
  font-size: 13px;
  opacity: 0.8;
}

.score-section {
  margin: 16px 0 24px;
}

.score-circle {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 3px solid rgba(255,255,255,0.5);
  margin-bottom: 8px;
}

.score-num {
  font-size: 40px;
  font-weight: 800;
  line-height: 1;
}

.score-unit {
  font-size: 14px;
  opacity: 0.8;
}

.grade-text {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 4px;
}

.stats-row {
  display: flex;
  justify-content: center;
  gap: 32px;
  margin: 24px 0;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-num {
  font-size: 24px;
  font-weight: 700;
}

.stat-num.correct { color: #a7f3d0; }
.stat-num.wrong { color: #fecaca; }

.stat-label {
  font-size: 12px;
  opacity: 0.7;
  margin-top: 2px;
}

.card-footer {
  font-size: 12px;
  opacity: 0.6;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(255,255,255,0.2);
}

.share-btn {
  font-size: 16px;
  padding: 12px 36px;
}
</style>

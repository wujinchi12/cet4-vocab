<script setup>
import { ref, computed } from 'vue'
import { addWrongAnswers } from '../api'
import ShareCard from './ShareCard.vue'

const props = defineProps({
  result: Object,
  quizType: { type: String, default: '' },
  quizTypeName: { type: String, default: '' },
})
defineEmits(['retry', 'newQuiz'])

const addedToBook = ref(false)
const adding = ref(false)

const wrongWords = computed(() =>
  props.result.results.filter(r => !r.is_correct)
)

async function addToBook() {
  if (wrongWords.value.length === 0) return
  adding.value = true
  try {
    const words = wrongWords.value.map(r => ({
      word_id: r.word_id,
      user_answer: r.user_answer,
      correct_answer: r.correct_answer,
      quiz_type: props.quizType,
    }))
    await addWrongAnswers({ words })
    addedToBook.value = true
  } finally {
    adding.value = false
  }
}
</script>

<template>
  <div class="quiz-result card">
    <h2>测验完成!</h2>
    <div class="score-circle" :class="result.score_percent >= 60 ? 'pass' : 'fail'">
      {{ Math.round(result.score_percent) }}%
    </div>
    <div class="stats">
      <span>正确: {{ result.correct_count }}</span>
      <span>错误: {{ result.wrong_count }}</span>
    </div>

    <div class="answers-review" v-if="wrongWords.length > 0">
      <div class="review-header">
        <h3>答案回顾</h3>
        <button
          class="btn-add-book"
          :disabled="addedToBook || adding"
          @click="addToBook"
        >
          {{ addedToBook ? '已加入错题本' : adding ? '添加中...' : '加入错题本' }}
        </button>
      </div>
      <div
        v-for="r in result.results"
        :key="r.word_id"
        class="answer-row"
        :class="{ correct: r.is_correct, wrong: !r.is_correct }"
      >
        <span class="word">{{ r.english }}</span>
        <span class="your-answer">{{ r.user_answer }}</span>
        <span class="correct-answer" v-if="!r.is_correct">{{ r.correct_answer }}</span>
        <span class="icon">{{ r.is_correct ? '✓' : '✗' }}</span>
      </div>
    </div>

    <div class="answers-review" v-else>
      <h3>全部正确!</h3>
    </div>

    <div class="result-actions">
      <button class="btn-outline" @click="$emit('retry')">再做一次</button>
      <button class="btn-primary" @click="$emit('newQuiz')">换题型</button>
    </div>

    <ShareCard :result="result" :quiz-type-name="quizTypeName" />
  </div>
</template>

<style scoped>
.quiz-result { text-align: center; padding: 32px; }
h2 { margin-bottom: 16px; }
.score-circle {
  width: 100px; height: 100px; margin: 0 auto 12px;
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-size: 28px; font-weight: 700; color: white;
}
.score-circle.pass { background: var(--success); }
.score-circle.fail { background: var(--danger); }
.stats { display: flex; justify-content: center; gap: 24px; margin-bottom: 24px; color: var(--text-secondary); }
.answers-review { text-align: left; margin: 20px 0; }
.answers-review h3 { margin-bottom: 12px; }
.review-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.review-header h3 { margin: 0; }
.btn-add-book {
  padding: 6px 14px; font-size: 13px; border-radius: 6px;
  background: var(--primary); color: white; border: none; cursor: pointer;
  white-space: nowrap; transition: opacity 0.2s;
}
.btn-add-book:disabled { opacity: 0.6; cursor: default; }
.btn-add-book:not(:disabled):hover { opacity: 0.85; }
.answer-row {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 14px; border-radius: 6px; margin-bottom: 6px; font-size: 14px;
}
.answer-row.correct { background: rgba(52,211,153,0.12); }
.answer-row.wrong { background: rgba(248,113,113,0.12); }
.word { font-weight: 600; min-width: 100px; }
.your-answer { color: var(--text-secondary); }
.correct-answer { color: var(--success); font-weight: 500; }
.icon { margin-left: auto; font-weight: 700; }
.correct .icon { color: var(--success); }
.wrong .icon { color: var(--danger); }
.result-actions { display: flex; gap: 12px; justify-content: center; margin-top: 20px; }
</style>

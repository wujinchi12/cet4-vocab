<script setup>
import { computed } from 'vue'

const props = defineProps({
  sectionTitle: String,
  questions: Array,
  answers: Object,
  submitted: Boolean,
})

const emit = defineEmits(['update:answer'])

const sectionType = computed(() => props.questions[0]?.question_type || 'vocab')
const sharedPassage = computed(() => props.questions[0]?.passage || '')

function onSelect(qId, value) {
  emit('update:answer', { question_id: qId, answer: value })
}

function onWritingInput(qId, value) {
  emit('update:answer', { question_id: qId, answer: value })
}

const typeLabels = { vocab: '词汇选择', cloze: '完形填空', reading: '阅读理解', writing: '作文' }

function isCorrect(q) {
  if (!props.submitted) return null
  return (props.answers[q.id] || '').trim().toLowerCase() === (q.correct_answer || '').trim().toLowerCase()
}

function wordCount(text) {
  if (!text) return 0
  return text.trim().split(/\s+/).filter(Boolean).length
}

function getOptionLabel(index) {
  return String.fromCharCode(65 + index)
}
</script>

<template>
  <div class="exam-section">
    <div class="section-header">
      <h3>{{ sectionTitle }}</h3>
      <span class="section-type-badge">{{ typeLabels[sectionType] || sectionType }}</span>
    </div>

    <!-- Shared passage for cloze / reading -->
    <div v-if="(sectionType === 'cloze' || sectionType === 'reading') && sharedPassage" class="passage-box">
      <p class="passage-text">{{ sharedPassage }}</p>
    </div>

    <!-- Writing -->
    <div v-if="sectionType === 'writing'" class="writing-area">
      <div class="writing-prompt">
        <pre class="prompt-text">{{ questions[0]?.question_text }}</pre>
      </div>
      <textarea
        class="writing-textarea"
        :value="answers[questions[0]?.id] || ''"
        :disabled="submitted"
        placeholder="在此输入你的作文..."
        @input="onWritingInput(questions[0]?.id, $event.target.value)"
      ></textarea>
      <div class="word-count">
        字数: {{ wordCount(answers[questions[0]?.id] || '') }}
        <span v-if="questions[0]?.options?.[3]"> / 建议 {{ questions[0].options[3] }} 词</span>
      </div>
    </div>

    <!-- Questions list -->
    <div
      v-for="(q, qi) in questions"
      :key="q.id"
      class="question-item"
      :class="{ correct: isCorrect(q) === true, incorrect: isCorrect(q) === false }"
    >
      <!-- Vocab: show question text with options -->
      <div v-if="sectionType === 'vocab'" class="q-body">
        <p class="q-text">{{ qi + 1 }}. {{ q.question_text }}</p>
        <div class="options-grid">
          <label
            v-for="(opt, oi) in q.options"
            :key="oi"
            class="option-label"
            :class="{
              selected: answers[q.id] === opt,
              'correct-answer': submitted && opt === q.correct_answer,
              'wrong-answer': submitted && answers[q.id] === opt && opt !== q.correct_answer,
            }"
          >
            <input
              type="radio"
              :name="'q-' + q.id"
              :value="opt"
              :checked="answers[q.id] === opt"
              :disabled="submitted"
              @change="onSelect(q.id, opt)"
            />
            <span>{{ getOptionLabel(oi) }}. {{ opt }}</span>
          </label>
        </div>
      </div>

      <!-- Cloze / Reading: each question with its own options -->
      <div v-if="sectionType === 'cloze' || sectionType === 'reading'" class="q-body">
        <p class="q-text">{{ qi + 1 }}. {{ q.question_text }}</p>
        <div class="options-grid">
          <label
            v-for="(opt, oi) in q.options"
            :key="oi"
            class="option-label"
            :class="{
              selected: answers[q.id] === opt,
              'correct-answer': submitted && opt === q.correct_answer,
              'wrong-answer': submitted && answers[q.id] === opt && opt !== q.correct_answer,
            }"
          >
            <input
              type="radio"
              :name="'q-' + q.id"
              :value="opt"
              :checked="answers[q.id] === opt"
              :disabled="submitted"
              @change="onSelect(q.id, opt)"
            />
            <span>{{ getOptionLabel(oi) }}. {{ opt }}</span>
          </label>
        </div>
      </div>

      <!-- Show correct answer after submission -->
      <div v-if="submitted && sectionType !== 'writing'" class="feedback">
        <span v-if="isCorrect(q)" class="feedback-correct">正确</span>
        <span v-else class="feedback-wrong">
          错误 — 正确答案: <strong>{{ q.correct_answer }}</strong>
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.exam-section {
  margin-bottom: 32px;
}
.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--primary);
}
.section-header h3 {
  margin: 0;
  font-size: 18px;
}
.section-type-badge {
  font-size: 12px;
  background: var(--primary);
  color: #fff;
  padding: 2px 8px;
  border-radius: 4px;
}

.passage-box {
  background: var(--bg, #f8f9fa);
  border-left: 4px solid var(--primary);
  padding: 16px;
  margin-bottom: 20px;
  border-radius: 4px;
}
.passage-text {
  white-space: pre-wrap;
  line-height: 1.8;
  margin: 0;
  font-size: 15px;
}

.question-item {
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 8px;
  border: 1px solid var(--border);
  transition: background 0.2s;
}
.question-item.correct {
  background: #e8f5e9;
  border-color: #4caf50;
}
.question-item.incorrect {
  background: #ffebee;
  border-color: #f44336;
}
.q-body { }
.q-text {
  font-weight: 500;
  margin: 0 0 8px 0;
  line-height: 1.6;
}

.options-grid {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.option-label {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  border: 1px solid transparent;
  transition: background 0.15s;
}
.option-label:hover:not(.correct-answer):not(.wrong-answer) {
  background: var(--bg, #f5f5f5);
}
.option-label.selected {
  background: #e3f2fd;
  border-color: var(--primary);
}
.option-label.correct-answer {
  background: #c8e6c9;
  border-color: #4caf50;
}
.option-label.wrong-answer {
  background: #ffcdd2;
  border-color: #f44336;
}
.option-label input {
  margin: 0;
}

.feedback {
  margin-top: 8px;
  font-size: 13px;
}
.feedback-correct {
  color: #4caf50;
  font-weight: 600;
}
.feedback-wrong {
  color: #f44336;
}

.writing-area {
  margin-bottom: 20px;
}
.writing-prompt {
  background: var(--bg, #f8f9fa);
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 12px;
}
.prompt-text {
  white-space: pre-wrap;
  margin: 0;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.8;
}
.writing-textarea {
  width: 100%;
  min-height: 300px;
  padding: 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.8;
  resize: vertical;
  font-family: inherit;
}
.writing-textarea:disabled {
  background: #f5f5f5;
}
.word-count {
  text-align: right;
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 4px;
}
</style>

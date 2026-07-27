<script setup>
import { ref, onMounted } from 'vue'
import { getWrongAnswerCount } from '../api'

const emit = defineEmits(['start'])

const quizType = ref('choice')
const count = ref(10)
const direction = ref('en_to_cn')
const source = ref('all')
const wrongCount = ref(0)

onMounted(async () => {
  try {
    const { data } = await getWrongAnswerCount()
    wrongCount.value = data.count
  } catch { /* ignore */ }
})

function start() {
  emit('start', {
    type: quizType.value,
    count: count.value,
    direction: direction.value,
    source: source.value,
  })
}
</script>

<template>
  <div class="setup card">
    <h3>开始测验</h3>

    <div class="field">
      <label>题目来源</label>
      <select v-model="source">
        <option value="all">全部词汇</option>
        <option value="wrong" :disabled="wrongCount === 0">
          错题复习 {{ wrongCount > 0 ? `(${wrongCount} 题)` : '(暂无错题)' }}
        </option>
      </select>
    </div>

    <div class="field">
      <label>题型</label>
      <select v-model="quizType">
        <option value="choice">选择题</option>
        <option value="fill">填空题</option>
        <option value="match">配对题</option>
        <option value="listening">听音辨义</option>
      </select>
    </div>

    <div class="field">
      <label>题目数量</label>
      <select v-model.number="count">
        <option :value="10">10 题</option>
        <option :value="20">20 题</option>
        <option :value="50">50 题</option>
      </select>
    </div>

    <div class="field">
      <label>出题方向</label>
      <select v-model="direction">
        <option value="en_to_cn">看英文选中文</option>
        <option value="cn_to_en">看中文选英文</option>
      </select>
    </div>

    <button class="btn-primary start-btn" @click="start">开始答题</button>
  </div>
</template>

<style scoped>
.setup { max-width: 400px; margin: 0 auto; }
h3 { margin-bottom: 20px; }
.field { margin-bottom: 16px; }
.field label { display: block; margin-bottom: 6px; font-size: 14px; color: var(--text-secondary); }
.field select { width: 100%; }
.start-btn { width: 100%; margin-top: 8px; }
</style>

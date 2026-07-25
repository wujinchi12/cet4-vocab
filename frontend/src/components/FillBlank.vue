<script setup>
import { ref } from 'vue'

const props = defineProps({ question: Object, index: Number, total: Number })
const emit = defineEmits(['answer'])

const answer = ref('')

function submit() {
  if (!answer.value.trim()) return
  emit('answer', { word_id: props.question.word_id, answer: answer.value.trim() })
  answer.value = ''
}
</script>

<template>
  <div class="fill-question">
    <div class="q-header">{{ index + 1 }} / {{ total }}</div>
    <h3 class="q-text">{{ question.question }}</h3>
    <form @submit.prevent="submit" class="fill-form">
      <input v-model="answer" placeholder="输入你的答案..." class="fill-input" />
      <button class="btn-primary" type="submit">确认</button>
    </form>
  </div>
</template>

<style scoped>
.q-header { font-size: 13px; color: var(--text-secondary); margin-bottom: 8px; }
.q-text { font-size: 20px; margin-bottom: 24px; text-align: center; }
.fill-form { display: flex; gap: 12px; max-width: 400px; margin: 0 auto; }
.fill-input { flex: 1; }
</style>

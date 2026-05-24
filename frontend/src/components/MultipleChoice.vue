<script setup>
import { ref } from 'vue'

const props = defineProps({ question: Object, index: Number, total: Number })
const emit = defineEmits(['answer'])

const selected = ref(null)

function choose(option) {
  if (selected.value) return
  selected.value = option
  setTimeout(() => {
    emit('answer', { word_id: props.question.word_id, answer: option, correct_answer: '' })
    selected.value = null
  }, 300)
}

function optionClass(opt) {
  if (!selected.value) return ''
  return opt === selected.value ? 'selected' : ''
}
</script>

<template>
  <div class="choice-question">
    <div class="q-header">{{ index + 1 }} / {{ total }}</div>
    <h3 class="q-text">{{ question.question }}</h3>
    <div class="options-grid">
      <button
        v-for="(opt, i) in question.options"
        :key="i"
        class="option-btn"
        :class="optionClass(opt)"
        @click="choose(opt)"
      >{{ opt }}</button>
    </div>
  </div>
</template>

<style scoped>
.q-header { font-size: 13px; color: var(--text-secondary); margin-bottom: 8px; }
.q-text { font-size: 20px; margin-bottom: 24px; text-align: center; }
.options-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.option-btn {
  padding: 16px;
  font-size: 16px;
  background: var(--card-bg);
  border: 2px solid var(--border);
  border-radius: var(--radius);
  text-align: center;
}
.option-btn:hover { border-color: var(--primary); }
.option-btn.selected { border-color: var(--primary); background: #eef2ff; }
@media (max-width: 480px) { .options-grid { grid-template-columns: 1fr; } }
</style>

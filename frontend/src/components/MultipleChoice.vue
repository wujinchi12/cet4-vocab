<script setup>
import { ref } from 'vue'

const props = defineProps({ question: Object, index: Number, total: Number })
const emit = defineEmits(['answer'])

const selected = ref(null)

function choose(option) {
  if (selected.value) return
  selected.value = option
  setTimeout(() => {
    emit('answer', { word_id: props.question.word_id, answer: option })
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
  font-weight: 600;
  color: var(--text);
  background: var(--card-bg);
  border: 2px solid var(--border);
  border-radius: var(--radius);
  text-align: center;
  transition: all 0.2s;
}
.option-btn:nth-child(4n+1):hover { border-color: #f87171; background: rgba(248,113,113,0.15); box-shadow: 0 0 16px rgba(248,113,113,0.2); }
.option-btn:nth-child(4n+2):hover { border-color: #60a5fa; background: rgba(96,165,250,0.15); box-shadow: 0 0 16px rgba(96,165,250,0.2); }
.option-btn:nth-child(4n+3):hover { border-color: #34d399; background: rgba(52,211,153,0.15); box-shadow: 0 0 16px rgba(52,211,153,0.2); }
.option-btn:nth-child(4n+0):hover { border-color: #fbbf24; background: rgba(251,191,36,0.15); box-shadow: 0 0 16px rgba(251,191,36,0.2); }
.option-btn.selected { border-color: var(--primary); background: rgba(99,102,241,0.25); box-shadow: 0 0 18px rgba(99,102,241,0.3); }
@media (max-width: 480px) { .options-grid { grid-template-columns: 1fr; } }
</style>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSpeech } from '../composables/useSpeech'

const props = defineProps({ question: Object, index: Number, total: Number })
const emit = defineEmits(['answer'])

const { speak, speaking } = useSpeech()
const answer = ref('')
const playCount = ref(0)

const englishWord = computed(() => {
  const match = props.question?.question?.match(/'([^']+)'/)
  return match ? match[1] : ''
})

function playAudio() {
  if (englishWord.value) speak(englishWord.value)
}

function submit() {
  if (!answer.value.trim()) return
  emit('answer', { word_id: props.question.word_id, answer: answer.value.trim() })
  answer.value = ''
  playCount.value = 0
}

onMounted(() => { playAudio() })
</script>

<template>
  <div class="listening-practice">
    <div class="q-header">{{ index + 1 }} / {{ total }}</div>
    <div class="audio-section">
      <button
        class="speak-btn large"
        :class="{ playing: speaking }"
        @click="playAudio"
        title="点击播放"
      >&#9654;</button>
      <p class="hint-text">听发音，写出对应的中文意思</p>
    </div>
    <form @submit.prevent="submit" class="fill-form">
      <input v-model="answer" placeholder="输入中文意思..." class="fill-input" />
      <button class="btn-primary" type="submit">确认</button>
    </form>
  </div>
</template>

<style scoped>
.listening-practice { text-align: center; }
.q-header { font-size: 13px; color: var(--text-secondary); margin-bottom: 16px; }
.audio-section { margin-bottom: 24px; }
.speak-btn.large {
  width: 64px; height: 64px; border-radius: 50%;
  border: 2px solid var(--border); background: rgba(255,255,255,0.06);
  color: var(--primary-light); font-size: 24px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 12px; padding: 0; transition: all 0.15s;
}
.speak-btn.large:hover { border-color: var(--primary); background: rgba(99,102,241,0.15); }
.speak-btn.large.playing { border-color: var(--primary); background: rgba(99,102,241,0.2); animation: pulse 1s infinite; }
@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(99,102,241,0.3); }
  50% { box-shadow: 0 0 0 12px rgba(99,102,241,0); }
}
.hint-text { font-size: 14px; color: var(--text-secondary); }
.fill-form { display: flex; gap: 12px; max-width: 400px; margin: 0 auto; }
.fill-input { flex: 1; }
</style>

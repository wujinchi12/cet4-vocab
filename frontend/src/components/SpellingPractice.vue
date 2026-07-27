<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSpeech } from '../composables/useSpeech'

const props = defineProps({
  question: { type: Object, required: true },
  index: { type: Number, required: true },
  total: { type: Number, required: true },
})

const emit = defineEmits(['answer'])
const { speak, speaking, supported } = useSpeech()

const answer = ref('')
const submitted = ref(false)

const chineseMeaning = computed(() => {
  const match = props.question?.question?.match(/写出\s*'([^']+)'\s*对应的英文单词/)
  return match ? match[1] : ''
})

function playAudio() {
  if (chineseMeaning.value) speak(chineseMeaning.value, 'zh-CN')
}

function submit() {
  if (!answer.value.trim() || submitted.value) return
  submitted.value = true
  emit('answer', { word_id: props.question.word_id, answer: answer.value.trim() })
}

onMounted(() => {
  setTimeout(() => playAudio(), 300)
})
</script>

<template>
  <div class="spelling-practice card">
    <div class="progress-bar">
      <div class="progress-fill" :style="{ width: ((index + 1) / total * 100) + '%' }"></div>
    </div>

    <div class="q-header">{{ index + 1 }} / {{ total }}</div>

    <div class="chinese-prompt">
      <span class="label">请拼写该单词</span>
      <span class="chinese-word">{{ chineseMeaning || question.question }}</span>
      <button
        class="speak-btn"
        :class="{ playing: speaking }"
        @click="playAudio"
        :title="speaking ? '播放中...' : '听发音'"
        :disabled="!supported"
      >{{ speaking ? '🔊' : '🔈' }}</button>
    </div>

    <form @submit.prevent="submit" class="spell-form">
      <input
        v-model="answer"
        placeholder="输入英文拼写..."
        class="spell-input"
        autofocus
        :disabled="submitted"
      />
      <button class="btn-primary" type="submit" :disabled="!answer.trim() || submitted">确认</button>
    </form>

    <p v-if="!supported" class="tts-warning">您的浏览器不支持语音合成</p>
  </div>
</template>

<style scoped>
.spelling-practice { max-width: 460px; margin: 0 auto; padding: 24px; text-align: center; }

.progress-bar {
  height: 4px; background: var(--border); border-radius: 2px;
  margin-bottom: 20px; overflow: hidden;
}
.progress-fill { height: 100%; background: var(--primary); transition: width 0.3s; border-radius: 2px; }

.q-header { font-size: 14px; color: var(--text-secondary); margin-bottom: 24px; }

.chinese-prompt { margin-bottom: 32px; }
.label { display: block; font-size: 14px; color: var(--text-secondary); margin-bottom: 8px; }
.chinese-word { font-size: 36px; font-weight: 700; color: var(--text); }
.speak-btn {
  display: block; margin: 12px auto 0; width: 44px; height: 44px; border-radius: 50%;
  border: 1px solid var(--border); background: rgba(255,255,255,0.04);
  font-size: 20px; cursor: pointer; transition: all 0.15s;
}
.speak-btn:hover:not(:disabled) { border-color: var(--primary); background: rgba(99,102,241,0.1); }
.speak-btn.playing { border-color: var(--primary); background: rgba(99,102,241,0.15); }
.speak-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.spell-form { display: flex; gap: 12px; }
.spell-input {
  flex: 1; padding: 12px 16px; font-size: 20px;
  background: rgba(255,255,255,0.04); border: 1px solid var(--border);
  border-radius: var(--radius); color: var(--text); outline: none;
  transition: border-color 0.2s; text-align: center;
}
.spell-input:focus { border-color: var(--primary); }
.spell-form .btn-primary { padding: 12px 24px; font-size: 16px; }

.tts-warning { margin-top: 12px; font-size: 12px; color: var(--text-secondary); }
</style>

<script setup>
import { ref, watch } from 'vue'
import { useSpeech } from '../composables/useSpeech'

const props = defineProps({ word: Object })
const flipped = ref(false)
const { speak, speaking } = useSpeech()

watch(() => props.word?.word_id, () => { flipped.value = false })

function flip() { flipped.value = !flipped.value }
</script>

<template>
  <div class="flashcard" :class="{ flipped }" @click="flip">
    <div class="card-inner">
      <div class="card-front">
        <button
          class="speak-btn"
          :class="{ playing: speaking }"
          @click.stop="speak(word?.english)"
          title="发音"
        >&#9654;</button>
        <span class="word-text">{{ word?.english }}</span>
        <span v-if="word?.phonetic" class="phonetic">{{ word.phonetic }}</span>
        <span class="hint">点击翻转</span>
      </div>
      <div class="card-back">
        <button
          class="speak-btn"
          :class="{ playing: speaking }"
          @click.stop="speak(word?.english)"
          title="发音"
        >&#9654;</button>
        <span class="word-text chinese">{{ word?.chinese }}</span>
        <span class="hint">{{ word?.english }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.flashcard {
  width: 100%;
  max-width: 400px;
  height: 240px;
  margin: 0 auto;
  perspective: 800px;
  cursor: pointer;
  user-select: none;
}
.card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.4s;
  transform-style: preserve-3d;
}
.flipped .card-inner { transform: rotateY(180deg); }
.card-front, .card-back {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--card-bg);
  backdrop-filter: blur(12px);
  backface-visibility: hidden;
  padding: 20px;
  overflow-y: auto;
}
.card-back { transform: rotateY(180deg); }
.word-text { font-size: 28px; font-weight: 700; }
.word-text.chinese {
  font-size: 17px;
  line-height: 1.5;
  word-break: break-word;
  text-align: center;
}
.phonetic { font-size: 14px; color: var(--text-secondary); margin-top: 8px; }
.hint { margin-top: 16px; font-size: 13px; color: var(--text-secondary); }

@media (max-width: 480px) {
  .flashcard { height: 200px; }
  .word-text { font-size: 22px; }
  .word-text.chinese { font-size: 15px; }
}
</style>

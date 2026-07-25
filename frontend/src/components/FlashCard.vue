<script setup>
import { ref, watch } from 'vue'

const props = defineProps({ word: Object })
const flipped = ref(false)

// Reset flip state when the word changes
watch(() => props.word?.word_id, () => { flipped.value = false })

function flip() { flipped.value = !flipped.value }
</script>

<template>
  <div class="flashcard" :class="{ flipped }" @click="flip">
    <div class="card-inner">
      <div class="card-front">
        <span class="word-text">{{ word?.english }}</span>
        <span class="hint">点击翻转</span>
      </div>
      <div class="card-back">
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
}
.card-back { transform: rotateY(180deg); }
.word-text { font-size: 28px; font-weight: 700; }
.word-text.chinese { font-size: 24px; }
.hint { margin-top: 16px; font-size: 13px; color: var(--text-secondary); }
</style>

<script setup>
import { useSpeech } from '../composables/useSpeech'

defineProps({
  word: { type: Object, required: true },
  showSpeak: { type: Boolean, default: false },
})

const { speak, speaking } = useSpeech()
</script>

<template>
  <div class="word-card">
    <div class="left">
      <button
        v-if="showSpeak"
        class="speak-btn"
        :class="{ playing: speaking }"
        @click.stop="speak(word.english)"
        :title="speaking ? '播放中...' : '发音'"
      >&#9654;</button>
      <span class="english">{{ word.english }}</span>
    </div>
    <div class="chinese">{{ word.chinese }}</div>
  </div>
</template>

<style scoped>
.word-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  border-bottom: 1px solid var(--border);
  transition: background 0.1s;
}
.word-card:hover { background: rgba(255,255,255,0.06); }
.left { display: flex; align-items: center; gap: 8px; }
.speak-btn {
  width: 26px; height: 26px; border-radius: 50%;
  border: 1px solid var(--border); background: rgba(255,255,255,0.04);
  color: var(--text-secondary); font-size: 10px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  padding: 0; transition: all 0.15s; flex-shrink: 0;
}
.speak-btn:hover { border-color: var(--primary); color: var(--primary); background: rgba(99,102,241,0.1); }
.speak-btn.playing { border-color: var(--primary); color: var(--primary); background: rgba(99,102,241,0.15); }
.english { font-weight: 600; font-size: 16px; color: var(--primary); }
.chinese { font-size: 15px; color: var(--text-secondary); }
</style>

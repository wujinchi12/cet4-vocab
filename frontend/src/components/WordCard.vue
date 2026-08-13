<script setup>
import { useSpeech } from '../composables/useSpeech'

defineProps({
  word: { type: Object, required: true },
  showSpeak: { type: Boolean, default: false },
  showPos: { type: Boolean, default: false },
  showFavorite: { type: Boolean, default: false },
  isFavorited: { type: Boolean, default: false },
})

const emit = defineEmits(['toggle-favorite'])

const { speak, speaking } = useSpeech()

const posLabels = { 'n.': '名词', 'v.': '动词', 'adj.': '形容词', 'adv.': '副词', 'other': '其他' }
</script>

<template>
  <div class="word-card">
    <div class="left">
      <button
        v-if="showFavorite"
        class="star-btn"
        :class="{ favorited: isFavorited }"
        @click.stop="emit('toggle-favorite', word.id)"
        :title="isFavorited ? '取消收藏' : '收藏'"
      >{{ isFavorited ? '★' : '☆' }}</button>
      <button
        v-if="showSpeak"
        class="speak-btn"
        :class="{ playing: speaking }"
        @click.stop="speak(word.english)"
        :title="speaking ? '播放中...' : '发音'"
      >&#9654;</button>
      <span class="english">{{ word.english }}</span>
      <span v-if="word.phonetic" class="phonetic">{{ word.phonetic }}</span>
      <span v-if="showPos && word.part_of_speech" class="pos-badge" :title="word.part_of_speech">
        {{ posLabels[word.part_of_speech.split(' ')[0]] || word.part_of_speech.split(' ')[0] }}
      </span>
    </div>
    <div class="chinese">{{ word.chinese }}</div>
  </div>
</template>

<style scoped>
.word-card {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  padding: 14px 20px;
  border-bottom: 1px solid var(--border);
  transition: background 0.1s;
}
.word-card:hover { background: rgba(255,255,255,0.06); }
.left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  flex-shrink: 0;
  min-width: 0;
}
.star-btn {
  width: 26px; height: 26px; border: none; background: none;
  font-size: 18px; cursor: pointer; flex-shrink: 0; padding: 0;
  color: var(--text-secondary); transition: all 0.15s; line-height: 1;
}
.star-btn:hover { color: #fbbf24; }
.star-btn.favorited { color: #fbbf24; }
.speak-btn {
  width: 26px; height: 26px; border-radius: 50%;
  border: 1px solid var(--border); background: rgba(255,255,255,0.04);
  color: var(--text-secondary); font-size: 10px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  padding: 0; transition: all 0.15s; flex-shrink: 0;
}
.speak-btn:hover { border-color: var(--primary); color: var(--primary); background: rgba(99,102,241,0.1); }
.speak-btn.playing { border-color: var(--primary); color: var(--primary); background: rgba(99,102,241,0.15); }
.english { font-weight: 600; font-size: 16px; color: var(--primary); white-space: nowrap; }
.phonetic { font-size: 12px; color: var(--text-secondary); word-break: break-word; }
.pos-badge {
  font-size: 11px; padding: 1px 6px; border-radius: 8px;
  background: rgba(99,102,241,0.15); color: var(--primary);
  flex-shrink: 0; white-space: nowrap;
}
.chinese {
  font-size: 15px;
  color: var(--text-secondary);
  flex: 1;
  min-width: 0;
  text-align: right;
  word-break: break-word;
  line-height: 1.5;
}
</style>

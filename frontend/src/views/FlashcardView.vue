<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { getDueWords, updateProgress } from '../api'
import { useLevel } from '../composables/useLevel'
import FlashCard from '../components/FlashCard.vue'
import ProgressBar from '../components/ProgressBar.vue'
import SessionControls from '../components/SessionControls.vue'

const { level } = useLevel()

const words = ref([])
const index = ref(0)
const loading = ref(true)
const finished = ref(false)
const submitting = ref(false)

async function loadWords() {
  loading.value = true
  try {
    const { data } = await getDueWords({ limit: 20, level: level.value })
    words.value = data
    index.value = 0
    finished.value = data.length === 0
  } catch (e) {
    console.error('Failed to load words:', e)
  } finally {
    loading.value = false
  }
}

const currentWord = computed(() => words.value[index.value] || null)

async function handleAnswer(knewIt) {
  const w = currentWord.value
  if (!w || submitting.value) return
  submitting.value = true
  try {
    await updateProgress(w.word_id, knewIt)
    if (index.value < words.value.length - 1) {
      index.value++
    } else {
      finished.value = true
    }
  } catch (e) {
    console.error('Failed to update progress:', e)
  } finally {
    submitting.value = false
  }
}

onMounted(loadWords)

watch(level, loadWords)
</script>

<template>
  <div>
    <h2>闪卡复习</h2>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else-if="finished" class="finished card">
      <h3>本轮复习完成!</h3>
      <p>所有单词已过完一遍，请稍后再来复习。</p>
      <button class="btn-primary" @click="loadWords">再来一轮</button>
    </div>

    <div v-else>
      <ProgressBar :current="index + 1" :total="words.length" />
      <FlashCard :word="currentWord" :key="currentWord?.word_id ?? 0" />
      <SessionControls
        @know="handleAnswer(true)"
        @dont-know="handleAnswer(false)"
        @end="finished = true"
      />
    </div>
  </div>
</template>

<style scoped>
h2 { margin-bottom: 8px; }
.loading { text-align: center; padding: 40px; color: var(--text-secondary); }
.finished { text-align: center; padding: 40px; }
.finished h3 { margin-bottom: 8px; }
.finished p { color: var(--text-secondary); margin-bottom: 20px; }
</style>

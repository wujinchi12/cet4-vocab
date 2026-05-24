<script setup>
import { ref, computed } from 'vue'

const props = defineProps({ question: Object })
const emit = defineEmits(['answer'])

const selectedLeft = ref(null)
const matches = ref({})

const pairs = computed(() => props.question.pairs || [])

function selectLeft(item) { selectedLeft.value = item }

function selectRight(item) {
  if (!selectedLeft.value) return
  matches.value = { ...matches.value, [selectedLeft.value.left]: item }
  selectedLeft.value = null

  if (Object.keys(matches.value).length === pairs.value.length) {
    const answers = pairs.value.map(p => ({
      word_id: p.word_id,
      answer: matches.value[p.left] || '',
      correct_answer: p.right,
    }))
    emit('answer', answers)
  }
}

function isMatchedLeft(item) { return matches.value[item.left] }

const unmatchedRights = computed(() =>
  pairs.value.filter(p => !Object.values(matches.value).includes(p.right))
)
</script>

<template>
  <div class="match-question">
    <h3>配对 — 点击左边再点击右边</h3>
    <div class="match-columns">
      <div class="col">
        <div
          v-for="p in pairs"
          :key="p.word_id"
          class="match-item"
          :class="{
            selected: selectedLeft?.left === p.left,
            matched: isMatchedLeft(p)
          }"
          @click="!isMatchedLeft(p) && selectLeft(p)"
        >{{ p.left }}</div>
      </div>
      <div class="col">
        <div
          v-for="r in unmatchedRights"
          :key="r.word_id"
          class="match-item right"
          @click="selectRight(r.right)"
        >{{ r.right }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.match-columns { display: flex; gap: 20px; margin-top: 20px; }
.col { flex: 1; }
.match-item {
  padding: 12px 16px;
  margin-bottom: 8px;
  background: var(--card-bg);
  border: 2px solid var(--border);
  border-radius: var(--radius);
  cursor: pointer;
  font-size: 15px;
  text-align: center;
}
.match-item:hover { border-color: var(--primary); }
.match-item.selected { border-color: var(--primary); background: #eef2ff; }
.match-item.matched { border-color: var(--success); background: #f0fdf4; opacity: 0.7; cursor: default; }
.match-item.right { color: var(--text-secondary); }
</style>

<script setup>
import { ref } from 'vue'
import { useQuizStore } from '../stores/quiz'
import { useLevel } from '../composables/useLevel'
import QuizSetup from '../components/QuizSetup.vue'
import MultipleChoice from '../components/MultipleChoice.vue'
import FillBlank from '../components/FillBlank.vue'
import MatchPairs from '../components/MatchPairs.vue'
import ListeningPractice from '../components/ListeningPractice.vue'
import SpellingPractice from '../components/SpellingPractice.vue'
import QuizResult from '../components/QuizResult.vue'

const store = useQuizStore()
const { level } = useLevel()
const step = ref('setup')
const currentIndex = ref(0)
const answers = ref([])
const config = ref(null)

async function start(configData) {
  config.value = configData
  let apiType, apiDir
  if (configData.type === 'listening') {
    apiType = 'fill'; apiDir = 'en_to_cn'
  } else if (configData.type === 'spelling') {
    apiType = 'fill'; apiDir = 'cn_to_en'
  } else {
    apiType = configData.type; apiDir = configData.direction
  }
  await store.startQuiz(apiType, configData.count, apiDir, configData.source || 'all', level.value)
  currentIndex.value = 0
  answers.value = []
  if (configData.type === 'match') {
    step.value = 'match'
  } else if (configData.type === 'listening') {
    step.value = 'listening'
  } else if (configData.type === 'spelling') {
    step.value = 'spelling'
  } else {
    step.value = 'question'
  }
}

async function handleAnswer(answer) {
  if (Array.isArray(answer)) {
    answers.value = answer
    await store.finishQuiz(answer)
    step.value = 'result'
    return
  }
  answers.value.push(answer)
  if (currentIndex.value < store.questions.length - 1) {
    currentIndex.value++
  } else {
    await store.finishQuiz(answers.value)
    step.value = 'result'
  }
}

function retry() {
  start(config.value)
}

function newQuiz() {
  store.reset()
  step.value = 'setup'
}
</script>

<template>
  <div>
    <h2>测验</h2>

    <QuizSetup v-if="step === 'setup'" @start="start" />

    <div v-else-if="step === 'question'">
      <MultipleChoice
        v-if="store.quizType === 'choice'"
        :question="store.questions[currentIndex]"
        :index="currentIndex"
        :total="store.questions.length"
        @answer="handleAnswer"
      />
      <FillBlank
        v-else
        :question="store.questions[currentIndex]"
        :index="currentIndex"
        :total="store.questions.length"
        @answer="handleAnswer"
      />
    </div>

    <ListeningPractice
      v-else-if="step === 'listening'"
      :question="store.questions[currentIndex]"
      :index="currentIndex"
      :total="store.questions.length"
      @answer="handleAnswer"
    />

    <MatchPairs
      v-else-if="step === 'match'"
      :question="store.questions[0]"
      @answer="handleAnswer"
    />

    <SpellingPractice
      v-else-if="step === 'spelling'"
      :question="store.questions[currentIndex]"
      :index="currentIndex"
      :total="store.questions.length"
      @answer="handleAnswer"
    />

    <QuizResult
      v-else-if="step === 'result'"
      :result="store.results"
      :quiz-type="config.type"
      :quiz-type-name="config.source === 'wrong' ? '错题复习' : config.type === 'choice' ? '选择题' : config.type === 'fill' ? '填空题' : config.type === 'match' ? '配对题' : config.type === 'listening' ? '听音辨义' : '拼写训练'"
      @retry="retry"
      @new-quiz="newQuiz"
    />
  </div>
</template>

<style scoped>
h2 { margin-bottom: 16px; }
</style>

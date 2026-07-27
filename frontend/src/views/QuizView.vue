<script setup>
import { ref } from 'vue'
import { useQuizStore } from '../stores/quiz'
import QuizSetup from '../components/QuizSetup.vue'
import MultipleChoice from '../components/MultipleChoice.vue'
import FillBlank from '../components/FillBlank.vue'
import MatchPairs from '../components/MatchPairs.vue'
import ListeningPractice from '../components/ListeningPractice.vue'
import QuizResult from '../components/QuizResult.vue'

const store = useQuizStore()
const step = ref('setup')
const currentIndex = ref(0)
const answers = ref([])
const config = ref(null)

async function start(configData) {
  config.value = configData
  const apiType = configData.type === 'listening' ? 'fill' : configData.type
  const apiDir = configData.type === 'listening' ? 'en_to_cn' : configData.direction
  await store.startQuiz(apiType, configData.count, apiDir, configData.source || 'all')
  currentIndex.value = 0
  answers.value = []
  if (configData.type === 'match') {
    step.value = 'match'
  } else if (configData.type === 'listening') {
    step.value = 'listening'
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

    <QuizResult
      v-else-if="step === 'result'"
      :result="store.results"
      :quiz-type="config.type"
      :quiz-type-name="config.source === 'wrong' ? '错题复习' : config.type === 'choice' ? '选择题' : config.type === 'fill' ? '填空题' : config.type === 'match' ? '配对题' : '听音辨义'"
      @retry="retry"
      @new-quiz="newQuiz"
    />
  </div>
</template>

<style scoped>
h2 { margin-bottom: 16px; }
</style>

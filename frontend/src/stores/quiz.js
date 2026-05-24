import { defineStore } from 'pinia'
import { generateQuiz, submitQuiz } from '../api'

export const useQuizStore = defineStore('quiz', {
  state: () => ({
    questions: [],
    results: null,
    quizType: 'choice',
    direction: 'en_to_cn',
    inProgress: false,
  }),
  actions: {
    async startQuiz(type, count, direction) {
      this.quizType = type
      this.direction = direction
      const { data } = await generateQuiz({ quiz_type: type, count, direction })
      this.questions = data
      this.results = null
      this.inProgress = true
    },
    async finishQuiz(answers) {
      const { data } = await submitQuiz({ quiz_type: this.quizType, answers })
      this.results = data
      this.inProgress = false
      return data
    },
    reset() {
      this.questions = []
      this.results = null
      this.inProgress = false
    }
  }
})

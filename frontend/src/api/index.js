import axios from 'axios'
import router from '../router'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

export const register = (data) => api.post('/auth/register', data)
export const login = (data) => api.post('/auth/login', data)
export const getWords = (params) => api.get('/words', { params })
export const getPosList = () => api.get('/words/pos/list')
export const getWord = (id) => api.get(`/words/${id}`)
export const getProgressSummary = () => api.get('/progress')
export const getDueWords = (limit = 20) => api.get('/progress/due', { params: { limit } })
export const updateProgress = (wordId, knewIt) => api.put(`/progress/${wordId}`, { knew_it: knewIt })
export const getWeakestWords = (limit = 20) => api.get('/progress/weakest', { params: { limit } })
export const generateQuiz = (data) => api.post('/quiz/generate', data)
export const submitQuiz = (data) => api.post('/quiz/submit', data)
export const getQuizHistory = () => api.get('/quiz/history')

export const addWrongAnswers = (data) => api.post('/wrong-answers/add', data)
export const getWrongAnswers = (params) => api.get('/wrong-answers', { params })
export const getWrongAnswerCount = () => api.get('/wrong-answers/count')
export const removeWrongAnswer = (wordId) => api.delete(`/wrong-answers/${wordId}`)
export const clearWrongAnswers = () => api.post('/wrong-answers/clear')

export const submitFeedback = (data) => api.post('/feedback', data)
export const getLeaderboard = (limit = 50) => api.get('/leaderboard', { params: { limit } })

// Admin
const adminApi = (token) => axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api',
  headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
})

export const getAdminUsers = (token) => adminApi(token).get('/admin/users')
export const getAdminUser = (token, id) => adminApi(token).get(`/admin/users/${id}`)
export const deleteAdminUser = (token, id) => adminApi(token).delete(`/admin/users/${id}`)
export const resetUserPassword = (token, id) => adminApi(token).post(`/admin/users/${id}/reset-password`)
export const getAdminFeedback = (token) => adminApi(token).get('/admin/feedback')

export default api

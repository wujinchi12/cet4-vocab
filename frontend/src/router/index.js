import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'home', component: () => import('../views/HomeView.vue') },
  { path: '/login', name: 'login', component: () => import('../views/AuthView.vue') },
  { path: '/register', name: 'register', component: () => import('../views/AuthView.vue') },
  { path: '/words', name: 'words', component: () => import('../views/WordListView.vue'), meta: { requiresAuth: true } },
  { path: '/flashcard', name: 'flashcard', component: () => import('../views/FlashcardView.vue'), meta: { requiresAuth: true } },
  { path: '/quiz', name: 'quiz', component: () => import('../views/QuizView.vue'), meta: { requiresAuth: true } },
  { path: '/profile', name: 'profile', component: () => import('../views/ProfileView.vue'), meta: { requiresAuth: true } },
  { path: '/leaderboard', name: 'leaderboard', component: () => import('../views/LeaderboardView.vue'), meta: { requiresAuth: true } },
  { path: '/admin', name: 'admin', component: () => import('../views/AdminView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('token')
    if (!token) return '/login'
  }
})

export default router

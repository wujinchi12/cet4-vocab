<script setup>
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

function handleLogout() {
  auth.logout()
  router.push('/')
}
</script>

<template>
  <nav class="navbar">
    <div class="nav-inner">
      <router-link to="/" class="logo">CET-4 词汇</router-link>
      <div class="nav-links">
        <template v-if="auth.isLoggedIn">
          <router-link to="/words">词汇表</router-link>
          <router-link to="/flashcard">闪卡</router-link>
          <router-link to="/quiz">测验</router-link>
          <router-link to="/leaderboard">排行榜</router-link>
          <router-link to="/profile">我的</router-link>
          <button class="btn-outline" @click="handleLogout">退出</button>
        </template>
        <template v-else>
          <router-link to="/login">登录</router-link>
          <router-link to="/register" class="btn-primary">注册</router-link>
        </template>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  background: var(--card-bg);
  border-bottom: 1px solid var(--border);
  padding: 0 16px;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}
.nav-inner {
  max-width: 960px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
}
.logo { font-size: 18px; font-weight: 700; color: var(--primary); }
.nav-links { display: flex; align-items: center; gap: 16px; }
.nav-links a { font-size: 14px; }

@media (max-width: 640px) {
  .nav-inner { height: 48px; padding: 0 4px; }
  .logo { font-size: 15px; }
  .nav-links { gap: 8px; }
  .nav-links a { font-size: 12px; }
}
@media (max-width: 400px) {
  .nav-links { gap: 5px; }
  .nav-links a { font-size: 11px; }
  .btn-outline { padding: 6px 10px; font-size: 11px; }
}
</style>

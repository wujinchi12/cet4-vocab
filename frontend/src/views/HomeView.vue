<script setup>
import { useAuthStore } from '../stores/auth'
import { useLevel } from '../composables/useLevel'
const auth = useAuthStore()
const { level } = useLevel()
</script>

<template>
  <div class="home">
    <h1>{{ level === 'cet4' ? '四级词汇学习' : '六级词汇学习' }}</h1>
    <p class="subtitle">覆盖四级 / 六级核心词汇 · 吴瑾赤 出品</p>
    <div class="mode-cards" v-if="auth.isLoggedIn">
      <router-link to="/words" class="mode-card card">
        <h3>词汇表</h3>
        <p>浏览和搜索全部词汇</p>
      </router-link>
      <router-link to="/flashcard" class="mode-card card">
        <h3>闪卡复习</h3>
        <p>科学记忆，间隔重复</p>
      </router-link>
      <router-link to="/quiz" class="mode-card card">
        <h3>测验模式</h3>
        <p>选择题、填空、配对</p>
      </router-link>
    </div>
    <div class="cta" v-else>
      <router-link to="/register" class="btn-primary">开始学习</router-link>
      <router-link to="/login">已有账号？登录</router-link>
    </div>
  </div>
</template>

<style scoped>
.home { text-align: center; padding-top: 60px; }
h1 { font-size: 32px; margin-bottom: 8px; }
.subtitle { color: var(--text-secondary); margin-bottom: 40px; font-size: 18px; }
.mode-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.mode-card { padding: 32px 20px; text-align: center; }
.mode-card h3 { margin-bottom: 8px; }
.mode-card p { color: var(--text-secondary); font-size: 14px; }
.cta { display: flex; flex-direction: column; gap: 12px; align-items: center; }
@media (max-width: 640px) { .mode-cards { grid-template-columns: 1fr; } }
</style>

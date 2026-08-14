<script setup>
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import { useLevel } from '../composables/useLevel'

const auth = useAuthStore()
const router = useRouter()
const { level, setLevel } = useLevel()

function handleLogout() {
  auth.logout()
  router.push('/')
}

const desktopItems = [
  { to: '/words', label: '词汇表' },
  { to: '/flashcard', label: '闪卡' },
  { to: '/quiz', label: '测验' },
  { to: '/wrong-answers', label: '错题本' },
  { to: '/favorites', label: '收藏库' },
  { to: '/real-exams', label: '真题库' },
  { to: '/exam', label: '模拟测试' },
  { to: '/leaderboard', label: '排行榜' },
  { to: '/profile', label: '我的' },
]

const mobileItems = [
  { to: '/words', label: '词汇' },
  { to: '/flashcard', label: '闪卡' },
  { to: '/quiz', label: '测验' },
  { to: '/real-exams', label: '真题库' },
  { to: '/exam', label: '模拟' },
  { to: '/profile', label: '我的' },
]
</script>

<template>
  <!-- 桌面端:左侧固定侧边栏 -->
  <aside class="sidebar">
    <router-link to="/" class="logo">CET 词汇</router-link>
    <div class="level-switch">
      <button :class="{ active: level === 'cet4' }" @click="setLevel('cet4')">四级</button>
      <button :class="{ active: level === 'cet6' }" @click="setLevel('cet6')">六级</button>
    </div>
    <nav class="nav-links" v-if="auth.isLoggedIn">
      <router-link v-for="item in desktopItems" :key="item.to" :to="item.to">{{ item.label }}</router-link>
      <button class="logout-btn" @click="handleLogout">退出登录</button>
    </nav>
    <nav class="nav-links" v-else>
      <router-link to="/login">登录</router-link>
      <router-link to="/register">注册</router-link>
    </nav>
  </aside>

  <!-- 移动端:顶部精简 header -->
  <header class="mobile-header">
    <router-link to="/" class="logo">CET 词汇</router-link>
    <div class="level-switch">
      <button :class="{ active: level === 'cet4' }" @click="setLevel('cet4')">四级</button>
      <button :class="{ active: level === 'cet6' }" @click="setLevel('cet6')">六级</button>
    </div>
    <button v-if="auth.isLoggedIn" class="logout-btn" @click="handleLogout">退出</button>
  </header>

  <!-- 移动端:底部固定 tab bar -->
  <nav class="mobile-tabbar" v-if="auth.isLoggedIn">
    <router-link v-for="item in mobileItems" :key="item.to" :to="item.to" class="tab-item">
      {{ item.label }}
    </router-link>
  </nav>
</template>

<style scoped>
.logo { font-size: 18px; font-weight: 700; color: var(--primary); }

.level-switch {
  display: flex;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 3px;
  gap: 2px;
}
.level-switch button {
  flex: 1;
  padding: 6px 14px;
  font-size: 13px;
  border-radius: 999px;
  background: transparent;
  color: var(--text-secondary);
  border: none;
  transition: all 0.15s;
}
.level-switch button.active {
  background: var(--primary);
  color: #fff;
}

/* 桌面侧边栏 */
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: 210px;
  padding: 24px 16px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background: var(--card-bg);
  border-right: 1px solid var(--border);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  z-index: 10;
}
.nav-links {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}
.nav-links a {
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 15px;
  color: var(--text-secondary);
  transition: all 0.15s;
}
.nav-links a:hover { background: rgba(255, 255, 255, 0.06); color: var(--text); }
.nav-links a.router-link-active { background: rgba(99, 102, 241, 0.15); color: var(--primary); }
.logout-btn {
  margin-top: auto;
  background: none;
  border: 1px solid var(--border);
  border-radius: 10px;
  color: var(--text-secondary);
  padding: 10px;
  font-size: 14px;
}
.logout-btn:hover { border-color: var(--danger); color: var(--danger); }

/* 移动端 header + tabbar */
.mobile-header, .mobile-tabbar { display: none; }

@media (max-width: 768px) {
  .sidebar { display: none; }

  .mobile-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    position: sticky;
    top: 0;
    padding: 10px 16px;
    background: var(--card-bg);
    border-bottom: 1px solid var(--border);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    z-index: 10;
  }
  .mobile-header .logo { font-size: 16px; }
  .mobile-header .level-switch { flex: 0 0 auto; }
  .mobile-header .level-switch button { padding: 5px 12px; font-size: 12px; }
  .mobile-header .logout-btn {
    flex-shrink: 0;
    background: none;
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text-secondary);
    padding: 6px 10px;
    font-size: 12px;
  }

  .mobile-tabbar {
    display: flex;
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    background: var(--card-bg);
    border-top: 1px solid var(--border);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    z-index: 10;
  }
  .tab-item {
    flex: 1;
    text-align: center;
    padding: 12px 4px;
    font-size: 13px;
    color: var(--text-secondary);
  }
  .tab-item.router-link-active { color: var(--primary); font-weight: 600; }
}
</style>

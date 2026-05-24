<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const isLogin = () => route.name === 'login'

const username = ref('')
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    if (isLogin()) {
      await auth.login({ username: username.value, password: password.value })
    } else {
      await auth.register({ username: username.value, email: email.value, password: password.value })
      await auth.login({ username: username.value, password: password.value })
    }
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || '操作失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-form card">
    <h2>{{ isLogin() ? '登录' : '注册' }}</h2>
    <form @submit.prevent="submit">
      <div class="field">
        <label>用户名</label>
        <input v-model="username" required />
      </div>
      <div class="field" v-if="!isLogin()">
        <label>邮箱</label>
        <input v-model="email" type="email" required />
      </div>
      <div class="field">
        <label>密码</label>
        <input v-model="password" type="password" required minlength="6" />
      </div>
      <p class="error" v-if="error">{{ error }}</p>
      <button class="btn-primary" type="submit" :disabled="loading">
        {{ loading ? '处理中...' : (isLogin() ? '登录' : '注册') }}
      </button>
    </form>
    <p class="switch">
      {{ isLogin() ? '还没有账号？' : '已有账号？' }}
      <router-link :to="isLogin() ? '/register' : '/login'">
        {{ isLogin() ? '注册' : '登录' }}
      </router-link>
    </p>
  </div>
</template>

<style scoped>
.auth-form { max-width: 400px; margin: 60px auto; }
h2 { margin-bottom: 24px; text-align: center; }
.field { margin-bottom: 16px; }
.field label { display: block; margin-bottom: 6px; font-size: 14px; color: var(--text-secondary); }
.field input { width: 100%; }
.error { color: var(--danger); font-size: 14px; margin-bottom: 12px; }
.auth-form button { width: 100%; }
.switch { text-align: center; margin-top: 16px; font-size: 14px; color: var(--text-secondary); }
</style>

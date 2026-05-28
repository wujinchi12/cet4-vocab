<template>
  <div class="admin-page">
    <!-- Login -->
    <div v-if="!adminToken" class="admin-login">
      <h2>管理后台</h2>
      <form @submit.prevent="login">
        <input v-model="keyInput" type="password" placeholder="请输入 Admin Key" />
        <button type="submit">登录</button>
      </form>
      <p v-if="loginError" class="error">{{ loginError }}</p>
    </div>

    <!-- Dashboard -->
    <div v-else class="admin-dashboard">
      <header class="admin-header">
        <h2>管理后台</h2>
        <div class="header-actions">
          <span class="user-count">{{ users.length }} 个用户</span>
          <button class="btn-refresh" @click="fetchUsers">刷新</button>
          <button class="btn-logout" @click="logout">退出</button>
        </div>
      </header>

      <div v-if="loading" class="loading">加载中...</div>

      <table v-else class="user-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>用户名</th>
            <th>邮箱</th>
            <th>注册时间</th>
            <th>已学单词</th>
            <th>测验次数</th>
            <th>平均分</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id">
            <td>{{ u.id }}</td>
            <td>{{ u.username }}</td>
            <td>{{ u.email }}</td>
            <td>{{ formatDate(u.created_at) }}</td>
            <td>{{ u.words_learned }}</td>
            <td>{{ u.quiz_count }}</td>
            <td>{{ u.avg_score ?? '-' }}%</td>
            <td class="actions">
              <button class="btn-sm" @click="resetPw(u)">重置密码</button>
              <button class="btn-sm btn-danger" @click="deleteU(u)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Reset Password Modal -->
      <div v-if="resetModal.show" class="modal-overlay" @click.self="resetModal.show = false">
        <div class="modal">
          <h3>密码已重置</h3>
          <p>用户: <strong>{{ resetModal.username }}</strong></p>
          <p>新密码: <code>{{ resetModal.newPassword }}</code></p>
          <p class="hint">请提醒用户尽快修改密码</p>
          <button @click="resetModal.show = false">关闭</button>
        </div>
      </div>

      <!-- Delete Confirm -->
      <div v-if="deleteModal.show" class="modal-overlay" @click.self="deleteModal.show = false">
        <div class="modal">
          <h3>确认删除</h3>
          <p>确定要删除用户 <strong>{{ deleteModal.username }}</strong> 吗？</p>
          <p class="hint">此操作不可撤销，用户的所有学习记录将被清除。</p>
          <div class="modal-actions">
            <button class="btn-danger" @click="confirmDelete">确认删除</button>
            <button @click="deleteModal.show = false">取消</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { getAdminUsers, deleteAdminUser, resetUserPassword } from '../api'

const adminToken = ref(sessionStorage.getItem('admin_token') || '')
const keyInput = ref('')
const loginError = ref('')
const users = ref([])
const loading = ref(false)

const resetModal = ref({ show: false, username: '', newPassword: '' })
const deleteModal = ref({ show: false, id: null, username: '' })

async function login() {
  loginError.value = ''
  try {
    await getAdminUsers(keyInput.value)
    adminToken.value = keyInput.value
    sessionStorage.setItem('admin_token', keyInput.value)
    await fetchUsers()
  } catch {
    loginError.value = 'Admin Key 无效'
  }
}

function logout() {
  adminToken.value = ''
  sessionStorage.removeItem('admin_token')
  users.value = []
}

async function fetchUsers() {
  loading.value = true
  try {
    const { data } = await getAdminUsers(adminToken.value)
    users.value = data.users
  } finally {
    loading.value = false
  }
}

async function deleteU(u) {
  deleteModal.value = { show: true, id: u.id, username: u.username }
}

async function confirmDelete() {
  await deleteAdminUser(adminToken.value, deleteModal.value.id)
  deleteModal.value.show = false
  await fetchUsers()
}

async function resetPw(u) {
  const { data } = await resetUserPassword(adminToken.value, u.id)
  resetModal.value = { show: true, username: data.username, newPassword: data.new_password }
}

function formatDate(iso) {
  if (!iso) return '-'
  return new Date(iso).toLocaleDateString('zh-CN')
}

// Auto-fetch if already logged in
if (adminToken.value) fetchUsers()
</script>

<style scoped>
.admin-page { max-width: 1100px; margin: 0 auto; padding: 24px; }

.admin-login {
  max-width: 360px; margin: 80px auto; text-align: center;
}
.admin-login h2 { margin-bottom: 20px; font-size: 1.5rem; }
.admin-login input {
  width: 100%; padding: 10px 14px; margin-bottom: 12px;
  border: 1px solid #d1d5db; border-radius: 8px; font-size: 1rem;
}
.admin-login button {
  width: 100%; padding: 10px; background: #1a1a2e; color: #fff;
  border: none; border-radius: 8px; font-size: 1rem; cursor: pointer;
}

.admin-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 20px; flex-wrap: wrap; gap: 12px;
}
.admin-header h2 { font-size: 1.4rem; }
.header-actions { display: flex; align-items: center; gap: 12px; }

.user-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.user-table th, .user-table td {
  padding: 10px 12px; text-align: left; border-bottom: 1px solid #e5e7eb;
}
.user-table th { background: #f9fafb; font-weight: 600; white-space: nowrap; }
.user-table tbody tr:hover { background: #f3f4f6; }

.actions { display: flex; gap: 6px; }

.btn-sm {
  padding: 4px 10px; font-size: 0.8rem; border: 1px solid #d1d5db;
  border-radius: 6px; cursor: pointer; background: #fff;
}
.btn-sm:hover { background: #f3f4f6; }
.btn-danger { color: #dc2626; border-color: #fca5a5; }
.btn-danger:hover { background: #fef2f2; }

.btn-refresh, .btn-logout {
  padding: 6px 14px; border: 1px solid #d1d5db; border-radius: 6px;
  cursor: pointer; background: #fff; font-size: 0.85rem;
}

.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center; z-index: 100;
}
.modal {
  background: #fff; padding: 28px; border-radius: 12px; max-width: 420px;
  width: 90%; box-shadow: 0 8px 30px rgba(0,0,0,0.15);
}
.modal h3 { margin-bottom: 12px; }
.modal code { background: #f3f4f6; padding: 4px 8px; border-radius: 4px; font-size: 1rem; }
.modal .hint { color: #6b7280; font-size: 0.85rem; margin-top: 8px; }
.modal-actions { display: flex; gap: 10px; margin-top: 20px; }
.modal button {
  padding: 8px 18px; border: 1px solid #d1d5db; border-radius: 6px;
  background: #fff; cursor: pointer; font-size: 0.9rem;
}
.modal .btn-danger { background: #dc2626; color: #fff; border-color: #dc2626; }
.modal .btn-danger:hover { background: #b91c1c; }

.error { color: #dc2626; margin-top: 10px; font-size: 0.9rem; }
.loading { text-align: center; padding: 40px; color: #6b7280; }
.user-count { color: #6b7280; font-size: 0.9rem; }
</style>

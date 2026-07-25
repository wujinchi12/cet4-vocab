<template>
  <div class="admin-page">
    <!-- Login -->
    <div v-if="!adminToken" class="admin-login">
      <div class="login-card card">
        <h2>管理后台</h2>
        <form @submit.prevent="login">
          <input v-model="keyInput" type="password" placeholder="请输入 Admin Key" />
          <button class="btn-primary" type="submit">登录</button>
        </form>
        <p v-if="loginError" class="error">{{ loginError }}</p>
      </div>
    </div>

    <!-- Dashboard -->
    <div v-else class="admin-dashboard">
      <header class="admin-header">
        <h2>管理后台</h2>
        <div class="header-actions">
          <button class="btn-sm btn-danger-outline" @click="logout">退出</button>
        </div>
      </header>

      <div class="tabs">
        <button class="tab" :class="{ active: activeTab === 'users' }" @click="switchTab('users')">用户管理</button>
        <button class="tab" :class="{ active: activeTab === 'feedback' }" @click="switchTab('feedback')">反馈列表</button>
      </div>

      <div v-if="loading" class="loading">加载中...</div>

      <!-- Users tab -->
      <div v-else-if="activeTab === 'users'" class="table-card card">
        <div class="table-header">
          <span class="user-count">{{ users.length }} 个用户</span>
          <button class="btn-sm" @click="fetchUsers">刷新</button>
        </div>
        <table class="user-table">
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
      </div>

      <!-- Feedback tab -->
      <div v-else-if="activeTab === 'feedback'" class="table-card card">
        <div class="table-header">
          <span class="user-count">{{ feedbacks.length }} 条反馈</span>
          <button class="btn-sm" @click="fetchFeedback">刷新</button>
        </div>
        <div v-if="feedbacks.length === 0" class="empty">暂无反馈</div>
        <table v-else class="user-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>类型</th>
              <th>内容</th>
              <th>联系方式</th>
              <th>时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="f in feedbacks" :key="f.id">
              <td>{{ f.id }}</td>
              <td>
                <span class="type-badge" :class="f.type">{{ f.type === 'suggestion' ? '建议' : '问题' }}</span>
              </td>
              <td class="content-cell">{{ f.content }}</td>
              <td>{{ f.contact || '-' }}</td>
              <td>{{ formatDate(f.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

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
import { getAdminUsers, deleteAdminUser, resetUserPassword, getAdminFeedback } from '../api'

const adminToken = ref(sessionStorage.getItem('admin_token') || '')
const keyInput = ref('')
const loginError = ref('')
const users = ref([])
const feedbacks = ref([])
const loading = ref(false)
const activeTab = ref('users')

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

async function fetchFeedback() {
  loading.value = true
  try {
    const { data } = await getAdminFeedback(adminToken.value)
    feedbacks.value = data.feedback
  } finally {
    loading.value = false
  }
}

function switchTab(tab) {
  activeTab.value = tab
  loading.value = false
  if (tab === 'users') fetchUsers()
  else fetchFeedback()
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
  display: flex; align-items: center; justify-content: center; min-height: 50vh;
}
.login-card {
  width: 100%; max-width: 380px; padding: 32px; text-align: center;
}
.login-card h2 { margin-bottom: 24px; font-size: 1.5rem; }
.login-card input {
  width: 100%; padding: 10px 14px; margin-bottom: 14px;
  border: 1px solid var(--border); border-radius: var(--radius); font-size: 1rem;
  background: rgba(255,255,255,0.05); color: var(--text);
}
.login-card button {
  width: 100%; padding: 11px; font-size: 1rem;
}

.admin-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 20px; flex-wrap: wrap; gap: 12px;
}
.admin-header h2 { font-size: 1.4rem; }
.header-actions { display: flex; align-items: center; gap: 10px; }
.user-count { color: var(--text-secondary); font-size: 0.9rem; }

.table-card { padding: 0; overflow: hidden; }

.user-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.user-table th, .user-table td {
  padding: 10px 14px; text-align: left; border-bottom: 1px solid var(--border);
}
.user-table th {
  background: rgba(255,255,255,0.03); font-weight: 600;
  white-space: nowrap; font-size: 0.8rem; color: var(--text-secondary);
  text-transform: uppercase; letter-spacing: 0.5px;
}
.user-table tbody tr { transition: background 0.15s; }
.user-table tbody tr:hover { background: rgba(255,255,255,0.04); }
.user-table tbody tr:last-child td { border-bottom: none; }

.actions { display: flex; gap: 6px; }

.btn-sm {
  padding: 4px 10px; font-size: 0.8rem; border: 1px solid rgba(255,255,255,0.12);
  border-radius: 6px; cursor: pointer; background: rgba(255,255,255,0.06); color: var(--text);
  transition: background 0.15s;
}
.btn-sm:hover { background: rgba(255,255,255,0.12); }
.btn-danger { color: #f87171; border-color: rgba(248,113,113,0.3); }
.btn-danger:hover { background: rgba(248,113,113,0.15); }
.btn-danger-outline { color: #f87171; border-color: rgba(248,113,113,0.3); }
.btn-danger-outline:hover { background: rgba(248,113,113,0.15); }

.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.6);
  display: flex; align-items: center; justify-content: center; z-index: 100;
  backdrop-filter: blur(4px);
}
.modal {
  background: #1a1a2e; padding: 28px; border-radius: 12px; max-width: 420px;
  width: 90%; box-shadow: 0 8px 30px rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.08);
}
.modal h3 { margin-bottom: 12px; }
.modal p { margin-bottom: 6px; }
.modal code { background: rgba(255,255,255,0.08); padding: 4px 8px; border-radius: 4px; font-size: 1rem; color: var(--primary-light); }
.modal .hint { color: var(--text-secondary); font-size: 0.85rem; margin-top: 8px; }
.modal-actions { display: flex; gap: 10px; margin-top: 20px; }
.modal button {
  padding: 8px 18px; border: 1px solid rgba(255,255,255,0.12); border-radius: 6px;
  background: rgba(255,255,255,0.06); cursor: pointer; font-size: 0.9rem; color: var(--text);
  transition: background 0.15s;
}
.modal button:hover { background: rgba(255,255,255,0.1); }
.modal .btn-danger { background: #dc2626; color: #fff; border-color: #dc2626; }
.modal .btn-danger:hover { background: #b91c1c; }

.error { color: var(--danger); margin-top: 12px; font-size: 0.9rem; }
.loading { text-align: center; padding: 60px 20px; color: var(--text-secondary); }
.empty { text-align: center; padding: 40px 20px; color: var(--text-secondary); }

.tabs { display: flex; gap: 4px; margin-bottom: 16px; }
.tab {
  padding: 8px 20px; border: 1px solid var(--border); border-radius: 8px;
  background: transparent; color: var(--text-secondary); cursor: pointer;
  font-size: 0.9rem; transition: all 0.15s;
}
.tab:hover { border-color: rgba(255,255,255,0.2); color: var(--text); }
.tab.active { border-color: var(--primary); background: rgba(99,102,241,0.12); color: var(--primary-light); }

.table-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px; border-bottom: 1px solid var(--border);
}

.type-badge {
  display: inline-block; padding: 2px 10px; border-radius: 10px;
  font-size: 0.8rem; font-weight: 500;
}
.type-badge.suggestion { background: rgba(99,102,241,0.15); color: var(--primary-light); }
.type-badge.bug { background: rgba(248,113,113,0.15); color: #f87171; }

.content-cell { max-width: 300px; white-space: normal; word-break: break-word; }
</style>

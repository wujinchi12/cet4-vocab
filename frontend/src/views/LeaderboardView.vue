<script setup>
import { ref, onMounted } from 'vue'
import { getLeaderboard } from '../api'

const entries = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await getLeaderboard()
    entries.value = data
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <h2>排行榜</h2>
    <p class="subtitle">按测验平均分排序</p>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else-if="entries.length === 0" class="empty card">
      还没有测验记录，快去完成一次测验吧！
    </div>

    <div v-else class="card leaderboard-card">
      <table>
        <thead>
          <tr>
            <th class="col-rank">排名</th>
            <th>用户名</th>
            <th>测验次数</th>
            <th>平均分</th>
            <th>最高分</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="entry in entries" :key="entry.rank">
            <td class="col-rank">
              <span class="rank-badge" :class="{ top3: entry.rank <= 3 }">
                {{ entry.rank }}
              </span>
            </td>
            <td class="col-username">{{ entry.username }}</td>
            <td>{{ entry.total_quizzes }}</td>
            <td>{{ entry.average_score }}%</td>
            <td>{{ entry.highest_score }}%</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
h2 { margin-bottom: 4px; }
.subtitle { color: var(--text-secondary); font-size: 14px; margin-bottom: 20px; }
.loading { text-align: center; padding: 40px; color: var(--text-secondary); }
.empty { text-align: center; padding: 40px; color: var(--text-secondary); }

.leaderboard-card { padding: 0; overflow: hidden; }

table {
  width: 100%;
  border-collapse: collapse;
}

th {
  text-align: left;
  padding: 14px 20px;
  font-size: 13px;
  color: var(--text-secondary);
  background: var(--bg);
  border-bottom: 1px solid var(--border);
}

td {
  padding: 14px 20px;
  border-bottom: 1px solid var(--border);
}

tr:last-child td { border-bottom: none; }

.col-rank { width: 60px; }
.col-username { font-weight: 500; }

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  font-size: 13px;
  font-weight: 600;
  background: var(--bg);
  color: var(--text-secondary);
}

.rank-badge.top3 {
  background: var(--primary);
  color: white;
}
</style>

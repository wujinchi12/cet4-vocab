<script setup>
import { ref, computed, onMounted } from 'vue'
import { Capacitor } from '@capacitor/core'
import { Browser } from '@capacitor/browser'

const apiBase = import.meta.env.VITE_API_BASE || '/api'
const staticBase = apiBase.replace(/\/api\/?$/, '')

const papers = ref([])
const loading = ref(true)
const error = ref('')
const isNative = Capacitor.isNativePlatform()

const categoryStyles = {
  '试卷': 'cat-paper',
  '听力原文': 'cat-listening',
  '写作': 'cat-writing',
  '答案': 'cat-answer',
  '合集': 'cat-collection',
}

const grouped = computed(() => {
  const map = new Map()
  for (const p of papers.value) {
    const key = p.year || 0
    if (!map.has(key)) map.set(key, [])
    map.get(key).push(p)
  }
  const years = [...map.keys()].sort((a, b) => b - a)
  return years.map((y) => ({ year: y, items: map.get(y) }))
})

function pdfUrl(p) {
  return `${staticBase}/exams/${p.filename}`
}

function fmtSize(bytes) {
  if (!bytes) return ''
  if (bytes >= 1024 * 1024) return (bytes / 1024 / 1024).toFixed(1) + ' MB'
  return Math.round(bytes / 1024) + ' KB'
}

async function openPdf(p) {
  const url = pdfUrl(p)
  if (isNative) {
    try {
      await Browser.open({ url })
    } catch (e) {
      console.error('Failed to open in browser', e)
    }
  } else {
    window.open(url, '_blank', 'noopener')
  }
}

onMounted(async () => {
  try {
    const res = await fetch(`${staticBase}/exams/index.json`)
    if (!res.ok) throw new Error('HTTP ' + res.status)
    const data = await res.json()
    papers.value = data.papers || []
  } catch (e) {
    error.value = '真题库加载失败，请稍后重试'
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="real-exam-view">
    <h2>真题库</h2>
    <p class="subtitle">历年大学英语四级（CET-4）真题试卷，在线阅读或下载打印</p>

    <div v-if="loading" class="empty-state">加载中...</div>
    <div v-else-if="error" class="empty-state">{{ error }}</div>
    <div v-else-if="papers.length === 0" class="empty-state">暂无真题</div>

    <div v-else>
      <section v-for="g in grouped" :key="g.year" class="year-group">
        <h3 class="year-heading">
          {{ g.year > 0 ? g.year + '年' : '综合 / 历年合集' }}
          <span class="year-count">{{ g.items.length }} 份</span>
        </h3>

        <div class="paper-grid">
          <div v-for="p in g.items" :key="p.slug" class="paper-card">
            <div class="paper-top">
              <span class="category-badge" :class="categoryStyles[p.category] || 'cat-paper'">
                {{ p.category }}
              </span>
              <span v-if="p.set" class="set-badge">第{{ p.set }}套</span>
            </div>

            <div class="paper-title">{{ p.title }}</div>
            <div v-if="p.note" class="paper-note">{{ p.note }}</div>

            <div class="paper-meta">
              <span v-if="p.pages">{{ p.pages }} 页</span>
              <span v-if="fmtSize(p.size)">{{ fmtSize(p.size) }}</span>
            </div>

            <div class="paper-actions">
              <button class="btn-primary" @click="openPdf(p)">在线阅读</button>
              <a
                v-if="!isNative"
                class="btn-outline"
                :href="pdfUrl(p)"
                :download="p.filename"
              >下载</a>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.real-exam-view {
  max-width: 860px;
  margin: 0 auto;
}
h2 { margin-bottom: 8px; }
.subtitle {
  color: var(--text-secondary);
  margin-bottom: 24px;
}

.year-group {
  margin-bottom: 32px;
}
.year-heading {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  margin: 0 0 14px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--border);
}
.year-count {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 400;
}

.paper-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 14px;
}

.paper-card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: border-color 0.15s, transform 0.15s;
}
.paper-card:hover {
  border-color: var(--primary);
  transform: translateY(-2px);
}

.paper-top {
  display: flex;
  align-items: center;
  gap: 8px;
}
.category-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  color: #fff;
}
.cat-paper { background: #6366f1; }
.cat-listening { background: #10b981; }
.cat-writing { background: #f59e0b; }
.cat-answer { background: #3b82f6; }
.cat-collection { background: #8b5cf6; }
.set-badge {
  font-size: 11px;
  color: var(--text-secondary);
  border: 1px solid var(--border);
  padding: 1px 6px;
  border-radius: 4px;
}

.paper-title {
  font-size: 15px;
  font-weight: 600;
  line-height: 1.4;
}
.paper-note {
  font-size: 12px;
  color: var(--text-secondary);
}
.paper-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--text-secondary);
}

.paper-actions {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}
.btn-primary {
  flex: 1;
  padding: 8px 12px;
  font-size: 13px;
  border-radius: 8px;
  border: none;
  background: var(--primary);
  color: #fff;
  cursor: pointer;
  transition: opacity 0.15s;
}
.btn-primary:hover { opacity: 0.9; }
.btn-outline {
  flex: 1;
  padding: 8px 12px;
  font-size: 13px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text);
  cursor: pointer;
  text-align: center;
  text-decoration: none;
  transition: border-color 0.15s;
}
.btn-outline:hover { border-color: var(--primary); color: var(--primary); }

.empty-state {
  text-align: center;
  padding: 48px;
  color: var(--text-secondary);
}

@media (max-width: 480px) {
  .paper-grid {
    grid-template-columns: 1fr;
  }
}
</style>

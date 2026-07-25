<script setup>
import { ref } from 'vue'
import { submitFeedback } from '../api'

const emit = defineEmits(['close'])
defineProps({ visible: Boolean })

const type = ref('suggestion')
const content = ref('')
const contact = ref('')
const submitting = ref(false)
const submitted = ref(false)
const error = ref('')

async function handleSubmit() {
  if (!content.value.trim()) {
    error.value = '请输入反馈内容'
    return
  }
  submitting.value = true
  error.value = ''
  try {
    await submitFeedback({
      type: type.value,
      content: content.value.trim(),
      contact: contact.value.trim() || null,
    })
    submitted.value = true
  } catch (e) {
    error.value = e.response?.data?.detail || '提交失败，请稍后重试'
  } finally {
    submitting.value = false
  }
}

function close() {
  type.value = 'suggestion'
  content.value = ''
  contact.value = ''
  submitted.value = false
  error.value = ''
  emit('close')
}
</script>

<template>
  <Teleport to="body">
    <div v-if="visible" class="modal-overlay" @click.self="close">
      <div class="feedback-card">
        <button class="close-btn" @click="close">&times;</button>

        <template v-if="submitted">
          <div class="success-state">
            <span class="check-icon">&#10004;</span>
            <h2>感谢反馈!</h2>
            <p>你的建议已收到，我会认真查看。</p>
            <button class="btn-primary" @click="close">关闭</button>
          </div>
        </template>

        <template v-else>
          <h2>提建议 / 反馈问题</h2>

          <div class="type-group">
            <button
              class="type-btn"
              :class="{ active: type === 'suggestion' }"
              @click="type = 'suggestion'"
            >&#128161; 建议</button>
            <button
              class="type-btn"
              :class="{ active: type === 'bug' }"
              @click="type = 'bug'"
            >&#128030; 问题反馈</button>
          </div>

          <form @submit.prevent="handleSubmit">
            <textarea
              v-model="content"
              class="content-input"
              rows="5"
              :placeholder="type === 'suggestion' ? '请描述你的建议或想法...' : '请描述遇到的问题...'"
              required
            ></textarea>

            <input
              v-model="contact"
              class="contact-input"
              placeholder="联系方式（选填，方便回复你）"
            />

            <p v-if="error" class="error">{{ error }}</p>

            <button class="btn-primary submit-btn" type="submit" :disabled="submitting">
              {{ submitting ? '提交中...' : '提交反馈' }}
            </button>
          </form>
        </template>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-overlay {
  position: fixed; inset: 0; z-index: 100;
  background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
}
.feedback-card {
  position: relative;
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 32px 28px 24px;
  max-width: 440px; width: 90%;
  color: var(--text);
}
.close-btn {
  position: absolute; top: 12px; right: 16px;
  background: none; border: none; color: var(--text-secondary);
  font-size: 22px; cursor: pointer; padding: 0; line-height: 1;
}
.close-btn:hover { color: var(--text); }
h2 { font-size: 1.25rem; margin-bottom: 16px; }

.type-group { display: flex; gap: 10px; margin-bottom: 14px; }
.type-btn {
  flex: 1; padding: 10px; border-radius: var(--radius);
  border: 1px solid var(--border); background: rgba(255,255,255,0.03);
  color: var(--text-secondary); font-size: 0.9rem; cursor: pointer;
  transition: all 0.15s;
}
.type-btn.active {
  border-color: var(--primary); background: rgba(99,102,241,0.15);
  color: var(--primary-light);
}
.type-btn:hover:not(.active) { border-color: rgba(255,255,255,0.2); }

.content-input {
  width: 100%; padding: 12px 14px; border-radius: var(--radius);
  border: 1px solid var(--border); background: rgba(255,255,255,0.04);
  color: var(--text); font-size: 0.95rem; resize: vertical;
  font-family: inherit; margin-bottom: 10px;
}
.content-input:focus { border-color: var(--primary); outline: none; }
.content-input::placeholder { color: var(--text-secondary); }

.contact-input {
  width: 100%; padding: 10px 14px; border-radius: var(--radius);
  border: 1px solid var(--border); background: rgba(255,255,255,0.04);
  color: var(--text); font-size: 0.9rem; margin-bottom: 10px;
}
.contact-input:focus { border-color: var(--primary); outline: none; }
.contact-input::placeholder { color: var(--text-secondary); }

.error { color: var(--danger); font-size: 0.85rem; margin-bottom: 8px; }
.submit-btn { width: 100%; padding: 11px; font-size: 1rem; }

.success-state { text-align: center; padding: 16px 0; }
.check-icon {
  display: inline-flex; align-items: center; justify-content: center;
  width: 56px; height: 56px; border-radius: 50%;
  background: rgba(52,211,153,0.15); color: var(--success);
  font-size: 28px; margin-bottom: 16px;
}
.success-state h2 { margin-bottom: 8px; }
.success-state p { color: var(--text-secondary); margin-bottom: 20px; font-size: 0.95rem; }
.success-state button { padding: 10px 40px; }
</style>

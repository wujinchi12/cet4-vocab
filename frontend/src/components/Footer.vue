<script setup>
import { ref } from 'vue'
import FeedbackModal from './FeedbackModal.vue'
import SupportModal from './SupportModal.vue'

const showFeedback = ref(false)
const showSupport = ref(false)
</script>

<template>
  <footer>
    <p>CET-4 词汇学习 &copy; 2026 吴瑾赤</p>
    <div class="footer-actions">
      <button class="footer-btn" @click="showFeedback = true">提建议</button>
      <button class="footer-btn" @click="showSupport = true">支持作者</button>
    </div>
  </footer>
  <FeedbackModal :visible="showFeedback" @close="showFeedback = false" />
  <SupportModal :visible="showSupport" @close="showSupport = false" />
</template>

<style scoped>
footer {
  text-align: center;
  padding: 24px;
  color: var(--text-secondary);
  font-size: 13px;
}
.footer-actions {
  display: flex; justify-content: center; gap: 12px; margin-top: 10px;
}
.footer-btn {
  background: none; border: 1px solid var(--border); border-radius: var(--radius);
  color: var(--text-secondary); padding: 4px 14px; font-size: 12px; cursor: pointer;
  transition: all 0.15s;
}
.footer-btn:hover { border-color: var(--primary); color: var(--primary-light); }
</style>

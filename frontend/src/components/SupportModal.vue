<script setup>
defineEmits(['close'])
defineProps({ visible: Boolean })
</script>

<template>
  <Teleport to="body">
    <div v-if="visible" class="modal-overlay" @click.self="$emit('close')" @keydown.escape="$emit('close')">
      <div class="support-card">
        <button class="close-btn" @click="$emit('close')">&times;</button>
        <div class="heart-icon">&#10084;</div>
        <h2>支持作者</h2>
        <p class="message">
          感谢你使用 <strong>CET-4 词汇学习</strong>！<br />
          如果这个工具对你的学习有帮助，<br />
          欢迎支持作者 <strong>吴瑾赤</strong> 继续创作。
        </p>
        <div class="qrcode-area">
          <img src="/qrcode.jpg" alt="赞赏码" class="qrcode-img" />
        </div>
        <p class="thanks">每一份支持都是前进的动力 &#127775;</p>
        <button class="btn-primary close-action" @click="$emit('close')">关闭</button>
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
.support-card {
  position: relative;
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 36px 32px 28px;
  max-width: 380px; width: 90%;
  text-align: center;
  color: var(--text);
}
.close-btn {
  position: absolute; top: 12px; right: 16px;
  background: none; border: none; color: var(--text-secondary);
  font-size: 24px; cursor: pointer; padding: 0; line-height: 1;
}
.close-btn:hover { color: var(--text); }
.heart-icon { font-size: 40px; margin-bottom: 8px; }
h2 { font-size: 1.4rem; margin-bottom: 12px; }
.message { font-size: 0.95rem; color: var(--text-secondary); line-height: 1.6; margin-bottom: 20px; }
.qrcode-area { margin-bottom: 16px; }
.qrcode-img {
  width: 180px; height: 180px; object-fit: cover;
  border-radius: 12px; border: 2px solid var(--border);
}
.thanks { font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 20px; }
.close-action { width: 100%; }
</style>

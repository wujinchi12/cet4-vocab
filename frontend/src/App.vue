<script setup>
import NavBar from './components/NavBar.vue'
import Footer from './components/Footer.vue'
import ParticleBackground from './components/ParticleBackground.vue'
</script>

<template>
  <ParticleBackground />
  <div class="app-content">
    <NavBar />
    <main>
      <router-view />
    </main>
    <Footer />
  </div>
</template>

<style scoped>
.app-content {
  position: relative;
  z-index: 1;
  margin-left: 210px;
}
@media (max-width: 768px) {
  .app-content {
    margin-left: 0;
    padding-bottom: 64px;
  }
}
</style>

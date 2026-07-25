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
}
</style>

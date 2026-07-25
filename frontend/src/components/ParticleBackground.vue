<template>
  <canvas ref="canvas" class="starry-canvas" />
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const canvas = ref(null)
let ctx = null
let stars = []
let animId = null
let w = 0, h = 0
let time = 0

const STAR_COUNT = 220

class Star {
  constructor() {
    this.x = Math.random() * w
    this.y = Math.random() * h
    this.baseR = Math.random() * 2.2 + 0.4
    // Each star has its own twinkle phase offset and speed
    this.twinklePhase = Math.random() * Math.PI * 2
    this.twinkleSpeed = Math.random() * 0.02 + 0.005
    this.twinkleAmp = Math.random() * 0.5 + 0.3
    // Slow drift
    this.driftVx = (Math.random() - 0.5) * 0.08
    this.driftVy = (Math.random() - 0.5) * 0.08
    // Color temperature: most white, some blue-ish, some yellow-ish
    const colorRand = Math.random()
    if (colorRand < 0.65) {
      this.color = [255, 255, 255]        // pure white
    } else if (colorRand < 0.85) {
      this.color = [180, 210, 255]        // cool blue
    } else {
      this.color = [255, 240, 200]        // warm yellow
    }
  }

  update() {
    this.x += this.driftVx
    this.y += this.driftVy
    if (this.x < -10) this.x = w + 10
    if (this.x > w + 10) this.x = -10
    if (this.y < -10) this.y = h + 10
    if (this.y > h + 10) this.y = -10
  }

  draw(t) {
    const twinkle = Math.sin(t * this.twinkleSpeed + this.twinklePhase)
    const alpha = 0.35 + this.twinkleAmp * 0.55 * (twinkle * 0.5 + 0.5)
    const r = this.baseR * (0.8 + 0.2 * (twinkle * 0.5 + 0.5))

    ctx.beginPath()
    ctx.arc(this.x, this.y, r, 0, Math.PI * 2)
    const [cr, cg, cb] = this.color
    ctx.fillStyle = `rgba(${cr},${cg},${cb},${alpha})`
    ctx.fill()

    // Glow halo for larger stars
    if (this.baseR > 1.5) {
      const glow = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, r * 3)
      glow.addColorStop(0, `rgba(${cr},${cg},${cb},${alpha * 0.5})`)
      glow.addColorStop(1, `rgba(${cr},${cg},${cb},0)`)
      ctx.beginPath()
      ctx.arc(this.x, this.y, r * 3, 0, Math.PI * 2)
      ctx.fillStyle = glow
      ctx.fill()
    }
  }
}

function init() {
  w = window.innerWidth
  h = window.innerHeight
  canvas.value.width = w
  canvas.value.height = h
  ctx = canvas.value.getContext('2d')
  stars = Array.from({ length: STAR_COUNT }, () => new Star())
}

function drawBackground() {
  // Deep space gradient
  const bg = ctx.createRadialGradient(w * 0.3, h * 0.3, 0, w * 0.5, h * 0.5, Math.max(w, h) * 0.7)
  bg.addColorStop(0, '#0a0a1a')
  bg.addColorStop(0.4, '#080820')
  bg.addColorStop(0.7, '#050515')
  bg.addColorStop(1, '#020210')
  ctx.fillStyle = bg
  ctx.fillRect(0, 0, w, h)

  // Subtle nebula patches
  const nebula1 = ctx.createRadialGradient(w * 0.2, h * 0.3, 0, w * 0.2, h * 0.3, w * 0.25)
  nebula1.addColorStop(0, 'rgba(20, 10, 60, 0.15)')
  nebula1.addColorStop(1, 'rgba(20, 10, 60, 0)')
  ctx.fillStyle = nebula1
  ctx.fillRect(0, 0, w, h)

  const nebula2 = ctx.createRadialGradient(w * 0.8, h * 0.7, 0, w * 0.8, h * 0.7, w * 0.3)
  nebula2.addColorStop(0, 'rgba(10, 20, 50, 0.12)')
  nebula2.addColorStop(1, 'rgba(10, 20, 50, 0)')
  ctx.fillStyle = nebula2
  ctx.fillRect(0, 0, w, h)
}

function animate() {
  time++
  drawBackground()

  for (const star of stars) {
    star.update()
    star.draw(time)
  }

  animId = requestAnimationFrame(animate)
}

function onResize() {
  w = window.innerWidth
  h = window.innerHeight
  canvas.value.width = w
  canvas.value.height = h
  // Re-seed stars for new dimensions
  stars = Array.from({ length: STAR_COUNT }, () => new Star())
}

onMounted(() => {
  init()
  animate()
  window.addEventListener('resize', onResize)
})

onUnmounted(() => {
  cancelAnimationFrame(animId)
  window.removeEventListener('resize', onResize)
})
</script>

<style scoped>
.starry-canvas {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}
</style>

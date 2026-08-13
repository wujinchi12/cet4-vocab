import { ref } from 'vue'

const level = ref(localStorage.getItem('cet_level') || 'cet4')

export function useLevel() {
  function setLevel(value) {
    level.value = value
    localStorage.setItem('cet_level', value)
  }
  return { level, setLevel }
}

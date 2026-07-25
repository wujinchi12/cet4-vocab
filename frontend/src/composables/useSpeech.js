import { ref } from 'vue'

export function useSpeech() {
  const speaking = ref(false)
  const supported = ref(typeof window !== 'undefined' && 'speechSynthesis' in window)

  function speak(text, lang = 'en-US') {
    if (!supported.value || !text) return
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = lang
    utterance.rate = 0.85
    speaking.value = true
    utterance.onend = () => { speaking.value = false }
    utterance.onerror = () => { speaking.value = false }
    window.speechSynthesis.speak(utterance)
  }

  return { speak, speaking, supported }
}

import { ref, computed } from 'vue'
import { getFavorites, toggleFavorite } from '../api'

const favoritedIds = ref(new Set())
const loaded = ref(false)

export function useFavorites() {
  async function load() {
    try {
      const allIds = []
      let page = 1
      while (true) {
        const { data } = await getFavorites({ page, size: 500 })
        for (const item of data.items) allIds.push(item.word_id)
        if (page * 500 >= data.total) break
        page++
      }
      favoritedIds.value = new Set(allIds)
    } catch { /* ignore */ }
    loaded.value = true
  }

  if (!loaded.value) load()

  function isFavorited(wordId) {
    return favoritedIds.value.has(wordId)
  }

  async function toggle(wordId) {
    try {
      const { data } = await toggleFavorite(wordId)
      const set = new Set(favoritedIds.value)
      if (data.favorited) set.add(wordId)
      else set.delete(wordId)
      favoritedIds.value = set
    } catch { /* ignore */ }
  }

  return { favoritedIds, loaded, load, isFavorited, toggle }
}

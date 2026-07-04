import { defineStore } from 'pinia'
import { ref, watchEffect } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const saved = localStorage.getItem('theme') === 'dark'
  const dark = ref(saved)

  // 立即应用，不等组件挂载
  if (saved) document.documentElement.classList.add('dark')

  function toggle() {
    dark.value = !dark.value
    localStorage.setItem('theme', dark.value ? 'dark' : 'light')
  }

  watchEffect(() => {
    document.documentElement.classList.toggle('dark', dark.value)
  })

  return { dark, toggle }
})

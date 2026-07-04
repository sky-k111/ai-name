<template>
  <router-view />
</template>

<script setup lang="ts">
import { useThemeStore } from './stores/theme'
// 全局初始化主题，确保所有页面刷新后深色模式不丢失
useThemeStore()
</script>

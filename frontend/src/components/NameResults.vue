<template>
  <div class="w-full max-w-[920px] mx-auto">
    <!-- 空状态：初始 -->
    <div
      v-if="state === 'idle'"
      class="text-center py-20 transition-opacity duration-500"
    >
      <p class="text-[17px] text-[#aeaeb2]">
        输入信息后点击「生成名字」，AI 将为你取名
      </p>
    </div>

    <!-- 加载中：骨架屏 -->
    <NameCardSkeleton v-if="state === 'loading'" />

    <!-- 空结果 -->
    <div
      v-if="state === 'empty'"
      class="text-center py-16 transition-opacity duration-500"
    >
      <p class="text-[17px] text-[#86868b] mb-3">
        暂未生成到合适的名字
      </p>
      <p class="text-[15px] text-[#aeaeb2]">
        请调整取名要求后重试
      </p>
    </div>

    <!-- 错误 -->
    <div
      v-if="state === 'error'"
      class="text-center py-16 transition-opacity duration-500"
    >
      <p class="text-[17px] text-[#ff3b30] mb-3">
        {{ errorMessage }}
      </p>
      <button
        class="text-[15px] text-[#0071e3] hover:underline transition-colors"
        @click="emit('retry')"
      >
        点击重试
      </button>
    </div>

    <!-- 成功：名字卡片 -->
    <NameGallery v-if="state === 'success'" :names="names" @favorite="emit('favorite', $event)" />
  </div>
</template>

<script setup lang="ts">
import type { FavoriteAction, LoadState, NameItem } from '../types'
import NameCardSkeleton from './NameCardSkeleton.vue'
import NameGallery from './NameGallery.vue'

const props = defineProps<{
  names: NameItem[]
  state: LoadState
  errorMessage: string
}>()
const emit = defineEmits<{
  retry: []
  favorite: [action: FavoriteAction]
}>()
</script>

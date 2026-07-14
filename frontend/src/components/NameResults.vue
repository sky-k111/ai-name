<template>
  <div class="w-full max-w-[820px] mx-auto">
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
    <div v-if="state === 'loading'" class="space-y-4">
      <div
        v-for="i in 5" :key="i"
        class="bg-white/80 backdrop-blur-xl rounded-2xl p-6
               shadow-[0_2px_12px_rgba(0,0,0,0.03)] border border-[#d2d2d7]/30
               animate-pulse"
        :style="{ animationDelay: `${(i - 1) * 0.1}s` }"
      >
        <div class="h-[28px] w-24 bg-[#e8e8ed] rounded mb-3" />
        <div class="h-[18px] w-full bg-[#e8e8ed] rounded mb-2" />
        <div class="h-[16px] w-48 bg-[#e8e8ed] rounded" />
      </div>
    </div>

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
    <div v-if="state === 'success'" class="space-y-5">
      <RecommendedNameCard
        v-for="(name, idx) in names"
        :key="name.full_name"
        :name="name"
        :index="idx"
        @favorite="emit('favorite', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { LoadState, NameItem } from '../types'
import RecommendedNameCard from './RecommendedNameCard.vue'

const props = defineProps<{
  names: NameItem[]
  state: LoadState
  errorMessage: string
}>()
const emit = defineEmits<{
  retry: []
  favorite: [name: NameItem]
}>()
</script>

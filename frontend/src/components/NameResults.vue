<template>
  <div class="w-full max-w-[680px] mx-auto">
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
    <TransitionGroup
      v-if="state === 'success'"
      name="card"
      tag="div"
      class="space-y-3"
      appear
    >
      <div
        v-for="(name, idx) in names"
        :key="name.full_name"
        class="bg-white/80 backdrop-blur-xl rounded-2xl p-6
               shadow-[0_2px_12px_rgba(0,0,0,0.03)] border border-[#d2d2d7]/30
               transition-all duration-300 hover:shadow-[0_4px_20px_rgba(0,0,0,0.06)]
               hover:-translate-y-[1px]"
        :style="{ transitionDelay: `${idx * 0.1}s` }"
      >
        <!-- 名字 -->
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-[28px] font-semibold text-[#1d1d1f] tracking-tight">
            {{ name.full_name }}
          </h3>
          <div class="flex gap-3">
            <button class="text-[13px] text-[#86868b] hover:text-[#0071e3] transition-colors" @click.stop="speak(name.full_name)">试读</button>
            <button class="text-[14px] text-[#aeaeb2] hover:text-[#0071e3] transition-colors" @click.stop="emit('favorite', name)">收藏</button>
          </div>
        </div>

        <!-- 寓意 -->
        <p class="text-[15px] text-[#3a3a3c] leading-relaxed mb-3">
          {{ name.meaning }}
        </p>

        <!-- 元信息 -->
        <div class="flex items-center gap-4 text-[13px] text-[#aeaeb2]">
          <span v-if="name.wuxing" class="flex items-center gap-1">
            <span class="w-1 h-1 rounded-full bg-[#aeaeb2]" />
            五行 {{ name.wuxing }}
          </span>
          <span v-if="name.source" class="flex items-center gap-1">
            <span class="w-1 h-1 rounded-full bg-[#aeaeb2]" />
            出处 {{ name.source }}
          </span>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import type { LoadState, NameItem } from '../types'

defineProps<{
  names: NameItem[]
  state: LoadState
  errorMessage: string
}>()

const emit = defineEmits<{
  retry: []
  favorite: [name: NameItem]
}>()

function speak(text: string) {
  const u = new SpeechSynthesisUtterance(text)
  u.lang = 'zh-CN'; u.rate = 0.8
  speechSynthesis.speak(u)
}
</script>

<style scoped>
/* 卡片入场动画 */
.card-enter-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.card-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
</style>

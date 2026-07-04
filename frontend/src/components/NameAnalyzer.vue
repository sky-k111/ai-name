<template>
  <div class="w-full max-w-[680px] mx-auto">
    <!-- 输入卡片 -->
    <div class="bg-white/80 backdrop-blur-xl rounded-2xl p-6
                shadow-[0_4px_24px_rgba(0,0,0,0.04)] border border-[#d2d2d7]/30 mb-8">
      <div class="flex items-center gap-4">
        <input
          v-model="name"
          type="text"
          maxlength="10"
          placeholder="请输入一个名字"
          class="flex-1 bg-transparent text-[20px] text-[#1d1d1f] placeholder-[#aeaeb2]
                 outline-none"
          :disabled="loading"
          @keydown.enter="handleAnalyze"
        />
        <div class="flex gap-3 items-center">
          <button
            v-for="g in [{v:'male',l:'男'},{v:'female',l:'女'}]" :key="g.v"
            class="text-[15px] transition-colors"
            :class="gender === g.v ? 'text-[#0071e3] font-medium' : 'text-[#86868b]'"
            :disabled="loading"
            @click="gender = g.v"
          >
            {{ g.l }}
          </button>
          <span class="w-px h-5 bg-[#d2d2d7]" />
          <div class="flex flex-col items-center">
            <button
              class="px-6 py-2.5 bg-[#0071e3] text-white text-[15px] font-medium
                     rounded-full transition-all duration-300
                     hover:scale-[1.02] active:scale-[0.98]
                     disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="!name.trim() || loading"
              @click="handleAnalyze"
            >
              <span v-if="!loading">分析</span>
              <span v-else class="flex items-center gap-2">
                <span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                分析中…
              </span>
            </button>
            <p v-if="!loading" class="text-[12px] text-[#aeaeb2] mt-1">预计 5-10 秒</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载 -->
    <div v-if="loading" class="bg-white/80 backdrop-blur-xl rounded-2xl p-8 animate-pulse
                    shadow-[0_2px_12px_rgba(0,0,0,0.03)]">
      <div class="h-8 w-32 bg-[#e8e8ed] rounded mb-4" />
      <div class="h-4 w-full bg-[#e8e8ed] rounded mb-2" />
      <div class="h-4 w-2/3 bg-[#e8e8ed] rounded" />
    </div>

    <!-- 错误 -->
    <div v-else-if="error" class="text-center py-10">
      <p class="text-[17px] text-[#ff3b30] mb-3">{{ error }}</p>
      <button class="text-[15px] text-[#0071e3] hover:underline" @click="handleAnalyze">重试</button>
    </div>

    <!-- 结果 -->
    <div v-else-if="result" class="bg-white/80 backdrop-blur-xl rounded-2xl p-8
                    shadow-[0_2px_12px_rgba(0,0,0,0.03)] border border-[#d2d2d7]/30
                    transition-all duration-500">
      <!-- 评分 -->
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-[28px] font-semibold text-[#1d1d1f]">"{{ name }}"</h2>
        <div class="text-right">
          <p class="text-[48px] font-semibold text-[#0071e3] leading-none">{{ result.score }}</p>
          <p class="text-[13px] text-[#86868b]">综合评分</p>
        </div>
      </div>

      <!-- 评价 -->
      <p class="text-[17px] text-[#3a3a3c] leading-relaxed mb-6">{{ result.summary }}</p>

      <!-- 属性 -->
      <div class="grid grid-cols-3 gap-4 mb-6">
        <div class="bg-[#f5f5f7] rounded-xl p-4">
          <p class="text-[13px] text-[#86868b] mb-1">名字寓意</p>
          <p class="text-[15px] text-[#1d1d1f]">{{ result.meaning }}</p>
        </div>
        <div class="bg-[#f5f5f7] rounded-xl p-4">
          <p class="text-[13px] text-[#86868b] mb-1">五行属性</p>
          <p class="text-[15px] text-[#1d1d1f]">{{ result.wuxing }}</p>
        </div>
        <div class="bg-[#f5f5f7] rounded-xl p-4">
          <p class="text-[13px] text-[#86868b] mb-1">文化出处</p>
          <p class="text-[15px] text-[#1d1d1f]">{{ result.source }}</p>
        </div>
      </div>

      <!-- 优缺点 -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <p class="text-[13px] text-green-600 font-medium mb-2">✓ 优点</p>
          <ul class="space-y-1">
            <li v-for="p in result.pros" :key="p" class="text-[14px] text-[#3a3a3c]">· {{ p }}</li>
          </ul>
        </div>
        <div>
          <p class="text-[13px] text-[#86868b] font-medium mb-2">可改进</p>
          <ul class="space-y-1">
            <li v-for="c in result.cons" :key="c" class="text-[14px] text-[#3a3a3c]">· {{ c }}</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

const name = ref('')
const gender = ref('male')
const loading = ref(false)
const error = ref('')
const result = ref<any>(null)

async function handleAnalyze() {
  if (!name.value.trim()) return
  loading.value = true
  error.value = ''
  result.value = null
  try {
    const token = localStorage.getItem('ai_naming_token')
    const res = await axios.post('/api/naming/analyze', {
      full_name: name.value.trim(),
      gender: gender.value,
    }, { headers: { Authorization: `Bearer ${token}` } })
    result.value = res.data
  } catch (e: any) {
    error.value = e.response?.data?.detail?.message || e.message || '分析失败'
  } finally {
    loading.value = false
  }
}
</script>

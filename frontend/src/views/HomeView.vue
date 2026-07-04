<template>
  <div class="min-h-screen bg-[#f5f5f7]">
    <!-- 顶部导航 -->
    <nav class="flex items-center justify-end max-w-[800px] mx-auto px-6 py-4">
      <template v-if="authStore.isLoggedIn">
        <span class="text-[14px] text-[#86868b] mr-4">{{ authStore.username }}</span>
        <button class="text-[16px] text-[#86868b] hover:text-[#1d1d1f] transition-colors mr-3" @click="theme.toggle()" :title="theme.dark?'切换浅色':'切换深色'">
          <svg v-if="theme.dark" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="5"/><path stroke-linecap="round" d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
          <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>
        </button>
        <button class="text-[14px] text-[#86868b] hover:text-[#1d1d1f] transition-colors mr-3" @click="$router.push('/balance')">钱包</button>
        <button class="text-[14px] text-[#86868b] hover:text-[#1d1d1f] transition-colors mr-3" @click="$router.push('/favorites')">收藏</button>
        <button class="text-[14px] text-[#86868b] hover:text-[#1d1d1f] transition-colors mr-4" @click="$router.push('/profile')">个人中心</button>
        <button
          v-if="authStore.isAdmin"
          class="text-[14px] text-[#86868b] hover:text-[#1d1d1f] transition-colors"
          @click="$router.push('/admin')"
        >
          管理后台
        </button>
        <button
          class="text-[14px] text-[#86868b] hover:text-[#1d1d1f] transition-colors ml-4"
          @click="$router.push('/history')"
        >
          历史记录
        </button>
        <button
          class="ml-4 text-[14px] text-[#86868b] hover:text-[#ff3b30] transition-colors"
          @click="handleLogout"
        >
          退出登录
        </button>
      </template>
      <template v-else>
        <button
          class="text-[14px] text-[#0071e3] hover:underline transition-colors"
          @click="$router.push('/login')"
        >
          登录
        </button>
      </template>
    </nav>

    <div class="max-w-[800px] mx-auto px-6 pb-16 min-h-[600px]">
      <!-- 标题 -->
      <header class="text-center mb-10">
        <h1 class="text-[36px] md:text-[44px] font-semibold text-[#1d1d1f]
                   tracking-tight leading-tight">
          AI 智能取名
        </h1>

        <!-- 模式切换 -->
        <div class="flex justify-center gap-1 mt-4 bg-[#e8e8ed] rounded-full p-1 w-fit mx-auto flex-wrap">
          <button v-for="m in modes" :key="m.key" class="px-4 py-1.5 rounded-full text-[13px] font-medium transition-all duration-300"
            :class="mode === m.key ? 'bg-white text-[#1d1d1f] shadow-sm' : 'text-[#86868b]'"
            @click="mode = m.key">
            {{ m.label }}
            <span v-if="m.fee" class="ml-1 text-[11px] opacity-50">{{ m.fee }}</span>
          </button>
        </div>
      </header>

      <!-- 名字分析 -->
      <section v-show="mode === 'analyze'" class="mb-10"><NameAnalyzer /></section>

      <!-- 名字对比 -->
      <section v-show="mode === 'compare'" class="mb-10"><CompareNames /></section>

      <!-- 精品取名 -->
      <section v-show="mode === 'premium'" class="mb-10"><PremiumNaming /></section>

      <div v-show="mode === 'name'">

      <!-- 表单 -->
      <section class="mb-10">
        <NameForm
          v-model="formData"
          :loading="isGenerating"
          :disabled="isGenerating"
          @submit="handleGenerate"
        />
      </section>

      <!-- 结果 -->
      <section v-if="showResults" class="mb-10">
        <NameResults
          :names="names"
          :state="resultState"
          :error-message="errorMessage"
          @retry="handleRetry"
          @favorite="handleFavorite"
        />
      </section>

      <!-- 微调 -->
      <section v-if="showRefine" class="mb-10">
        <RefineChat
          :history="chatHistory"
          :loading="isRefining"
          :disabled="isRefining"
          @send="handleRefine"
        />
      </section>

      </div>

      <!-- 底部留白 -->
      <footer class="h-16" />
    </div>

    <!-- Toast -->
    <Transition name="toast">
      <div
        v-if="toast"
        class="fixed top-6 left-1/2 -translate-x-1/2 px-5 py-3 rounded-full
               text-[15px] font-medium shadow-[0_4px_16px_rgba(0,0,0,0.12)]
               backdrop-blur-xl z-50"
        :class="toast.type === 'error'
          ? 'bg-[#ff3b30]/90 text-white'
          : 'bg-[#1d1d1f]/90 text-white'"
      >
        {{ toast.message }}
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useThemeStore } from '../stores/theme'
import type { GenerateRequest, NameItem, ChatMessage, LoadState } from '../types'
import { generateNames, refineNames, addFavorite } from '../api'
import NameForm from '../components/NameForm.vue'
import NameResults from '../components/NameResults.vue'
import RefineChat from '../components/RefineChat.vue'
import NameAnalyzer from '../components/NameAnalyzer.vue'
import CompareNames from '../components/CompareNames.vue'
import PremiumNaming from '../components/PremiumNaming.vue'

const router = useRouter()
const authStore = useAuthStore()
const theme = useThemeStore()
const mode = ref('name')
const modes = [
  { key: 'name', label: '取名', fee: '免费' },
  { key: 'analyze', label: '名字分析', fee: '¥1' },
  { key: 'compare', label: '名字对比', fee: '¥1' },
  { key: 'premium', label: '精品取名', fee: '¥2' },
]

// ── 状态 ────────────────────────────────────────────────────

const formData = ref<GenerateRequest>({
  surname: '',
  gender: 'male',
  birthday: '',
  birth_time: '',
  style: '',
  expectations: '',
})

const names = ref<NameItem[]>([])
const resultState = ref<LoadState>('idle')
const errorMessage = ref('')
const conversationId = ref('')
const chatHistory = ref<ChatMessage[]>([])
const isGenerating = ref(false)
const isRefining = ref(false)
const toast = ref<{ type: 'info' | 'error'; message: string } | null>(null)

// ── 计算属性 ────────────────────────────────────────────────

const showResults = computed(() => resultState.value !== 'idle')
const showRefine = computed(() => resultState.value === 'success')

// ── Toast ───────────────────────────────────────────────────

function showToast(message: string, type: 'info' | 'error' = 'info') {
  toast.value = { type, message }
  setTimeout(() => { toast.value = null }, 3000)
}

// ── 请求逻辑 ────────────────────────────────────────────────

async function handleGenerate(data: GenerateRequest) {
  formData.value = { ...data }
  isGenerating.value = true
  resultState.value = 'loading'
  names.value = []
  errorMessage.value = ''
  chatHistory.value = []

  try {
    const res = await generateNames(data)
    conversationId.value = res.conversation_id
    names.value = res.names
    resultState.value = res.names.length > 0 ? 'success' : 'empty'

    if (res.names.length > 0) {
      // 添加 AI 消息到对话历史
      const summary = res.names.map(n => n.full_name).join('、')
      chatHistory.value.push({
        role: 'assistant',
        content: `为你推荐：${summary}。你觉得怎么样？`,
      })
    }
  } catch (e: any) {
    errorMessage.value = e.message || '生成失败，请重试'
    resultState.value = 'error'
    showToast(errorMessage.value, 'error')
  } finally {
    isGenerating.value = false
  }
}

async function handleRefine(feedback: string) {
  isRefining.value = true

  // 添加用户消息
  chatHistory.value.push({ role: 'user', content: feedback })

  try {
    const res = await refineNames({
      conversation_id: conversationId.value,
      original_request: formData.value,
      history: chatHistory.value.slice(0, -1), // 不含刚加的 user 消息
      feedback,
    })

    names.value = res.names
    resultState.value = res.names.length > 0 ? 'success' : 'empty'

    if (res.names.length > 0) {
      const summary = res.names.map(n => n.full_name).join('、')
      chatHistory.value.push({
        role: 'assistant',
        content: `根据你的反馈，调整为：${summary}。还需要调整吗？`,
      })
    }
  } catch (e: any) {
    errorMessage.value = e.message || '微调失败，请重试'
    showToast(errorMessage.value, 'error')
    // 移除刚才添加的失败 user 消息
    chatHistory.value.pop()
  } finally {
    isRefining.value = false
  }
}

function handleRetry() {
  handleGenerate(formData.value)
}

async function handleFavorite(name: any) {
  try { await addFavorite(name.full_name, name); showToast('已收藏', 'info') } catch(e:any) { showToast(e.message || '收藏失败', 'error') }
}

function handleLogout() {
  authStore.clearAuth()
  router.push('/login')
}
</script>

<style scoped>
.toast-enter-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.toast-leave-active {
  transition: all 0.25s ease-in;
}
.toast-enter-from {
  opacity: 0;
  transform: translateY(-12px);
}
.toast-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>

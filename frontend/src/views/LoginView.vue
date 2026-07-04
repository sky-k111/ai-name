<template>
  <div class="min-h-screen bg-[#f5f5f7] flex items-center justify-center px-6">
    <div class="w-full max-w-[400px]">
      <!-- 标题 -->
      <div class="text-center mb-10">
        <h1 class="text-[28px] font-semibold text-[#1d1d1f] tracking-tight">
          {{ isRegister ? '创建账号' : '登录' }}
        </h1>
        <p class="mt-2 text-[15px] text-[#86868b]">
          {{ isRegister ? '注册后开始取名' : '登录查看取名历史' }}
        </p>
      </div>

      <!-- 卡片 -->
      <div
        class="bg-white/80 backdrop-blur-xl rounded-2xl p-8
               shadow-[0_4px_24px_rgba(0,0,0,0.04)] border border-[#d2d2d7]/30"
      >
        <!-- 错误提示 -->
        <div
          v-if="error"
          class="mb-4 px-4 py-3 bg-[#ff3b30]/10 text-[#ff3b30] text-[14px] rounded-xl"
        >
          {{ error }}
        </div>

        <!-- 用户名 -->
        <div class="mb-5">
          <label class="block text-[13px] font-medium text-[#86868b] mb-2 tracking-wide">
            用户名
          </label>
          <input
            v-model="form.username"
            type="text"
            maxlength="50"
            placeholder="请输入用户名"
            class="w-full px-4 py-3 bg-[#f5f5f7] rounded-xl text-[17px] text-[#1d1d1f]
                   placeholder-[#aeaeb2] outline-none border border-transparent
                   focus:border-[#0071e3] transition-colors"
            :disabled="loading"
            @keydown.enter="handleSubmit"
          />
        </div>

        <!-- 密码 -->
        <div class="mb-6">
          <label class="block text-[13px] font-medium text-[#86868b] mb-2 tracking-wide">
            密码
          </label>
          <div class="relative">
            <input
              v-model="form.password"
              :type="showPw ? 'text' : 'password'"
              maxlength="100"
              :placeholder="isRegister ? '请输入密码（至少6位）' : '请输入密码'"
              class="w-full px-4 py-3 pr-10 bg-[#f5f5f7] rounded-xl text-[17px] text-[#1d1d1f]
                     placeholder-[#aeaeb2] outline-none border border-transparent
                     focus:border-[#0071e3] transition-colors"
              :disabled="loading"
              @keydown.enter="handleSubmit"
            />
            <button type="button" class="absolute right-3 top-1/2 -translate-y-1/2 text-[#aeaeb2] hover:text-[#1d1d1f] transition-colors" @click="showPw = !showPw">
              <svg v-if="showPw" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
              <svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
            </button>
          </div>
          <!-- 密码强度 -->
          <div v-if="isRegister && form.password" class="mt-2">
            <div class="flex gap-1">
              <div class="h-1 flex-1 rounded-full transition-colors" :class="strength >= 1 ? (strength===1?'bg-red-400':strength===2?'bg-yellow-400':'bg-green-400') : 'bg-[#e8e8ed]'"/>
              <div class="h-1 flex-1 rounded-full transition-colors" :class="strength >= 2 ? (strength===2?'bg-yellow-400':'bg-green-400') : 'bg-[#e8e8ed]'"/>
              <div class="h-1 flex-1 rounded-full transition-colors" :class="strength >= 3 ? 'bg-green-400' : 'bg-[#e8e8ed]'"/>
            </div>
            <p class="text-[12px] mt-1" :class="strength===1?'text-red-400':strength===2?'text-yellow-500':'text-green-500'">{{ strengthLabel }}</p>
          </div>
        </div>

        <!-- 按钮 -->
        <button
          class="w-full py-3 bg-[#0071e3] text-white text-[17px] font-medium
                 rounded-full transition-all duration-300
                 hover:scale-[1.01] hover:shadow-[0_4px_16px_rgba(0,113,227,0.35)]
                 active:scale-[0.98]
                 disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="!canSubmit || loading"
          @click="handleSubmit"
        >
          <span v-if="!loading">{{ isRegister ? '注册' : '登录' }}</span>
          <span v-else class="flex items-center justify-center gap-2">
            <span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full
                         animate-spin" />
            处理中…
          </span>
        </button>

        <!-- 忘记密码 -->
        <p v-if="!isRegister" class="mt-2 text-center">
          <button class="text-[14px] text-[#86868b] hover:text-[#0071e3] transition-colors" @click="showReset = true">
            忘记密码？
          </button>
        </p>

        <!-- 切换 -->
        <p class="mt-3 text-center text-[14px] text-[#86868b]">
          {{ isRegister ? '已有账号？' : '没有账号？' }}
          <button class="text-[#0071e3] hover:underline transition-colors" :disabled="loading" @click="toggleMode">
            {{ isRegister ? '去登录' : '去注册' }}
          </button>
        </p>
      </div>
    </div>

    <!-- 忘记密码弹窗 -->
    <div v-if="showReset" class="fixed inset-0 bg-black/30 backdrop-blur-sm z-50 flex items-center justify-center" @click.self="showReset = false">
      <div class="bg-white rounded-2xl p-8 w-full max-w-[380px] mx-4 shadow-xl">
        <h2 class="text-[20px] font-semibold text-[#1d1d1f] mb-4">重置密码</h2>
        <div v-if="resetError" class="mb-3 text-[14px] text-[#ff3b30]">{{ resetError }}</div>
        <div v-if="resetOk" class="mb-3 text-[14px] text-green-600">{{ resetOk }}</div>

        <input v-model="resetEmail" type="email" placeholder="输入绑定的邮箱" class="w-full px-4 py-3 bg-[#f5f5f7] rounded-xl text-[17px] outline-none border border-transparent focus:border-[#0071e3] mb-3" :disabled="resetStep > 1" />
        <button v-if="resetStep === 1" class="w-full py-3 bg-[#0071e3] text-white rounded-full font-medium hover:scale-[1.01] transition-all disabled:opacity-50"
          :disabled="!resetEmail || resetCountdown > 0" @click="handleForgotPassword">
          {{ resetCountdown > 0 ? `${resetCountdown}秒后重试` : '发送验证码' }}
        </button>

        <div v-if="resetStep >= 2" class="space-y-3">
          <input v-model="resetCode" maxlength="6" placeholder="输入6位验证码" class="w-full px-4 py-3 bg-[#f5f5f7] rounded-xl text-[17px] text-center tracking-[8px] outline-none border border-transparent focus:border-[#0071e3]" />
          <input v-model="resetNewPw" type="password" placeholder="新密码（至少6位）" class="w-full px-4 py-3 bg-[#f5f5f7] rounded-xl text-[17px] outline-none border border-transparent focus:border-[#0071e3]" />
          <button class="w-full py-3 bg-[#0071e3] text-white rounded-full font-medium hover:scale-[1.01] transition-all disabled:opacity-50"
            :disabled="resetCode.length !== 6 || resetNewPw.length < 6" @click="handleResetPassword">
            重置密码
          </button>
        </div>

        <button class="mt-4 w-full text-[14px] text-[#86868b] hover:text-[#1d1d1f] transition-colors" @click="showReset = false">取消</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { login, register, forgotPassword, resetPassword } from '../api'

const router = useRouter()
const authStore = useAuthStore()

const isRegister = ref(false)
const loading = ref(false)
const error = ref('')
const showPw = ref(false)
let errorTimer: any = null

function showError(msg: string) {
  error.value = msg
  clearTimeout(errorTimer)
  errorTimer = setTimeout(() => { error.value = '' }, 5000)
}

// 忘记密码
const showReset = ref(false)
const resetStep = ref(1)
const resetEmail = ref('')
const resetCode = ref('')
const resetNewPw = ref('')
const resetError = ref('')
const resetOk = ref('')
let resetTimer: any = null

function showResetError(msg: string) {
  resetError.value = msg
  clearTimeout(resetTimer)
  resetTimer = setTimeout(() => { resetError.value = '' }, 5000)
}
function showResetOk(msg: string) {
  resetOk.value = msg
  clearTimeout(resetTimer)
  resetTimer = setTimeout(() => { resetOk.value = '' }, 5000)
}
const sendingReset = ref(false)
const resetCountdown = ref(0)

const form = reactive({
  username: '',
  password: '',
})

const canSubmit = computed(() => {
  const hasUsername = form.username.trim().length >= 2
  const hasPassword = isRegister.value
    ? form.password.length >= 6
    : form.password.length >= 1
  return hasUsername && hasPassword
})

const strength = computed(() => {
  const p = form.password
  if (p.length < 6) return 0
  const hasLetter = /[a-zA-Z]/.test(p)
  const hasDigit = /\d/.test(p)
  const hasSpecial = /[^a-zA-Z0-9]/.test(p)
  if (hasLetter && hasDigit && hasSpecial) return 3  // 强
  if (hasLetter && hasDigit) return 2                 // 中
  return 1                                              // 弱
})

const strengthLabel = computed(() => {
  const labels = ['', '弱', '中', '强']
  return labels[strength.value] || ''
})

function toggleMode() {
  isRegister.value = !isRegister.value
  clearTimeout(errorTimer)
  error.value = ''
}

function startResetCountdown() {
  resetCountdown.value = 60
  const timer = setInterval(() => { resetCountdown.value--; if (resetCountdown.value <= 0) clearInterval(timer) }, 1000)
}

async function handleForgotPassword() {
  resetError.value = ''; resetOk.value = ''
  try {
    await forgotPassword(resetEmail.value)
    resetStep.value = 2
    showResetOk('验证码已发送，请查收邮件')
    startResetCountdown()
  } catch (e: any) { showResetError(e.message) }
}

async function handleResetPassword() {
  resetError.value = ''; resetOk.value = ''
  try {
    await resetPassword(resetEmail.value, resetCode.value, resetNewPw.value)
    showResetOk('密码已重置！请使用新密码登录')
    setTimeout(() => { showReset.value = false; resetStep.value = 1; resetCode.value = ''; resetNewPw.value = '' }, 2000)
  } catch (e: any) { showResetError(e.message) }
}

async function handleSubmit() {
  if (!canSubmit.value) return
  loading.value = true
  error.value = ''

  try {
    const fn = isRegister.value ? register : login
    const res = await fn(form.username.trim(), form.password)
    authStore.setAuth(res.token, res.username, res.role || 'user')
    router.push('/')
  } catch (e: any) {
    const msg = e.response?.data?.detail || e.message || '请求失败'
    showError(msg)
  } finally {
    loading.value = false
  }
}
</script>

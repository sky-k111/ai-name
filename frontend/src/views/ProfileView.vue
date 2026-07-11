<template>
  <div class="min-h-screen bg-[#f6f3ec]">
    <div class="max-w-[680px] mx-auto px-6 py-16">

      <!-- 头部 -->
      <div class="flex items-center justify-between mb-12">
        <h1 class="text-[32px] font-semibold text-[#1d1d1f] tracking-tight">个人中心</h1>
        <button class="text-[15px] text-[#0071e3] hover:underline transition-colors" @click="$router.push('/')">← 返回</button>
      </div>

      <!-- 成功提示 -->
      <div v-if="successMsg" class="mb-4 px-4 py-3 bg-green-100 text-green-700 text-[14px] rounded-xl">{{ successMsg }}</div>
      <!-- 错误提示 -->
      <div v-if="error" class="mb-4 px-4 py-3 bg-[#ff3b30]/10 text-[#ff3b30] text-[14px] rounded-xl">{{ error }}</div>

      <!-- Tab -->
      <div class="flex gap-6 mb-8 border-b border-[#d2d2d7]/40">
        <button v-for="t in tabs" :key="t.key" class="text-[15px] pb-3 -mb-[1px] border-b-2 transition-colors"
          :class="activeTab === t.key ? 'text-[#1d1d1f] border-[#1d1d1f] font-medium' : 'text-[#86868b] border-transparent hover:text-[#1d1d1f]'"
          @click="activeTab = t.key; clearMessages()">{{ t.label }}</button>
      </div>

      <!-- 个人信息 -->
      <div v-if="activeTab === 'info'" class="bg-white/80 backdrop-blur-xl rounded-2xl p-8 shadow-[0_2px_12px_rgba(0,0,0,0.03)] space-y-5">
        <!-- 头像 -->
        <div class="flex items-center gap-5">
          <div class="w-20 h-20 rounded-full bg-[#e8e8ed] flex items-center justify-center overflow-hidden shrink-0">
            <img v-if="profile.avatar" :src="profile.avatar" class="w-full h-full object-cover" />
            <span v-else class="text-[28px] text-[#aeaeb2]">{{ profile.username?.[0]?.toUpperCase() }}</span>
          </div>
          <div>
            <label class="text-[13px] text-[#0071e3] hover:underline cursor-pointer transition-colors">
              更换头像
              <input type="file" accept="image/*" class="hidden" @change="handleAvatarUpload" />
            </label>
            <p class="text-[13px] text-[#aeaeb2] mt-1">支持 JPG/PNG，≤1MB</p>
          </div>
        </div>

        <div class="h-px bg-[#d2d2d7]/30" />

        <!-- 用户名 -->
        <div class="flex items-center justify-between">
          <div><p class="text-[13px] text-[#86868b]">用户名</p>
            <p class="text-[17px] text-[#1d1d1f]">{{ profile.username }}</p>
          </div>
          <button class="text-[14px] text-[#0071e3] hover:underline" @click="showChangeUsername=true; newUsername=profile.username">修改</button>
        </div>

        <!-- 邮箱 -->
        <div class="flex items-center justify-between">
          <div><p class="text-[13px] text-[#86868b]">邮箱</p><p class="text-[17px]" :class="profile.email ? 'text-[#1d1d1f]' : 'text-[#aeaeb2]'">{{ profile.email || '未绑定' }}</p></div>
          <button class="text-[14px] text-[#0071e3] hover:underline" @click="activeTab = 'email'; clearMessages()">{{ profile.email ? '更换' : '绑定' }}</button>
        </div>

        <!-- 角色 -->
        <div class="flex items-center justify-between">
          <div><p class="text-[13px] text-[#86868b]">角色</p><p class="text-[17px] text-[#1d1d1f]">{{ profile.role === 'admin' ? '管理员' : '普通用户' }}</p></div>
        </div>

        <!-- 注册时间 -->
        <div class="flex items-center justify-between">
          <div><p class="text-[13px] text-[#86868b]">注册时间</p><p class="text-[17px] text-[#1d1d1f]">{{ formatTime(profile.created_at) }}</p></div>
        </div>

        <div class="h-px bg-[#d2d2d7]/30" />

        <!-- 统计 -->
        <div>
          <p class="text-[13px] font-medium text-[#86868b] mb-3 tracking-wide">取名统计</p>
          <div class="grid grid-cols-2 gap-3">
            <div class="bg-[#f5f5f7] rounded-xl p-3"><p class="text-[22px] font-semibold text-[#1d1d1f]">{{ stats.total }}</p><p class="text-[12px] text-[#86868b]">总记录</p></div>
            <div class="bg-[#f5f5f7] rounded-xl p-3"><p class="text-[22px] font-semibold text-[#1d1d1f]">{{ stats.favorites }}</p><p class="text-[12px] text-[#86868b]">收藏数</p></div>
          </div>
        </div>

        <!-- 修改用户名弹窗 -->
        <div v-if="showChangeUsername" class="fixed inset-0 bg-black/30 backdrop-blur-sm z-50 flex items-center justify-center" @click.self="showChangeUsername=false">
          <div class="bg-white rounded-2xl p-6 w-full max-w-[360px] mx-4 shadow-xl">
            <h3 class="text-[18px] font-semibold text-[#1d1d1f] mb-4">修改用户名</h3>
            <input v-model="newUsername" maxlength="50" placeholder="新用户名（2-50字）" class="w-full px-4 py-3 bg-[#f5f5f7] rounded-xl text-[17px] outline-none mb-3 border border-transparent focus:border-[#0071e3]" @keydown.enter="handleChangeUsername"/>
            <div class="flex gap-3">
              <button class="flex-1 py-2.5 bg-[#0071e3] text-white rounded-full font-medium disabled:opacity-50" :disabled="newUsername.length<2" @click="handleChangeUsername">确认</button>
              <button class="flex-1 py-2.5 bg-[#f5f5f7] rounded-full font-medium" @click="showChangeUsername=false">取消</button>
            </div>
          </div>
        </div>

        <div class="h-px bg-[#d2d2d7]/30" />

        <!-- 注销账号 -->
        <div class="pt-2">
          <button class="text-[14px] text-[#ff3b30] hover:underline transition-colors" @click="handleDeleteAccount">
            注销账号
          </button>
          <p class="text-[13px] text-[#aeaeb2] mt-1">注销后无法登录，所有数据丢失</p>
        </div>
      </div>

      <!-- 修改密码 -->
      <div v-if="activeTab === 'password'" class="bg-white/80 backdrop-blur-xl rounded-2xl p-8 shadow-[0_2px_12px_rgba(0,0,0,0.03)] space-y-4">
        <input v-model="pwForm.old" type="password" placeholder="当前密码" class="w-full px-4 py-3 bg-[#f5f5f7] rounded-xl text-[17px] outline-none border border-transparent focus:border-[#0071e3]" />
        <input v-model="pwForm.new1" type="password" placeholder="新密码（至少6位）" class="w-full px-4 py-3 bg-[#f5f5f7] rounded-xl text-[17px] outline-none border border-transparent focus:border-[#0071e3]" />
        <button class="w-full py-3 bg-[#0071e3] text-white text-[17px] font-medium rounded-full hover:scale-[1.01] transition-all disabled:opacity-50"
          :disabled="!pwForm.old || pwForm.new1.length < 6" @click="handleChangePassword">
          修改密码
        </button>
      </div>

      <!-- 绑定邮箱 -->
      <div v-if="activeTab === 'email'" class="bg-white/80 backdrop-blur-xl rounded-2xl p-8 shadow-[0_2px_12px_rgba(0,0,0,0.03)] space-y-4">
        <p class="text-[15px] text-[#86868b]">绑定邮箱后可用于登录和找回密码</p>
        <input v-model="emailForm" type="email" placeholder="输入邮箱地址" class="w-full px-4 py-3 bg-[#f5f5f7] rounded-xl text-[17px] outline-none border border-transparent focus:border-[#0071e3]" />
        <button class="w-full py-3 bg-[#0071e3] text-white text-[17px] font-medium rounded-full hover:scale-[1.01] transition-all disabled:opacity-50"
          :disabled="!emailForm || countdown > 0" @click="sendBindCode">
          {{ countdown > 0 ? `${countdown}秒后重试` : '发送验证码' }}
        </button>
        <div v-if="codeSent" class="flex gap-3">
          <input v-model="codeForm" maxlength="6" placeholder="输入6位验证码" class="flex-1 px-4 py-3 bg-[#f5f5f7] rounded-xl text-[17px] text-center tracking-[8px] outline-none border border-transparent focus:border-[#0071e3]" />
          <button class="px-6 py-3 bg-[#0071e3] text-white rounded-full font-medium hover:scale-[1.01] transition-all disabled:opacity-50"
            :disabled="codeForm.length !== 6" @click="handleVerifyEmail">确认</button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { getProfile, updateProfile, updateUsername, changePassword, bindEmail, verifyEmail, uploadAvatar, deleteAccount, getStats } from '../api'

const router = useRouter()
const authStore = useAuthStore()

const tabs = [
  { key: 'info', label: '个人信息' },
  { key: 'password', label: '修改密码' },
  { key: 'email', label: '绑定邮箱' },
]
const activeTab = ref('info')
const profile = reactive<any>({})
const error = ref('')
const successMsg = ref('')
let msgTimer: any = null

function showError(msg: string) {
  error.value = msg
  successMsg.value = ''
  clearTimeout(msgTimer)
  msgTimer = setTimeout(() => { error.value = '' }, 5000)
}
function showSuccess(msg: string) {
  successMsg.value = msg
  error.value = ''
  clearTimeout(msgTimer)
  msgTimer = setTimeout(() => { successMsg.value = '' }, 5000)
}
const emailForm = ref('')
const codeForm = ref('')
const codeSent = ref(false)
const sendingCode = ref(false)
const countdown = ref(0)

const pwForm = reactive({ old: '', new1: '' })
const stats = reactive({ total: 0, favorites: 0 })
const showChangeUsername = ref(false)
const newUsername = ref('')

function clearMessages() { error.value = ''; successMsg.value = '' }
function formatTime(s: string) { return s?.replace('T', ' ').slice(0, 19) || '' }

async function loadProfile() {
  try {
    Object.assign(profile, await getProfile())
    const s = await getStats()
    Object.assign(stats, s)
  } catch (e: any) { showError(e.message) }
}

async function handleChangeUsername() {
  if (newUsername.value.length < 2) return
  try {
    await updateProfile(newUsername.value.trim())
    await updateUsername(newUsername.value.trim())
    profile.username = newUsername.value.trim()
    authStore.username = newUsername.value.trim()
    showChangeUsername.value = false
    showSuccess('用户名已更新')
  } catch (e: any) { showError(e.message) }
}

async function handleDeleteAccount() {
  if (!confirm('确定要注销账号吗？注销后无法登录，但数据不会丢失。')) return
  try {
    await deleteAccount()
    authStore.clearAuth()
    router.push('/login')
  } catch (e: any) { showError(e.message) }
}


async function handleChangePassword() {
  try {
    await changePassword(pwForm.old, pwForm.new1)
    showSuccess('密码已修改')
    pwForm.old = ''; pwForm.new1 = ''
  } catch (e: any) { showError(e.message) }
}

function startCountdown() {
  countdown.value = 60
  const timer = setInterval(() => { countdown.value--; if (countdown.value <= 0) clearInterval(timer) }, 1000)
}

async function sendBindCode() {
  try {
    await bindEmail(emailForm.value)
    codeSent.value = true
    showSuccess('验证码已发送')
    startCountdown()
  } catch (e: any) { showError(e.message) }
}

async function handleVerifyEmail() {
  try {
    await verifyEmail(emailForm.value, codeForm.value)
    profile.email = emailForm.value
    codeSent.value = false; codeForm.value = ''
    showSuccess('邮箱绑定成功')
  } catch (e: any) { showError(e.message) }
}

async function handleAvatarUpload(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  if (file.size > 1024 * 1024) { showError('图片不能超过1MB'); return }
  const reader = new FileReader()
  reader.onload = async () => {
    try {
      await uploadAvatar(reader.result as string)
      profile.avatar = reader.result
      showSuccess('头像已更新')
    } catch (err: any) { showError(err.message) }
  }
  reader.readAsDataURL(file)
}

onMounted(async () => {
  if (!authStore.isLoggedIn) { router.push('/login'); return }
  await loadProfile()
})
</script>

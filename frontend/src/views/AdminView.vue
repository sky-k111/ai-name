<template>
  <div class="min-h-screen bg-[#f6f3ec] text-[#191916]">
    <nav class="mx-auto flex max-w-[1120px] items-center justify-between px-6 py-6">
      <span class="font-serif text-xl tracking-[.12em]">后台管理</span>
      <button class="text-sm text-[#77736a] hover:text-[#32695d]" @click="$router.push('/')">← 返回名笺</button>
    </nav>
    <main class="mx-auto max-w-[1120px] px-6 pb-24">
      <p class="text-xs tracking-[.3em] text-[#32695d]">ADMIN</p>
      <h1 class="mt-3 font-serif text-5xl">{{ authStore.username }} · 管理员</h1>

      <!-- 统计卡片 -->
      <div class="mt-10 grid grid-cols-3 gap-4">
        <div class="cursor-pointer rounded-2xl border border-[#d9d1c3] bg-white/55 p-6 hover:shadow-[0_8px_30px_rgba(58,50,38,.1)] transition-shadow" @click="showUserModal('all')">
          <p class="text-xs tracking-[.12em] text-[#77736a]">总用户数</p>
          <p class="mt-2 font-serif text-4xl text-[#32695d]">{{ stats.users }}</p>
        </div>
        <div class="rounded-2xl border border-[#d9d1c3] bg-white/55 p-6">
          <p class="text-xs tracking-[.12em] text-[#77736a]">取名次数</p>
          <p class="mt-2 font-serif text-4xl text-[#191916]">{{ stats.namings }}</p>
        </div>
        <div class="cursor-pointer rounded-2xl border border-[#d9d1c3] bg-white/55 p-6 hover:shadow-[0_8px_30px_rgba(58,50,38,.1)] transition-shadow" @click="showUserModal('active')">
          <p class="text-xs tracking-[.12em] text-[#77736a]">今日活跃</p>
          <p class="mt-2 font-serif text-4xl text-[#32695d]">{{ stats.todayActive }}</p>
        </div>
      </div>

      <!-- Tab 切换 -->
      <div class="mt-12 mb-6 flex gap-6 border-b border-[#d9d1c3]">
        <button v-for="tab in tabs" :key="tab.key" class="pb-3 text-sm" :class="activeTab===tab.key?'border-b-2 border-[#32695d] text-[#32695d]':'text-[#77736a]'" @click="activeTab=tab.key">{{ tab.label }}</button>
      </div>

      <!-- 认证日志 -->
      <div v-if="activeTab==='logs'" class="space-y-2">
        <div v-if="logsLoading" class="py-16 text-center text-[#9a958b]">加载中…</div>
        <div v-else-if="logs.length===0" class="py-16 text-center text-[#9a958b]">暂无日志</div>
        <div v-else class="overflow-hidden rounded-2xl border border-[#d9d1c3] bg-white/55">
          <div v-for="log in logs" :key="log.id" class="flex items-center justify-between px-6 py-3 border-b border-[#d9d1c3]/50 last:border-0 text-sm">
            <span class="font-medium">{{ log.username }}</span>
            <span class="rounded-full px-2.5 py-0.5 text-xs" :class="actionClass(log.action)">{{ actionLabel(log.action) }}</span>
            <span class="text-[#9a958b] font-mono text-xs">{{ log.ip_address }}</span>
            <span class="text-[#9a958b] text-xs">{{ formatTime(log.created_at) }}</span>
          </div>
        </div>
      </div>

      <!-- 取名记录 -->
      <div v-if="activeTab==='namings'" class="space-y-2">
        <div v-if="namingsLoading" class="py-16 text-center text-[#9a958b]">加载中…</div>
        <div v-else-if="namings.length===0" class="py-16 text-center text-[#9a958b]">暂无记录</div>
        <div v-else v-for="n in namings" :key="n.id" class="flex items-center justify-between rounded-2xl border border-[#d9d1c3] bg-white/55 p-5 text-sm" :class="n.is_deleted?'opacity-50':''">
          <div class="flex items-center gap-3">
            <span :class="n.is_deleted?'line-through text-[#9a958b]':'font-medium'">{{ n.username }} · {{ n.surname }} · {{ n.gender==='male'?'男':'女' }}</span>
            <span class="text-[#9a958b]">{{ n.names_count }}个名字</span>
            <span v-if="n.is_deleted" class="rounded-full bg-[#f3e7e3] px-2 py-0.5 text-xs text-[#b65345]">已删除</span>
          </div>
          <span class="text-xs text-[#9a958b]">{{ formatTime(n.created_at) }}</span>
        </div>
      </div>
    </main>

    <!-- 用户列表弹窗 -->
    <div v-if="userModal" class="fixed inset-0 z-[90] bg-[#191916]/35 backdrop-blur-[3px] flex items-center justify-center" @click.self="userModal=null">
      <div class="rounded-[28px] bg-[#f6f3ec] p-8 w-full max-w-[640px] max-h-[80vh] overflow-y-auto mx-4 shadow-[-24px_0_80px_rgba(25,25,22,.2)]">
        <div class="flex items-center justify-between mb-6">
          <h2 class="font-serif text-2xl">{{ userModal==='all'?'全部用户':'今日活跃' }}</h2>
          <button class="grid h-10 w-10 place-items-center rounded-full border border-[#d9d1c3] text-xl text-[#77736a] hover:text-[#32695d]" @click="userModal=null">×</button>
        </div>
        <div v-if="modalLoading" class="py-10 text-center text-[#9a958b]">加载中…</div>
        <div v-else-if="modalUsers.length===0" class="py-10 text-center text-[#9a958b]">暂无数据</div>
        <div v-else class="space-y-2">
          <div v-for="u in modalUsers" :key="u.id" class="flex items-center justify-between rounded-xl border border-[#d9d1c3] bg-white/55 px-4 py-3">
            <div>
              <span class="font-medium">{{ u.username }}</span>
              <span v-if="u.email" class="ml-3 text-sm text-[#9a958b]">{{ u.email }}</span>
              <span v-if="u.role==='admin'" class="ml-2 rounded-full bg-[#e5eee9] px-2 py-0.5 text-xs text-[#32695d]">管理员</span>
              <span v-if="u.is_deleted" class="ml-2 rounded-full bg-[#f3e7e3] px-2 py-0.5 text-xs text-[#b65345]">已注销</span>
            </div>
            <div class="flex items-center gap-4 text-xs text-[#9a958b]">
              <span>取名{{ u.naming_count }}次</span>
              <span>{{ formatTime(u.created_at).slice(0,10) }}</span>
              <button class="text-[#b65345] hover:underline" @click.stop="handleResetPw(u)">重置密码</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { getAuthLogs, getAllNamings, getAllUsers, getActiveUsers, adminResetPassword } from '../api'

const router = useRouter()
const authStore = useAuthStore()
const tabs = [{key:'logs',label:'认证日志'},{key:'namings',label:'取名记录'}]
const activeTab = ref('logs')
const logs=ref<any[]>([]); const logsLoading=ref(true)
const namings=ref<any[]>([]); const namingsLoading=ref(true)
const stats=reactive({users:0,namings:0,todayActive:0})
const userModal=ref<string|null>(null); const modalUsers=ref<any[]>([]); const modalLoading=ref(false)

function formatTime(s:string){return s?.replace('T',' ').slice(0,19)||''}
function actionLabel(a:string){return {register:'注册',login:'登录',logout:'登出',delete_account:'注销'}[a]||a}
function actionClass(a:string){return ({register:'bg-[#e5eee9] text-[#32695d]',login:'bg-[#ebe7dc] text-[#77736a]',logout:'bg-[#d9d1c3] text-[#77736a]',delete_account:'bg-[#f3e7e3] text-[#b65345]'})[a]||'bg-[#d9d1c3] text-[#77736a]'}

async function loadLogs(){logsLoading.value=true;try{const r=await getAuthLogs(); logs.value=r.items; stats.users=(await getAllUsers()).total; stats.todayActive=new Set(r.items.filter((l:any)=>l.created_at?.startsWith(new Date().toISOString().slice(0,10))).map((l:any)=>l.username)).size}catch{}finally{logsLoading.value=false}}
async function loadNamings(){namingsLoading.value=true;try{const r=await getAllNamings(); namings.value=r.items; stats.namings=r.total}catch{}finally{namingsLoading.value=false}}
async function showUserModal(t:string){userModal.value=t;modalLoading.value=true;modalUsers.value=[];try{const r=t==='all'?await getAllUsers():await getActiveUsers(); modalUsers.value=r.items}catch{}finally{modalLoading.value=false}}
async function handleResetPw(u:any){const p=prompt(`重置${u.username}的密码，输入新密码（至少6位）：`); if(!p||p.length<6)return; try{await adminResetPassword(u.id,p); alert(`已重置${u.username}的密码为：${p}`)}catch(e:any){alert(e.message||'重置失败')}}

onMounted(async()=>{if(!authStore.isLoggedIn){router.push('/login');return}; await Promise.all([loadLogs(),loadNamings()])})
</script>

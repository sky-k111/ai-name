<template>
  <div class="min-h-screen bg-[#f6f3ec] text-[#191916]">
    <nav class="mx-auto flex max-w-[1120px] items-center justify-between px-6 py-6">
      <button class="font-serif text-xl tracking-[.12em]" @click="mode = 'name'">名笺</button>
      <div class="flex items-center gap-5 text-sm text-[#77736a]">
        <button @click="settingsOpen = true"><span class="mr-2 inline-block h-2 w-2 rounded-full" :class="hasUserKey ? 'bg-[#32695d]' : 'bg-[#b7a178]'"/>模型设置</button>
        <template v-if="authStore.isLoggedIn">
          <button v-if="authStore.isAdmin" @click="$router.push('/admin')">后台</button><button @click="historyOpen=true">历史</button><button @click="favoritesOpen=true">收藏</button><button @click="profileOpen=true">{{ authStore.username }}</button><button class="text-[#b65345]" @click="handleLogout">退出</button>
        </template>
        <button v-else class="rounded-full border border-[#32695d]/35 px-4 py-2 text-[#32695d]" @click="authOpen = true">登录</button>
      </div>
    </nav>

    <main class="mx-auto max-w-[1120px] px-6 pb-24">
      <header ref="hero" class="grid gap-8 border-y border-[#d9d1c3] py-12 md:grid-cols-[1.25fr_.75fr] md:py-16">
        <div><p class="hero-line text-xs tracking-[.3em] text-[#32695d]">CHINESE NAMING STUDIO</p><h1 class="hero-line mt-5 max-w-3xl font-serif text-5xl leading-[1.08] tracking-tight md:text-7xl">为一个名字，<br><span class="text-[#32695d]">寻找恰好的出处。</span></h1></div>
        <div class="hero-line self-end text-sm leading-7 text-[#77736a]"><p>结合音律、五行与文化典故，借助大语言模型生成有依据、可比较、能继续推敲的中文名字。</p></div>
      </header>

      <section class="mx-auto mt-10 max-w-[980px]">
        <div ref="workbench" class="min-w-0 rounded-[30px] border border-[#d9d1c3] bg-[#fbfaf6] p-5 shadow-[0_24px_80px_rgba(58,50,38,.08)] md:p-10 lg:p-12">
          <div class="mb-9 flex items-center justify-between border-b border-[#e5dfd3] pb-6"><div class="flex items-center gap-5"><button class="group grid h-11 w-11 place-items-center rounded-full border border-[#d9d1c3] text-[#32695d] transition-colors hover:bg-[#edf1ed]" aria-label="选择工作方式" @click="openModeDrawer"><span class="space-y-1"><i class="block h-px w-4 bg-current transition-transform group-hover:translate-x-0.5"/><i class="block h-px w-3 bg-current"/><i class="block h-px w-4 bg-current transition-transform group-hover:translate-x-0.5"/></span></button><div><p class="text-xs tracking-[.2em] text-[#b65345]">{{ activeMode.index }} / {{ activeMode.fee }}</p><h2 class="mt-2 font-serif text-3xl md:text-4xl">{{ activeMode.title }}</h2></div></div><span class="rounded-full bg-[#edf1ed] px-3 py-1.5 text-xs text-[#32695d]">AI</span></div>
          <NameAnalyzer v-if="mode === 'analyze'" :auth-guard="requestAuth" />
          <CompareNames v-else-if="mode === 'compare'" :auth-guard="requestAuth" />
          <PremiumNaming v-else-if="mode === 'premium'" :auth-guard="requestAuth" />
          <template v-else>
            <NameForm v-model="formData" :loading="isGenerating" :disabled="isGenerating" @submit="handleGenerate" />
            <section v-if="showResults" class="mt-10"><NameResults :names="names" :state="resultState" :error-message="errorMessage" @retry="handleRetry" @favorite="handleFavorite" /></section>
            <section v-if="showRefine && authStore.isLoggedIn" class="mt-10"><RefineChat :history="chatHistory" :loading="isRefining" :disabled="isRefining" @send="handleRefine" /></section>
            <p v-else-if="showRefine" class="mt-8 text-center text-sm text-[#77736a]">登录后可继续微调并保存本次结果。</p>
          </template>
        </div>
      </section>
    </main>

    <div v-if="modeMenuOpen" ref="modeLayer" class="fixed inset-0 z-[70] bg-[#191916]/25 backdrop-blur-[2px]" @click.self="closeModeDrawer">
      <aside ref="modePanel" class="h-full w-[min(360px,88vw)] bg-[#f6f3ec] px-7 py-8 shadow-[24px_0_80px_rgba(25,25,22,.18)]">
        <div class="flex items-center justify-between"><div><p class="text-xs tracking-[.24em] text-[#32695d]">WORK MODES</p><h2 class="mt-3 font-serif text-3xl">选择工作方式</h2></div><button class="grid h-10 w-10 place-items-center rounded-full border border-[#d9d1c3] text-xl text-[#77736a]" @click="closeModeDrawer">×</button></div>
        <div class="mt-12 space-y-1"><button v-for="m in modes" :key="m.key" class="mode-entry group flex w-full items-center justify-between border-b border-[#d9d1c3] py-5 text-left" :class="mode===m.key?'text-[#32695d]':'text-[#77736a]'" @click="selectMode(m.key)"><span class="flex items-center"><b class="mr-5 font-serif text-lg font-normal text-[#b7a178]">{{m.index}}</b><span>{{m.label}}</span></span><span class="flex items-center gap-3 text-xs"><i>{{m.fee}}</i><b class="font-normal transition-transform group-hover:translate-x-1">→</b></span></button></div>
      </aside>
    </div>

    <AuthDrawer :open="authOpen" @close="authOpen = false" @success="afterLogin" @guest="useGuestTrial" />
    <ModelSettingsDrawer :open="settingsOpen" @close="settingsOpen = false" @saved="refreshKeyState" />
    <HistoryDrawer v-show="historyOpen" :open="historyOpen" @close="historyOpen=false" />
    <FavoritesDrawer v-show="favoritesOpen" :open="favoritesOpen" @close="favoritesOpen=false" />
    <ProfileDrawer v-show="profileOpen" :open="profileOpen" @close="profileOpen=false" />
    <Transition name="toast"><div v-if="toast" class="fixed left-1/2 top-6 z-[100] -translate-x-1/2 rounded-full px-5 py-3 text-sm text-white shadow-xl" :class="toast.type === 'error' ? 'bg-[#b65345]' : 'bg-[#32695d]'">{{ toast.message }}</div></Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import gsap from 'gsap'
import { useAuthStore } from '../stores/auth'
import type { GenerateRequest, NameItem, ChatMessage, LoadState } from '../types'
import { DEEPSEEK_KEY_SESSION, addFavorite, generateNames, guestGenerateNames, refineNames } from '../api'
import NameForm from '../components/NameForm.vue'; import NameResults from '../components/NameResults.vue'; import RefineChat from '../components/RefineChat.vue'
import NameAnalyzer from '../components/NameAnalyzer.vue'; import CompareNames from '../components/CompareNames.vue'; import PremiumNaming from '../components/PremiumNaming.vue'
import AuthDrawer from '../components/AuthDrawer.vue'; import ModelSettingsDrawer from '../components/ModelSettingsDrawer.vue'
import HistoryDrawer from '../components/HistoryDrawer.vue'; import FavoritesDrawer from '../components/FavoritesDrawer.vue'; import ProfileDrawer from '../components/ProfileDrawer.vue'

const router = useRouter(); const authStore = useAuthStore(); const hero = ref<HTMLElement>(); const workbench = ref<HTMLElement>(); const modeLayer=ref<HTMLElement>(); const modePanel=ref<HTMLElement>(); const modeMenuOpen=ref(false)
const mode = ref('name'); const modes = [{key:'name',index:'01',label:'智能取名',fee:'基础',title:'写下关于名字的期待'},{key:'analyze',index:'02',label:'名字分析',fee:'¥1',title:'读懂一个名字'},{key:'compare',index:'03',label:'名字对比',fee:'¥1',title:'把候选名字放在一起'},{key:'premium',index:'04',label:'精品取名',fee:'¥2',title:'更完整的命名推演'}]
const activeMode = computed(() => modes.find(m => m.key === mode.value) || modes[0])
const formData = ref<GenerateRequest>({ surname:'', gender:'male', birthday:'', birth_time:'', style:'', expectations:'' })
const names=ref<NameItem[]>([]); const resultState=ref<LoadState>('idle'); const errorMessage=ref(''); const conversationId=ref(''); const chatHistory=ref<ChatMessage[]>([])
const isGenerating=ref(false); const isRefining=ref(false); const authOpen=ref(false); const settingsOpen=ref(false); const historyOpen=ref(false); const favoritesOpen=ref(false); const profileOpen=ref(false); const pendingGenerate=ref<GenerateRequest|null>(null); const hasUserKey=ref(!!sessionStorage.getItem(DEEPSEEK_KEY_SESSION)); const toast=ref<{type:'info'|'error';message:string}|null>(null)
const showResults=computed(()=>resultState.value!=='idle'); const showRefine=computed(()=>resultState.value==='success')

onMounted(() => { if (!matchMedia('(prefers-reduced-motion: reduce)').matches) gsap.timeline().from('.hero-line',{y:24,opacity:0,duration:.7,stagger:.1,ease:'power3.out'}).from(workbench.value!,{y:28,opacity:0,duration:.65,ease:'power3.out'},'-=.35') })
function changeMode(value:string){ if(value===mode.value)return; mode.value=value; nextTick(()=>{ if(!matchMedia('(prefers-reduced-motion: reduce)').matches) gsap.from(workbench.value!,{opacity:.45,y:8,duration:.28,ease:'power2.out'}) }) }
async function openModeDrawer(){modeMenuOpen.value=true;await nextTick();if(!matchMedia('(prefers-reduced-motion: reduce)').matches)gsap.timeline({defaults:{ease:'power3.out'}}).fromTo(modeLayer.value!,{autoAlpha:0},{autoAlpha:1,duration:.22}).fromTo(modePanel.value!,{xPercent:-104},{xPercent:0,duration:.52},0).fromTo(modePanel.value!.querySelectorAll('.mode-entry'),{autoAlpha:0,x:-12},{autoAlpha:1,x:0,duration:.35,stagger:.045},.18)}
function closeModeDrawer(){if(!modeMenuOpen.value)return;if(matchMedia('(prefers-reduced-motion: reduce)').matches){modeMenuOpen.value=false;return}gsap.timeline({onComplete:()=>modeMenuOpen.value=false}).to(modePanel.value!,{xPercent:-104,duration:.38,ease:'power3.in'}).to(modeLayer.value!,{autoAlpha:0,duration:.18},'<.12')}
function selectMode(value:string){changeMode(value);closeModeDrawer()}
function showToast(message:string,type:'info'|'error'='info'){toast.value={message,type};setTimeout(()=>toast.value=null,3000)}
function requestAuth(){ if(authStore.isLoggedIn)return true; authOpen.value=true; return false }
async function handleGenerate(data:GenerateRequest){ formData.value={...data}; if(!authStore.isLoggedIn){pendingGenerate.value={...data};authOpen.value=true;return} await runGenerate(data,false) }
async function runGenerate(data:GenerateRequest,guest:boolean){isGenerating.value=true;resultState.value='loading';names.value=[];errorMessage.value='';chatHistory.value=[];try{const res=guest?await guestGenerateNames(data):await generateNames(data);conversationId.value=res.conversation_id;names.value=res.names;resultState.value=res.names.length?'success':'empty';if(res.names.length)chatHistory.value.push({role:'assistant',content:`为你推荐：${res.names.map(n=>n.full_name).join('、')}。你觉得怎么样？`})}catch(e:any){errorMessage.value=e.message||'生成失败，请重试';resultState.value='error';showToast(errorMessage.value,'error')}finally{isGenerating.value=false}}
function afterLogin(){authOpen.value=false;showToast('已登录，继续刚才的操作');if(pendingGenerate.value){const data=pendingGenerate.value;pendingGenerate.value=null;runGenerate(data,false)}}
function useGuestTrial(){authOpen.value=false;if(pendingGenerate.value){const data=pendingGenerate.value;pendingGenerate.value=null;runGenerate(data,true)}else showToast('填写基础取名信息后即可体验')}
async function handleRefine(feedback:string){if(!requestAuth())return;isRefining.value=true;chatHistory.value.push({role:'user',content:feedback});try{const res=await refineNames({conversation_id:conversationId.value,original_request:formData.value,history:chatHistory.value.slice(0,-1),feedback});names.value=res.names;resultState.value=res.names.length?'success':'empty';if(res.names.length)chatHistory.value.push({role:'assistant',content:`调整为：${res.names.map(n=>n.full_name).join('、')}。`})}catch(e:any){showToast(e.message||'微调失败','error');chatHistory.value.pop()}finally{isRefining.value=false}}
function handleRetry(){handleGenerate(formData.value)}
async function handleFavorite(name:any){if(!requestAuth())return;try{await addFavorite(name.full_name,name);showToast('已收藏')}catch(e:any){showToast(e.message||'收藏失败','error')}}
function handleLogout(){authStore.clearAuth();showToast('已退出，仍可继续浏览')}
function refreshKeyState(){hasUserKey.value=!!sessionStorage.getItem(DEEPSEEK_KEY_SESSION);showToast(hasUserKey.value?'会话 Key 已启用':'会话 Key 已清除')}
</script>

<style scoped>
:deep(.bg-\[\#0071e3\]){background-color:#32695d}:deep(.text-\[\#0071e3\]){color:#32695d}:deep(.bg-white\/80){background-color:rgba(255,255,255,.66)}
.toast-enter-active,.toast-leave-active{transition:.25s ease}.toast-enter-from,.toast-leave-to{opacity:0;transform:translate(-50%,-8px)}
@media (prefers-reduced-motion:reduce){*{scroll-behavior:auto!important;transition-duration:.01ms!important}}
</style>

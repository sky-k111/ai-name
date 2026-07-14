<template>
  <div class="home-shell min-h-screen text-[#191916]">
    <div class="home-atmosphere" aria-hidden="true">
      <span class="atmosphere-mark home-atmosphere__ink" />
      <span class="atmosphere-mark home-atmosphere__moon" />
      <span class="atmosphere-mark home-atmosphere__script">声 · 义 · 形</span>
      <span class="home-atmosphere__rule" />
    </div>
    <nav class="home-content mx-auto flex max-w-[1120px] items-center justify-between px-6 py-6">
      <button class="font-serif text-xl tracking-[.12em]" @click="mode = 'name'">名笺</button>
      <div class="flex items-center gap-5 text-sm text-[#77736a]">
        <button @click="settingsOpen = true"><span class="mr-2 inline-block h-2 w-2 rounded-full" :class="hasUserKey ? 'bg-[#32695d]' : 'bg-[#b7a178]'"/>模型设置</button>
        <template v-if="authStore.isLoggedIn">
          <button v-if="authStore.isAdmin" @click="$router.push('/admin')">后台</button><button @click="historyOpen=true">历史</button><button @click="favoritesOpen=true">收藏</button><button @click="profileOpen=true">{{ authStore.username }}</button><button class="text-[#b65345]" @click="handleLogout">退出</button>
        </template>
        <button v-else class="rounded-full border border-[#32695d]/35 px-4 py-2 text-[#32695d]" @click="authOpen = true">登录</button>
      </div>
    </nav>

    <main class="home-content mx-auto max-w-[1120px] px-6 pb-24">
      <header ref="hero" class="home-hero grid gap-8 border-y border-[#d9d1c3] py-12 md:grid-cols-[1.25fr_.75fr] md:py-16">
        <span class="hero-watermark" aria-hidden="true">名</span>
        <div><p class="hero-line text-xs tracking-[.3em] text-[#32695d]">CHINESE NAMING STUDIO</p><h1 class="hero-line mt-5 max-w-3xl font-serif text-5xl leading-[1.08] tracking-tight md:text-7xl">为一个名字，<br><span class="text-[#32695d]">寻找恰好的出处。</span></h1></div>
        <div class="hero-line self-end text-sm leading-7 text-[#77736a]"><p>结合音律、五行与文化典故，借助大语言模型生成有依据、可比较、能继续推敲的中文名字。</p></div>
      </header>

      <section class="mx-auto mt-10 max-w-[980px]">
        <div ref="workbench" class="workbench-shell min-w-0 rounded-[30px] border border-[#d9d1c3] bg-[#fbfaf6] p-5 shadow-[0_24px_80px_rgba(58,50,38,.08)] md:p-10 lg:p-12">
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

    <AuthDrawer v-if="authOpen" :open="authOpen" @close="authOpen = false" @success="afterLogin" @guest="useGuestTrial" />
    <ModelSettingsDrawer v-if="settingsOpen" :open="settingsOpen" @close="settingsOpen = false" @saved="refreshKeyState" />
    <HistoryDrawer v-if="historyOpen" :open="historyOpen" @close="historyOpen=false" />
    <FavoritesDrawer v-if="favoritesOpen" :open="favoritesOpen" @close="favoritesOpen=false" />
    <ProfileDrawer v-if="profileOpen" :open="profileOpen" @close="profileOpen=false" />
    <ActionToast
      v-if="toast"
      :key="toast.id"
      :title="toast.title"
      :detail="toast.detail"
      :type="toast.type"
      @close="closeToast(toast.id)"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, defineAsyncComponent, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import gsap from 'gsap'
import { useAuthStore } from '../stores/auth'
import type { FavoriteAction, GenerateRequest, NameItem, ChatMessage, LoadState } from '../types'
import { DEEPSEEK_KEY_SESSION, addFavorite, generateNames, guestGenerateNames, refineNames } from '../api'
import NameForm from '../components/NameForm.vue'
import ActionToast from '../components/ActionToast.vue'

const NameResults = defineAsyncComponent(() => import('../components/NameResults.vue'))
const RefineChat = defineAsyncComponent(() => import('../components/RefineChat.vue'))
const NameAnalyzer = defineAsyncComponent(() => import('../components/NameAnalyzer.vue'))
const CompareNames = defineAsyncComponent(() => import('../components/CompareNames.vue'))
const PremiumNaming = defineAsyncComponent(() => import('../components/PremiumNaming.vue'))
const AuthDrawer = defineAsyncComponent(() => import('../components/AuthDrawer.vue'))
const ModelSettingsDrawer = defineAsyncComponent(() => import('../components/ModelSettingsDrawer.vue'))
const HistoryDrawer = defineAsyncComponent(() => import('../components/HistoryDrawer.vue'))
const FavoritesDrawer = defineAsyncComponent(() => import('../components/FavoritesDrawer.vue'))
const ProfileDrawer = defineAsyncComponent(() => import('../components/ProfileDrawer.vue'))

const router = useRouter(); const authStore = useAuthStore(); const hero = ref<HTMLElement>(); const workbench = ref<HTMLElement>(); const modeLayer=ref<HTMLElement>(); const modePanel=ref<HTMLElement>(); const modeMenuOpen=ref(false)
const mode = ref('name'); const modes = [{key:'name',index:'01',label:'智能取名',fee:'基础',title:'写下关于名字的期待'},{key:'analyze',index:'02',label:'名字分析',fee:'¥1',title:'读懂一个名字'},{key:'compare',index:'03',label:'名字对比',fee:'¥1',title:'把候选名字放在一起'},{key:'premium',index:'04',label:'精品取名',fee:'¥2',title:'更完整的命名推演'}]
const activeMode = computed(() => modes.find(m => m.key === mode.value) || modes[0])
const formData = ref<GenerateRequest>({ surname:'', gender:'male', birthday:'', birth_time:'', style:'', expectations:'' })
const names=ref<NameItem[]>([]); const resultState=ref<LoadState>('idle'); const errorMessage=ref(''); const conversationId=ref(''); const chatHistory=ref<ChatMessage[]>([])
const isGenerating=ref(false); const isRefining=ref(false); const authOpen=ref(false); const settingsOpen=ref(false); const historyOpen=ref(false); const favoritesOpen=ref(false); const profileOpen=ref(false); const pendingGenerate=ref<GenerateRequest|null>(null); const hasUserKey=ref(!!sessionStorage.getItem(DEEPSEEK_KEY_SESSION)); const toast=ref<{id:number;type:'success'|'info'|'error';title:string;detail:string}|null>(null)
let toastId = 0
let pageTimeline: gsap.core.Timeline | null = null
const showResults=computed(()=>resultState.value!=='idle'); const showRefine=computed(()=>resultState.value==='success')

onMounted(() => { if (!matchMedia('(prefers-reduced-motion: reduce)').matches) pageTimeline=gsap.timeline().from('.atmosphere-mark',{autoAlpha:0,scale:.92,duration:1.1,stagger:.12,ease:'power2.out'}).from('.hero-line',{y:24,opacity:0,duration:.7,stagger:.1,ease:'power3.out'},.08).from(workbench.value!,{y:28,opacity:0,duration:.65,ease:'power3.out'},'-=.35') })
onBeforeUnmount(()=>pageTimeline?.kill())
function changeMode(value:string){ if(value===mode.value)return; mode.value=value; nextTick(()=>{ if(!matchMedia('(prefers-reduced-motion: reduce)').matches) gsap.from(workbench.value!,{opacity:.45,y:8,duration:.28,ease:'power2.out'}) }) }
async function openModeDrawer(){modeMenuOpen.value=true;await nextTick();if(!matchMedia('(prefers-reduced-motion: reduce)').matches)gsap.timeline({defaults:{ease:'power3.out'}}).fromTo(modeLayer.value!,{autoAlpha:0},{autoAlpha:1,duration:.22}).fromTo(modePanel.value!,{xPercent:-104},{xPercent:0,duration:.52},0).fromTo(modePanel.value!.querySelectorAll('.mode-entry'),{autoAlpha:0,x:-12},{autoAlpha:1,x:0,duration:.35,stagger:.045},.18)}
function closeModeDrawer(){if(!modeMenuOpen.value)return;if(matchMedia('(prefers-reduced-motion: reduce)').matches){modeMenuOpen.value=false;return}gsap.timeline({onComplete:()=>modeMenuOpen.value=false}).to(modePanel.value!,{xPercent:-104,duration:.38,ease:'power3.in'}).to(modeLayer.value!,{autoAlpha:0,duration:.18},'<.12')}
function selectMode(value:string){changeMode(value);closeModeDrawer()}
function showToast(title:string,type:'success'|'info'|'error'='info',detail=''){toast.value={id:++toastId,title,detail,type}}
function closeToast(id:number){if(toast.value?.id===id)toast.value=null}
function requestAuth(){ if(authStore.isLoggedIn)return true; authOpen.value=true; return false }
async function handleGenerate(data:GenerateRequest){ formData.value={...data}; if(!authStore.isLoggedIn){pendingGenerate.value={...data};authOpen.value=true;return} await runGenerate(data,false) }
async function runGenerate(data:GenerateRequest,guest:boolean){isGenerating.value=true;resultState.value='loading';names.value=[];errorMessage.value='';chatHistory.value=[];try{const res=guest?await guestGenerateNames(data):await generateNames(data);conversationId.value=res.conversation_id;names.value=res.names;resultState.value=res.names.length?'success':'empty';if(res.names.length)chatHistory.value.push({role:'assistant',content:`为你推荐：${res.names.map(n=>n.full_name).join('、')}。你觉得怎么样？`})}catch(e:any){errorMessage.value=e.message||'生成失败，请重试';resultState.value='error';showToast(errorMessage.value,'error')}finally{isGenerating.value=false}}
function afterLogin(){authOpen.value=false;showToast('已登录，继续刚才的操作');if(pendingGenerate.value){const data=pendingGenerate.value;pendingGenerate.value=null;runGenerate(data,false)}}
function useGuestTrial(){authOpen.value=false;if(pendingGenerate.value){const data=pendingGenerate.value;pendingGenerate.value=null;runGenerate(data,true)}else showToast('填写基础取名信息后即可体验')}
async function handleRefine(feedback:string){if(!requestAuth())return;isRefining.value=true;chatHistory.value.push({role:'user',content:feedback});try{const res=await refineNames({conversation_id:conversationId.value,original_request:formData.value,history:chatHistory.value.slice(0,-1),feedback});names.value=res.names;resultState.value=res.names.length?'success':'empty';if(res.names.length)chatHistory.value.push({role:'assistant',content:`调整为：${res.names.map(n=>n.full_name).join('、')}。`})}catch(e:any){showToast(e.message||'微调失败','error');chatHistory.value.pop()}finally{isRefining.value=false}}
function handleRetry(){handleGenerate(formData.value)}
async function handleFavorite(action:FavoriteAction){
  if(!requestAuth()){action.complete('cancelled');return}
  try{
    await addFavorite(action.name.full_name,action.name)
    action.complete('saved')
    showToast(`「${action.name.full_name}」已收入收藏`,'success','可以在顶部“收藏”中随时查看')
  }catch(e:any){
    const message=e.message||'收藏失败'
    if(message.includes('已收藏过')){
      action.complete('saved')
      showToast(`「${action.name.full_name}」已在收藏中`,'info','无需重复收藏，可以直接前往收藏查看')
    }else{
      action.complete('error')
      showToast(message,'error','本次没有保存，请稍后重试')
    }
  }
}
function handleLogout(){authStore.clearAuth();showToast('已退出，仍可继续浏览')}
function refreshKeyState(){hasUserKey.value=!!sessionStorage.getItem(DEEPSEEK_KEY_SESSION);showToast(hasUserKey.value?'会话 Key 已启用':'会话 Key 已清除')}
</script>

<style scoped>
.home-shell { position: relative; isolation: isolate; overflow: hidden; background: radial-gradient(circle at 16% 12%,rgba(50,105,93,.07),transparent 27%),radial-gradient(circle at 86% 70%,rgba(183,161,120,.11),transparent 31%),#f6f3ec; }
.home-shell::before { position: absolute; z-index: -2; inset: 0; opacity: .3; background-image: repeating-radial-gradient(circle at 18% 24%,rgba(52,43,31,.045) 0 .45px,transparent .65px 4px); background-size: 6px 6px; content: ""; pointer-events: none; }
.home-content { position: relative; z-index: 1; }
.home-atmosphere { position: absolute; z-index: -1; inset: 0; overflow: hidden; pointer-events: none; }
.home-atmosphere__ink { position: absolute; top: 5%; left: -15%; width: 58vw; height: 38vw; border-radius: 50%; background: radial-gradient(ellipse,rgba(29,47,39,.13),rgba(50,105,93,.055) 38%,transparent 72%); filter: blur(7px); transform: rotate(13deg); }
.home-atmosphere__moon { position: absolute; top: 29%; right: 5%; width: clamp(130px,18vw,250px); height: clamp(130px,18vw,250px); border: 1px solid rgba(183,161,120,.17); border-radius: 50%; background: radial-gradient(circle at 38% 36%,rgba(255,255,255,.58),rgba(183,161,120,.08) 58%,transparent 70%); }
.home-atmosphere__moon::after { position: absolute; inset: 17%; border: 1px solid rgba(50,105,93,.08); border-radius: inherit; content: ""; }
.home-atmosphere__script { position: absolute; top: 43%; right: 2.2%; color: rgba(50,105,93,.18); font-family: "STKaiti","KaiTi",serif; font-size: 11px; letter-spacing: .52em; writing-mode: vertical-rl; }
.home-atmosphere__rule { position: absolute; top: 17%; right: 4%; width: 1px; height: 19%; background: linear-gradient(transparent,rgba(183,161,120,.35),transparent); }
.home-hero { position: relative; }.hero-watermark { position: absolute; z-index: -1; top: 50%; left: 48%; color: rgba(50,105,93,.045); font-family: "STKaiti","KaiTi",serif; font-size: clamp(150px,22vw,300px); line-height: .7; transform: translate(-50%,-50%) rotate(-7deg); }
.workbench-shell { position: relative; isolation: isolate; background-image: linear-gradient(145deg,rgba(255,255,255,.5),transparent 43%),radial-gradient(circle at 95% 5%,rgba(183,161,120,.12),transparent 22%); }
.workbench-shell::after { position: absolute; z-index: -1; right: -22px; bottom: -22px; width: 120px; height: 120px; border-right: 1px solid rgba(50,105,93,.14); border-bottom: 1px solid rgba(50,105,93,.14); border-radius: 0 0 34px; content: ""; pointer-events: none; }
:deep(.bg-\[\#0071e3\]){background-color:#32695d}:deep(.text-\[\#0071e3\]){color:#32695d}:deep(.bg-white\/80){background-color:rgba(255,255,255,.66)}
@media(max-width:700px){.home-atmosphere__ink{top:2%;left:-42%;width:120vw;height:86vw}.home-atmosphere__moon{top:23%;right:-24%}.home-atmosphere__script,.home-atmosphere__rule{display:none}.hero-watermark{left:70%;font-size:52vw}}
@media (prefers-reduced-motion:reduce){*{scroll-behavior:auto!important;transition-duration:.01ms!important}}
</style>

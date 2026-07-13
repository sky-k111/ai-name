<template>
  <Teleport to="body">
    <div v-if="open" ref="layer" class="drawer-layer fixed inset-0 z-[80] flex items-center justify-end bg-[#191916]/35 p-3 backdrop-blur-[3px] sm:p-5" @click.self="requestClose">
      <aside ref="panel" role="dialog" aria-modal="true" aria-labelledby="auth-title" class="drawer-panel relative max-h-[calc(100dvh-24px)] w-full max-w-[480px] overflow-y-auto rounded-[28px] bg-[#f6f3ec] shadow-[-24px_0_80px_rgba(25,25,22,.2)] sm:max-h-[calc(100dvh-40px)]">
        <div class="absolute inset-y-0 left-0 w-px bg-[#b7a178]/50" />
        <div ref="accent" class="absolute left-0 top-0 h-32 w-[3px] origin-top bg-[#32695d]" />
        <div class="flex min-h-full flex-col px-7 py-7 sm:px-11 sm:py-9">
          <div class="drawer-item flex items-center justify-between">
            <div class="flex items-center gap-3"><span class="grid h-9 w-9 place-items-center rounded-full border border-[#32695d]/25 font-serif text-[#32695d]">名</span><span class="text-xs tracking-[.22em] text-[#77736a]">MEMBER ACCESS</span></div>
            <button class="group grid h-10 w-10 place-items-center rounded-full border border-[#d9d1c3] text-[#77736a] transition-colors hover:border-[#32695d]/40 hover:text-[#32695d]" aria-label="关闭登录窗口" @click="requestClose"><span class="text-xl transition-transform duration-300 group-hover:rotate-90">×</span></button>
          </div>

          <div ref="copy" class="mt-14">
            <p class="drawer-item text-xs tracking-[.24em] text-[#32695d]">{{ registering ? 'NEW ACCOUNT' : 'WELCOME BACK' }}</p>
            <h2 id="auth-title" class="drawer-item mt-4 font-serif text-[42px] leading-tight text-[#191916]">{{ registering ? '创建你的名笺' : '继续命名旅程' }}</h2>
            <p class="drawer-item mt-4 max-w-sm text-sm leading-7 text-[#77736a]">{{ registering ? '保存每一次灵感、比较与推敲，让好名字不再擦肩而过。' : '登录后可保存结果、收藏名字，并从上次停下的地方继续。' }}</p>
          </div>

          <form ref="formEl" class="mt-10 space-y-5" @submit.prevent="submit">
            <label class="drawer-item field group block"><span>用户名</span><input ref="usernameInput" v-model.trim="username" autocomplete="username" placeholder="输入你的用户名" /></label>
            <label class="drawer-item field group block"><span>密码</span><div class="flex items-center"><input v-model="password" :type="showPassword ? 'text' : 'password'" :autocomplete="registering ? 'new-password' : 'current-password'" placeholder="至少 6 位" class="flex-1"/><button type="button" class="text-xs text-[#77736a] hover:text-[#32695d]" @click="showPassword=!showPassword">{{ showPassword ? '隐藏' : '显示' }}</button></div></label>
<<<<<<< HEAD
=======
            <div v-if="registering && password" class="drawer-item mt-2">
              <div class="flex gap-1 mb-1"><div class="h-1 flex-1 rounded-full transition-colors" :class="pwStrength >= 1 ? (pwStrength===1?'bg-[#b65345]':pwStrength===2?'bg-[#b7a178]':'bg-[#32695d]') : 'bg-[#d9d1c3]'"/><div class="h-1 flex-1 rounded-full transition-colors" :class="pwStrength >= 2 ? (pwStrength===2?'bg-[#b7a178]':'bg-[#32695d]') : 'bg-[#d9d1c3]'"/><div class="h-1 flex-1 rounded-full transition-colors" :class="pwStrength >= 3 ? 'bg-[#32695d]' : 'bg-[#d9d1c3]'"/></div>
              <p class="text-xs" :class="pwStrength===1?'text-[#b65345]':pwStrength===2?'text-[#b7a178]':'text-[#32695d]'">{{ ['','弱','中','强'][pwStrength] || '' }}</p>
            </div>
>>>>>>> 62f878f (合并PR: 宣纸UI+所有修复+Makefile+安全更新)
            <div class="min-h-5"><p v-if="error" class="text-sm text-[#b65345]">{{ error }}</p></div>
            <button :disabled="loading" class="drawer-item group flex w-full items-center justify-between rounded-full bg-[#32695d] px-6 py-4 text-white shadow-[0_12px_30px_rgba(50,105,93,.18)] transition-transform hover:-translate-y-0.5 disabled:opacity-50"><span>{{ loading ? '请稍候…' : registering ? '注册并继续' : '登录并继续' }}</span><span class="transition-transform group-hover:translate-x-1">→</span></button>
          </form>

          <button class="drawer-item mt-5 text-sm text-[#32695d]" @click="toggleMode">{{ registering ? '已有账户？返回登录' : '第一次来？创建账户' }}</button>
          <div class="drawer-item my-8 flex items-center gap-3 text-[11px] tracking-[.18em] text-[#9a958b]"><span class="h-px flex-1 bg-[#d9d1c3]"/>QUICK START<span class="h-px flex-1 bg-[#d9d1c3]"/></div>
          <button class="drawer-item group flex w-full items-center justify-between rounded-full border border-[#32695d]/30 px-6 py-4 text-[#32695d] transition-colors hover:bg-[#edf1ed]" @click="closeThen('guest')"><span>先体验一次基础取名</span><span class="transition-transform group-hover:translate-x-1">↗</span></button>
          <p class="drawer-item mt-4 text-center text-xs leading-5 text-[#9a958b]">游客结果不会保存，高级功能需登录。</p>
        </div>
      </aside>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
<<<<<<< HEAD
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'
=======
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
>>>>>>> 62f878f (合并PR: 宣纸UI+所有修复+Makefile+安全更新)
import gsap from 'gsap'
import { login, register } from '../api'
import { useAuthStore } from '../stores/auth'

const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{ close: []; success: []; guest: [] }>()
const auth = useAuthStore()
const layer=ref<HTMLElement>(); const panel=ref<HTMLElement>(); const accent=ref<HTMLElement>(); const copy=ref<HTMLElement>(); const formEl=ref<HTMLFormElement>(); const usernameInput=ref<HTMLInputElement>()
const username=ref(''); const password=ref(''); const registering=ref(false); const showPassword=ref(false); const loading=ref(false); const error=ref('')
<<<<<<< HEAD
=======
const pwStrength = computed(() => { const p = password.value; if (p.length < 6) return 0; const hasLetter = /[a-zA-Z]/.test(p); const hasDigit = /\d/.test(p); const hasSpecial = /[^a-zA-Z0-9]/.test(p); if (hasLetter && hasDigit && hasSpecial) return 3; if (hasLetter && hasDigit) return 2; return 1 })
>>>>>>> 62f878f (合并PR: 宣纸UI+所有修复+Makefile+安全更新)
let timeline: gsap.core.Timeline | null = null
const media = gsap.matchMedia()

watch(() => props.open, async value => {
  if (!value) return
  document.body.style.overflow='hidden'; await nextTick(); timeline?.kill(); media.revert()
  media.add('(prefers-reduced-motion: no-preference)', () => {
    timeline=gsap.timeline({defaults:{ease:'power3.out'}})
      .fromTo(layer.value!,{autoAlpha:0},{autoAlpha:1,duration:.24})
      .fromTo(panel.value!,{xPercent:104},{xPercent:0,duration:.62},0)
      .fromTo(accent.value!,{scaleY:0},{scaleY:1,duration:.55},.2)
      .fromTo(panel.value!.querySelectorAll('.drawer-item'),{autoAlpha:0,y:16},{autoAlpha:1,y:0,duration:.45,stagger:.045},.2)
    return () => timeline?.kill()
  })
  setTimeout(()=>usernameInput.value?.focus(),300)
  window.addEventListener('keydown',onKeydown)
})
function onKeydown(e:KeyboardEvent){if(e.key==='Escape')requestClose()}
function finish(event:'close'|'success'|'guest'){document.body.style.overflow='';window.removeEventListener('keydown',onKeydown);if(event==='close')emit('close');else if(event==='success')emit('success');else emit('guest')}
function closeThen(event:'close'|'success'|'guest'){
  if(!timeline||matchMedia('(prefers-reduced-motion: reduce)').matches){finish(event);return}
  timeline.eventCallback('onReverseComplete',()=>finish(event)).timeScale(1.35).reverse()
}
function requestClose(){closeThen('close')}
function toggleMode(){registering.value=!registering.value;error.value='';nextTick(()=>{if(!matchMedia('(prefers-reduced-motion: reduce)').matches)gsap.fromTo([copy.value,formEl.value],{autoAlpha:.35,y:8},{autoAlpha:1,y:0,duration:.35,ease:'power2.out',stagger:.05})})}
async function submit(){if(username.value.length<2||password.value.length<6){error.value='用户名至少 2 位，密码至少 6 位';return}loading.value=true;error.value='';try{const r=registering.value?await register(username.value,password.value):await login(username.value,password.value);auth.setAuth(r.token,r.username,r.role);closeThen('success')}catch(e:any){error.value=e.message||'操作失败';if(formEl.value&&!matchMedia('(prefers-reduced-motion: reduce)').matches)gsap.fromTo(formEl.value,{x:-5},{x:0,duration:.32,ease:'power2.out',clearProps:'transform'})}finally{loading.value=false}}
onBeforeUnmount(()=>{timeline?.kill();media.revert();document.body.style.overflow='';window.removeEventListener('keydown',onKeydown)})
</script>

<style scoped>
.drawer-panel,.drawer-item{will-change:transform,opacity}.field>span{display:block;font-size:12px;letter-spacing:.12em;color:#9a958b}.field input{width:100%;background:transparent;padding:12px 0 10px;outline:none;color:#191916}.field{border-bottom:1px solid #d9d1c3;transition:border-color .25s}.field:focus-within{border-color:#32695d}
</style>

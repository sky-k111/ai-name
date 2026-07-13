<template>
  <Teleport to="body">
    <div v-if="open" ref="layer" class="fixed inset-0 z-[80] flex items-center justify-end bg-[#191916]/35 p-3 backdrop-blur-[3px] sm:p-5" @click.self="requestClose">
      <aside ref="panel" role="dialog" aria-modal="true" aria-labelledby="model-title" class="drawer-panel relative max-h-[calc(100dvh-24px)] w-full max-w-[480px] overflow-y-auto rounded-[28px] bg-[#f6f3ec] shadow-[-24px_0_80px_rgba(25,25,22,.2)] sm:max-h-[calc(100dvh-40px)]">
        <div class="absolute inset-y-0 left-0 w-px bg-[#b7a178]/50"/><div ref="accent" class="absolute left-0 top-0 h-32 w-[3px] origin-top bg-[#b7a178]"/>
        <div class="flex min-h-full flex-col px-7 py-7 sm:px-11 sm:py-9">
          <div class="drawer-item flex items-center justify-between"><div class="flex items-center gap-3"><span class="grid h-9 w-9 place-items-center rounded-full border border-[#b7a178]/40 font-serif text-[#32695d]">模</span><span class="text-xs tracking-[.22em] text-[#77736a]">MODEL CONTROL</span></div><button class="group grid h-10 w-10 place-items-center rounded-full border border-[#d9d1c3] text-[#77736a] hover:text-[#32695d]" aria-label="关闭模型设置" @click="requestClose"><span class="text-xl transition-transform duration-300 group-hover:rotate-90">×</span></button></div>
          <div class="mt-14"><p class="drawer-item text-xs tracking-[.24em] text-[#32695d]">DEEPSEEK PROVIDER</p><h2 id="model-title" class="drawer-item mt-4 font-serif text-[42px] leading-tight">模型与密钥</h2><p class="drawer-item mt-4 text-sm leading-7 text-[#77736a]">选择使用项目提供的模型配置，或仅在当前浏览器会话中使用你的私人 Key。</p></div>

          <div class="drawer-item mt-9 rounded-[20px] border border-[#d9d1c3] bg-white/55 p-5">
<<<<<<< HEAD
            <div class="flex items-center justify-between"><div><p class="text-sm font-medium">项目模型通道</p><p class="mt-1 text-xs text-[#9a958b]">DeepSeek Chat</p></div><span class="flex items-center gap-2 rounded-full px-3 py-1.5 text-xs" :class="systemKey?'bg-[#e5eee9] text-[#32695d]':'bg-[#f3e7e3] text-[#b65345]'"><i class="h-1.5 w-1.5 rounded-full bg-current"/>{{ systemKey?'可用':'未配置' }}</span></div>
          </div>

          <div class="drawer-item mt-8">
            <div class="flex items-end justify-between"><label class="text-xs tracking-[.12em] text-[#77736a]">你的 DEEPSEEK API KEY</label><span class="text-[11px] text-[#9a958b]">可选</span></div>
            <div class="mt-3 flex items-center rounded-2xl border border-[#d9d1c3] bg-white/60 px-4 transition-colors focus-within:border-[#32695d]"><input ref="keyInput" v-model="key" :type="showKey?'text':'password'" autocomplete="off" spellcheck="false" placeholder="sk-..." class="min-w-0 flex-1 bg-transparent py-4 font-mono text-sm outline-none"/><button class="ml-3 text-xs text-[#77736a] hover:text-[#32695d]" @click="showKey=!showKey">{{ showKey?'隐藏':'显示' }}</button></div>
            <div class="mt-3 flex items-center gap-2 text-xs text-[#9a958b]"><span class="h-1.5 w-1.5 rounded-full" :class="key.trim()?'bg-[#32695d]':'bg-[#c9c2b7]'"/>{{ key.trim()?'将优先使用你的会话 Key':'当前使用项目模型配置' }}</div>
=======
            <div class="flex items-center justify-between"><div><p class="text-sm font-medium">项目模型通道</p><p class="mt-1 text-xs text-[#9a958b]">AI 大语言模型</p></div><span class="flex items-center gap-2 rounded-full px-3 py-1.5 text-xs" :class="systemKey?'bg-[#e5eee9] text-[#32695d]':'bg-[#f3e7e3] text-[#b65345]'"><i class="h-1.5 w-1.5 rounded-full bg-current"/>{{ systemKey?'可用':'未配置' }}</span></div>
          </div>

          <div class="drawer-item mt-8">
            <div class="flex items-end justify-between"><label class="text-xs tracking-[.12em] text-[#77736a]">你的 API KEY</label><span class="text-[11px] text-[#9a958b]">可选 · 填写后优先使用</span></div>
            <div class="mt-3 flex items-center rounded-2xl border border-[#d9d1c3] bg-white/60 px-4 transition-colors focus-within:border-[#32695d]"><input ref="keyInput" v-model="key" type="text" autocomplete="off" spellcheck="false" placeholder="sk-..." class="min-w-0 flex-1 bg-transparent py-4 font-mono text-sm outline-none"/></div>
            <div class="mt-3 flex items-center gap-2 text-xs text-[#9a958b]"><span class="h-1.5 w-1.5 rounded-full" :class="key.trim()?'bg-[#32695d]':'bg-[#c9c2b7]'"/>{{ key.trim()?'将优先使用你的 API Key 请求 AI，不计入系统用量':'留空则使用项目默认模型' }}</div>
>>>>>>> 62f878f (合并PR: 宣纸UI+所有修复+Makefile+安全更新)
          </div>

          <div class="drawer-item mt-8 rounded-2xl bg-[#ebe7dc] p-4 text-xs leading-6 text-[#77736a]"><p class="font-medium text-[#191916]">隐私边界</p><p class="mt-1">Key 只进入 sessionStorage，并随模型请求发送。关闭标签页后浏览器会自动清除。</p></div>
          <div class="mt-auto pt-10">
            <button class="drawer-item group flex w-full items-center justify-between rounded-full bg-[#32695d] px-6 py-4 text-white shadow-[0_12px_30px_rgba(50,105,93,.18)] transition-transform hover:-translate-y-0.5" @click="save"><span>{{ key.trim()?'启用我的会话 Key':'使用项目配置' }}</span><span class="transition-transform group-hover:translate-x-1">→</span></button>
            <button v-if="storedKey" class="drawer-item mt-4 w-full text-sm text-[#b65345]" @click="clear">清除已保存的会话 Key</button>
          </div>
        </div>
      </aside>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'
import gsap from 'gsap'
import { DEEPSEEK_KEY_SESSION, getModelStatus } from '../api'
const props=defineProps<{open:boolean}>();const emit=defineEmits<{close:[];saved:[]}>()
const key=ref('');const storedKey=ref('');const showKey=ref(false);const systemKey=ref(false);const layer=ref<HTMLElement>();const panel=ref<HTMLElement>();const accent=ref<HTMLElement>();const keyInput=ref<HTMLInputElement>()
let timeline:gsap.core.Timeline|null=null;const media=gsap.matchMedia()
watch(()=>props.open,async value=>{if(!value)return;key.value=sessionStorage.getItem(DEEPSEEK_KEY_SESSION)||'';storedKey.value=key.value;showKey.value=false;document.body.style.overflow='hidden';getModelStatus().then(r=>systemKey.value=r.system_key_configured).catch(()=>{});await nextTick();timeline?.kill();media.revert();media.add('(prefers-reduced-motion: no-preference)',()=>{timeline=gsap.timeline({defaults:{ease:'power3.out'}}).fromTo(layer.value!,{autoAlpha:0},{autoAlpha:1,duration:.24}).fromTo(panel.value!,{xPercent:104},{xPercent:0,duration:.62},0).fromTo(accent.value!,{scaleY:0},{scaleY:1,duration:.55},.2).fromTo(panel.value!.querySelectorAll('.drawer-item'),{autoAlpha:0,y:16},{autoAlpha:1,y:0,duration:.45,stagger:.05},.2);return()=>timeline?.kill()});window.addEventListener('keydown',onKeydown)})
function onKeydown(e:KeyboardEvent){if(e.key==='Escape')requestClose()}
function finish(){document.body.style.overflow='';window.removeEventListener('keydown',onKeydown);emit('close')}
function requestClose(){if(!timeline||matchMedia('(prefers-reduced-motion: reduce)').matches){finish();return}timeline.eventCallback('onReverseComplete',finish).timeScale(1.35).reverse()}
function save(){const value=key.value.trim();if(value)sessionStorage.setItem(DEEPSEEK_KEY_SESSION,value);else sessionStorage.removeItem(DEEPSEEK_KEY_SESSION);storedKey.value=value;emit('saved');requestClose()}
function clear(){key.value='';storedKey.value='';sessionStorage.removeItem(DEEPSEEK_KEY_SESSION);emit('saved');if(!matchMedia('(prefers-reduced-motion: reduce)').matches)gsap.fromTo(keyInput.value!,{backgroundColor:'rgba(182,83,69,.12)'},{backgroundColor:'transparent',duration:.55,ease:'power2.out',clearProps:'backgroundColor'})}
onBeforeUnmount(()=>{timeline?.kill();media.revert();document.body.style.overflow='';window.removeEventListener('keydown',onKeydown)})
</script>

<style scoped>.drawer-panel,.drawer-item{will-change:transform,opacity}</style>

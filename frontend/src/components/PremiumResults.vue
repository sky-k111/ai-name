<template>
  <div class="w-full max-w-[680px] mx-auto">
    <div v-if="state==='idle'" class="text-center py-20"><p class="text-[17px] text-[#aeaeb2]">输入信息后点击「生成名字」</p></div>

    <div v-if="state==='loading'" class="space-y-4">
      <div v-for="i in 3" :key="i" class="bg-white/80 rounded-2xl p-6 animate-pulse"><div class="h-7 w-24 bg-[#e8e8ed] rounded mb-3"/><div class="h-4 w-full bg-[#e8e8ed] rounded mb-2"/><div class="h-4 w-2/3 bg-[#e8e8ed] rounded"/></div>
    </div>

    <div v-if="state==='empty'" class="text-center py-16"><p class="text-[17px] text-[#86868b]">暂未生成到合适的名字</p></div>
    <div v-if="state==='error'" class="text-center py-16"><p class="text-[17px] text-[#ff3b30] mb-3">{{errorMessage}}</p><button class="text-[15px] text-[#0071e3] hover:underline" @click="emit('retry')">重试</button></div>

    <div v-if="state==='success'" class="flex justify-end mb-3">
      <button class="text-[13px] text-[#0071e3] hover:underline transition-colors" @click="exportPDF">导出报告 PDF</button>
    </div>

    <TransitionGroup v-if="state==='success'" name="card" tag="div" class="space-y-4" appear>
      <div v-for="(name, idx) in names" :key="name.full_name"
        class="bg-white/80 backdrop-blur-xl rounded-2xl p-6 shadow-[0_2px_12px_rgba(0,0,0,0.03)] border border-[#d2d2d7]/30"
        :style="{ transitionDelay: `${idx * 0.1}s` }">
        <!-- 头部 -->
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-[28px] font-semibold text-[#1d1d1f]">{{ name.full_name }}</h3>
          <div class="flex gap-3">
            <button class="text-[13px] text-[#86868b] hover:text-[#0071e3] transition-colors" @click="handleSpeech(name.full_name)">试读</button>
            <button class="text-[13px] text-[#aeaeb2] hover:text-[#0071e3] transition-colors" @click="emit('favorite', name)">收藏</button>
          </div>
        </div>

        <!-- 寓意 -->
        <p class="text-[15px] text-[#3a3a3c] leading-relaxed mb-4">{{ name.meaning }}</p>

        <!-- 属性标签 -->
        <div class="flex flex-wrap gap-2 mb-4">
          <span class="px-3 py-1 bg-[#f5f5f7] rounded-full text-[13px] text-[#86868b]">五行 {{ name.wuxing }}</span>
          <span class="px-3 py-1 bg-[#f5f5f7] rounded-full text-[13px] text-[#86868b]">出处 {{ name.source }}</span>
          <span v-if="name.sound_analysis" class="px-3 py-1 bg-[#f5f5f7] rounded-full text-[13px] text-[#86868b]">音律分析</span>
          <span v-if="name.char_analysis" class="px-3 py-1 bg-[#f5f5f7] rounded-full text-[13px] text-[#86868b]">字形分析</span>
          <span class="px-3 py-1 rounded-full text-[13px] font-medium"
            :class="(name.popularity||'').includes('低') ? 'bg-green-100 text-green-700' : (name.popularity||'').includes('高') ? 'bg-red-100 text-red-600' : 'bg-yellow-100 text-yellow-700'">
            重名概率{{ name.popularity ? name.popularity.replace('重名概率','') : '未知' }}
          </span>
        </div>

        <!-- 八字 -->
        <div v-if="name.bazi" class="bg-[#f5f5f7] rounded-xl p-4 mb-3">
          <p class="text-[13px] font-medium text-[#86868b] mb-1">八字分析</p>
          <p class="text-[14px] text-[#3a3a3c] leading-relaxed">{{ name.bazi }}</p>
        </div>

        <!-- 音律 -->
        <div v-if="name.sound_analysis" class="bg-[#f5f5f7] rounded-xl p-4 mb-3">
          <p class="text-[13px] font-medium text-[#86868b] mb-1">音律分析</p>
          <p class="text-[14px] text-[#3a3a3c] leading-relaxed">{{ name.sound_analysis }}</p>
        </div>

        <!-- 字形 -->
        <div v-if="name.char_analysis" class="bg-[#f5f5f7] rounded-xl p-4 mb-3">
          <p class="text-[13px] font-medium text-[#86868b] mb-1">字形分析</p>
          <p class="text-[14px] text-[#3a3a3c] leading-relaxed">{{ name.char_analysis }}</p>
        </div>

      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { nextTick } from 'vue'
import html2canvas from 'html2canvas'
import { jsPDF } from 'jspdf'
import type { LoadState, NameItem } from '../types'

const props = defineProps<{ names: NameItem[]; state: LoadState; errorMessage: string }>()
const emit = defineEmits<{ retry: []; favorite: [name: NameItem] }>()

function handleSpeech(text: string) {
  const u = new SpeechSynthesisUtterance(text)
  u.lang = 'zh-CN'; u.rate = 0.8
  speechSynthesis.speak(u)
}

async function exportPDF() {
  // 创建一个离屏容器用于渲染中文内容
  const div = document.createElement('div')
  div.style.cssText = 'position:fixed;left:-9999px;top:0;width:700px;background:white;padding:30px;font-family:"PingFang SC","Microsoft YaHei",sans-serif;color:#1d1d1f;'
  div.innerHTML = `<h1 style="text-align:center;font-size:22px;margin-bottom:8px">AI 精品取名报告</h1>
<p style="text-align:center;color:#86868b;font-size:12px;margin-bottom:20px">${new Date().toLocaleDateString('zh-CN')}</p>
${props.names.map((n, i) => `
<div style="margin-bottom:16px;padding:16px;background:#f5f5f7;border-radius:12px">
  <h3 style="font-size:18px;margin-bottom:8px">${i + 1}. ${n.full_name}</h3>
  <p style="font-size:13px;line-height:1.8;margin-bottom:4px"><b>寓意：</b>${n.meaning || ''}</p>
  ${n.bazi ? `<p style="font-size:13px;line-height:1.8;margin-bottom:4px"><b>八字：</b>${n.bazi}</p>` : ''}
  ${n.sound_analysis ? `<p style="font-size:13px;line-height:1.8;margin-bottom:4px"><b>音律：</b>${n.sound_analysis}</p>` : ''}
  ${n.char_analysis ? `<p style="font-size:13px;line-height:1.8;margin-bottom:4px"><b>字形：</b>${n.char_analysis}</p>` : ''}
  <p style="font-size:12px;color:#86868b">五行 ${n.wuxing} · 出处 ${n.source || ''} · 重名${n.popularity || '未知'}</p>
</div>`).join('')}`
  document.body.appendChild(div)
  await nextTick()

  const canvas = await html2canvas(div, { scale: 2, useCORS: true })
  document.body.removeChild(div)

  const pdf = new jsPDF('p', 'mm', 'a4')
  const imgW = 190; const imgH = (canvas.height * imgW) / canvas.width
  let hLeft = imgH; let page = 0
  while (hLeft > 0) {
    if (page > 0) pdf.addPage()
    pdf.addImage(canvas.toDataURL('image/png'), 'PNG', 10, 10 - page * 277, imgW, imgH)
    hLeft -= 277; page++
  }
  pdf.save('取名报告.pdf')
}
</script>

<style scoped>
.card-enter-active { transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
.card-enter-from { opacity: 0; transform: translateY(8px); }
</style>

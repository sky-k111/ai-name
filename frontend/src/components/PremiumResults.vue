<template>
  <div class="premium-results w-full max-w-[920px] mx-auto">
    <div v-if="state==='idle'" class="result-notice" aria-live="polite">
      <span class="result-notice__seal" aria-hidden="true">候</span>
      <p>写下取名线索，名帖会在这里展开</p>
    </div>

    <NameCardSkeleton v-if="state==='loading'" />

    <div v-if="state==='empty'" class="result-notice" aria-live="polite">
      <span class="result-notice__seal" aria-hidden="true">寻</span>
      <p>这一轮还没有遇见合适的名字</p>
      <span class="result-notice__hint">换一组期望或补充线索，再试一次</span>
    </div>
    <div v-if="state==='error'" class="result-notice result-notice--error" role="alert">
      <span class="result-notice__seal" aria-hidden="true">缓</span>
      <p>{{ errorMessage }}</p>
      <button class="retry-button" type="button" @click="emit('retry')">重新推演</button>
    </div>

    <div v-if="state==='success'" class="result-toolbar">
      <p>共得 {{ names.length }} 帖</p>
      <button class="export-button" type="button" :disabled="isExporting" @click="exportPDF">
        <svg viewBox="0 0 20 20" aria-hidden="true">
          <path d="M10 2v10m0 0 4-4m-4 4L6 8M3.5 13.5v2A1.5 1.5 0 0 0 5 17h10a1.5 1.5 0 0 0 1.5-1.5v-2" />
        </svg>
        {{ isExporting ? '正在装订' : '导出完整名笺' }}
      </button>
    </div>

    <NameGallery v-if="state==='success'" :names="names" @favorite="emit('favorite', $event)" />
  </div>
</template>

<script setup lang="ts">
import { nextTick, ref } from 'vue'
import type { FavoriteAction, LoadState, NameItem } from '../types'
import NameCardSkeleton from './NameCardSkeleton.vue'
import NameGallery from './NameGallery.vue'

const props = defineProps<{ names: NameItem[]; state: LoadState; errorMessage: string }>()
const emit = defineEmits<{ retry: []; favorite: [action: FavoriteAction] }>()
const isExporting = ref(false)

async function exportPDF() {
  if (isExporting.value) return
  isExporting.value = true
  const div = document.createElement('div')

  try {
    const [{ default: html2canvas }, { jsPDF }] = await Promise.all([
      import('html2canvas'),
      import('jspdf'),
    ])
    // 创建一个离屏容器用于渲染中文内容
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

    const pdf = new jsPDF('p', 'mm', 'a4')
    const imgW = 190; const imgH = (canvas.height * imgW) / canvas.width
    let hLeft = imgH; let page = 0
    while (hLeft > 0) {
      if (page > 0) pdf.addPage()
      pdf.addImage(canvas.toDataURL('image/png'), 'PNG', 10, 10 - page * 277, imgW, imgH)
      hLeft -= 277; page++
    }
    pdf.save('取名报告.pdf')
  } finally {
    div.remove()
    isExporting.value = false
  }
}
</script>

<style scoped>
.result-notice {
  min-height: 230px;
  display: grid;
  place-items: center;
  align-content: center;
  gap: 10px;
  padding: 48px 24px;
  color: #425b52;
  text-align: center;
  border: 1px dashed rgba(37, 76, 64, 0.22);
  border-radius: 24px;
  background: rgba(248, 246, 238, 0.52);
}

.result-notice__seal {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  color: #9d4d3f;
  font-family: "STKaiti", "KaiTi", serif;
  font-size: 18px;
  border: 1px solid rgba(157, 77, 63, 0.46);
  border-radius: 8px;
  transform: rotate(-3deg);
}

.result-notice p { margin: 0; font-family: "STKaiti", "KaiTi", serif; font-size: 18px; }
.result-notice__hint { color: #7c8882; font-size: 13px; }
.result-notice--error { border-color: rgba(157, 77, 63, 0.28); }

.retry-button,
.export-button {
  min-height: 44px;
  border: 1px solid rgba(37, 76, 64, 0.25);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.7);
  color: #254c40;
  font-size: 13px;
  font-weight: 600;
  transition: border-color 180ms ease, background 180ms ease, transform 180ms ease;
}

.retry-button { margin-top: 4px; padding: 0 20px; }
.retry-button:hover,
.export-button:hover:not(:disabled) { border-color: rgba(37, 76, 64, 0.5); background: #fff; transform: translateY(-1px); }
.retry-button:focus-visible,
.export-button:focus-visible { outline: 2px solid #bf8a52; outline-offset: 3px; }

.result-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;
  padding: 0 4px;
}

.result-toolbar p { margin: 0; color: #738079; font-size: 12px; letter-spacing: 0.12em; }
.export-button { display: inline-flex; align-items: center; gap: 7px; padding: 0 16px; }
.export-button svg { width: 17px; height: 17px; fill: none; stroke: currentColor; stroke-width: 1.5; stroke-linecap: round; stroke-linejoin: round; }
.export-button:disabled { cursor: wait; opacity: 0.58; }

@media (max-width: 540px) {
  .result-notice { min-height: 200px; border-radius: 20px; }
  .result-toolbar { align-items: flex-start; }
}
</style>

<template>
  <WorkspaceDrawer :open="open" title="取名历史" kicker="NAMING ARCHIVE" :description="`共 ${total} 条记录`" width="680px" @close="emit('close')">
    <div class="min-h-[480px]">
    <div class="mb-6 flex items-center justify-between gap-3">
      <select v-model="filter" class="rounded-full border border-[#d9d1c3] bg-white/55 px-4 py-2 text-sm outline-none" @change="load">
        <option value="">全部类型</option><option value="naming">取名</option><option value="analyze">分析</option><option value="compare">对比</option><option value="premium">精品</option>
      </select>
      <div class="flex gap-3">
        <button v-if="items.length && !batchMode" class="text-sm text-[#77736a]" @click="batchMode=true">选择</button>
        <button v-if="batchMode" class="text-sm text-[#b65345]" @click="batchDelete">删除选中({{selected.length}})</button>
        <button v-if="batchMode" class="text-sm text-[#77736a]" @click="batchMode=false; selected=[]">取消</button>
        <button v-if="items.length && !batchMode" class="text-sm text-[#b65345]" @click="clear">清空全部</button>
      </div>
    </div>
    <p v-if="loading" class="py-16 text-center text-[#9a958b]">正在整理名笺…</p>
    <p v-else-if="error" class="py-10 text-center text-[#b65345]">{{ error }}</p>
    <p v-else-if="!items.length" class="py-16 text-center text-[#9a958b]">还没有取名记录</p>
    <div v-else class="space-y-3">
      <article v-for="item in items" :key="item.id" class="rounded-2xl border border-[#d9d1c3] bg-white/55 p-5">
        <div class="flex items-center justify-between gap-4">
          <button v-if="batchMode" class="w-5 h-5 rounded-full border-2 shrink-0 flex items-center justify-center" :class="selected.includes(item.id)?'border-[#32695d] bg-[#32695d]':'border-[#d9d1c3]'" @click="toggleSelect(item.id)">
            <svg v-if="selected.includes(item.id)" class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>
          </button>
          <button class="min-w-0 flex-1 text-left" @click="expanded = expanded === item.id ? null : item.id">
            <p class="font-serif text-xl">{{ item.surname }} · {{ item.gender === "male" ? "男" : "女" }}</p>
            <p class="mt-1 text-xs text-[#9a958b]">{{ formatTime(item.created_at) }} · {{ item.names.length }} 个名字</p>
          </button>
          <button v-if="!batchMode" class="text-xs text-[#b65345]" @click="remove(item.id)">删除</button>
        </div>
        <div v-if="expanded === item.id" class="mt-4 space-y-4 border-t border-[#e5dfd3] pt-4">
          <div v-for="name in item.names" :key="name.full_name" class="border-l-2 border-[#32695d]/35 pl-4">
            <div class="flex items-baseline gap-3"><p class="font-serif text-xl">{{ name.full_name }}</p><p v-if="name.score" class="text-2xl font-semibold text-[#32695d]">{{ name.score }}</p></div>
            <p class="mt-1 text-sm leading-6 text-[#77736a]">{{ name.meaning }}</p>
          </div>
        </div>
      </article>
    </div>
    </div>
  </WorkspaceDrawer>
</template>
<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import WorkspaceDrawer from "./WorkspaceDrawer.vue";
import { clearAllHistory, deleteHistory, getHistory, batchDeleteHistory } from "../api";
import type { HistoryItem } from "../types";
const props = defineProps<{ open: boolean }>();
const emit = defineEmits<{ close: [] }>();
watch(() => props.open, v => { if (v) load() });
onMounted(load);
const items = ref<HistoryItem[]>([]), total = ref(0), loading = ref(true), error = ref(""), filter = ref(""), expanded = ref<number | null>(null), batchMode = ref(false), selected = ref<number[]>([]);
const formatTime = (v: string) => v?.replace("T", " ").slice(0, 16) || "";
function toggleSelect(id: number) { const i = selected.value.indexOf(id); i >= 0 ? selected.value.splice(i,1) : selected.value.push(id) }
async function load() { loading.value = true; error.value = ""; try { const r = await getHistory(0, 50, filter.value || undefined); items.value = r.items; total.value = r.total } catch (e: any) { error.value = e.message } finally { loading.value = false } }
async function remove(id: number) { await deleteHistory(id); items.value = items.value.filter(i => i.id !== id); total.value-- }
async function clear() { if (!confirm("确定清空全部历史吗？")) return; await clearAllHistory(); items.value = []; total.value = 0 }
async function batchDelete() { if (!selected.value.length) return; await batchDeleteHistory(selected.value); items.value = items.value.filter(i => !selected.value.includes(i.id)); total.value = items.value.length; selected.value = []; batchMode.value = false }
</script>

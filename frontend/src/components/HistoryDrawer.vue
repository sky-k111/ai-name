<template>
  <WorkspaceDrawer
    :open="open"
    title="取名历史"
    kicker="NAMING ARCHIVE"
    :description="`共 ${total} 条记录`"
    width="700px"
    @close="emit('close')"
    ><div class="mb-6 flex items-center justify-between gap-3">
      <select
        v-model="filter"
        class="rounded-full border border-[#d9d1c3] bg-white/55 px-4 py-2 text-sm outline-none"
        @change="load"
      >
        <option value="">全部类型</option>
        <option value="naming">取名</option>
        <option value="analyze">分析</option>
        <option value="compare">对比</option>
        <option value="premium">精品</option></select
      ><button
        v-if="items.length"
        class="text-sm text-[#b65345]"
        @click="clear"
      >
        清空全部
      </button>
    </div>
    <p v-if="loading" class="py-16 text-center text-[#9a958b]">正在整理名笺…</p>
    <p v-else-if="error" class="py-10 text-center text-[#b65345]">
      {{ error }}
    </p>
    <p v-else-if="!items.length" class="py-16 text-center text-[#9a958b]">
      还没有取名记录
    </p>
    <div v-else class="space-y-3">
      <article
        v-for="item in items"
        :key="item.id"
        class="rounded-2xl border border-[#d9d1c3] bg-white/55 p-5"
      >
        <div class="flex items-center justify-between gap-4">
          <button
            class="min-w-0 flex-1 text-left"
            @click="expanded = expanded === item.id ? null : item.id"
          >
            <p class="font-serif text-xl">
              {{ item.surname }} · {{ item.gender === "male" ? "男" : "女" }}
            </p>
            <p class="mt-1 text-xs text-[#9a958b]">
              {{ formatTime(item.created_at) }} · {{ item.names.length }} 个名字
            </p></button
          ><button class="text-xs text-[#b65345]" @click="remove(item.id)">
            删除
          </button>
        </div>
        <div
          v-if="expanded === item.id"
          class="mt-4 space-y-4 border-t border-[#e5dfd3] pt-4"
        >
          <div
            v-for="name in item.names"
            :key="name.full_name"
            class="border-l-2 border-[#32695d]/35 pl-4"
          >
            <p class="font-serif text-xl">{{ name.full_name }}</p>
            <p class="mt-1 text-sm leading-6 text-[#77736a]">
              {{ name.meaning }}
            </p>
          </div>
        </div>
      </article>
    </div></WorkspaceDrawer
  >
</template>
<script setup lang="ts">
import { onMounted, ref } from "vue";
import WorkspaceDrawer from "./WorkspaceDrawer.vue";
import { clearAllHistory, deleteHistory, getHistory } from "../api";
import type { HistoryItem } from "../types";
defineProps<{ open: boolean }>();
const emit = defineEmits<{ close: [] }>();
const items = ref<HistoryItem[]>([]),
  total = ref(0),
  loading = ref(true),
  error = ref(""),
  filter = ref(""),
  expanded = ref<number | null>(null);
const formatTime = (v: string) => v?.replace("T", " ").slice(0, 16) || "";
async function load() {
  loading.value = true;
  error.value = "";
  try {
    const r = await getHistory(0, 50, filter.value || undefined);
    items.value = r.items;
    total.value = r.total;
  } catch (e: any) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}
async function remove(id: number) {
  await deleteHistory(id);
  items.value = items.value.filter((i) => i.id !== id);
  total.value--;
}
async function clear() {
  if (!confirm("确定清空全部历史吗？")) return;
  await clearAllHistory();
  items.value = [];
  total.value = 0;
}
onMounted(load);
</script>

<template>
  <WorkspaceDrawer
    :open="open"
    title="收藏名笺"
    kicker="NAME COLLECTION"
    description="留住值得继续推敲的名字"
    width="620px"
    @close="emit('close')"
    ><p v-if="loading" class="py-16 text-center text-[#9a958b]">
      正在取出收藏…
    </p>
    <p v-else-if="error" class="py-10 text-center text-[#b65345]">
      {{ error }}
    </p>
    <p v-else-if="!items.length" class="py-16 text-center text-[#9a958b]">
      还没有收藏
    </p>
    <div v-else class="space-y-3">
      <article
        v-for="item in items"
        :key="item.id"
        class="rounded-2xl border border-[#d9d1c3] bg-white/55 p-5"
      >
        <div class="flex items-start justify-between gap-5">
          <div>
            <h3 class="font-serif text-2xl">{{ item.full_name }}</h3>
            <p class="mt-2 text-sm leading-6 text-[#77736a]">
              {{ item.name_data?.meaning || "" }}
            </p>
            <p class="mt-2 text-xs text-[#9a958b]">
              五行 {{ item.name_data?.wuxing }} · 出处
              {{ item.name_data?.source }}
            </p>
          </div>
          <button
            class="shrink-0 text-xs text-[#b65345]"
            @click="remove(item.id)"
          >
            取消收藏
          </button>
        </div>
      </article>
    </div></WorkspaceDrawer
  >
</template>
<script setup lang="ts">
import { onMounted, ref } from "vue";
import WorkspaceDrawer from "./WorkspaceDrawer.vue";
import { getFavorites, removeFavorite } from "../api";
defineProps<{ open: boolean }>();
const emit = defineEmits<{ close: [] }>();
const items = ref<any[]>([]),
  loading = ref(true),
  error = ref("");
async function load() {
  try {
    const r: any = await getFavorites();
    items.value = r.items;
  } catch (e: any) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}
async function remove(id: number) {
  try {
    await removeFavorite(id);
    items.value = items.value.filter((i) => i.id !== id);
  } catch (e: any) {
    error.value = e.message;
  }
}
onMounted(load);
</script>

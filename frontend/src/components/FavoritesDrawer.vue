<template>
  <WorkspaceDrawer
    :open="open"
    title="收藏名笺"
    kicker="NAME COLLECTION"
    description="留住值得继续推敲的名字"
    width="680px"
    :suspended="!!selected"
    @close="emit('close')"
  >
    <div v-if="loading" class="collection-loading" aria-label="正在取出收藏" aria-busy="true">
      <article v-for="i in 3" :key="i"><i /><b /><span /></article>
    </div>
    <div v-else-if="error" class="collection-state collection-state--error" role="alert">
      <p>{{ error }}</p><button type="button" @click="load">重新加载</button>
    </div>
    <div v-else-if="!items.length" class="collection-state">
      <svg viewBox="0 0 48 48" aria-hidden="true"><path d="M14 8h20v32L24 33l-10 7V8Z"/><path d="M20 17h8M20 23h8"/></svg>
      <h3>还没有收藏名笺</h3>
      <p>遇到喜欢的名字时，可以把它留在这里继续推敲。</p>
      <button type="button" @click="emit('close')">返回工作台</button>
    </div>
    <div v-else class="collection-list">
      <article v-for="(item, index) in items" :key="item.id" class="collection-card">
        <span class="collection-card__rule" aria-hidden="true" />
        <div class="collection-card__header">
          <button class="collection-card__identity" type="button" :aria-label="`打开 ${item.full_name} 的完整名笺`" @click="openDetail(item, index, $event)">
            <p>COLLECTED · {{ String(index + 1).padStart(2, "0") }}</p>
            <h3>{{ item.full_name }}</h3>
          </button>
          <button
            class="collection-card__remove"
            type="button"
            :disabled="removing.includes(item.id)"
            :aria-label="`取消收藏 ${item.full_name}`"
            @click="remove(item.id)"
          >
            <svg viewBox="0 0 20 20" aria-hidden="true"><path d="M5.5 3.25h9v13.5L10 13.9l-4.5 2.85V3.25Z"/><path d="m7 7 6 6M13 7l-6 6"/></svg>
          </button>
        </div>
        <p class="collection-card__meaning">{{ item.name_data?.meaning || "等待继续补充这枚名字的寓意。" }}</p>
        <dl>
          <div v-if="item.name_data?.wuxing"><dt>五行</dt><dd>{{ item.name_data.wuxing }}</dd></div>
          <div v-if="item.name_data?.source"><dt>出处</dt><dd>{{ item.name_data.source }}</dd></div>
        </dl>
        <button class="collection-card__folio" type="button" @click="openDetail(item, index, $event)">
          <span>展开完整名笺</span>
          <svg viewBox="0 0 20 20" aria-hidden="true"><path d="M4 10h11M11 6l4 4-4 4" /></svg>
        </button>
      </article>
    </div>
  </WorkspaceDrawer>
  <NameDetailSheet v-if="selected" :name="selected.name" :index="selected.index" @close="closeDetail" />
</template>

<script setup lang="ts">
import { nextTick, ref, watch } from "vue";
import WorkspaceDrawer from "./WorkspaceDrawer.vue";
import NameDetailSheet from "./NameDetailSheet.vue";
import { getFavorites, removeFavorite } from "../api";
import type { NameItem } from "../types";

interface FavoriteItem { id: number; full_name: string; name_data?: Partial<NameItem>; created_at?: string }
const props = defineProps<{ open: boolean }>();
const emit = defineEmits<{ close: [] }>();
const items = ref<FavoriteItem[]>([]);
const loading = ref(true);
const error = ref("");
const removing = ref<number[]>([]);
const selected = ref<{ name: NameItem; index: number } | null>(null);
let detailTrigger: HTMLElement | null = null;

watch(() => props.open, (value) => { if (value) load(); }, { immediate: true });
async function load() {
  loading.value = true; error.value = "";
  try { const result: any = await getFavorites(); items.value = result.items; }
  catch (cause: any) { error.value = cause.message || "收藏加载失败"; }
  finally { loading.value = false; }
}
async function remove(id: number) {
  if (removing.value.includes(id)) return;
  removing.value = [...removing.value, id]; error.value = "";
  try { await removeFavorite(id); items.value = items.value.filter((item) => item.id !== id); }
  catch (cause: any) { error.value = cause.message || "取消收藏失败"; }
  finally { removing.value = removing.value.filter((value) => value !== id); }
}
function openDetail(item: FavoriteItem, index: number, event: MouseEvent) {
  detailTrigger = event.currentTarget as HTMLElement;
  const data = item.name_data || {};
  selected.value = {
    index,
    name: {
      ...data,
      full_name: item.full_name,
      meaning: data.meaning || "这枚名字已经收入收藏，等待继续补充它的寓意。",
      wuxing: data.wuxing || "",
      source: data.source || "",
    },
  };
}
async function closeDetail() {
  selected.value = null;
  await nextTick();
  detailTrigger?.focus();
}
</script>

<style scoped>
.collection-list,.collection-loading { display: grid; gap: 14px; }
.collection-card { position: relative; overflow: hidden; border: 1px solid rgba(183,161,120,.34); border-radius: 21px; background: linear-gradient(135deg,rgba(255,254,249,.92),rgba(242,238,228,.75)); padding: 23px 24px 20px; transition: transform 180ms ease,border-color 180ms ease,box-shadow 180ms ease; }
.collection-card:hover { transform: translateY(-1px); border-color: rgba(50,105,93,.42); box-shadow: 0 14px 34px rgba(58,50,38,.08); }
.collection-card__rule { position: absolute; top: 0; left: 0; width: 108px; height: 2px; background: linear-gradient(90deg,#32695d 0 58%,#b7a178 58%); }
.collection-card__header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; }
.collection-card__identity { min-width: 0; cursor: pointer; text-align: left; }
.collection-card__header p { color: #8e887e; font-size: 9px; letter-spacing: .16em; }
.collection-card h3 { margin-top: 9px; font-family: "Songti SC","STSong",serif; font-size: 31px; font-weight: 400; letter-spacing: .07em; }
.collection-card__remove { display: grid; width: 44px; height: 44px; flex: 0 0 44px; cursor: pointer; place-items: center; border-radius: 50%; color: #a64235; transition: background-color 180ms ease; }
.collection-card__remove:hover { background: rgba(166,66,53,.08); }.collection-card__remove:disabled { cursor: wait; opacity: .4; }.collection-card button:focus-visible,.collection-state button:focus-visible { outline: 2px solid #32695d; outline-offset: 3px; }
.collection-card__header svg { width: 19px; height: 19px; fill: none; stroke: currentColor; stroke-linecap: round; stroke-linejoin: round; stroke-width: 1.35; }
.collection-card__meaning { margin-top: 16px; color: #57534b; font-size: 13px; line-height: 1.8; }
.collection-card dl { display: grid; grid-template-columns: .6fr 1.4fr; gap: 16px; margin-top: 17px; padding-top: 15px; border-top: 1px solid rgba(183,161,120,.24); }
.collection-card dt { color: #918b80; font-size: 9px; letter-spacing: .15em; }.collection-card dd { margin-top: 5px; color: #393730; font-family: "Songti SC","STSong",serif; font-size: 13px; line-height: 1.55; }
.collection-card__folio { display: inline-flex; min-height: 42px; cursor: pointer; align-items: center; gap: 9px; margin-top: 14px; color: #32695d; font-size: 11px; letter-spacing: .06em; }.collection-card__folio svg { width: 17px; fill: none; stroke: currentColor; stroke-linecap: round; stroke-linejoin: round; stroke-width: 1.4; transition: transform 180ms ease; }.collection-card__folio:hover svg { transform: translateX(3px); }
.collection-loading article { position: relative; overflow: hidden; height: 162px; border: 1px solid rgba(183,161,120,.25); border-radius: 21px; background: rgba(255,255,255,.42); padding: 24px; }
.collection-loading article::after { position: absolute; inset: 0; background: linear-gradient(105deg,transparent 30%,rgba(255,255,255,.65) 48%,transparent 65%); content: ""; animation: collection-shimmer 1.6s ease-in-out infinite; transform: translateX(-100%); }
.collection-loading i,.collection-loading b,.collection-loading span { display: block; border-radius: 999px; background: rgba(183,174,157,.27); }.collection-loading i { width: 120px; height: 8px; }.collection-loading b { width: 140px; height: 30px; margin-top: 15px; border-radius: 4px; }.collection-loading span { width: 85%; height: 10px; margin-top: 22px; }
.collection-state { display: grid; min-height: 360px; place-items: center; align-content: center; text-align: center; }.collection-state svg { width: 48px; height: 48px; fill: none; stroke: #b7a178; stroke-linecap: round; stroke-linejoin: round; stroke-width: 1.2; }.collection-state h3 { margin-top: 18px; font-family: "Songti SC","STSong",serif; font-size: 24px; font-weight: 400; }.collection-state p { max-width: 330px; margin-top: 8px; color: #77736a; font-size: 13px; line-height: 1.7; }.collection-state button { min-height: 44px; margin-top: 18px; cursor: pointer; color: #32695d; font-size: 13px; }.collection-state--error { color: #a64235; }.collection-state--error button { color: #a64235; }
@keyframes collection-shimmer { 55%,100% { transform: translateX(100%); } }
@media (max-width:640px) { .collection-card { padding: 21px 18px 18px; }.collection-card h3 { font-size: 27px; }.collection-card dl { grid-template-columns: 1fr; } }
@media (prefers-reduced-motion:reduce) { .collection-loading article::after { animation:none; }.collection-card { transition-duration:.01ms!important; } }
</style>

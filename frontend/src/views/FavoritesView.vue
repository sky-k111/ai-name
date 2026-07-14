<template>
  <div class="favorites-page">
    <span class="favorites-page__wash" aria-hidden="true" />
    <main>
      <header class="favorites-page__header">
        <div>
          <p>NAME COLLECTION · 私人名笺库</p>
          <h1>收藏名笺</h1>
          <span>把值得反复推敲的名字，留成一册。</span>
        </div>
        <button type="button" @click="$router.push('/')">返回工作台</button>
      </header>

      <div v-if="loading" class="favorites-state" aria-busy="true">正在取出收藏名笺…</div>
      <div v-else-if="!items.length" class="favorites-state">
        <strong>藏</strong><h2>册中尚无名笺</h2><p>从推荐结果中收藏一个名字，它会出现在这里。</p>
      </div>
      <section v-else class="favorites-grid" aria-label="收藏的名字">
        <article v-for="(item, index) in items" :key="item.id" class="favorite-card">
          <span class="favorite-card__rule" aria-hidden="true" />
          <div class="favorite-card__index">COLLECTED · {{ String(index + 1).padStart(2, '0') }}</div>
          <button class="favorite-card__name" type="button" @click="openDetail(item, index)">{{ item.full_name }}</button>
          <p>{{ item.name_data?.meaning || '这枚名字已经收入收藏，等待继续补充它的寓意。' }}</p>
          <dl>
            <div><dt>五行</dt><dd>{{ item.name_data?.wuxing || '待补充' }}</dd></div>
            <div><dt>出处</dt><dd>{{ item.name_data?.source || '待补充' }}</dd></div>
          </dl>
          <footer>
            <button type="button" @click="openDetail(item, index)">完整名笺 <span>→</span></button>
            <button type="button" class="favorite-card__remove" @click="handleRemove(item.id)">取消收藏</button>
          </footer>
        </article>
      </section>
    </main>
    <NameDetailSheet v-if="selected" :name="selected.name" :index="selected.index" @close="selected = null" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { getFavorites, removeFavorite } from "../api";
import NameDetailSheet from "../components/NameDetailSheet.vue";
import type { NameItem } from "../types";

interface FavoriteItem { id: number; full_name: string; name_data?: Partial<NameItem>; created_at?: string }
const items = ref<FavoriteItem[]>([]);
const loading = ref(true);
const selected = ref<{ name: NameItem; index: number } | null>(null);

async function load() { try { const result: any = await getFavorites(); items.value = result.items; } catch {} finally { loading.value = false; } }
async function handleRemove(id: number) { try { await removeFavorite(id); items.value = items.value.filter((item) => item.id !== id); } catch {} }
function openDetail(item: FavoriteItem, index: number) {
  const data = item.name_data || {};
  selected.value = { index, name: { ...data, full_name: item.full_name, meaning: data.meaning || "这枚名字已经收入收藏，等待继续补充它的寓意。", wuxing: data.wuxing || "", source: data.source || "" } };
}
onMounted(load);
</script>

<style scoped>
.favorites-page { position: relative; isolation: isolate; min-height: 100vh; overflow: hidden; background: radial-gradient(circle at 12% 18%,rgba(50,105,93,.09),transparent 26%),radial-gradient(circle at 88% 72%,rgba(183,161,120,.13),transparent 30%),#f6f3ec; color: #20211d; }
.favorites-page::before { position: fixed; z-index: -1; inset: 0; opacity: .28; background-image: repeating-radial-gradient(circle at 17% 23%,rgba(52,43,31,.05) 0 .45px,transparent .65px 4px); background-size: 6px 6px; content: ""; pointer-events: none; }
.favorites-page__wash { position: absolute; z-index: -1; top: 120px; right: -12vw; width: 46vw; height: 32vw; border-radius: 50%; background: radial-gradient(ellipse,rgba(36,54,46,.12),rgba(50,105,93,.04) 42%,transparent 72%); filter: blur(6px); transform: rotate(-14deg); }
.favorites-page main { width: min(1040px,calc(100% - 40px)); margin: 0 auto; padding: 64px 0 90px; }
.favorites-page__header { display: flex; align-items: flex-end; justify-content: space-between; gap: 32px; border-block: 1px solid rgba(183,161,120,.42); padding: 38px 0; }.favorites-page__header p { color: #32695d; font-size: 9px; letter-spacing: .22em; }.favorites-page__header h1 { margin-top: 14px; font-family: "Songti SC","STSong",serif; font-size: clamp(46px,7vw,78px); font-weight: 400; }.favorites-page__header span { display: block; margin-top: 12px; color: #777168; font-size: 13px; }.favorites-page__header button { min-height: 44px; cursor: pointer; border-bottom: 1px solid rgba(50,105,93,.4); color: #32695d; font-size: 12px; }
.favorites-grid { display: grid; grid-template-columns: repeat(2,minmax(0,1fr)); gap: 18px; margin-top: 34px; }.favorite-card { position: relative; overflow: hidden; border: 1px solid rgba(183,161,120,.38); border-radius: 24px; background: linear-gradient(142deg,rgba(255,254,249,.94),rgba(240,236,225,.82)); padding: 27px 28px 22px; box-shadow: 0 18px 48px rgba(58,50,38,.06); }.favorite-card__rule { position: absolute; top: 0; left: 0; width: 47%; height: 3px; background: linear-gradient(90deg,#32695d 0 55%,#b7a178 55%); }.favorite-card__index { color: #918b80; font-size: 8px; letter-spacing: .18em; }.favorite-card__name { display: block; cursor: pointer; margin-top: 16px; color: #22231f; font-family: "Songti SC","STSong",serif; font-size: 42px; letter-spacing: .08em; }.favorite-card>p { min-height: 50px; margin-top: 15px; color: #5c5850; font-size: 13px; line-height: 1.85; }.favorite-card dl { display: grid; grid-template-columns: .55fr 1.45fr; gap: 15px; margin-top: 17px; padding: 15px 0; border-block: 1px solid rgba(183,161,120,.25); }.favorite-card dt { color: #918b80; font-size: 8px; letter-spacing: .13em; }.favorite-card dd { margin-top: 5px; font-family: "Songti SC","STSong",serif; font-size: 12px; line-height: 1.55; }.favorite-card footer { display: flex; align-items: center; justify-content: space-between; gap: 14px; margin-top: 13px; }.favorite-card footer button { min-height: 42px; cursor: pointer; color: #32695d; font-size: 11px; }.favorite-card footer button span { display: inline-block; margin-left: 7px; transition: transform 180ms ease; }.favorite-card footer button:hover span { transform: translateX(3px); }.favorite-card footer .favorite-card__remove { color: #a64235; }.favorite-card button:focus-visible,.favorites-page__header button:focus-visible { outline: 2px solid #32695d; outline-offset: 3px; }
.favorites-state { display: grid; min-height: 430px; place-items: center; align-content: center; color: #777168; text-align: center; }.favorites-state strong { display: grid; width: 65px; height: 72px; place-items: center; border: 1px solid rgba(166,66,53,.5); color: #a64235; font-family: "STKaiti","KaiTi",serif; font-size: 28px; font-weight: 400; transform: rotate(-3deg); }.favorites-state h2 { margin-top: 22px; font-family: "Songti SC","STSong",serif; font-size: 25px; font-weight: 400; }.favorites-state p { margin-top: 8px; font-size: 13px; }
@media(max-width:700px){.favorites-page main{width:min(100% - 28px,1040px);padding-top:28px}.favorites-page__header{align-items:flex-start;flex-direction:column;padding:26px 0}.favorites-grid{grid-template-columns:1fr}.favorite-card{padding:24px 21px 20px}.favorite-card__name{font-size:36px}}
</style>

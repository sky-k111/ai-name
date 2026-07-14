<template>
  <article ref="card" class="name-card" :class="{ 'is-expanded': expanded }">
    <span ref="rule" class="name-card__rule" aria-hidden="true" />
    <div class="name-card__paper" aria-hidden="true" />

    <div class="name-card__body">
      <button
        type="button"
        class="name-card__summary"
        :aria-label="`${expanded ? '收起' : '展开'}名字 ${name.full_name} 的详细解读`"
        :aria-expanded="expanded"
        :aria-controls="detailId"
        @click="expanded = !expanded"
      >
        <span class="name-card__header">
          <span class="name-card__identity">
            <span class="name-card__eyebrow">
              <span>RECOMMENDED NAME</span>
              <span aria-hidden="true">·</span>
              <span>候选 {{ rankLabel }}</span>
            </span>
            <span class="name-card__name" role="heading" aria-level="3">{{ name.full_name }}</span>
          </span>

          <span
            class="name-card__seal"
            :aria-label="typeof name.score === 'number' ? `综合评分 ${name.score} 分` : '推荐候选名字'"
          >
            <strong>{{ typeof name.score === "number" ? name.score : "荐" }}</strong>
            <span>{{ typeof name.score === "number" ? "综合" : "入选" }}</span>
          </span>
        </span>

        <span class="name-card__meaning" :class="{ 'name-card__meaning--clamped': !expanded }">
          {{ name.summary || name.meaning }}
        </span>

        <span class="name-card__preview">
          <span class="name-card__preview-tags">
            <span v-if="name.wuxing">五行 · {{ name.wuxing }}</span>
            <span v-if="name.source">出处 · {{ name.source }}</span>
          </span>
          <span class="name-card__toggle-label">
            {{ expanded ? "收起名笺" : "展开详解" }}
            <svg viewBox="0 0 20 20" aria-hidden="true" :class="{ 'is-open': expanded }">
              <path d="m5.5 7.5 4.5 4.5 4.5-4.5" />
            </svg>
          </span>
        </span>
      </button>

      <div
        :id="detailId"
        class="name-card__expand-region"
        :class="{ 'is-open': expanded }"
        :aria-hidden="!expanded"
      >
        <div class="name-card__expand-inner">
          <dl v-if="metaItems.length" class="name-card__meta">
            <div v-for="item in metaItems" :key="item.label">
              <dt>{{ item.label }}</dt>
              <dd>{{ item.value }}</dd>
            </div>
          </dl>

          <div v-if="analysisItems.length" class="name-card__details">
            <section v-for="item in analysisItems" :key="item.label">
              <p>{{ item.english }}</p>
              <h4>{{ item.label }}</h4>
              <div>{{ item.text }}</div>
            </section>
          </div>
        </div>
      </div>

      <footer class="name-card__footer">
        <span class="name-card__quiet">一名一笺，自有来处</span>

        <button
          ref="favoriteButton"
          type="button"
          class="name-card__action name-card__action--favorite"
          :class="{
            'is-saving': favoriteState === 'saving',
            'is-saved': favoriteState === 'saved',
            'is-error': favoriteState === 'error',
          }"
          :aria-label="favoriteAriaLabel"
          :aria-pressed="favoriteState === 'saved'"
          :disabled="favoriteState === 'saving' || favoriteState === 'saved'"
          @click="handleFavorite"
        >
          <span ref="favoriteRing" class="name-card__favorite-ring" aria-hidden="true" />
          <svg ref="favoriteIcon" viewBox="0 0 20 20" aria-hidden="true">
            <path d="M5.5 3.25h9v13.5L10 13.9l-4.5 2.85V3.25Z" />
          </svg>
          <span>{{ favoriteLabel }}</span>
          <span v-if="favoriteState === 'saved'" ref="favoriteStamp" class="name-card__favorite-stamp" aria-hidden="true">藏</span>
        </button>
      </footer>
    </div>
  </article>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import gsap from "gsap";
import type { FavoriteAction, FavoriteCompletion, NameItem } from "../types";

const props = defineProps<{ name: NameItem; index: number }>();
const emit = defineEmits<{ favorite: [action: FavoriteAction] }>();
const card = ref<HTMLElement>();
const rule = ref<HTMLElement>();
const favoriteButton = ref<HTMLButtonElement>();
const favoriteIcon = ref<SVGElement>();
const favoriteRing = ref<HTMLElement>();
const favoriteStamp = ref<HTMLElement>();
const expanded = ref(false);
const favoriteState = ref<"idle" | "saving" | "saved" | "error">("idle");
const detailId = `name-detail-${Math.random().toString(36).slice(2)}`;
let entrance: gsap.core.Timeline | null = null;
let favoriteResetTimer: ReturnType<typeof setTimeout> | undefined;
let favoriteTweens: gsap.core.Tween[] = [];

const rankLabel = computed(() => String(props.name.rank || props.index + 1).padStart(2, "0"));
const popularityLabel = computed(() =>
  (props.name.popularity || "").replace("重名概率", "").replace("重名率", "") || "未知",
);
const metaItems = computed(() => [
  { label: "五行", value: props.name.wuxing },
  { label: "典籍出处", value: props.name.source },
  { label: "重名率", value: props.name.popularity ? popularityLabel.value : "" },
].filter((item): item is { label: string; value: string } => Boolean(item.value)));
const analysisItems = computed(() => [
  { label: "八字契合", english: "BIRTH CHART", text: props.name.bazi },
  { label: "音律解读", english: "PHONETICS", text: props.name.sound_analysis },
  { label: "字形审美", english: "CHARACTER", text: props.name.char_analysis },
].filter((item): item is { label: string; english: string; text: string } => Boolean(item.text)));
const favoriteLabel = computed(() => ({
  idle: "收藏名笺",
  saving: "正在收藏",
  saved: "已收藏",
  error: "收藏失败",
})[favoriteState.value]);
const favoriteAriaLabel = computed(() => favoriteState.value === "saved"
  ? `名字 ${props.name.full_name} 已收藏`
  : `${favoriteLabel.value}：${props.name.full_name}`);

function handleFavorite() {
  if (favoriteState.value === "saving" || favoriteState.value === "saved") return;
  if (favoriteResetTimer) clearTimeout(favoriteResetTimer);
  favoriteState.value = "saving";
  emit("favorite", { name: props.name, complete: completeFavorite });
}

async function completeFavorite(status: FavoriteCompletion) {
  favoriteTweens.forEach((tween) => tween.kill());
  favoriteTweens = [];
  if (status === "cancelled") {
    favoriteState.value = "idle";
    return;
  }
  if (status === "error") {
    favoriteState.value = "error";
    if (!matchMedia("(prefers-reduced-motion: reduce)").matches && favoriteButton.value) {
      favoriteTweens.push(gsap.fromTo(
        favoriteButton.value,
        { x: -5 },
        { x: 0, duration: 0.45, ease: "elastic.out(1, 0.28)", clearProps: "transform" },
      ));
    }
    favoriteResetTimer = setTimeout(() => { favoriteState.value = "idle"; }, 2600);
    return;
  }

  favoriteState.value = "saved";
  await nextTick();
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  if (favoriteIcon.value) {
    favoriteTweens.push(gsap.fromTo(
      favoriteIcon.value,
      { scale: 0.62, y: 5, rotation: -10 },
      { scale: 1, y: 0, rotation: 0, duration: 0.56, ease: "back.out(2.4)", clearProps: "transform" },
    ));
  }
  if (favoriteStamp.value) {
    favoriteTweens.push(gsap.fromTo(
      favoriteStamp.value,
      { autoAlpha: 0, scale: 1.7, rotation: -12 },
      { autoAlpha: 1, scale: 1, rotation: -3, duration: 0.48, ease: "back.out(2)" },
    ));
  }
  if (favoriteRing.value) {
    favoriteTweens.push(gsap.fromTo(
      favoriteRing.value,
      { autoAlpha: 0.55, scale: 0.35 },
      { autoAlpha: 0, scale: 1.5, duration: 0.62, ease: "power2.out" },
    ));
  }
}

onMounted(() => {
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  entrance = gsap.timeline({ delay: props.index * 0.07 })
    .fromTo(card.value!, { autoAlpha: 0, y: 20 }, { autoAlpha: 1, y: 0, duration: 0.58, ease: "power3.out", clearProps: "transform,opacity,visibility" })
    .fromTo(rule.value!, { scaleX: 0 }, { scaleX: 1, duration: 0.48, ease: "power2.out", clearProps: "transform" }, 0.1);
});

onBeforeUnmount(() => {
  entrance?.kill();
  favoriteTweens.forEach((tween) => tween.kill());
  if (favoriteResetTimer) clearTimeout(favoriteResetTimer);
});
</script>

<style scoped>
.name-card {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  border: 1px solid rgba(183, 161, 120, 0.38);
  border-radius: 28px;
  background: linear-gradient(138deg, rgba(255, 254, 249, 0.96), rgba(245, 241, 231, 0.92));
  box-shadow: 0 18px 52px rgba(58, 50, 38, 0.08);
  color: #191916;
  transition: transform 220ms ease, border-color 220ms ease, box-shadow 220ms ease;
}
.name-card:hover {
  transform: translateY(-2px);
  border-color: rgba(50, 105, 93, 0.42);
  box-shadow: 0 24px 64px rgba(58, 50, 38, 0.12);
}
.name-card.is-expanded {
  border-color: rgba(50, 105, 93, 0.48);
  box-shadow: 0 26px 68px rgba(50, 80, 67, 0.12);
}
.name-card__rule {
  position: absolute;
  z-index: 2;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  transform-origin: left;
  background: linear-gradient(90deg, #32695d 0 24%, #b7a178 24% 64%, transparent 88%);
}
.name-card__paper {
  position: absolute;
  z-index: -1;
  inset: 0;
  opacity: 0.34;
  background-image:
    repeating-radial-gradient(circle at 18% 24%, rgba(52, 43, 31, 0.05) 0 0.45px, transparent 0.65px 4px),
    linear-gradient(110deg, rgba(255, 255, 255, 0.5), transparent 45%, rgba(136, 108, 65, 0.06));
  background-size: 6px 6px, 100% 100%;
  pointer-events: none;
}
.name-card__body { position: relative; z-index: 1; padding: 30px 32px 24px; }
.name-card__summary {
  display: block;
  width: 100%;
  cursor: pointer;
  color: inherit;
  text-align: left;
}
.name-card__summary:focus-visible {
  border-radius: 16px;
  outline: 2px solid #32695d;
  outline-offset: 7px;
}
.name-card__header { display: flex; align-items: flex-start; justify-content: space-between; gap: 24px; }
.name-card__identity { display: block; min-width: 0; }
.name-card__eyebrow { display: flex; flex-wrap: wrap; gap: 8px; color: #77736a; font-size: 10px; letter-spacing: 0.18em; }
.name-card__name { display: block; margin-top: 14px; font-family: "Songti SC", "STSong", serif; font-size: clamp(38px, 5vw, 54px); font-weight: 400; line-height: 1.08; letter-spacing: 0.08em; }
.name-card__seal { position: relative; display: grid; flex: 0 0 58px; height: 64px; place-items: center; align-content: center; border: 1px solid rgba(166, 66, 53, 0.58); color: #9b4035; transform: rotate(2deg); }
.name-card__seal::before { position: absolute; width: 48px; height: 54px; border: 1px solid rgba(166, 66, 53, 0.22); content: ""; }
.name-card__seal strong { font-family: "STKaiti", "KaiTi", serif; font-size: 24px; font-weight: 400; line-height: 1; }
.name-card__seal span { margin-top: 4px; font-size: 8px; letter-spacing: 0.2em; }
.name-card__meaning { display: block; max-width: 680px; margin-top: 20px; color: #49473f; font-size: 15px; line-height: 1.85; }
.name-card__meaning--clamped { display: -webkit-box; overflow: hidden; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }
.name-card__preview { display: flex; align-items: center; justify-content: space-between; gap: 18px; margin-top: 18px; }
.name-card__preview-tags { display: flex; min-width: 0; flex-wrap: wrap; gap: 7px; }
.name-card__preview-tags > span { overflow: hidden; max-width: 300px; padding: 6px 9px; border: 1px solid rgba(183, 161, 120, 0.24); border-radius: 999px; background: rgba(235, 231, 220, 0.46); color: #6f6a61; font-size: 10px; text-overflow: ellipsis; white-space: nowrap; }
.name-card__toggle-label { display: inline-flex; flex: 0 0 auto; align-items: center; gap: 6px; color: #32695d; font-size: 12px; }
.name-card__toggle-label svg { width: 17px; height: 17px; fill: none; stroke: currentColor; stroke-linecap: round; stroke-linejoin: round; stroke-width: 1.5; transition: transform 220ms ease; }
.name-card__toggle-label svg.is-open { transform: rotate(180deg); }
.name-card__expand-region { display: grid; grid-template-rows: 0fr; opacity: 0; transition: grid-template-rows 280ms cubic-bezier(0.22, 1, 0.36, 1), opacity 180ms ease; }
.name-card__expand-region.is-open { grid-template-rows: 1fr; opacity: 1; }
.name-card__expand-inner { min-height: 0; overflow: hidden; }
.name-card__meta { display: grid; grid-template-columns: minmax(120px, 0.65fr) minmax(220px, 1.7fr) minmax(90px, 0.55fr); gap: 16px; margin-top: 20px; padding: 18px 0; border-block: 1px solid rgba(183, 161, 120, 0.28); }
.name-card__meta div { min-width: 0; }
.name-card__meta dt { color: #918b80; font-size: 10px; letter-spacing: 0.16em; }
.name-card__meta dd { margin-top: 6px; color: #292923; font-family: "Songti SC", "STSong", serif; font-size: 14px; line-height: 1.55; }
.name-card__details { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; padding-top: 18px; }
.name-card__details section { border-left: 2px solid rgba(50, 105, 93, 0.28); background: rgba(235, 231, 220, 0.58); padding: 16px; }
.name-card__details section > p { color: #918b80; font-size: 8px; letter-spacing: 0.18em; }
.name-card__details h4 { margin-top: 7px; font-family: "Songti SC", "STSong", serif; font-size: 17px; font-weight: 400; }
.name-card__details section > div { margin-top: 9px; color: #5d5950; font-size: 13px; line-height: 1.75; }
.name-card__footer { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-top: 17px; padding-top: 16px; border-top: 1px solid rgba(183, 161, 120, 0.2); }
.name-card__action { display: inline-flex; cursor: pointer; align-items: center; gap: 8px; border-radius: 999px; color: #32695d; font-size: 12px; transition: color 180ms ease, background-color 180ms ease; }
.name-card__action:focus-visible { outline: 2px solid #32695d; outline-offset: 4px; }
.name-card__action svg { width: 17px; height: 17px; fill: none; stroke: currentColor; stroke-linecap: round; stroke-linejoin: round; stroke-width: 1.5; }
.name-card__action--favorite { position: relative; overflow: visible; min-width: 112px; justify-content: center; padding: 9px 13px; border: 1px solid rgba(50, 105, 93, 0.28); }
.name-card__action--favorite:hover { background: rgba(50, 105, 93, 0.08); }
.name-card__action--favorite:disabled { cursor: default; opacity: 1; }
.name-card__action--favorite.is-saving { cursor: wait; color: #7d817c; }
.name-card__action--favorite.is-saving svg { animation: bookmark-breathe 900ms ease-in-out infinite alternate; }
.name-card__action--favorite.is-saved { border-color: rgba(50, 105, 93, 0.48); background: rgba(50, 105, 93, 0.1); color: #254c40; }
.name-card__action--favorite.is-saved svg { fill: currentColor; }
.name-card__action--favorite.is-error { border-color: rgba(166, 66, 53, 0.42); color: #9b4035; }
.name-card__favorite-ring { position: absolute; width: 30px; height: 30px; border: 1px solid rgba(166, 66, 53, 0.58); border-radius: 999px; opacity: 0; pointer-events: none; }
.name-card__favorite-stamp { display: grid; width: 22px; height: 22px; place-items: center; border: 1px solid rgba(166, 66, 53, 0.58); color: #9b4035; font-family: "STKaiti", "KaiTi", serif; font-size: 10px; transform: rotate(-3deg); }
.name-card__quiet { color: #918b80; font-family: "Songti SC", "STSong", serif; font-size: 12px; }
@keyframes bookmark-breathe { to { opacity: 0.48; transform: translateY(-1px); } }

@media (max-width: 640px) {
  .name-card { border-radius: 20px; }
  .name-card__body { padding: 24px 20px 18px; }
  .name-card__header { gap: 16px; }
  .name-card__name { font-size: 38px; }
  .name-card__seal { flex-basis: 50px; height: 56px; }
  .name-card__seal::before { width: 41px; height: 47px; }
  .name-card__meta { grid-template-columns: 1fr 1fr; }
  .name-card__meta div:nth-child(2) { grid-column: 1 / -1; grid-row: 2; }
  .name-card__details { grid-template-columns: 1fr; }
  .name-card__preview { align-items: flex-start; flex-direction: column; gap: 12px; }
  .name-card__preview-tags > span { max-width: min(250px, 72vw); }
  .name-card__footer { align-items: stretch; flex-direction: column; }
  .name-card__action--favorite { justify-content: center; }
}

@media (prefers-reduced-motion: reduce) {
  .name-card, .name-card__action, .name-card__action svg, .name-card__toggle-label svg, .name-card__expand-region { transition-duration: 0.01ms !important; }
  .name-card__action--favorite.is-saving svg { animation: none; }
}
</style>

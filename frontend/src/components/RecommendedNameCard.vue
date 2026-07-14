<template>
  <article ref="card" class="name-card">
    <span ref="rule" class="name-card__rule" aria-hidden="true" />
    <div class="name-card__paper" aria-hidden="true" />

    <div class="name-card__body">
      <header class="name-card__header">
        <div class="name-card__identity">
          <p class="name-card__eyebrow">
            <span>RECOMMENDED NAME</span>
            <span aria-hidden="true">·</span>
            <span>候选 {{ rankLabel }}</span>
          </p>
          <h3>{{ name.full_name }}</h3>
        </div>

        <div
          class="name-card__seal"
          :aria-label="typeof name.score === 'number' ? `综合评分 ${name.score} 分` : '推荐候选名字'"
        >
          <strong>{{ typeof name.score === "number" ? name.score : "荐" }}</strong>
          <span>{{ typeof name.score === "number" ? "综合" : "入选" }}</span>
        </div>
      </header>

      <p
        class="name-card__meaning"
        :class="{ 'name-card__meaning--clamped': hasLongMeaning && !expanded }"
      >
        {{ name.summary || name.meaning }}
      </p>

      <dl class="name-card__meta">
        <div v-if="name.wuxing">
          <dt>五行</dt>
          <dd>{{ name.wuxing }}</dd>
        </div>
        <div v-if="name.source">
          <dt>出处</dt>
          <dd>{{ name.source }}</dd>
        </div>
        <div v-if="name.popularity">
          <dt>重名率</dt>
          <dd>{{ popularityLabel }}</dd>
        </div>
      </dl>

      <Transition name="detail-fade">
        <div v-if="expanded && analysisItems.length" :id="detailId" class="name-card__details">
          <section v-for="item in analysisItems" :key="item.label">
            <p>{{ item.english }}</p>
            <h4>{{ item.label }}</h4>
            <div>{{ item.text }}</div>
          </section>
        </div>
      </Transition>

      <footer class="name-card__footer">
        <button
          v-if="hasDetails"
          type="button"
          class="name-card__action name-card__action--details"
          :aria-expanded="expanded"
          :aria-controls="analysisItems.length ? detailId : undefined"
          @click="expanded = !expanded"
        >
          <span>{{ expanded ? "收起解读" : "展开完整解读" }}</span>
          <svg viewBox="0 0 20 20" aria-hidden="true" :class="{ 'is-open': expanded }">
            <path d="m5.5 7.5 4.5 4.5 4.5-4.5" />
          </svg>
        </button>
        <span v-else class="name-card__quiet">一名一笺，自有来处</span>

        <button
          type="button"
          class="name-card__action name-card__action--favorite"
          :aria-label="`收藏名字 ${name.full_name}`"
          @click="emit('favorite', name)"
        >
          <svg viewBox="0 0 20 20" aria-hidden="true">
            <path d="M5.5 3.25h9v13.5L10 13.9l-4.5 2.85V3.25Z" />
          </svg>
          <span>收藏名笺</span>
        </button>
      </footer>
    </div>
  </article>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import gsap from "gsap";
import type { NameItem } from "../types";

const props = defineProps<{ name: NameItem; index: number }>();
const emit = defineEmits<{ favorite: [name: NameItem] }>();
const card = ref<HTMLElement>();
const rule = ref<HTMLElement>();
const expanded = ref(false);
const detailId = `name-detail-${Math.random().toString(36).slice(2)}`;
let entrance: gsap.core.Timeline | null = null;

const rankLabel = computed(() => String(props.name.rank || props.index + 1).padStart(2, "0"));
const popularityLabel = computed(() =>
  (props.name.popularity || "").replace("重名概率", "").replace("重名率", "") || "未知",
);
const hasLongMeaning = computed(() => (props.name.summary || props.name.meaning || "").length > 88);
const analysisItems = computed(() => [
  { label: "八字契合", english: "BIRTH CHART", text: props.name.bazi },
  { label: "音律解读", english: "PHONETICS", text: props.name.sound_analysis },
  { label: "字形审美", english: "CHARACTER", text: props.name.char_analysis },
].filter((item): item is { label: string; english: string; text: string } => Boolean(item.text)));
const hasDetails = computed(() => hasLongMeaning.value || analysisItems.value.length > 0);

onMounted(() => {
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  entrance = gsap.timeline({ delay: props.index * 0.07 })
    .fromTo(card.value!, { autoAlpha: 0, y: 20 }, { autoAlpha: 1, y: 0, duration: 0.58, ease: "power3.out", clearProps: "transform,opacity,visibility" })
    .fromTo(rule.value!, { scaleX: 0 }, { scaleX: 1, duration: 0.48, ease: "power2.out", clearProps: "transform" }, 0.1);
});

onBeforeUnmount(() => entrance?.kill());
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
.name-card__header { display: flex; align-items: flex-start; justify-content: space-between; gap: 24px; }
.name-card__identity { min-width: 0; }
.name-card__eyebrow { display: flex; flex-wrap: wrap; gap: 8px; color: #77736a; font-size: 10px; letter-spacing: 0.18em; }
.name-card h3 { margin-top: 14px; font-family: "Songti SC", "STSong", serif; font-size: clamp(38px, 5vw, 54px); font-weight: 400; line-height: 1.08; letter-spacing: 0.08em; }
.name-card__seal { position: relative; display: grid; flex: 0 0 58px; height: 64px; place-items: center; align-content: center; border: 1px solid rgba(166, 66, 53, 0.58); color: #9b4035; transform: rotate(2deg); }
.name-card__seal::before { position: absolute; width: 48px; height: 54px; border: 1px solid rgba(166, 66, 53, 0.22); content: ""; }
.name-card__seal strong { font-family: "STKaiti", "KaiTi", serif; font-size: 24px; font-weight: 400; line-height: 1; }
.name-card__seal span { margin-top: 4px; font-size: 8px; letter-spacing: 0.2em; }
.name-card__meaning { max-width: 680px; margin-top: 22px; color: #49473f; font-size: 15px; line-height: 1.9; }
.name-card__meaning--clamped { display: -webkit-box; overflow: hidden; -webkit-box-orient: vertical; -webkit-line-clamp: 3; }
.name-card__meta { display: grid; grid-template-columns: minmax(120px, 0.65fr) minmax(220px, 1.7fr) minmax(90px, 0.55fr); gap: 16px; margin-top: 24px; padding: 18px 0; border-block: 1px solid rgba(183, 161, 120, 0.28); }
.name-card__meta div { min-width: 0; }
.name-card__meta dt { color: #918b80; font-size: 10px; letter-spacing: 0.16em; }
.name-card__meta dd { margin-top: 6px; color: #292923; font-family: "Songti SC", "STSong", serif; font-size: 14px; line-height: 1.55; }
.name-card__details { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; padding-top: 18px; }
.name-card__details section { border-left: 2px solid rgba(50, 105, 93, 0.28); background: rgba(235, 231, 220, 0.58); padding: 16px; }
.name-card__details section > p { color: #918b80; font-size: 8px; letter-spacing: 0.18em; }
.name-card__details h4 { margin-top: 7px; font-family: "Songti SC", "STSong", serif; font-size: 17px; font-weight: 400; }
.name-card__details section > div { margin-top: 9px; color: #5d5950; font-size: 13px; line-height: 1.75; }
.name-card__footer { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding-top: 18px; }
.name-card__action { display: inline-flex; cursor: pointer; align-items: center; gap: 8px; border-radius: 999px; color: #32695d; font-size: 12px; transition: color 180ms ease, background-color 180ms ease; }
.name-card__action:focus-visible { outline: 2px solid #32695d; outline-offset: 4px; }
.name-card__action svg { width: 17px; height: 17px; fill: none; stroke: currentColor; stroke-linecap: round; stroke-linejoin: round; stroke-width: 1.5; }
.name-card__action--details { padding: 8px 2px; }
.name-card__action--details svg { transition: transform 200ms ease; }
.name-card__action--details svg.is-open { transform: rotate(180deg); }
.name-card__action--favorite { padding: 9px 13px; border: 1px solid rgba(50, 105, 93, 0.28); }
.name-card__action--favorite:hover { background: rgba(50, 105, 93, 0.08); }
.name-card__quiet { color: #918b80; font-family: "Songti SC", "STSong", serif; font-size: 12px; }
.detail-fade-enter-active, .detail-fade-leave-active { transition: opacity 180ms ease, transform 180ms ease; }
.detail-fade-enter-from, .detail-fade-leave-to { opacity: 0; transform: translateY(-6px); }

@media (max-width: 640px) {
  .name-card { border-radius: 20px; }
  .name-card__body { padding: 24px 20px 18px; }
  .name-card__header { gap: 16px; }
  .name-card h3 { font-size: 38px; }
  .name-card__seal { flex-basis: 50px; height: 56px; }
  .name-card__seal::before { width: 41px; height: 47px; }
  .name-card__meta { grid-template-columns: 1fr 1fr; }
  .name-card__meta div:nth-child(2) { grid-column: 1 / -1; grid-row: 2; }
  .name-card__details { grid-template-columns: 1fr; }
  .name-card__footer { align-items: stretch; flex-direction: column; }
  .name-card__action--favorite { justify-content: center; }
}

@media (prefers-reduced-motion: reduce) {
  .name-card, .name-card__action, .name-card__action svg, .detail-fade-enter-active, .detail-fade-leave-active { transition-duration: 0.01ms !important; }
}
</style>

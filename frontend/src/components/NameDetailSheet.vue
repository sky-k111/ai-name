<template>
  <Teleport to="body">
    <div ref="layer" class="detail-layer" @mousedown.self="requestClose">
      <article
        ref="panel"
        class="detail-sheet"
        role="dialog"
        aria-modal="true"
        :aria-labelledby="titleId"
        :aria-describedby="summaryId"
        tabindex="-1"
      >
        <span class="detail-sheet__rule" aria-hidden="true" />
        <header class="detail-sheet__topbar">
          <div>
            <p>COMPLETE NAME FOLIO · 完整名笺</p>
            <span>候选 {{ rankLabel }}</span>
          </div>
          <button ref="closeButton" type="button" aria-label="关闭完整名笺" @click="requestClose">
            <svg viewBox="0 0 20 20" aria-hidden="true"><path d="M5 5l10 10M15 5 5 15" /></svg>
          </button>
        </header>

        <div class="detail-sheet__layout">
          <aside class="detail-sheet__identity">
            <div class="detail-sheet__index"><span>NAME</span><strong>{{ rankLabel }}</strong></div>
            <h2 :id="titleId">{{ name.full_name }}</h2>
            <div class="detail-sheet__glyphs" aria-hidden="true">
              <span v-for="(char, index) in characters" :key="`${char}-${index}`">{{ char }}</span>
            </div>
            <div class="detail-sheet__seal" :aria-label="scoreLabel">
              <strong>{{ typeof name.score === "number" ? name.score : "荐" }}</strong>
              <span>{{ typeof name.score === "number" ? "综合评分" : "推荐入选" }}</span>
            </div>
            <dl>
              <div v-if="name.wuxing"><dt>五行</dt><dd>{{ name.wuxing }}</dd></div>
              <div v-if="name.popularity"><dt>重名参考</dt><dd>{{ popularityLabel }}</dd></div>
              <div v-if="name.source"><dt>典籍</dt><dd>{{ name.source }}</dd></div>
            </dl>
          </aside>

          <main class="detail-sheet__content">
            <section class="detail-lead">
              <p class="detail-kicker">WHY THIS NAME</p>
              <h3>为什么是这个名字</h3>
              <p :id="summaryId">{{ name.naming_story || name.summary || name.meaning }}</p>
            </section>

            <section v-if="name.source || name.source_quote || name.source_context" class="detail-source">
              <div class="detail-heading"><span>01</span><div><p>ORIGIN & CONTEXT</p><h3>典故与出处</h3></div></div>
              <blockquote v-if="name.source_quote">“{{ name.source_quote }}”</blockquote>
              <p class="detail-source__book">{{ name.source }}</p>
              <p v-if="name.source_context" class="detail-copy">{{ name.source_context }}</p>
              <p v-else class="detail-copy">{{ name.meaning }}</p>
              <p class="detail-source__notice">典籍线索由模型整理，定名前建议核对原文。</p>
            </section>

            <div class="detail-grid">
              <section v-if="name.character_meaning || name.char_analysis">
                <div class="detail-heading"><span>02</span><div><p>CHARACTERS</p><h3>字义与字形</h3></div></div>
                <p class="detail-copy">{{ name.character_meaning || name.char_analysis }}</p>
                <p v-if="name.character_meaning && name.char_analysis" class="detail-note">{{ name.char_analysis }}</p>
              </section>
              <section v-if="name.sound_analysis">
                <div class="detail-heading"><span>03</span><div><p>PHONETICS</p><h3>音律与称呼</h3></div></div>
                <p class="detail-copy">{{ name.sound_analysis }}</p>
              </section>
              <section v-if="name.bazi || name.wuxing">
                <div class="detail-heading"><span>04</span><div><p>ELEMENTS</p><h3>五行与命理</h3></div></div>
                <p class="detail-copy">{{ name.bazi || `此名五行取向为${name.wuxing}。` }}</p>
              </section>
              <section v-if="name.usage_advice || name.popularity">
                <div class="detail-heading"><span>05</span><div><p>IN USE</p><h3>使用建议</h3></div></div>
                <p class="detail-copy">{{ name.usage_advice || `重名参考：${popularityLabel}` }}</p>
              </section>
            </div>

            <footer>
              <span>一名一笺，自有来处</span>
              <button type="button" @click="requestClose">返回候选名字</button>
            </footer>
          </main>
        </div>
      </article>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import gsap from "gsap";
import type { NameItem } from "../types";

const props = defineProps<{ name: NameItem; index: number }>();
const emit = defineEmits<{ close: [] }>();
const layer = ref<HTMLElement>();
const panel = ref<HTMLElement>();
const closeButton = ref<HTMLButtonElement>();
const titleId = `name-folio-title-${Math.random().toString(36).slice(2)}`;
const summaryId = `name-folio-summary-${Math.random().toString(36).slice(2)}`;
const rankLabel = computed(() => String(props.name.rank || props.index + 1).padStart(2, "0"));
const characters = computed(() => Array.from(props.name.full_name));
const popularityLabel = computed(() => (props.name.popularity || "").replace("重名概率", "").replace("重名率", "") || "未知");
const scoreLabel = computed(() => typeof props.name.score === "number" ? `综合评分 ${props.name.score} 分` : "推荐候选名字");
const reduceMotion = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
let closing = false;
let previousFocus: HTMLElement | null = null;
let originalOverflow = "";
let layerTween: gsap.core.Tween | undefined;
let panelTween: gsap.core.Tween | undefined;

onMounted(async () => {
  previousFocus = document.activeElement as HTMLElement | null;
  originalOverflow = document.body.style.overflow;
  document.body.style.overflow = "hidden";
  document.addEventListener("keydown", handleKeydown);
  await nextTick();
  closeButton.value?.focus();
  if (reduceMotion()) return;
  layerTween = gsap.fromTo(layer.value!, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.22, ease: "power2.out" });
  panelTween = gsap.fromTo(panel.value!, { autoAlpha: 0, y: 24, scale: 0.985 }, { autoAlpha: 1, y: 0, scale: 1, duration: 0.38, ease: "power3.out", clearProps: "transform,opacity,visibility" });
});

function requestClose() {
  if (closing) return;
  closing = true;
  if (reduceMotion()) { emit("close"); return; }
  panelTween = gsap.to(panel.value!, { autoAlpha: 0, y: 18, scale: 0.99, duration: 0.24, ease: "power2.in" });
  layerTween = gsap.to(layer.value!, { autoAlpha: 0, duration: 0.22, ease: "power2.in", onComplete: () => emit("close") });
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === "Escape") { event.preventDefault(); requestClose(); return; }
  if (event.key !== "Tab" || !panel.value) return;
  const focusable = Array.from(panel.value.querySelectorAll<HTMLElement>('button:not([disabled]), [href], [tabindex]:not([tabindex="-1"])'));
  if (!focusable.length) return;
  const first = focusable[0];
  const last = focusable[focusable.length - 1];
  if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
  else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
}

onBeforeUnmount(() => {
  document.removeEventListener("keydown", handleKeydown);
  layerTween?.kill();
  panelTween?.kill();
  document.body.style.overflow = originalOverflow;
  previousFocus?.focus();
});
</script>

<style scoped>
.detail-layer { position: fixed; z-index: 145; inset: 0; display: grid; place-items: center; padding: 18px; background: rgba(25, 25, 22, 0.5); backdrop-filter: blur(8px); }
.detail-sheet { position: relative; overflow: hidden auto; width: min(1080px, 100%); max-height: calc(100dvh - 36px); border: 1px solid rgba(183, 161, 120, 0.5); border-radius: 30px; outline: none; background: #f8f5ec; box-shadow: 0 34px 100px rgba(20, 26, 23, 0.3); color: #20211d; }
.detail-sheet::before { position: absolute; z-index: 0; inset: 0; opacity: 0.34; background-image: repeating-radial-gradient(circle at 18% 24%, rgba(52,43,31,.05) 0 .45px, transparent .65px 4px); background-size: 6px 6px; content: ""; pointer-events: none; }
.detail-sheet__rule { position: absolute; z-index: 2; top: 0; left: 0; width: 72%; height: 3px; background: linear-gradient(90deg,#32695d 0 34%,#b7a178 34% 72%,transparent); }
.detail-sheet__topbar,.detail-sheet__layout { position: relative; z-index: 1; }
.detail-sheet__topbar { display: flex; align-items: center; justify-content: space-between; padding: 22px 28px; border-bottom: 1px solid rgba(183,161,120,.28); }
.detail-sheet__topbar > div { display: flex; align-items: center; gap: 12px; }
.detail-sheet__topbar p { color: #32695d; font-size: 9px; letter-spacing: .2em; }
.detail-sheet__topbar span { color: #918b80; font-size: 10px; }
.detail-sheet__topbar button { display: grid; width: 44px; height: 44px; cursor: pointer; place-items: center; border: 1px solid rgba(50,105,93,.24); border-radius: 999px; color: #32695d; }
.detail-sheet__topbar button:hover { background: rgba(50,105,93,.08); }
.detail-sheet__topbar button:focus-visible,.detail-sheet__content footer button:focus-visible { outline: 2px solid #32695d; outline-offset: 3px; }
.detail-sheet__topbar svg { width: 18px; height: 18px; fill: none; stroke: currentColor; stroke-linecap: round; stroke-width: 1.5; }
.detail-sheet__layout { display: grid; grid-template-columns: minmax(250px,.72fr) minmax(0,1.8fr); }
.detail-sheet__identity { position: sticky; top: 0; align-self: start; min-height: 620px; padding: 40px 34px; border-right: 1px solid rgba(183,161,120,.28); background: rgba(235,231,220,.34); }
.detail-sheet__index { display: flex; align-items: baseline; justify-content: space-between; color: #b7a178; }
.detail-sheet__index span { font-size: 8px; letter-spacing: .2em; }.detail-sheet__index strong { font-family: Georgia,serif; font-size: 24px; font-weight: 400; }
.detail-sheet__identity h2 { margin-top: 34px; font-family: "Songti SC","STSong",serif; font-size: clamp(50px,6vw,72px); font-weight: 400; line-height: 1.08; letter-spacing: .08em; writing-mode: vertical-rl; }
.detail-sheet__glyphs { display: flex; flex-wrap: wrap; gap: 7px; margin-top: 28px; }.detail-sheet__glyphs span { display: grid; width: 34px; height: 34px; place-items: center; border: 1px solid rgba(183,161,120,.32); color: #777168; font-family: "STKaiti","KaiTi",serif; }
.detail-sheet__seal { display: grid; width: 70px; height: 76px; place-items: center; align-content: center; margin-top: 28px; border: 1px solid rgba(166,66,53,.58); color: #9b4035; transform: rotate(-2deg); }.detail-sheet__seal strong { font-family: Georgia,serif; font-size: 27px; font-weight: 400; }.detail-sheet__seal span { margin-top: 5px; font-size: 7px; letter-spacing: .14em; }
.detail-sheet__identity dl { display: grid; gap: 14px; margin-top: 32px; padding-top: 22px; border-top: 1px solid rgba(183,161,120,.28); }.detail-sheet__identity dt { color: #918b80; font-size: 9px; letter-spacing: .13em; }.detail-sheet__identity dd { margin-top: 5px; color: #3d403a; font-family: "Songti SC","STSong",serif; font-size: 13px; line-height: 1.6; }
.detail-sheet__content { padding: 46px 48px 34px; }
.detail-kicker,.detail-heading p { color: #918b80; font-size: 8px; letter-spacing: .2em; }.detail-lead h3 { margin-top: 12px; font-family: "Songti SC","STSong",serif; font-size: 30px; font-weight: 400; }.detail-lead > p:last-child { margin-top: 18px; color: #454840; font-size: 16px; line-height: 2; }
.detail-source,.detail-grid section { margin-top: 34px; padding-top: 26px; border-top: 1px solid rgba(183,161,120,.3); }.detail-heading { display: flex; align-items: flex-start; gap: 14px; }.detail-heading > span { color: #b7a178; font-family: Georgia,serif; font-size: 13px; }.detail-heading h3 { margin-top: 6px; font-family: "Songti SC","STSong",serif; font-size: 20px; font-weight: 400; }
.detail-source blockquote { margin: 26px 0 0; color: #254c40; font-family: "STKaiti","KaiTi",serif; font-size: clamp(23px,3vw,34px); line-height: 1.55; }.detail-source__book { margin-top: 14px; color: #9b4035; font-size: 11px; letter-spacing: .08em; }.detail-copy { margin-top: 18px; color: #50534d; font-size: 14px; line-height: 1.95; }.detail-note { margin-top: 12px; padding-left: 12px; border-left: 2px solid rgba(50,105,93,.28); color: #777b74; font-size: 12px; line-height: 1.8; }
.detail-source__notice { margin-top: 12px; color: #918b80; font-size: 10px; letter-spacing: .06em; }
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; column-gap: 28px; }.detail-sheet__content footer { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-top: 44px; padding-top: 22px; border-top: 1px solid rgba(183,161,120,.34); }.detail-sheet__content footer span { color: #918b80; font-family: "STKaiti","KaiTi",serif; font-size: 13px; }.detail-sheet__content footer button { min-height: 44px; cursor: pointer; border: 1px solid rgba(50,105,93,.3); border-radius: 999px; padding: 0 18px; color: #32695d; font-size: 12px; }
@media(max-width:760px){.detail-layer{padding:0}.detail-sheet{width:100%;height:100dvh;max-height:none;border:0;border-radius:0}.detail-sheet__topbar{padding:16px 18px}.detail-sheet__topbar>div{align-items:flex-start;flex-direction:column;gap:5px}.detail-sheet__layout{grid-template-columns:1fr}.detail-sheet__identity{position:relative;min-height:0;padding:28px 22px;border-right:0;border-bottom:1px solid rgba(183,161,120,.28)}.detail-sheet__identity h2{margin-top:22px;font-size:52px;writing-mode:initial}.detail-sheet__glyphs{margin-top:20px}.detail-sheet__seal{position:absolute;top:67px;right:22px;margin:0}.detail-sheet__identity dl{grid-template-columns:1fr 1fr}.detail-sheet__identity dl div:last-child{grid-column:1/-1}.detail-sheet__content{padding:32px 22px 28px}.detail-lead>p:last-child,.detail-copy{font-size:16px}.detail-grid{grid-template-columns:1fr}.detail-sheet__content footer{align-items:stretch;flex-direction:column}.detail-sheet__content footer button{width:100%}}
@media(prefers-reduced-motion:reduce){.detail-layer{backdrop-filter:none}}
</style>

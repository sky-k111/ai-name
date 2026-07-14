<template>
  <section ref="root" class="creation-stage" aria-busy="true">
    <span class="creation-stage__rule" aria-hidden="true" />
    <span class="creation-stage__grain" aria-hidden="true" />
    <p class="sr-only" role="status" aria-live="polite">正在生成推荐名字，请稍候。</p>

    <header class="creation-stage__header">
      <div>
        <p>AI NAMING IN PROGRESS</p>
        <h3>一枚名字，正在成笺</h3>
      </div>
      <span>PROCESS · {{ String(stageIndex + 1).padStart(2, "0") }}</span>
    </header>

    <div class="creation-stage__canvas" aria-hidden="true">
      <svg class="creation-stage__ink" viewBox="0 0 620 260" preserveAspectRatio="none">
        <path class="ink-path ink-path--wash" d="M-35 189C70 105 155 228 254 142S412 83 494 127s127 8 171-34" />
        <path class="ink-path" d="M-22 204C89 124 162 224 260 151s169-80 252-22 119 5 156-24" />
        <path class="ink-path ink-path--fine" d="M35 72c89 22 145-49 229-13s151 32 244-9" />
      </svg>

      <div class="creation-stage__folio">
        <span class="creation-stage__folio-index">NAME / FOLIO</span>
        <div class="creation-stage__character"><span>名</span><i /></div>
        <p>{{ stages[stageIndex].label }}</p>
        <small>{{ stages[stageIndex].detail }}</small>
      </div>

      <div class="creation-stage__slips">
        <span v-for="stage in stages" :key="stage.label" class="creation-slip" :class="{ 'is-active': stage.label === stages[stageIndex].label }">
          <i>{{ stage.glyph }}</i><b>{{ stage.label }}</b>
        </span>
      </div>
      <span class="creation-stage__brush" />
    </div>

    <footer class="creation-stage__footer">
      <div class="creation-stage__steps" aria-hidden="true">
        <i v-for="(_, index) in stages" :key="index" :class="{ 'is-active': index === stageIndex }" />
      </div>
      <p>模型正在综合字义、音律与文化出处</p>
      <span>通常需要数秒</span>
    </footer>
  </section>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";
import gsap from "gsap";

const stages = [
  { glyph: "字", label: "择字", detail: "从含义与气质中寻找合适的字" },
  { glyph: "音", label: "辨音", detail: "推敲声调、节奏与日常称呼" },
  { glyph: "典", label: "寻典", detail: "整理可追溯的文化出处" },
  { glyph: "笺", label: "成笺", detail: "汇成一组可以继续比较的名字" },
];
const root = ref<HTMLElement>();
const stageIndex = ref(0);
const media = gsap.matchMedia();
let timeline: gsap.core.Timeline | null = null;

onMounted(() => {
  if (!root.value) return;
  media.add({ motion: "(prefers-reduced-motion: no-preference)", reduce: "(prefers-reduced-motion: reduce)" }, (context) => {
    if (context.conditions?.reduce) return;
    const paths = Array.from(root.value!.querySelectorAll<SVGPathElement>(".ink-path"));
    paths.forEach((path) => {
      const length = path.getTotalLength();
      gsap.set(path, { strokeDasharray: length, strokeDashoffset: length });
    });
    const slips = root.value!.querySelectorAll(".creation-slip");
    const character = root.value!.querySelector(".creation-stage__character span");
    const brush = root.value!.querySelector(".creation-stage__brush");
    timeline = gsap.timeline({ repeat: -1, defaults: { ease: "power2.out" } })
      .set(paths, { strokeDashoffset: (_index, target: SVGPathElement) => target.getTotalLength(), autoAlpha: 0.18 })
      .set(slips, { autoAlpha: 0, y: 12 })
      .set(brush, { xPercent: -120, autoAlpha: 0 })
      .call(() => { stageIndex.value = 0; })
      .to(paths, { strokeDashoffset: 0, autoAlpha: 0.72, duration: 2.8, stagger: 0.12, ease: "power1.inOut" }, 0)
      .to(slips, { autoAlpha: 1, y: 0, duration: 0.48, stagger: 0.18 }, 0.18)
      .fromTo(character, { autoAlpha: 0.35, scale: 0.92 }, { autoAlpha: 1, scale: 1, duration: 0.8, ease: "power3.out" }, 0.2)
      .to(brush, { xPercent: 130, autoAlpha: 0.7, duration: 1.6, ease: "power2.inOut" }, 0.25)
      .call(() => { stageIndex.value = 1; }, [], 1.05)
      .call(() => { stageIndex.value = 2; }, [], 1.95)
      .call(() => { stageIndex.value = 3; }, [], 2.85)
      .to(character, { scale: 1.025, duration: 0.6, yoyo: true, repeat: 1 }, 2.7)
      .to(paths, { autoAlpha: 0.22, duration: 0.5, ease: "power2.in" }, 3.65)
      .to(slips, { autoAlpha: 0.42, y: -5, duration: 0.42, ease: "power2.in" }, 3.65)
      .to({}, { duration: 0.22 });
  }, root.value);
});

onBeforeUnmount(() => { timeline?.kill(); media.revert(); });
</script>

<style scoped>
.creation-stage { position: relative; isolation: isolate; overflow: hidden; min-height: 430px; border: 1px solid rgba(183,161,120,.4); border-radius: 30px; background: linear-gradient(145deg,rgba(255,254,249,.96),rgba(239,235,224,.88)); box-shadow: 0 22px 62px rgba(58,50,38,.08); color: #22231f; }
.creation-stage__rule { position: absolute; z-index: 4; top: 0; left: 0; width: 74%; height: 3px; background: linear-gradient(90deg,#32695d 0 31%,#b7a178 31% 68%,transparent); }
.creation-stage__grain { position: absolute; z-index: -1; inset: 0; opacity: .42; background-image: repeating-radial-gradient(circle at 19% 23%,rgba(52,43,31,.055) 0 .45px,transparent .65px 4px),linear-gradient(112deg,rgba(255,255,255,.48),transparent 48%,rgba(122,101,67,.06)); background-size: 6px 6px,100% 100%; }
.creation-stage__header { display: flex; align-items: flex-start; justify-content: space-between; gap: 24px; padding: 28px 32px 20px; border-bottom: 1px solid rgba(183,161,120,.25); }
.creation-stage__header p,.creation-stage__header > span,.creation-stage__folio-index { color: #817b71; font-size: 8px; letter-spacing: .22em; }
.creation-stage__header h3 { margin-top: 10px; font-family: "Songti SC","STSong",serif; font-size: clamp(24px,3vw,32px); font-weight: 400; letter-spacing: .04em; }
.creation-stage__header > span { color: #32695d; white-space: nowrap; }
.creation-stage__canvas { position: relative; display: grid; min-height: 264px; grid-template-columns: minmax(220px,.8fr) minmax(300px,1.2fr); align-items: center; padding: 28px 34px 24px; }
.creation-stage__ink { position: absolute; z-index: -1; inset: 0; width: 100%; height: 100%; opacity: .68; }
.ink-path { fill: none; stroke: #32695d; stroke-width: 1.45; stroke-linecap: round; vector-effect: non-scaling-stroke; }.ink-path--wash { opacity: .09; stroke: #1f2924; stroke-width: 17; filter: blur(5px); }.ink-path--fine { opacity: .25; stroke: #b7a178; stroke-width: .85; }
.creation-stage__folio { position: relative; align-self: stretch; border-right: 1px solid rgba(183,161,120,.29); padding: 12px 30px 8px 0; }
.creation-stage__character { position: relative; display: grid; width: 98px; height: 112px; place-items: center; margin-top: 17px; border: 1px solid rgba(50,105,93,.2); background: rgba(248,246,238,.72); }
.creation-stage__character::before,.creation-stage__character::after { position: absolute; background: rgba(183,161,120,.2); content: ""; }.creation-stage__character::before { top: 50%; left: 0; width: 100%; height: 1px; }.creation-stage__character::after { top: 0; left: 50%; width: 1px; height: 100%; }
.creation-stage__character span { position: relative; z-index: 1; font-family: "STKaiti","KaiTi",serif; font-size: 64px; line-height: 1; }.creation-stage__character i { position: absolute; right: -12px; bottom: -9px; width: 32px; height: 38px; border: 1px solid rgba(166,66,53,.58); transform: rotate(-4deg); }
.creation-stage__folio > p { margin-top: 20px; color: #2d5549; font-family: "Songti SC","STSong",serif; font-size: 20px; }.creation-stage__folio > small { display: block; max-width: 230px; margin-top: 7px; color: #777168; font-size: 11px; line-height: 1.7; }
.creation-stage__slips { display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; padding-left: 32px; }
.creation-slip { display: flex; min-height: 144px; align-items: center; flex-direction: column; justify-content: space-between; border: 1px solid rgba(183,161,120,.3); background: rgba(250,248,240,.68); padding: 17px 8px 14px; transition: border-color 220ms ease,background-color 220ms ease,color 220ms ease; }.creation-slip.is-active { border-color: rgba(50,105,93,.5); background: rgba(235,240,234,.82); color: #2d5549; }.creation-slip i { font-family: "STKaiti","KaiTi",serif; font-size: 31px; font-style: normal; }.creation-slip b { font-size: 9px; font-weight: 400; letter-spacing: .18em; writing-mode: vertical-rl; }
.creation-stage__brush { position: absolute; right: 9%; bottom: 22%; width: 42%; height: 1px; transform-origin: left; background: linear-gradient(90deg,transparent,#a64235 45%,transparent); box-shadow: 0 0 9px rgba(166,66,53,.24); }
.creation-stage__footer { display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: 15px; border-top: 1px solid rgba(183,161,120,.25); padding: 17px 32px; color: #777168; font-size: 10px; }.creation-stage__footer > span { color: #9a9489; letter-spacing: .08em; }
.creation-stage__steps { display: flex; gap: 5px; }.creation-stage__steps i { width: 15px; height: 2px; background: rgba(183,161,120,.38); transition: background-color 220ms ease,transform 220ms ease; }.creation-stage__steps i.is-active { background: #32695d; transform: scaleX(1.15); }
@media(max-width:700px){.creation-stage{min-height:0;border-radius:22px}.creation-stage__header{padding:23px 20px 17px}.creation-stage__header>span{display:none}.creation-stage__canvas{grid-template-columns:1fr;gap:25px;padding:24px 20px}.creation-stage__folio{display:grid;grid-template-columns:88px 1fr;grid-template-rows:auto auto auto;border-right:0;border-bottom:1px solid rgba(183,161,120,.28);padding:0 0 22px}.creation-stage__folio-index{grid-column:1/-1}.creation-stage__character{grid-row:2/4;width:72px;height:82px}.creation-stage__character span{font-size:48px}.creation-stage__folio>p{align-self:end;margin-top:15px}.creation-stage__folio>small{align-self:start}.creation-stage__slips{gap:6px;padding-left:0}.creation-slip{min-height:110px;padding:13px 5px 10px}.creation-slip i{font-size:25px}.creation-stage__footer{grid-template-columns:auto 1fr;padding:15px 20px}.creation-stage__footer>span{display:none}}
@media(prefers-reduced-motion:reduce){.creation-slip,.creation-stage__steps i{transition:none}}
</style>

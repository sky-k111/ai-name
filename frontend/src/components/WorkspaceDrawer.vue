<template>
  <Teleport to="body"><div v-if="open" ref="layer" class="drawer-layer fixed inset-0 z-[80] flex items-center justify-end bg-[#191916]/35 p-3 backdrop-blur-[3px] sm:p-5" @click.self="close">
      <aside ref="panel" role="dialog" :aria-modal="suspended ? undefined : 'true'" :aria-hidden="suspended ? 'true' : undefined" :inert="suspended || undefined" :aria-labelledby="drawerId" class="drawer-panel relative w-full overflow-hidden rounded-[28px] bg-[#f6f3ec] shadow-[-24px_0_80px_rgba(25,25,22,.2)]" :style="{ maxWidth: width }">
        <div class="absolute inset-y-0 left-0 w-px bg-[#b7a178]/50" /><div ref="accent" class="absolute left-0 top-0 h-32 w-[3px] origin-top bg-[#32695d]" />
        <div class="drawer-paper" aria-hidden="true"><span>笺</span><i /></div>
        <div class="relative z-[1] flex h-full flex-col">
          <header class="drawer-item flex shrink-0 items-start justify-between border-b border-[#d9d1c3] px-7 py-7 sm:px-10">
            <div><p class="text-xs tracking-[.24em] text-[#32695d]">{{ kicker }}</p><h2 :id="drawerId" class="mt-3 font-serif text-4xl">{{ title }}</h2><p v-if="description" class="mt-2 text-sm text-[#77736a]">{{ description }}</p></div>
            <button class="group grid h-10 w-10 place-items-center rounded-full border border-[#d9d1c3] text-xl text-[#77736a]" aria-label="关闭" @click="close"><span class="transition-transform duration-300 group-hover:rotate-90">×</span></button>
          </header>
          <main class="drawer-content min-h-0 flex-1 overflow-y-auto overscroll-contain px-7 py-7 sm:px-10"><slot /></main>
        </div>
      </aside></div
  ></Teleport>
</template>
<script setup lang="ts">
import { nextTick, onBeforeUnmount, ref, watch } from "vue";
import gsap from "gsap";
const props = withDefaults(defineProps<{ open: boolean; title: string; kicker: string; description?: string; width?: string; suspended?: boolean }>(), { width: "640px", suspended: false });
const emit = defineEmits<{ close: [] }>();
const layer = ref<HTMLElement>(); const panel = ref<HTMLElement>(); const accent = ref<HTMLElement>(); const drawerId = `drawer-${Math.random().toString(36).slice(2)}`;
let timeline: gsap.core.Timeline | null = null;
watch(() => props.open, async (value) => {
    if (!value) return;
    const scrollY = window.scrollY;
    document.body.style.position = "fixed";
    document.body.style.top = `-${scrollY}px`;
    document.body.style.width = "100%";
    await nextTick();
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) { window.addEventListener("keydown", onKey); return }
    timeline?.kill();
    timeline = gsap.timeline({ defaults: { ease: "power3.out" } })
      .fromTo(layer.value!, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.24 })
      .fromTo(panel.value!, { xPercent: 104 }, { xPercent: 0, duration: 0.62 }, 0)
      .fromTo(accent.value!, { scaleY: 0 }, { scaleY: 1, duration: 0.5 }, 0.2)
      .fromTo(panel.value!.querySelectorAll(".drawer-item, .drawer-content > *"), { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, duration: 0.42, stagger: 0.045 }, 0.2);
    window.addEventListener("keydown", onKey);
}, { immediate: true });
function onKey(e: KeyboardEvent) { if (e.key === "Escape" && !props.suspended) close(); }
function finish() { const scrollY = document.body.style.top; document.body.style.position = ""; document.body.style.top = ""; document.body.style.width = ""; window.scrollTo(0, parseInt(scrollY || "0") * -1); window.removeEventListener("keydown", onKey); emit("close"); }
function close() { if (!timeline || matchMedia("(prefers-reduced-motion: reduce)").matches) { finish(); return } timeline.eventCallback("onReverseComplete", finish).timeScale(1.35).reverse(); }
onBeforeUnmount(() => { timeline?.kill(); const scrollY = document.body.style.top; document.body.style.position = ""; document.body.style.top = ""; document.body.style.width = ""; window.scrollTo(0, parseInt(scrollY || "0") * -1); window.removeEventListener("keydown", onKey); });
</script>
<style scoped>
.drawer-layer { will-change: opacity; }
.drawer-panel {
  height: calc(100dvh - 24px);
  background-image: radial-gradient(circle at 82% 18%,rgba(183,161,120,.12),transparent 25%),linear-gradient(145deg,rgba(255,254,249,.45),transparent 44%);
  will-change: transform;
}
.drawer-content { scrollbar-gutter: stable; }
.drawer-paper { position: absolute; z-index: 0; inset: 0; overflow: hidden; opacity: .5; pointer-events: none; }
.drawer-paper::before { position: absolute; inset: 0; opacity: .38; background-image: repeating-radial-gradient(circle at 19% 23%,rgba(52,43,31,.045) 0 .45px,transparent .65px 4px); background-size: 6px 6px; content: ""; }
.drawer-paper span { position: absolute; right: -22px; top: 15%; color: rgba(50,105,93,.045); font-family: "STKaiti","KaiTi",serif; font-size: 190px; line-height: 1; transform: rotate(6deg); }
.drawer-paper i { position: absolute; right: -30%; bottom: -12%; width: 94%; height: 42%; border-radius: 50%; background: radial-gradient(ellipse,rgba(50,105,93,.12),rgba(183,161,120,.06) 42%,transparent 72%); filter: blur(8px); transform: rotate(-12deg); }
@media (min-width: 640px) {
  .drawer-panel { height: min(760px, calc(100dvh - 40px)); }
}
</style>

<template>
  <Teleport to="body">
    <div class="action-toast-layer">
      <div
        ref="panel"
        class="action-toast"
        :class="`action-toast--${type}`"
        :role="type === 'error' ? 'alert' : 'status'"
        :aria-live="type === 'error' ? 'assertive' : 'polite'"
      >
        <span class="action-toast__seal" aria-hidden="true">{{ type === "error" ? "缓" : "藏" }}</span>
        <span class="action-toast__copy">
          <strong>{{ title }}</strong>
          <span v-if="detail">{{ detail }}</span>
        </span>
        <button type="button" aria-label="关闭提示" @click="dismiss">
          <svg viewBox="0 0 20 20" aria-hidden="true"><path d="M5 5l10 10M15 5 5 15" /></svg>
        </button>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";
import gsap from "gsap";

const props = withDefaults(defineProps<{
  title: string;
  detail?: string;
  type?: "success" | "info" | "error";
  duration?: number;
}>(), { detail: "", type: "success", duration: 4200 });
const emit = defineEmits<{ close: [] }>();
const panel = ref<HTMLElement>();
let timer: ReturnType<typeof setTimeout> | undefined;
let enterTween: gsap.core.Tween | undefined;
let exitTween: gsap.core.Tween | undefined;
let closing = false;

const reduceMotion = () => matchMedia("(prefers-reduced-motion: reduce)").matches;

onMounted(() => {
  if (!reduceMotion()) {
    enterTween = gsap.fromTo(
      panel.value!,
      { autoAlpha: 0, y: -16, scale: 0.96 },
      { autoAlpha: 1, y: 0, scale: 1, duration: 0.42, ease: "back.out(1.7)", clearProps: "transform,opacity,visibility" },
    );
  }
  timer = setTimeout(dismiss, props.duration);
});

function dismiss() {
  if (closing) return;
  closing = true;
  if (timer) clearTimeout(timer);
  if (reduceMotion()) {
    emit("close");
    return;
  }
  exitTween = gsap.to(panel.value!, {
    autoAlpha: 0,
    y: -10,
    scale: 0.98,
    duration: 0.22,
    ease: "power2.in",
    onComplete: () => emit("close"),
  });
}

onBeforeUnmount(() => {
  if (timer) clearTimeout(timer);
  enterTween?.kill();
  exitTween?.kill();
});
</script>

<style scoped>
.action-toast-layer { position: fixed; z-index: 160; top: 22px; right: 18px; left: 18px; display: flex; justify-content: center; pointer-events: none; }
.action-toast { display: grid; width: min(440px, 100%); min-height: 72px; grid-template-columns: 42px minmax(0, 1fr) 36px; align-items: center; gap: 13px; padding: 12px 12px 12px 14px; border: 1px solid rgba(50, 105, 93, 0.32); border-radius: 18px; background: rgba(250, 248, 240, 0.96); box-shadow: 0 20px 60px rgba(31, 43, 37, 0.2); color: #254c40; backdrop-filter: blur(16px); pointer-events: auto; }
.action-toast--error { border-color: rgba(166, 66, 53, 0.38); color: #8e3d34; }
.action-toast__seal { display: grid; width: 40px; height: 40px; place-items: center; border: 1px solid rgba(166, 66, 53, 0.55); color: #9b4035; font-family: "STKaiti", "KaiTi", serif; font-size: 17px; transform: rotate(-3deg); }
.action-toast__copy { display: flex; min-width: 0; flex-direction: column; gap: 4px; }
.action-toast__copy strong { overflow: hidden; font-family: "Songti SC", "STSong", serif; font-size: 16px; font-weight: 400; text-overflow: ellipsis; white-space: nowrap; }
.action-toast__copy > span { color: #747a74; font-size: 11px; line-height: 1.5; }
.action-toast button { display: grid; width: 36px; height: 36px; cursor: pointer; place-items: center; border-radius: 999px; color: #7b837e; }
.action-toast button:hover { background: rgba(50, 105, 93, 0.08); }
.action-toast button:focus-visible { outline: 2px solid currentColor; outline-offset: 2px; }
.action-toast svg { width: 16px; height: 16px; fill: none; stroke: currentColor; stroke-linecap: round; stroke-width: 1.5; }
@media (max-width: 520px) { .action-toast-layer { top: 12px; right: 10px; left: 10px; }.action-toast { min-height: 66px; grid-template-columns: 38px minmax(0, 1fr) 34px; border-radius: 15px; }.action-toast__seal { width: 36px; height: 36px; } }
@media (prefers-reduced-motion: reduce) { .action-toast { backdrop-filter: none; } }
</style>

<template>
  <form class="writing-form" :aria-busy="loading" @submit.prevent="handleSubmit">
    <span class="writing-form__rule" aria-hidden="true" />
    <div class="writing-form__grain" aria-hidden="true" />

    <div class="writing-form__primary">
      <label class="surname-field">
        <span class="field-heading">
          <span>姓氏</span>
          <em>必填</em>
        </span>
        <span class="surname-field__input">
          <input
            v-model.trim="form.surname"
            type="text"
            maxlength="5"
            autocomplete="family-name"
            placeholder="输入姓氏"
            :disabled="disabled"
            required
            @input="syncModel"
          />
          <i aria-hidden="true">氏</i>
        </span>
        <small>复姓也可以直接填写</small>
      </label>

      <fieldset class="gender-field" :disabled="disabled">
        <legend class="field-heading"><span>性别</span></legend>
        <div class="gender-options">
          <button
            v-for="option in genderOptions"
            :key="option.value"
            type="button"
            :class="{ 'is-active': form.gender === option.value }"
            :aria-pressed="form.gender === option.value"
            @click="selectGender(option.value)"
          >
            <span aria-hidden="true">{{ option.seal }}</span>
            <strong>{{ option.label }}</strong>
          </button>
        </div>
      </fieldset>
    </div>

    <div class="writing-form__timing">
      <label class="line-field">
        <span class="field-heading"><span>出生日期</span></span>
        <span class="line-field__control">
          <input
            v-model="form.birthday"
            type="date"
            :disabled="disabled"
            aria-label="出生日期"
            @input="syncModel"
          />
        </span>
      </label>

      <label class="line-field">
        <span class="field-heading"><span>出生时辰</span></span>
        <span class="line-field__control line-field__control--select">
          <select v-model="form.birth_time" :disabled="disabled" aria-label="出生时辰" @change="syncModel">
            <option value="">请选择时辰</option>
            <option v-for="time in timeOptions" :key="time" :value="time">{{ time }}</option>
          </select>
          <svg viewBox="0 0 20 20" aria-hidden="true"><path d="m5.5 7.5 4.5 4.5 4.5-4.5" /></svg>
        </span>
      </label>
    </div>

    <section class="writing-form__optional" aria-labelledby="optional-title">
      <div class="optional-heading">
        <p id="optional-title">补充线索</p>
      </div>

      <label class="line-field line-field--wide">
        <span class="field-heading"><span>取名风格</span></span>
        <span class="line-field__control">
          <input
            v-model.trim="form.style"
            type="text"
            maxlength="50"
            placeholder="例如：文雅书香、清朗自然、沉稳大气"
            :disabled="disabled"
            @input="syncModel"
          />
        </span>
      </label>

      <label class="note-field">
        <span class="field-heading"><span>其他说明</span></span>
        <textarea
          v-model.trim="form.expectations"
          maxlength="200"
          rows="3"
          placeholder="例如寓意、字数、避讳字，或希望名字传达的气质。"
          :disabled="disabled"
          @input="syncModel"
        />
        <span class="note-field__count">{{ form.expectations?.length || 0 }} / 200</span>
      </label>
    </section>

    <footer class="writing-form__footer">
      <p>填写姓氏即可开始，其他线索用于提高匹配度。</p>
      <button type="submit" :disabled="disabled || !canSubmit" class="submit-button">
        <span v-if="loading" class="submit-button__spinner" aria-hidden="true" />
        <span>{{ loading ? "正在生成" : "生成名字" }}</span>
        <svg v-if="!loading" viewBox="0 0 20 20" aria-hidden="true"><path d="M4 10h11M11 6l4 4-4 4" /></svg>
      </button>
    </footer>
  </form>
</template>

<script setup lang="ts">
import { computed, reactive, watch } from "vue";
import type { Gender, GenerateRequest } from "../types";

const props = defineProps<{
  modelValue: GenerateRequest;
  loading: boolean;
  disabled: boolean;
}>();
const emit = defineEmits<{
  "update:modelValue": [value: GenerateRequest];
  submit: [value: GenerateRequest];
}>();

const genderOptions = [
  { label: "男", seal: "乾", value: "male" as Gender },
  { label: "女", seal: "坤", value: "female" as Gender },
];
const timeOptions = ["子时", "丑时", "寅时", "卯时", "辰时", "巳时", "午时", "未时", "申时", "酉时", "戌时", "亥时"];
const form = reactive<GenerateRequest>({ ...props.modelValue });
const canSubmit = computed(() => Boolean(form.surname.trim() && form.gender));

watch(() => props.modelValue, (value) => Object.assign(form, value), { deep: true });
function syncModel() { emit("update:modelValue", { ...form }); }
function selectGender(gender: Gender) { form.gender = gender; syncModel(); }
function handleSubmit() { if (canSubmit.value && !props.disabled) emit("submit", { ...form }); }
</script>

<style scoped>
.writing-form { position: relative; isolation: isolate; overflow: hidden; border: 1px solid rgba(183,161,120,.36); border-radius: 26px; background: linear-gradient(138deg,rgba(255,254,249,.92),rgba(244,240,230,.78)); box-shadow: 0 18px 50px rgba(58,50,38,.06); color: #191916; }
.writing-form__rule { position: absolute; z-index: 2; top: 0; left: 0; width: 68%; height: 3px; background: linear-gradient(90deg,#32695d 0 38%,#b7a178 38% 76%,transparent); }
.writing-form__grain { position: absolute; z-index: -1; inset: 0; opacity: .28; background-image: repeating-radial-gradient(circle at 18% 24%,rgba(52,43,31,.05) 0 .45px,transparent .65px 4px),linear-gradient(110deg,rgba(255,255,255,.48),transparent 46%,rgba(136,108,65,.05)); background-size: 6px 6px,100% 100%; pointer-events: none; }
.writing-form__primary { display: grid; grid-template-columns: minmax(0,1.45fr) minmax(230px,.75fr); gap: 0; }
.surname-field,.gender-field { min-width: 0; padding: 29px 30px 26px; }
.gender-field { border-left: 1px solid rgba(183,161,120,.26); }
.field-heading { display: flex; align-items: center; justify-content: space-between; gap: 12px; color: #4f4b44; font-size: 14px; font-style: normal; font-weight: 500; letter-spacing: .05em; }
.field-heading em { color: #8f887d; font-size: 10px; font-style: normal; font-weight: 400; letter-spacing: .12em; }
.surname-field__input { display: flex; align-items: baseline; margin-top: 15px; border-bottom: 1px solid rgba(50,105,93,.34); }
.surname-field__input::after,.line-field__control::after { position: absolute; right: 0; bottom: -1px; left: 0; height: 1px; background: #32695d; content: ""; transform: scaleX(0); transform-origin: left; transition: transform 220ms ease; }
.surname-field:focus-within .surname-field__input::after,.line-field:focus-within .line-field__control::after { transform: scaleX(1); }
.surname-field__input { position: relative; }
.surname-field__input input { min-width: 0; flex: 1; background: transparent; padding: 3px 0 9px; color: #191916; font-family: "Songti SC","STSong",serif; font-size: clamp(34px,4.5vw,48px); line-height: 1.1; letter-spacing: .08em; outline: none; }
.surname-field__input input::placeholder { color: #c2bcb0; }.surname-field__input i { color: #aaa296; font-family: "STKaiti","KaiTi",serif; font-size: 18px; font-style: normal; }
.surname-field small { display: block; margin-top: 9px; color: #777168; font-size: 12px; }
.gender-options { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 17px; }
.gender-options button { display: flex; min-height: 66px; cursor: pointer; align-items: center; justify-content: center; gap: 10px; border: 1px solid rgba(183,161,120,.38); border-radius: 14px; background: rgba(255,255,255,.34); color: #68635a; transition: border-color 180ms ease,background-color 180ms ease,color 180ms ease; }
.gender-options button:hover { border-color: rgba(50,105,93,.42); }.gender-options button.is-active { border-color: #32695d; background: rgba(50,105,93,.08); color: #32695d; }
.gender-options button > span { display: grid; width: 29px; height: 33px; place-items: center; border: 1px solid currentColor; font-family: "STKaiti","KaiTi",serif; font-size: 13px; }.gender-options strong { font-size: 16px; font-weight: 500; }
.writing-form__timing { display: grid; grid-template-columns: 1fr 1fr; border-top: 1px solid rgba(183,161,120,.26); border-bottom: 1px solid rgba(183,161,120,.26); }
.line-field { min-width: 0; padding: 22px 30px 21px; }.line-field + .line-field { border-left: 1px solid rgba(183,161,120,.26); }
.line-field__control { position: relative; display: flex; align-items: center; margin-top: 10px; border-bottom: 1px solid rgba(183,161,120,.28); }
.line-field input,.line-field select { min-width: 0; min-height: 46px; width: 100%; cursor: text; appearance: none; border: 0; background: transparent; color: #292923; font-size: 16px; outline: none; }
.line-field select { cursor: pointer; padding-right: 28px; }.line-field input::placeholder,.note-field textarea::placeholder { color: #aaa49a; }
.line-field__control--select svg { position: absolute; right: 2px; width: 18px; height: 18px; fill: none; stroke: #77736a; stroke-linecap: round; stroke-linejoin: round; stroke-width: 1.4; pointer-events: none; }
.writing-form__optional { padding: 25px 30px 27px; }.optional-heading { display: flex; align-items: baseline; justify-content: space-between; gap: 14px; }.optional-heading p { font-family: "Songti SC","STSong",serif; font-size: 24px; }
.line-field--wide { margin-top: 20px; padding: 0; }.note-field { position: relative; display: block; margin-top: 24px; }.note-field textarea { width: 100%; min-height: 108px; resize: vertical; border: 1px solid rgba(183,161,120,.3); border-radius: 15px; background: rgba(255,255,255,.34); margin-top: 11px; padding: 15px 16px 29px; color: #292923; font-size: 16px; line-height: 1.75; outline: none; transition: border-color 180ms ease,background-color 180ms ease; }.note-field textarea:focus { border-color: #32695d; background: rgba(255,255,255,.58); }.note-field__count { position: absolute; right: 13px; bottom: 10px; color: #918b80; font-size: 11px; letter-spacing: .06em; }
.writing-form__footer { display: flex; align-items: center; justify-content: space-between; gap: 24px; border-top: 1px solid rgba(183,161,120,.26); padding: 22px 30px; background: rgba(235,231,220,.35); }.writing-form__footer > p { max-width: 420px; color: #555149; font-family: "Songti SC","STSong",serif; font-size: 14px; line-height: 1.65; }
.submit-button { display: inline-flex; min-width: 158px; min-height: 50px; cursor: pointer; align-items: center; justify-content: center; gap: 12px; border-radius: 999px; background: #32695d; padding: 0 23px; color: white; box-shadow: 0 12px 26px rgba(50,105,93,.18); font-size: 15px; transition: background-color 180ms ease,box-shadow 180ms ease,transform 180ms ease; }.submit-button:hover:not(:disabled) { background: #285b50; box-shadow: 0 15px 32px rgba(50,105,93,.24); transform: translateY(-1px); }.submit-button:active:not(:disabled) { transform: translateY(0); }.submit-button:disabled { cursor: not-allowed; opacity: .42; box-shadow: none; }.submit-button:focus-visible,.gender-options button:focus-visible { outline: 2px solid #32695d; outline-offset: 3px; }
.submit-button svg { width: 19px; height: 19px; fill: none; stroke: currentColor; stroke-linecap: round; stroke-linejoin: round; stroke-width: 1.5; }.submit-button__spinner { width: 17px; height: 17px; border: 2px solid rgba(255,255,255,.35); border-top-color: white; border-radius: 50%; animation: ink-spin .8s linear infinite; }
input:disabled,select:disabled,textarea:disabled,fieldset:disabled { cursor: not-allowed; opacity: .62; }
@keyframes ink-spin { to { transform: rotate(360deg); } }
@media (max-width: 700px) {
  .writing-form { border-radius: 20px; }.writing-form__primary,.writing-form__timing { grid-template-columns: 1fr; }.surname-field,.gender-field,.line-field,.writing-form__optional,.writing-form__footer { padding-inline: 20px; }.gender-field,.line-field + .line-field { border-left: 0; border-top: 1px solid rgba(183,161,120,.26); }.writing-form__footer { align-items: stretch; flex-direction: column; }.submit-button { width: 100%; }
}
@media (prefers-reduced-motion: reduce) { .surname-field__input::after,.line-field__control::after,.gender-options button,.note-field textarea,.submit-button { transition-duration: .01ms!important; }.submit-button__spinner { animation-duration: 1.5s; } }
</style>

<template>
  <WorkspaceDrawer
    :open="open"
    title="个人资料"
    kicker="MEMBER PROFILE"
    :description="profile.username || '管理你的账户与安全设置'"
    width="680px"
    @close="emit('close')"
    ><div
      v-if="success"
      class="mb-5 rounded-xl bg-[#e5eee9] px-4 py-3 text-sm text-[#32695d]"
    >
      {{ success }}
    </div>
    <div
      v-if="error"
      class="mb-5 rounded-xl bg-[#f3e7e3] px-4 py-3 text-sm text-[#b65345]"
    >
      {{ error }}
    </div>
    <div class="mb-7 flex gap-6 border-b border-[#d9d1c3]">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="pb-3 text-sm"
        :class="
          active === tab.key
            ? 'border-b-2 border-[#32695d] text-[#32695d]'
            : 'text-[#77736a]'
        "
        @click="active = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>
    <p v-if="loading" class="py-16 text-center text-[#9a958b]">正在读取资料…</p>
    <template v-else
      ><section v-if="active === 'info'" class="space-y-5">
        <div
          class="flex items-center gap-5 rounded-2xl border border-[#d9d1c3] bg-white/55 p-5"
        >
          <div
            class="grid h-20 w-20 shrink-0 place-items-center overflow-hidden rounded-full bg-[#e9e5db] font-serif text-3xl text-[#32695d]"
          >
            <img
              v-if="profile.avatar"
              :src="profile.avatar"
              class="h-full w-full object-cover"
            /><span v-else>{{ profile.username?.[0]?.toUpperCase() }}</span>
          </div>
          <div>
            <p class="font-serif text-2xl">{{ profile.username }}</p>
            <label
              class="mt-2 inline-block cursor-pointer text-xs text-[#32695d]"
              >更换头像<input
                type="file"
                accept="image/*"
                class="hidden"
                @change="upload"
            /></label>
          </div>
        </div>
        <div class="rounded-2xl border border-[#d9d1c3] bg-white/55 p-5">
          <label class="text-xs tracking-[.12em] text-[#9a958b]">用户名</label>
          <div class="mt-2 flex gap-3">
            <input
              v-model.trim="newUsername"
              maxlength="50"
              class="min-w-0 flex-1 border-b border-[#d9d1c3] bg-transparent py-2 outline-none focus:border-[#32695d]"
            /><button class="text-sm text-[#32695d]" @click="saveUsername">
              保存
            </button>
          </div>
          <div class="mt-6 grid grid-cols-2 gap-3">
            <div class="rounded-xl bg-[#ebe7dc] p-4">
              <strong class="font-serif text-2xl">{{ stats.total }}</strong>
              <p class="text-xs text-[#77736a]">总记录</p>
            </div>
            <div class="rounded-xl bg-[#ebe7dc] p-4">
              <strong class="font-serif text-2xl">{{ stats.favorites }}</strong>
              <p class="text-xs text-[#77736a]">收藏数</p>
            </div>
          </div>
          <p class="mt-5 text-sm text-[#77736a]">
            邮箱：{{ profile.email || "未绑定" }}
          </p>
        </div>
      </section>
      <section v-else-if="active === 'password'" class="space-y-4">
        <input
          v-model="password.old"
          type="password"
          placeholder="当前密码"
          class="field"
        /><input
          v-model="password.next"
          type="password"
          placeholder="新密码（至少 6 位）"
          class="field"
        /><button
          class="primary"
          :disabled="!password.old || password.next.length < 6"
          @click="savePassword"
        >
          修改密码
        </button>
      </section>
      <section v-else class="space-y-4">
        <p class="text-sm leading-6 text-[#77736a]">
          绑定邮箱后可用于登录和找回密码。
        </p>
        <input
          v-model="email"
          type="email"
          placeholder="邮箱地址"
          class="field"
        /><button
          class="primary"
          :disabled="!email || countdown > 0"
          @click="sendCode"
        >
          {{ countdown ? `${countdown} 秒后重试` : "发送验证码" }}
        </button>
        <div v-if="codeSent" class="flex gap-3">
          <input
            v-model="code"
            maxlength="6"
            placeholder="6 位验证码"
            class="field flex-1"
          /><button
            class="rounded-full bg-[#32695d] px-6 text-white"
            :disabled="code.length !== 6"
            @click="confirmEmail"
          >
            确认
          </button>
        </div>
      </section></template
    ></WorkspaceDrawer
  >
</template>
<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import WorkspaceDrawer from "./WorkspaceDrawer.vue";
import {
  bindEmail,
  changePassword,
  getProfile,
  getStats,
  updateProfile,
  updateUsername,
  uploadAvatar,
  verifyEmail,
} from "../api";
import { useAuthStore } from "../stores/auth";
defineProps<{ open: boolean }>();
const emit = defineEmits<{ close: [] }>(),
  auth = useAuthStore();
const tabs = [
    { key: "info", label: "个人信息" },
    { key: "password", label: "修改密码" },
    { key: "email", label: "绑定邮箱" },
  ],
  active = ref("info"),
  profile = reactive<any>({}),
  stats = reactive({ total: 0, favorites: 0 }),
  loading = ref(true),
  error = ref(""),
  success = ref(""),
  newUsername = ref(""),
  password = reactive({ old: "", next: "" }),
  email = ref(""),
  code = ref(""),
  codeSent = ref(false),
  countdown = ref(0);
function ok(v: string) {
  success.value = v;
  error.value = "";
  setTimeout(() => (success.value = ""), 3000);
}
function fail(e: any) {
  error.value = e?.message || "操作失败";
  success.value = "";
}
async function load() {
  try {
    Object.assign(profile, await getProfile());
    Object.assign(stats, await getStats());
    newUsername.value = profile.username;
    email.value = profile.email || "";
  } catch (e) {
    fail(e);
  } finally {
    loading.value = false;
  }
}
async function saveUsername() {
  if (newUsername.value.length < 2) return;
  try {
    await updateProfile(newUsername.value);
    await updateUsername(newUsername.value);
    profile.username = newUsername.value;
    auth.username = newUsername.value;
    ok("用户名已更新");
  } catch (e) {
    fail(e);
  }
}
async function savePassword() {
  try {
    await changePassword(password.old, password.next);
    password.old = "";
    password.next = "";
    ok("密码已修改");
  } catch (e) {
    fail(e);
  }
}
async function sendCode() {
  try {
    await bindEmail(email.value);
    codeSent.value = true;
    countdown.value = 60;
    const id = setInterval(() => {
      countdown.value--;
      if (countdown.value <= 0) clearInterval(id);
    }, 1000);
    ok("验证码已发送");
  } catch (e) {
    fail(e);
  }
}
async function confirmEmail() {
  try {
    await verifyEmail(email.value, code.value);
    profile.email = email.value;
    codeSent.value = false;
    code.value = "";
    ok("邮箱绑定成功");
  } catch (e) {
    fail(e);
  }
}
async function upload(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0];
  if (!file) return;
  if (file.size > 1024 * 1024) {
    fail(new Error("图片不能超过 1MB"));
    return;
  }
  const reader = new FileReader();
  reader.onload = async () => {
    try {
      await uploadAvatar(reader.result as string);
      profile.avatar = reader.result;
      ok("头像已更新");
    } catch (e) {
      fail(e);
    }
  };
  reader.readAsDataURL(file);
}
onMounted(load);
</script>
<style scoped>
.field {
  width: 100%;
  border: 1px solid #d9d1c3;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.55);
  padding: 14px 16px;
  outline: none;
}
.field:focus {
  border-color: #32695d;
}
.primary {
  width: 100%;
  border-radius: 999px;
  background: #32695d;
  padding: 14px;
  color: white;
}
.primary:disabled {
  opacity: 0.45;
}
</style>

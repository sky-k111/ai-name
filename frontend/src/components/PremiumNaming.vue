<template>
  <div class="w-full max-w-[820px] mx-auto">
    <NameForm v-model="form" :loading="loading" :disabled="loading" estimate="10-15" @submit="handleSubmit" />
    <ActionToast
      v-if="toast"
      :key="toast.id"
      :title="toast.title"
      :detail="toast.detail"
      :type="toast.type"
      @close="closeToast(toast.id)"
    />
    <section v-if="showResults" class="mt-10">
      <PremiumResults :names="names" :state="state" :error-message="error" @retry="handleSubmit(form)" @favorite="handleFavorite" />
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import type { FavoriteAction, GenerateRequest, NameItem, LoadState } from '../types'
import { premiumNaming, addFavorite } from '../api'
import NameForm from './NameForm.vue'
import PremiumResults from './PremiumResults.vue'
import ActionToast from './ActionToast.vue'

const props = defineProps<{ authGuard?: () => boolean }>()

const form = reactive<GenerateRequest>({ surname:'', gender:'male', birthday:'', birth_time:'', style:'', expectations:'' })
const names = ref<NameItem[]>([])
const state = ref<LoadState>('idle')
const error = ref('')
const loading = ref(false)
const showResults = computed(() => state.value !== 'idle')

async function handleSubmit(data: GenerateRequest) {
  Object.assign(form, data)
  if (props.authGuard && !props.authGuard()) return
  loading.value=true; state.value='loading'; names.value=[]; error.value=''
  try { const r = await premiumNaming(data); names.value=r.names; state.value=r.names.length?'success':'empty' } catch(e:any){ error.value=e.message; state.value='error' } finally{loading.value=false}
}

const toast = ref<{id:number;type:'success'|'info'|'error';title:string;detail:string}|null>(null)
let toastId = 0
function showToast(title:string,type:'success'|'info'|'error',detail:string){toast.value={id:++toastId,title,type,detail}}
function closeToast(id:number){if(toast.value?.id===id)toast.value=null}
async function handleFavorite(action: FavoriteAction) {
  try {
    await addFavorite(action.name.full_name, action.name)
    action.complete('saved')
    showToast(`「${action.name.full_name}」已收入收藏`, 'success', '可以在顶部“收藏”中随时查看')
  } catch(e:any) {
    const message = e.message || '收藏失败'
    if (message.includes('已收藏过')) {
      action.complete('saved')
      showToast(`「${action.name.full_name}」已在收藏中`, 'info', '无需重复收藏，可以直接前往收藏查看')
    } else {
      action.complete('error')
      showToast(message, 'error', '本次没有保存，请稍后重试')
    }
  }
}
</script>

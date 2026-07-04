<template>
  <div class="min-h-screen bg-[#f5f5f7]">
    <div class="max-w-[800px] mx-auto px-6 py-16">
      <!-- 顶部 -->
      <div class="flex items-start justify-between mb-8">
        <div>
          <h1 class="text-[36px] font-semibold text-[#1d1d1f] tracking-tight">
            取名历史
          </h1>
          <p class="mt-2 text-[15px] text-[#86868b]">
            共 {{ total }} 条记录
          </p>
          <select v-model="filter" class="mt-2 text-[14px] bg-[#f5f5f7] rounded-lg px-3 py-1.5 outline-none border border-[#d2d2d7]/30" @change="loadData">
            <option value="">全部类型</option>
            <option value="naming">仅取名</option>
            <option value="analyze">仅分析</option>
            <option value="compare">仅对比</option>
            <option value="premium">仅精品</option>
          </select>
        </div>
        <div class="flex items-center gap-3">
          <button v-if="items.length > 0" class="text-[14px] text-[#ff3b30] hover:underline whitespace-nowrap" @click="handleClearAll">一键清空</button>
          <button v-if="items.length > 0" class="text-[14px] text-[#86868b] hover:text-[#1d1d1f] whitespace-nowrap" @click="toggleBatchMode">{{ batchMode ? '完成' : '选择' }}</button>
          <button v-if="batchMode && selectedIds.length>0" class="text-[14px] text-[#ff3b30] hover:underline whitespace-nowrap" @click="handleBatchDelete">删除选中({{ selectedIds.length }})</button>
          <button class="text-[15px] text-[#0071e3] hover:underline whitespace-nowrap" @click="$router.push('/')">← 返回主页</button>
        </div>
      </div>

      <!-- 加载中 -->
      <div v-if="loading" class="space-y-4">
        <div v-for="i in 3" :key="i"
          class="bg-white/80 backdrop-blur-xl rounded-2xl p-6 animate-pulse shadow-[0_2px_12px_rgba(0,0,0,0.03)]">
          <div class="h-5 w-24 bg-[#e8e8ed] rounded mb-3" />
          <div class="h-4 w-48 bg-[#e8e8ed] rounded" />
        </div>
      </div>

      <!-- 错误 -->
      <div v-else-if="error" class="text-center py-20">
        <p class="text-[17px] text-[#ff3b30] mb-3">{{ error }}</p>
        <button class="text-[15px] text-[#0071e3] hover:underline transition-colors" @click="loadData">
          点击重试
        </button>
      </div>

      <!-- 空 -->
      <div v-else-if="items.length === 0" class="text-center py-20">
        <p class="text-[17px] text-[#86868b]">还没有取名记录</p>
        <button class="mt-4 text-[15px] text-[#0071e3] hover:underline transition-colors" @click="$router.push('/')">
          去取名
        </button>
      </div>

      <!-- 列表 -->
      <div v-else class="space-y-3">
        <div
          v-for="item in items" :key="item.id"
          class="bg-white/80 backdrop-blur-xl rounded-2xl p-5
                 shadow-[0_2px_12px_rgba(0,0,0,0.03)] border border-[#d2d2d7]/30
                 transition-all duration-300 hover:shadow-[0_4px_20px_rgba(0,0,0,0.06)]
                 hover:-translate-y-[1px]"
        >
          <div class="flex items-center gap-3">
            <!-- 批量选择框 -->
            <button
              v-if="batchMode"
              class="shrink-0 w-5 h-5 rounded-full border-2 flex items-center justify-center
                     transition-all duration-200"
              :class="isSelected(item.id)
                ? 'border-[#0071e3] bg-[#0071e3]'
                : 'border-[#d2d2d7]'"
              @click.stop="toggleSelect(item.id)"
            >
              <svg v-if="isSelected(item.id)" class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>
            </button>

            <!-- 内容 -->
            <div class="flex-1 cursor-pointer min-w-0" @click="toggleExpand(item.id)">
              <div class="flex items-center justify-between">
                <div>
                  <span class="text-[17px] font-medium text-[#1d1d1f]">
                    {{ item.surname }} · {{ item.gender === 'male' ? '男' : '女' }}
                  </span>
                  <span v-if="item.record_type === 'analyze'" class="ml-2 px-2 py-0.5 rounded-full bg-purple-100 text-purple-600 text-[12px] font-medium">分析</span>
                  <span class="ml-3 text-[14px] text-[#aeaeb2]">
                    {{ formatTime(item.created_at) }}
                  </span>
                </div>
                <span class="text-[#86868b] text-[13px] shrink-0">
                  {{ item.names.length }} 个名字 {{ expandedId === item.id ? '▾' : '▸' }}
                </span>
              </div>
            </div>

            <!-- 删除按钮（非批量模式） -->
            <button
              v-if="!batchMode"
              class="shrink-0 w-8 h-8 flex items-center justify-center rounded-full
                     text-[#aeaeb2] hover:text-[#ff3b30] hover:bg-[#ff3b30]/5
                     transition-all duration-200"
              @click.stop="handleDelete(item.id)"
            >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
              </svg>
            </button>
          </div>

          <!-- 展开：名字列表 -->
          <div v-if="expandedId === item.id" class="mt-4 pt-4 border-t border-[#d2d2d7]/30 space-y-3">
            <div v-for="name in item.names" :key="name.full_name"
              class="pl-4 border-l-2 border-[#0071e3]/30">
              <p class="text-[17px] font-medium text-[#1d1d1f]">{{ name.full_name }}</p>
              <p class="text-[14px] text-[#3a3a3c] mt-1">{{ name.meaning }}</p>
              <p class="text-[13px] text-[#aeaeb2] mt-1">
                五行 {{ name.wuxing }} · 出处 {{ name.source }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { getHistory, deleteHistory, batchDeleteHistory, clearAllHistory } from '../api'
import type { HistoryItem } from '../types'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const items = ref<HistoryItem[]>([])
const total = ref(0)
const expandedId = ref<number | null>(null)
const error = ref('')
const batchMode = ref(false)
const selectedIds = ref<number[]>([])
const filter = ref('')

function formatTime(iso: string): string {
  if (!iso) return ''
  return iso.replace('T', ' ').slice(0, 16)
}

function toggleExpand(id: number) {
  expandedId.value = expandedId.value === id ? null : id
}

function toggleBatchMode() {
  batchMode.value = !batchMode.value
  selectedIds.value = []
  expandedId.value = null
}

function isSelected(id: number) {
  return selectedIds.value.includes(id)
}

function toggleSelect(id: number) {
  const idx = selectedIds.value.indexOf(id)
  if (idx >= 0) selectedIds.value.splice(idx, 1)
  else selectedIds.value.push(id)
}

async function handleDelete(id: number) {
  try {
    await deleteHistory(id)
    items.value = items.value.filter(item => item.id !== id)
    total.value--
  } catch (e: any) {
    error.value = e.message || '删除失败'
  }
}

async function handleClearAll() {
  if (!confirm('确定要清空所有取名历史吗？此操作不可撤销。')) return
  try {
    await clearAllHistory()
    items.value = []
    total.value = 0
  } catch (e: any) { error.value = e.message || '清空失败' }
}

async function handleBatchDelete() {
  if (selectedIds.value.length === 0) return
  try {
    await batchDeleteHistory(selectedIds.value)
    items.value = items.value.filter(item => !selectedIds.value.includes(item.id))
    total.value = items.value.length
    selectedIds.value = []
    batchMode.value = false
  } catch (e: any) {
    error.value = e.message || '批量删除失败'
  }
}

onMounted(() => { loadData() })

async function loadData() {
  if (!authStore.isLoggedIn) {
    router.push('/login')
    return
  }
  loading.value = true
  error.value = ''
  try {
    const res = await getHistory(0, 50, filter.value || undefined)
    items.value = res.items
    total.value = res.total
  } catch (e: any) {
    error.value = e.message || '加载失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

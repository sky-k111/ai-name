import axios from 'axios'
import type { GenerateRequest, GenerateResponse, RefineRequest, RefineResponse, HistoryListResponse } from '../types'

const http = axios.create({
  baseURL: '/api',
  timeout: 35000,
  headers: { 'Content-Type': 'application/json' },
})

/** 注册 */
export async function register(username: string, password: string): Promise<{ token: string; username: string; role: string }> {
  const res = await http.post('/auth/register', { username, password })
  return res.data
}

/** 登录 */
export async function login(username: string, password: string): Promise<{ token: string; username: string; role: string }> {
  const res = await http.post('/auth/login', { username, password })
  return res.data
}

// 请求拦截：自动注入 token
http.interceptors.request.use((config) => {
  const token = localStorage.getItem('ai_naming_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截：统一错误处理 + 401 自动跳转登录
http.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('ai_naming_token')
      localStorage.removeItem('ai_naming_username')
      window.location.href = '/login'
      return Promise.reject(new Error('登录已过期，请重新登录'))
    }
    if (!error.response) {
      return Promise.reject(new Error('网络连接异常，请检查网络后重试'))
    }
    const detail = error.response.data?.detail
    if (typeof detail === 'string') {
      return Promise.reject(new Error(detail))
    }
    if (detail?.message) {
      return Promise.reject(new Error(detail.message))
    }
    return Promise.reject(new Error(error.message || '请求失败'))
  },
)

/** 首次生成名字 */
export async function generateNames(data: GenerateRequest): Promise<GenerateResponse> {
  const res = await http.post('/naming/generate', data)
  return res.data
}

/** 微调名字 */
export async function refineNames(data: RefineRequest): Promise<RefineResponse> {
  const res = await http.post('/naming/refine', data)
  return res.data
}

/** 取名历史列表（支持分页和类型筛选） */
export async function getHistory(skip: number = 0, limit: number = 20, recordType?: string): Promise<HistoryListResponse> {
  const params: any = { skip, limit }
  if (recordType) params.record_type = recordType
  const res = await http.get('/naming/history', { params })
  return res.data
}

/** 全部取名记录（管理员） */
export async function getAllNamings(): Promise<HistoryListResponse> {
  const res = await http.get('/admin/namings')
  return res.data
}

/** 认证日志（管理员） */
export async function getAuthLogs(): Promise<{ total: number; items: any[] }> {
  const res = await http.get('/auth/logs')
  return res.data
}

/** 全部用户列表（管理员） */
export async function getAllUsers(): Promise<{ total: number; items: any[] }> {
  const res = await http.get('/admin/users')
  return res.data
}

/** 今日活跃用户（管理员） */
export async function getActiveUsers(): Promise<{ total: number; items: any[] }> {
  const res = await http.get('/admin/active-users')
  return res.data
}

/** 管理员重置用户密码 */
export async function adminResetPassword(userId: number, newPassword: string): Promise<void> {
  await http.put('/admin/reset-password', { user_id: userId, new_password: newPassword })
}

/** 注销当前账号 */
export async function deleteAccount(): Promise<void> {
  await http.delete('/user/account')
}

/** 删除单条取名历史 */
export async function deleteHistory(id: number): Promise<void> {
  await http.delete(`/naming/history/${id}`)
}

/** 名字对比 */
export async function compareNames(names: string[], gender: string): Promise<any> {
  const res = await http.post('/naming/compare', { names, gender })
  return res.data
}

/** 精品取名 */
export async function premiumNaming(data: any): Promise<any> {
  const res = await http.post('/naming/premium', data)
  return res.data
}

/** 获取余额 */
export async function getBalance(): Promise<any> {
  const res = await http.get('/payment/balance')
  return res.data
}

/** 充值 */
export async function recharge(amount: number): Promise<any> {
  const res = await http.post('/payment/recharge', { amount })
  return res.data
}

/** 买VIP */
export async function buyVip(level: string): Promise<any> {
  const res = await http.post('/payment/buy-vip', { level })
  return res.data
}

/** 交易记录 */
export async function getTransactions(): Promise<any> {
  const res = await http.get('/payment/transactions')
  return res.data
}

/** 收藏列表 */
export async function getFavorites(): Promise<any> {
  const res = await http.get('/favorites')
  return res.data
}

/** 添加收藏 */
export async function addFavorite(fullName: string, nameData: any): Promise<any> {
  const res = await http.post('/favorites', { full_name: fullName, name_data: nameData })
  return res.data
}

/** 取消收藏 */
export async function removeFavorite(id: number): Promise<void> {
  await http.delete(`/favorites/${id}`)
}

/** 个人取名统计 */
export async function getStats(): Promise<any> {
  const res = await http.get('/user/stats')
  return res.data
}

/** 导出个人数据 */
export async function exportData(): Promise<any> {
  const res = await http.get('/user/export')
  return res.data
}

/** 批量删除取名历史 */
export async function batchDeleteHistory(ids: number[]): Promise<{ deleted_count: number }> {
  const res = await http.post('/naming/history/batch-delete', { ids })
  return res.data
}

/** 一键清空所有历史 */
export async function clearAllHistory(): Promise<{ deleted_count: number }> {
  const res = await http.delete('/naming/history')
  return res.data
}

/** 获取个人资料 */
export async function getProfile(): Promise<any> {
  const res = await http.get('/user/profile')
  return res.data
}

/** 修改昵称 */
export async function updateProfile(nickname: string): Promise<void> {
  await http.put('/user/profile', { nickname })
}

/** 修改用户名 */
export async function updateUsername(username: string): Promise<void> {
  await http.put('/user/profile', { username })
}

/** 修改密码 */
export async function changePassword(oldPassword: string, newPassword: string): Promise<void> {
  await http.put('/user/password', { old_password: oldPassword, new_password: newPassword })
}

/** 发送绑定邮箱验证码 */
export async function bindEmail(email: string): Promise<void> {
  await http.post('/user/email/bind', { email })
}

/** 确认绑定邮箱 */
export async function verifyEmail(email: string, code: string): Promise<void> {
  await http.post('/user/email/verify', { email, code })
}

/** 上传头像 */
export async function uploadAvatar(avatar: string): Promise<void> {
  await http.post('/user/avatar', { avatar })
}

/** 忘记密码 — 发送验证码 */
export async function forgotPassword(email: string): Promise<void> {
  await http.post('/auth/forgot-password', { email })
}

/** 重置密码 */
export async function resetPassword(email: string, code: string, newPassword: string): Promise<void> {
  await http.post('/auth/reset-password', { email, code, new_password: newPassword })
}

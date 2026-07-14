/** 性别 */
export type Gender = 'male' | 'female'

/** 取名请求 */
export interface GenerateRequest {
  surname: string
  gender: Gender
  birthday?: string
  birth_time?: string
  style?: string
  expectations?: string
}

/** 单个名字 */
export interface NameItem {
  full_name: string
  meaning: string
  wuxing: string
  source: string
  bazi?: string
  sound_analysis?: string
  char_analysis?: string
  popularity?: string
  source_quote?: string
  source_context?: string
  character_meaning?: string
  naming_story?: string
  usage_advice?: string
  score?: number
  sound_score?: number
  meaning_score?: number
  wuxing_score?: number
  char_score?: number
  summary?: string
  rank?: number
}

export type FavoriteCompletion = 'saved' | 'error' | 'cancelled'

export interface FavoriteAction {
  name: NameItem
  complete: (status: FavoriteCompletion) => void
}

/** 生成响应 */
export interface GenerateResponse {
  conversation_id: string
  names: NameItem[]
}

/** 对话消息 */
export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

/** 微调请求 */
export interface RefineRequest {
  conversation_id?: string
  original_request: GenerateRequest
  history: ChatMessage[]
  feedback: string
}

/** 微调响应 */
export interface RefineResponse {
  names: NameItem[]
}

/** API 错误响应 */
export interface ApiError {
  error: boolean
  message: string
  code: string
}

/** 页面加载状态 */
export type LoadState = 'idle' | 'loading' | 'success' | 'error' | 'empty'

/** 历史记录项 */
export interface HistoryItem {
  id: number
  surname: string
  gender: Gender
  names: NameItem[]
  record_type: string
  created_at: string
}

/** 历史记录列表响应 */
export interface HistoryListResponse {
  total: number
  items: HistoryItem[]
}

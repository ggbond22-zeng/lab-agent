import { getToken } from '@/utils/auth'
import request from '@/utils/request'

export function ChatApi(data) {
  return request({
    url: '/api/ai/chat',
    method: 'post',
    data,
    timeout: 60000
  })
}

// 流式输出模型调用接口
export async function chatStreamApi(data, onEvent) {
  const baseURL = import.meta.env.VITE_API_BASE_URL || ''
  const token = getToken()
  const res = await fetch(`${baseURL}/api/ai/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'text/event-stream',
      // fetch能够自定义请求头和鉴权
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    },
    body: JSON.stringify(data)
  })

  if (res.status === 401) {
    throw new Error('登录已过期，请重新登录')
  }

  if (!res.ok || !res.body) {
    throw new Error('流式接口请求失败')
  }

  const contentType = res.headers.get('content-type') || ''
  if (!contentType.includes('text/event-stream')) {
    const payload = await res.json().catch(() => null)
    throw new Error(payload?.message || '流式接口返回异常')
  }

  // getReader() 按二进制块读响应体，而不是等全部加载完
  const reader = res.body.getReader()
  const decoder = new TextDecoder('utf-8')
  // buffer 用于存储被拆散的字体
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    // 读取到了done 说明后端流式已结束
    if (done) break
    // 将读取到的文本进行解码 关键：stream: true 因为一个中文汉字会被拆成3个字节，如果结尾只拆了一半也会进行保留
    buffer += decoder.decode(value, { stream: true })

    // 因为每个 SSE 帧都是以\n\n进行分隔的
    const chunks = buffer.split('\n\n')
    // 用来存储结尾被拆的不完整的字
    buffer = chunks.pop() || ''

    for (const chunk of chunks) {
      // 一帧里面可能会有别的数据，只要开头为 data: 的数据
      const line = chunk
        .split('\n')
        .map((item) => item.trim())
        .find((item) => item.startsWith('data:'))
      if (!line) continue
      // 将 data: 开头去掉，剩下的就是JSON
      const raw = line.slice(5).trim()
      if (!raw || raw === '[DONE]') continue
      try {
        onEvent(JSON.parse(raw))
      } catch {
        // 半包或脏数据，跳过 等待下一帧
      }
    }
  }
}

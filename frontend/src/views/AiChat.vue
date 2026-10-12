<template>
  <el-card>
    <template #header>
      <div style="font-weight: bold; font-size: 16px">
        <span>智能体预约</span>
      </div>
    </template>
    <div
      ref="listRef"
      style="
        /* 高度随视口自适应：桌面约 465px，手机端自动收紧，min-height 保证最小可用 */
        height: calc(100vh - 300px);
        min-height: 320px;
        padding: 6px 4px;
        background-color: #fafafa;
        border-radius: 8px;
        overflow-y: auto;
      "
    >
      <div
        v-for="(item, index) in messages"
        :key="index"
        :style="{
          display: 'flex',
          justifyContent: item.role === 'user' ? 'flex-end' : 'flex-start',
          marginBottom: '15px'
        }"
      >
        <div
          :style="{
            maxWidth: '70%',
            padding: '6px 8px',
            borderRadius: '8px',
            backgroundColor: item.role === 'user' ? '#409eff' : '#fff',
            color: item.role === 'user' ? '#fff' : '#333',
            lineHeight: '1.6',
            boxShadow: '0 1px 2px rgba(0, 0, 0, 0.06)'
          }"
        >
          <div
            v-if="item.role === 'assistant' && item.status"
            style="margin-bottom: 8px; font-size: 12px; color: #909399"
          >
            {{ item.status }}
          </div>

          <div
            v-if="item.role === 'assistant' && item.steps?.length"
            style="margin-bottom: 10px; font-size: 12px; color: #909399; line-height: 1.5"
          >
            <div v-for="(step, i) in item.steps" :key="i">. {{ step }}</div>
          </div>
          <div v-html="parseMarkdowm(item.content)"></div>
        </div>
      </div>
    </div>
    <div style="margin-top: 10px; display: flex; align-items: flex-end; gap: 8px">
      <el-input
        v-model="input"
        type="textarea"
        placeholder="问问实验室如何预约、开放时间等"
        :row="2"
        @keydown.enter.exact.prevent="handleSend"
        @keydown.enter.shift.stop
      ></el-input>
      <el-button type="primary" :loading="loading" @click="handleSend">发送</el-button>
    </div>
  </el-card>
</template>

<script setup>
import { ChatApi, chatStreamApi } from '@/api/ai'
import { marked } from 'marked'
import { ref, reactive, nextTick } from 'vue'
import DOMPurify from 'dompurify' // 过滤危险的 HTML 防止 XSS 攻击
import { ElMessage } from 'element-plus'

const loading = ref(false)
const input = ref('')
const listRef = ref()
// 消息框初始信息
const messages = ref([
  {
    role: 'assistant',
    content: '欢迎使用实验室预约助手，在预约过程中有什么问题我都可以帮您解答哟~'
  }
])

// 发送和收到回复自动加载到底部
const scrollToButtom = () => {
  // nextTick 表示在vue前端页面加载完成后执行的操作
  nextTick(() => {
    const elem = listRef.value // listRef.value 就是绑定了 listRef 的div
    // scrollTop当前滚动到了哪里 scrollHeight 表示滚动条全部内容的总高度 高度是从上往下增加
    if (elem) elem.scrollTop = elem.scrollHeight
  })
}

const handleSend = async () => {
  // 得到输入框中的内容，trim() 等于Python中的 strip()
  const text = input.value.trim()
  // 如果输入框中没有内容或ai正在回复时，点击输入框无效
  if (!text || loading.value) return
  // 将信息提交并显示到前端页面
  messages.value.push({ role: 'user', content: text })

  // 将内容发送后重置输入框
  input.value = ''
  loading.value = true
  scrollToButtom()

  // 必须要用reactive对象 普通对象 push 后再修改字段，视图可能不会更新
  const assistant = reactive({
    role: 'assistant',
    content: '', // 模型最终输出内容
    status: '正在思考...', // 流式传输状态信息
    steps: [] // 过程流水，告诉用户当前进行到了哪一步
  })

  messages.value.push(assistant)

  const history = messages.value
    .filter((item) => item.role === 'user' || item.role === 'assistant') // 历史信息只需要用户信息和模型回复信息
    .slice(0, -1) // 去掉前端进入的默认信息和刚刚 push 进来的空信息
    .map(({ role, content }) => ({ role, content })) // 只保留 role、content 其余的过滤掉

  try {
    // 将历史记录作为消息发送给大模型
    const data = { messages: history }
    await chatStreamApi(data, (evt) => {
      if (evt.type === 'status') {
        assistant.status = evt.message || '正在思考...'
      } else if (evt.type === 'tool_start') {
        const label = evt.label || evt.name || '工具'
        assistant.status = `正在${label}...`
        assistant.steps.push(`开始：${label}`)
      } else if (evt.type === 'tool_end') {
        const label = evt.label || evt.name || '工具'
        assistant.status = `${label}完成`
        assistant.steps.push(`完成：${label}`)
      } else if (evt.type === 'token') {
        assistant.content += evt.content || ''
        assistant.status = '' // 模型开始输出正文了，不需要再输出思考
      } else if (evt.type === 'done') {
        assistant.status = ''
      } else if (evt.type === 'error') {
        assistant.status = ''
        if (!assistant.content) {
          assistant.content = evt.message || '请求失败'
        }
        ElMessage.error(evt.message || '请求失败')
      }
      scrollToButtom()
    })
  } catch (err) {
    assistant.status = ''
    if (!assistant.content) {
      assistant.content = err.message || '网络异常'
    }
    ElMessage.error(err.message || '网络异常')
  } finally {
    loading.value = false
    assistant.status = ''
    scrollToButtom()
  }
}

// 如果模型输出的是markdown格式，将markdown格式转化为安全的 html 字符串
const parseMarkdowm = (text) => {
  if (!text) return ''
  marked.setOptions({ breaks: true }) // 把 \n 转换为 <br>
  // 使用markdown 解析，然后使用 DOMPurify 清洗
  const rawHtml = marked.parse(text)
  return DOMPurify.sanitize(rawHtml)
}
</script>

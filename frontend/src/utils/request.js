// 使用 axios 将前后端进行接口联调
import axios from 'axios'
import { getToken, logout } from './auth'
import { ElMessage } from 'element-plus'
import router from '@/router'


// 配置联调服务 只有配置了service 前后端的数据才能进行联调
const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',  // 连接的接口
  timeout: 30000  // 请求超时时间 30s
})


// 请求拦截器的配置
service.interceptors.request.use(
    (config) => {
        // 先获取token
        const token = getToken()
        // 如果token存在，就将token存放在请求头中
        // 如果token不存在，说明用户还未进行登录，此时也不需要进行操作
        if (token) {
            // `xxx ${}` 类似于 Python的 f插值法
            config.headers.Authorization = `Bearer ${token}`  // 根据api调用时的代码示例得知
        }
        return config
    },
    (err) => Promise.reject(err)
)

// 响应拦截器的配置
service.interceptors.response.use(
    (res) => {
        // res 就是接口调用成功后 后端返回的信息，包含网页的状态响应、后端校验后范湖的信息与状态码等信息
        const data = res.data
        // 如果 data的状态码 不是200 说明登录请求没有成功，此时弹出失败的信息告知用户
        if (data.code !== 200) {
            ElMessage.error(data.message || '请求失败')
            // 如果 data的状态码 是401 说明未授权，直接返回登录界面让用户重新登录
            if (data.code === 401) {
                logout()
                router.push('/login')
                return Promise.reject(data)  // 表示将错误信息抛出显示
            }
        }
        return data   // 如果登录请求成功，返回后端的响应数据
    },
    (err) => {
        // 当请求登录失败时，如果有错误信息
        if (err.response) {
            // 先得到失败的状态码
            const httpStatusCode = err.response.status
            // 因为状态码 401 是特殊的情况，表示当前网页响应未授权，因此要特殊处理
            if (httpStatusCode === 401) {
                logout()
                router.push('/login')
            } else {
              // ?.表示如果err.response.data为空，在获取messages值时不会发生报错，直接得到空值
              ElMessage.error(err.response.data?.message || '请求失败')
            }
        } else {
            // 如果连错误的响应都没有，通常就是服务端没有启动，或是网络出现异常
            ElMessage.error('网络异常，请检查后端服务')
        }
        return Promise.reject(err)
    }
)

// 将 service 服务导出才能使用
export default service


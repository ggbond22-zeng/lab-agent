<template>
  <div class="login-container">
    <div class="login-box">
      <h1 style="font-size: 30px">实验室预约系统</h1>
      <div style="margin-top: 7px; margin-bottom: 20px; font-size: 15px">
        基于Agent的智能预约系统
      </div>
      <el-form ref="FromRef" :rules="rules" :model="form" label-width="0px" style="width: 100%">
        <el-form-item prop="username">
          <el-input
            size="large"
            v-model="form.username"
            placeholder="请输入账号"
            :prefix-icon="User"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            type="password"
            show-password
            size="large"
            v-model="form.password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
          />
        </el-form-item>
      </el-form>
      <div>
        <el-button
          type="primary"
          size="large"
          style="width: 100%"
          @click="login"
          :loading="loadingValue"
          >登 录</el-button
        >
        <!-- style="color: var(--el-color-primary)" 从element-plus 中默认的主题色 -->
        <div style="text-align: right; margin-top: 10px" ;>
          还没有账号？请 <router-link style="color: var(--el-color-primary)" to="/register">注册</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import router from '@/router' // router.push 对应导入
import { loginApi } from '@/api/auth'
import { useUser } from '@/utils/user'

const { saveLoginData } = useUser()

const FromRef = ref()

const form = reactive({
  username: '',
  password: ''
})

// 配置前端表单校验
const rules = {
  // trigger: 'blur' 触发条件，在没有填写时触发
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const loadingValue = ref(false) // 定义一个响应式变量来控制加载状态

// 登录操作
const login = async () => {
  // FromRef.value.validate()会根据rules中的校验方式进行校验，如果没有校验内容.catch(() => false) 会捕获 并返回false
  const valid = await FromRef.value.validate().catch(() => false)
  if (!valid) return   // 如果没有校验内容 直接返回结束进程

  loadingValue.value = true // 开始加载
  try {
    const res = await loginApi(form) // 将登录输入的数据传入loginApi中进行登录请求
    if (res.code === 200) {
      saveLoginData(res.data) // 请求成功后将token和用户信息保存到浏览器本地存储
      ElMessage.success('登录成功')
      // 登录成功后跳转到系统首页
      await router.push('/manager/home') // 如果后续有其他操作，需要等待这一步页面跳转之后才能进行
    }
  } finally {
    loadingValue.value = false // 停止加载
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}
.login-box {
  width: 400px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
  background-color: #fff;
}
</style>

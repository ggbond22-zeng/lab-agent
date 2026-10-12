<template>
  <div class="register-container">
    <div class="register-box">
      <h1 style="font-size: 30px">创建实验室预约系统账号</h1>
      <div style="margin-top: 7px; margin-bottom: 20px; font-size: 15px"></div>
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
        <el-form-item prop="confirmPassword">
          <el-input
            type="password"
            show-password
            size="large"
            v-model="form.confirmPassword"
            placeholder="请再次输入密码"
            :prefix-icon="Lock"
          />
        </el-form-item>
      </el-form>
      <div>
        <el-button
          :loading="loadingValue"
          type="primary"
          size="large"
          style="width: 100%"
          @click="register"
          >注 册</el-button
        >
        <!-- style="color: var(--el-color-primary)" 从element-plus 中默认的主题色 -->
        <div style="text-align: right; margin-top: 10px">
          已有账号？请
          <router-link style="color: var(--el-color-primary)" to="/login">登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { User, Lock } from '@element-plus/icons-vue'
import { registerApi } from '@/api/auth'
import { ElMessage } from 'element-plus'
import router from '@/router'

const form = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

const FromRef = ref()

const validatePass = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请输入密码'))
  } else {
    if (value !== form.password) {
      callback(new Error('两次密码不一致，请输入正确的密码'))
    } else {
      callback()
    }
  }
}

const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  confirmPassword: [{ validator: validatePass, trigger: 'blur' }]
}

const loadingValue = ref(false) // 定义一个响应式变量来控制加载状态

// 注册后的点击函数事件
const register = async () => {
  // 先查看校验信息
  const valid = await FromRef.value.validate().catch(() => false)
  if (!valid) return

  loadingValue.value = true
  try {
    // 请求注册api
    const res = await registerApi(form)
    if (res.code === 200) {
      ElMessage.success('注册成功')
      await router.push('/login')
    }
  } finally {
    loadingValue.value = false
  }
}
</script>

<style scoped>
.register-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}
.register-box {
  /* min()：桌面保持 400px 定宽，手机端最宽只占视口 92%，避免横向溢出 */
  width: min(400px, 92vw);
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
  background-color: #fff;
}
</style>

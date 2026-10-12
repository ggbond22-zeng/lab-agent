<template>
  <div style="width: 50%">
    <el-card>
      <template #header>
        <div style="font-weight: bold; font-size: 16px">
          <span>修改密码</span>
        </div>
      </template>
      <el-form
        ref="FormRef"
        :model="form"
        :rules="rules"
        label-width="80px"
        style="width: 100%; padding-right: 50px"
      >
        <el-form-item label="原密码" prop="oldPassword">
          <el-input
            v-model="form.oldPassword"
            type="password"
            show-password
            placeholer="请输入名称"
          />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="form.newPassword"
            type="password"
            show-password
            placeholer="请输入名称"
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            show-password
            placeholer="请输入名称"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="handlePassword">提 交</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { updatePassword } from '@/api/user'
import router from '@/router'
import { logout } from '@/utils/auth'
import { ElMessage } from 'element-plus'
import { ref, reactive } from 'vue'

const FormRef = ref()
const submitting = ref(false)

const form = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 确认密码的校验函数
const validatePass = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请确认密码'))
  } else {
    if (value !== form.newPassword) {
      callback(new Error('两次密码不一致，请输入正确的密码'))
    } else {
      callback()
    }
  }
}

const rules = {
  oldPassword: [{ required: true, message: '原密码必填', trigger: 'blur' }],
  newPassword: [{ required: true, message: '新密码必填', trigger: 'blur' }],
  confirmPassword: [{ validator: validatePass, trigger: 'blur' }]
}

const handlePassword = async () => {
  const valid = await FormRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    // 因为后端的名称是old_password 因此要对应传值
    const res = await updatePassword({
      old_password: form.oldPassword,
      new_password: form.newPassword
    })
    if (res.code === 200) {
      ElMessage.success('修改密码成功，请重新登录')
      logout()
      await router.push('/login')
    }
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div style="width: 50%">
    <el-card>
      <template #header>
        <div style="font-weight: bold; font-size: 16px">
          <span>个人信息</span>
        </div>
      </template>
      <el-form
        ref="FormRef"
        :model="form"
        :rules="rules"
        v-loading="loading"
        label-width="60px"
        style="width: 100%; padding-right: 50px"
      >
        <el-form-item label="头像">
          <el-upload
            class="avatar-uploader"
            :http-request="hanldeFileUpload"
            :show-file-list="false"
            accept="image/jpg,image/jpeg,image/png,image/gif,image/webp"
            :before-upload="beforeAvatarUpload"
          >
            <img v-if="form.avatar" :src="form.avatar" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
        <el-form-item label="账号">
          <el-input disabled v-model="form.username" />
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholer="请输入名称" />
        </el-form-item>
        <el-form-item label="身份">
          <el-input disabled v-model="roleLabel" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">保存修改</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { getUserInfo, updateUserInfo } from '@/api/user'
import { ref, reactive, onMounted, computed } from 'vue'
import { useUser } from '@/utils/user'
import { ElMessage } from 'element-plus'
import { uploadFileApi } from '@/api/upload'

const { updateData } = useUser()

const FormRef = ref()
const loading = ref(false)
const submitting = ref(false)

const form = reactive({
  username: '',
  name: '',
  role: '',
  email: '',
  phone: '',
  avatar: ''
})

const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  // type: 'email' 是邮箱自带的验证方式
  email: [{ type: 'email', message: '邮箱格式错误', trigger: 'blur' }],
  // 手机号使用正则表达式进行验证
  phone: [{ pattern: /^1[3-9]\d{9}$/, message: '手机号格式错误', trigger: 'blur' }]
}

// 因为在role角色信息存储在数据库中的是英文，我们想让他在前端显示的是中文，就需要对其进行计算操作
const roleLabel = computed(() => {
  return form.role === 'admin' ? '管理员' : form.role === 'student' ? '学生' : '未知角色'
})

// beforeAvatarUpload 是对上传的头像进行校验的函数
const beforeAvatarUpload = (file) => {
  const imageType = ['image/jpe', 'image/jpeg', 'image/png', 'image/gif', 'image/webp']
  if (!imageType.includes(file.type)) {
    ElMessage.error('只能上传图片')
    return false
  }
  if (file.size / 1024 / 1024 > 2) {
    ElMessage.error('上传的文件大小不能超过2MB')
    return false
  }
  return true
}

// 将文件通过api请求后端上传至数据库中
const hanldeFileUpload = async ({ file }) => {
  try {
    const res = await uploadFileApi(file)
    if (res.code === 200) {
      form.avatar = res.data?.url // 上传后的文件可以显示在前端中展示
    }
  } catch {}
}

// 将用户对应的信息加载到输入框中
const loadUserInfo = async () => {
  loading.value = true
  try {
    const res = await getUserInfo()
    if (res.code === 200) {
      // 使用该方法将 res.data 中的数据逐个加载到 form 中
      Object.assign(form, res.data)
    }
  } finally {
    loading.value = false
  }
}

// 提交修改内容
const handleSubmit = async () => {
  const valid = await FormRef.value.validate().catch(() => false)
  if (!valid) return // 如果没有校验内容，就返回false
  submitting.value = true
  try {
    // 调用请求api 修改数据库中的信息
    const res = await updateUserInfo(form)
    if (res.code === 200) {
      // 同步修改浏览器本地存储的信息
      updateData(res.data)
      console.log(res.data);
      
      ElMessage.success('修改成功')
    }
  } finally {
    submitting.value = false
  }
}

// 在上述代码执行完成后调用 loadUserInfo函数
onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped>
.avatar-uploader .avatar {
  width: 140px;
  height: 140px;
  display: block;
}
</style>
<style>
.avatar-uploader .el-upload {
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}
.avatar-uploader .el-upload:hover {
  border-color: var(--el-color-primary);
}
.el-icon.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 140px;
  height: 140px;
  text-align: center;
}
</style>

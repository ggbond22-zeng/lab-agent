<template>
  <div>
    <el-card>
      <template #header>
        <div style="font-weight: bold; font-size: 16px">
          <span>用户信息</span>
        </div>
      </template>
      <div style="margin-bottom: 10px">
        <el-input
          placeholder="请输入账号或名称进行搜索"
          style="width: 240px; margin-right: 8px"
          v-model="params.keyword"
          clearable
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        ></el-input>
        <el-button :icon="Search" type="primary" @click="handleSearch">搜索</el-button>
        <el-button :icon="Plus" type="success" @click="handleAdd">新增</el-button>
      </div>
      <el-table
        :data="tableData"
        style="width: 100%; margin-bottom: 10px"
        v-loading="loading"
        :header-cell-style="{ backgroundColor: '#f5f7fa', color: 'black' }"
      >
        <el-table-column prop="username" label="账号" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="avatar" label="头像">
          <template #default="{ row }">
            <div style="min-height: 50px">
              <img
                v-if="row.avatar"
                style="width: 50px; height: 50px; border-radius: 50%"
                :src="row.avatar"
                alt=""
              />
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="phone" label="电话" />
        <el-table-column prop="role" label="角色" width="100px">
          <template #default="{ row }">
            {{ row.role === 'admin' ? '管理员' : '学生' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100px">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160px">
          <template #default="{ row }">
            <el-button type="primary" text bg @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" text bg @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        style="display: flex; justify-content: flex-end"
        v-model:current-page="params.page"
        v-model:page-size="params.pageSize"
        background
        layout="total, prev, pager, next"
        :total="total"
        @current-change="load"
      />
    </el-card>
    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑' : '新增'" width="500">
      <el-form
        ref="FormRef"
        :model="form"
        :rules="rules"
        v-loading="loading"
        label-width="60px"
        style="width: 100%; padding-right: 50px; margin-top: 10px"
      > 
        <el-form-item label="账号" prop="username">
          <el-input :disabled="!!form.id" v-model="form.username" placeholer="请输入账号" />
        </el-form-item>
        <!-- 使用 v-if 当 form.id 不存在时显示密码输入框 因为修改时不需要修改密码 -->
        <el-form-item label="密码" prop="password" v-if="!form.id">
          <el-input type="password" show-password v-model="form.password" placeholer="请输入密码" />
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholer="请输入名称" />
        </el-form-item>
        <el-form-item label="身份">
          <el-select v-model="form.role">
            <el-option label="学生" value="student"></el-option>
            <el-option label="管理员" value="admin"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">正常</el-radio>
            <el-radio :value="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" :loading="Formloading" @click="handleSave">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { createUserApi, deleteUserApi, getUserList, updateUserApi } from '@/api/user'
import { ref, reactive, onMounted } from 'vue'
import { Search, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const FormRef = ref()
const total = ref(0)
const dialogVisible = ref(false)
const loading = ref(false)
const tableData = ref([])
const Formloading = ref(false)

const params = reactive({
  keyword: '',
  page: 1,
  pageSize: 10
})

const form = reactive({
  username: '',
  name: '',
  role: 'student',
  email: '',
  phone: '',
  avatar: '',
  status: 1
})

const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 3, max: 10, message: '密码长度在3-10位', trigger: 'blur' }
  ],
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  // type: 'email' 是邮箱自带的验证方式
  email: [{ type: 'email', message: '邮箱格式错误', trigger: 'blur' }],
  // 手机号使用正则表达式进行验证
  phone: [{ pattern: /^1[3-9]\d{9}$/, message: '手机号格式错误', trigger: 'blur' }]
}

// 对form表单进行重置
const resetForm = () => {
  Object.assign(form, {
    id: null,
    username: '',
    name: '',
    role: 'student',
    email: '',
    phone: '',
    avatar: '',
    status: 1
  })
}

const handleClose = () => {
  dialogVisible.value = false
}

// 点击添加按钮
const handleAdd = () => {
  resetForm()
  dialogVisible.value = true // 让对话框弹出显示
}

// 点击编辑按钮
const handleEdit = (row) => {
  // 先重置表单内容
  resetForm()
  // 再将用户的信息填充到表单当中
  Object.assign(form, {
    id: row.id,
    username: row.username,
    name: row.name,
    role: row.role,
    email: row.email,
    phone: row.phone,
    avatar: row.avatar,
    status: row.status
  })
  dialogVisible.value = true
}

// 点击删除按钮
const handleDelete = (row) => {
  ElMessageBox.confirm(`是否确认删除 ${row.name} 用户？`, '确认删除', { type: 'warning' }).then(
    async () => {
      const res = await deleteUserApi(row.id)
      if (res.code === 200) {
        ElMessage.success('用户已删除')
        load()
      }
    }
  )
}

// 点击保存按钮
const handleSave = async () => {
  const valid = await FormRef.value.validate().catch(() => false)
  if (!valid) return
  Formloading.value = true
  try {
    // 因为新增和修改要共用对话框，在api调用时先判断是什么方法
    const res = form.id ? await updateUserApi(form.id, form) : await createUserApi(form)
    if (res.code === 200) {
      dialogVisible.value = false // 保存成功后自动关闭对话框
      ElMessage.success('保存成功')
      load()
    }
  } finally {
    Formloading.value = false
  }
}

// 加载数据到页面中
const load = async () => {
  loading.value = true
  try {
    const res = await getUserList({
      page: params.page,
      page_size: params.pageSize,
      keyword: params.keyword
    })
    if (res.code === 200) {
      tableData.value = res.data?.list
      total.value = res.data?.total
    }
  } finally {
    loading.value = false
  }
}

const handleSearch = async () => {
  params.page = 1
  load()
}

// 自动触发钩子函数
onMounted(() => {
  load()
})
</script>

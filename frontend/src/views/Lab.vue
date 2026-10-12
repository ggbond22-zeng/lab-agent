<template>
  <div>
    <el-card>
      <template #header>
        <div style="font-weight: bold; font-size: 16px">
          <span>实验室信息</span>
        </div>
      </template>
      <div style="margin-bottom: 10px">
        <el-input
          placeholder="请输入名称或地址进行搜索"
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
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="description" label="简介" />
        <el-table-column prop="capacity" label="容量" width="70px" />
        <el-table-column prop="location" label="位置" />
        <el-table-column label="开放时间">
          <template #default="{ row }">
            {{ row.open_time && row.close_time ? `${row.open_time} - ${row.close_time}` : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="img" label="封面">
          <template #default="{ row }">
            <div style="min-height: 50px">
              <img v-if="row.img" style="width: 50px; height: 50px" :src="row.img" alt="" />
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100px">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? '开放' : '关闭' }}
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
        label-width="70px"
        style="width: 100%; padding-right: 30px; margin-top: 10px;"
      >
        <el-form-item label="封面">
          <el-upload
            class="avatar-uploader"
            :http-request="hanldeFileUpload"
            :show-file-list="false"
            accept="image/jpg,image/jpeg,image/png,image/gif,image/webp"
            :before-upload="beforeAvatarUpload"
          >
            <img v-if="form.img" :src="form.img" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholer="请输入名称" />
        </el-form-item>
        <el-form-item label="简介">
          <el-input type="textarea" v-model="form.description" placeholer="请输入简介" />
        </el-form-item>
        <el-form-item label="容量" prop="capacity">
          <el-input-number v-model="form.capacity" placeholer="请输入容量" :min="1" :max="500"/>
        </el-form-item>
        <el-form-item label="位置">
          <el-input type="textarea" v-model="form.location" />
        </el-form-item>
        <el-form-item label="开放时间">
          <el-time-picker
            v-model="form.open_time"
            format="HH:mm"
            value-format="HH:mm"
            placeholer="开始"
            style="width: 150px; margin-right: 6px;"
          >
          </el-time-picker>
          <el-time-picker
            v-model="form.close_time"
            format="HH:mm"
            value-format="HH:mm"
            placeholer="结束"
            style="width: 150px;"
          >
          </el-time-picker>
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">开启</el-radio>
            <el-radio :value="0">关闭</el-radio>
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
import { createLabApi, deleteLabApi, getLabList, updateLabApi } from '@/api/lab'
import { ref, reactive, onMounted } from 'vue'
import { Search, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { uploadFileApi } from '@/api/upload'

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
  name: '',
  description: '',
  capacity: 1,
  location: '',
  open_time: '',
  close_time: '',
  img: '',
  status: 1
})

const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  capacity: [{ required: true, message: '请输入实验室容量', trigger: 'blur' }]
}

// 对form表单进行重置
const resetForm = () => {
  Object.assign(form, {
    id: null,
    name: '',
    description: '',
    capacity: 20,
    location: '',
    open_time: '8:00',
    close_time: '18:00',
    img: '',
    status: 1
  })
}

const handleClose = () => {
  dialogVisible.value = false
}

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
      form.img = res.data?.url // 上传后的文件可以显示在前端中展示
    }
  } catch {}
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
    name: row.name,
    description: row.name,
    capacity: row.capacity,
    location: row.location,
    open_time: row.open_time,
    close_tiem: row.close_tiem,
    img: row.img,
    status: row.status
  })
  dialogVisible.value = true
}

// 点击删除按钮
const handleDelete = (row) => {
  ElMessageBox.confirm(`是否确认删除 ${row.name} 实验室？`, '确认删除', { type: 'warning' }).then(
    async () => {
      const res = await deleteLabApi(row.id)
      if (res.code === 200) {
        ElMessage.success('实验室已删除')
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
    const res = form.id ? await updateLabApi(form.id, form) : await createLabApi(form)
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
    const res = await getLabList({
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

<style scoped>
.avatar-uploader .avatar {
  width: 120px;
  height: 120px;
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
  width: 120px;
  height: 120px;
  text-align: center;
}
</style>

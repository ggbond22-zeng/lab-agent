<template>
  <el-card shadow="never" style="margin-bottom: 10px">
    <div style="display: flex; justify-content: space-between; align-items: center; gap: 30px">
      <div style="font-size: 20px; font-weight: bold">欢迎使用实验室预约系统</div>
      <el-button type="primary" text bg @click="router.push('/manager/ai-chat')"
        >ai对话助手</el-button
      >
    </div>
  </el-card>
  <el-row :gutter="16" style="margin-bottom: 16px">
    <el-col :xs="24" :sm="8" v-for="item in statCards" :key="item.label">
      <el-card shadow="hover" style="margin-bottom: 16px">
        <div style="color: #909399; font-size: 13px">{{ item.label }}</div>
        <div style="margin-top: 8px; font-size: 28px; font-weight: 700; color: #303133">
          {{ item.value }}
        </div>
      </el-card>
    </el-col>
  </el-row>

  <el-card shadow="never" style="margin-bottom: 16px">
    <template #header>
      <span style="font-weight: 600">当且各实验室预约状态</span>
    </template>
    <div style="margin-bottom: 10px">
      <el-date-picker
        placeholder="请选择日期进行搜索"
        style="width: 240px; margin-right: 8px"
        v-model="params.date"
        format="YYYY-MM-DD"
        value-format="YYYY-MM-DD"
        clearable
        @keyup.enter="handleSearch"
        @clear="handleSearch"
      />
      <el-button :icon="Search" type="primary" @click="handleSearch">搜索</el-button>
    </div>
    <el-table
      :data="tableData"
      style="width: 100%; margin-bottom: 10px"
      v-loading="loading"
      :header-cell-style="{ backgroundColor: '#f5f7fa', color: 'black' }"
    >
      <el-table-column prop="lab_name" label="实验室"></el-table-column>
      <el-table-column prop="type" label="预约类型">
        <template #default="{ row }">
          <el-tag :type="row.type === '实验室' ? 'success' : 'primary'">{{ row.type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="equipment_name" label="设备">
        <template #default="{ row }">
          {{ row.equipment_name || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="date" label="日期"></el-table-column>
      <el-table-column label="预约时段">
        <template #default="{ row }"> {{ row.start_time }} - {{ row.end_time }} </template>
      </el-table-column>
    </el-table>
    <el-pagination
      style="display: flex; justify-content: flex-end"
      v-model:current-page="params.page"
      v-model:page-size="params.page_size"
      background
      layout="total, prev, pager, next"
      :total="total"
      @current-change="load"
    />
  </el-card>
</template>

<script setup>
import { getEquipmentList } from '@/api/equipment'
import { getLabList } from '@/api/lab'
import { ReservationPageListApi, ReservationPageListHomeApi } from '@/api/reservation'
import router from '@/router'
import { useUser } from '@/utils/user'
import { computed, onMounted, ref, reactive } from 'vue'
import { Search } from '@element-plus/icons-vue'

const { userInfo } = useUser()

const labTotal = ref('-')
const reservationTotal = ref('-')
const tableData = ref([])
const total = ref(null)
const loading = ref(false)

const params = reactive({
  date: null,   // 如果传入后端可以为空的数据尽量不要写 ''空字符串 都要写为null
  page: 1,
  page_size: 10,
  status: 1
})

const statCards = computed(() => [
  { label: '开放实验室（约）', value: labTotal.value },
  { label: '与我相关的预约', value: reservationTotal.value },
  { label: 'AI 助手', value: '已接入' }
])

const load = async () => {
  loading.value = true
  try {
    const res = await ReservationPageListHomeApi(params)
    if (res.code === 200) {
      tableData.value = res.data?.list
      total.value = res.data?.total
    }
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  params.page = 1
  load()
}

onMounted(async () => {
  load()
  try {
    const labRes = await getLabList({ page: 1, page_size: 10, status: 1 })
    if (labRes.code === 200) {
      labTotal.value = labRes.data?.total ?? 0
    }
  } catch {
    labTotal.value = '-'
  }
  try {
    const resRes = await ReservationPageListApi({ page: 1, page_size: 10 })
    if (resRes.code === 200) reservationTotal.value = resRes.data?.total ?? 0
  } catch {
    reservationTotal.value = '-'
  }
})
</script>

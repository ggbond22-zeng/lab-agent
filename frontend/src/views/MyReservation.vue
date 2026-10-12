<template>
  <el-card>
    <template #header>
      <div style="font-weight: bold; font-size: 16px">
        <span>我的预约信息</span>
      </div>
    </template>
    <div style="margin-bottom: 10px">
      <el-select
        placeholder="请选择预约状态进行搜索"
        v-model="params.status"
        style="width: 240px; margin-right: 8px"
        clearable
        @change="handleSearch"
        @clear="handleSearch"
      >
        <el-option :value="0" label="未审核"></el-option>
        <el-option :value="1" label="已通过"></el-option>
        <el-option :value="2" label="已拒绝"></el-option>
        <el-option :value="3" label="已取消"></el-option>
      </el-select>
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
      <el-table-column prop="remark" label="备注"></el-table-column>
      <el-table-column label="预约状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button v-if="row.status === 0" type="danger" text bg @click="handleCancel(row)"
            >取消</el-button
          >
        </template>
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
import { ref, reactive, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { cancelReservationApi, ReservationPageListApi } from '@/api/reservation'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const tableData = ref([])
const total = ref(null)

const params = reactive({
  page: 1,
  page_size: 10,
  status: null
})

const statusType = (status) => {
  return { 0: 'warning', 1: 'success', 2: 'danger', 3: 'info' }[status] || '-'
}

const statusText = (status) => {
  return { 0: '未审批', 1: '已通过', 2: '已拒绝', 3: '已取消' }[status] || '-'
}

const load = async () => {
  loading.value = true
  try {
    const res = await ReservationPageListApi(params)
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

const handleCancel = (row) => {
  ElMessageBox.confirm(`确认取消 ${row.lab_name} 的预约？`, '确认取消', { type: 'warning' }).then(
    async () => {
      const res = await cancelReservationApi(row.id)
      if (res.code === 200) {
        ElMessage.success('预约取消成功')
        load()
      }
    }
  )
}

onMounted(() => {
  load()
})
</script>

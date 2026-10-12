<template>
  <el-card>
    <template #header>
      <div style="display: flex; justify-content: space-between; align-items: center">
        <div style="font-weight: bold; font-size: 16px">
          <span>{{ lab?.name || '实验室' }}设备列表</span>
        </div>
        <div>
          <el-button @click="router.push('/manager/lablist')">返回实验室列表</el-button>
          <el-button type="primary" @click="handleReserveLab(lab)">预约实验室</el-button>
        </div>
      </div>
    </template>
    <div style="margin-bottom: 10px">
      <el-input
        placeholder="请输入设备名称进行搜索"
        style="width: 240px; margin-right: 8px"
        v-model="params.keyword"
        clearable
        @keyup.enter="handleSearch"
        @clear="handleSearch"
      ></el-input>
      <el-button :icon="Search" type="primary" @click="handleSearch">搜索</el-button>
    </div>
    <div v-if="lab" style="margin-bottom: 10px">
      <div style="margin-bottom: 10px">简介：{{ lab.description }}</div>
      <div style="margin-bottom: 10px">
        位置：{{ lab.location || '-' }}<span style="margin: 0 10px">|</span>容量：{{
          lab.capacity
        }}
        人<span style="margin: 0 10px">|</span>开放时间：{{
          lab.open_time && lab.close_time ? `${lab.open_time} - ${lab.close_time}` : '-'
        }}
      </div>
    </div>
    <el-table
      :data="tableData"
      style="width: 100%; margin-bottom: 10px"
      v-loading="loading"
      :header-cell-style="{ backgroundColor: '#f5f7fa', color: 'black' }"
    >
      <el-table-column prop="img" label="封面">
        <template #default="{ row }">
          <div style="min-height: 50px">
            <el-image
              v-if="row.img"
              style="width: 50px; height: 50px"
              :src="row.img"
              alt=""
              :preview-src-list="[row.img]"
              :preview-teleported="true"
            />
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="description" label="简介" />
      <el-table-column prop="spec" label="型号规格" />
      <el-table-column prop="quantity" label="设备数量" />
      <el-table-column prop="status" label="状态" width="100px">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'danger'">
            {{ row.status === 1 ? '正常' : '维修' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100px">
        <template #default="{ row }">
          <el-button :disabled="!row.status" type="primary" text bg @click="handleReserveEquipment(row)"
            >预约</el-button
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
      @current-change="loadEquipment"
    />
  </el-card>
  <!-- 组件内需要传入哪些变量就绑定哪些变量 -->
  <reserve-dialog
    v-model:visible="reserveVisible"
    :lab-id="lab?.id"
    :lab-name="lab?.name"
    :equipment-id="currentEquipment?.id"
    :equipment-name="currentEquipment?.name"
  ></reserve-dialog>
</template>

<script setup>
import ReserveDialog from '@/components/ReserveDialog.vue'
import { getEquipmentList } from '@/api/equipment'
import { getLab } from '@/api/lab'
import { ElMessage } from 'element-plus'
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const lab = ref(null)
const total = ref(0)
const tableData = ref([])
const loading = ref(false)

const reserveVisible = ref(false)
const currentEquipment = ref(null)

const params = reactive({
  keyword: '',
  page: 1,
  page_size: 10,
  lab_id: Number(route.query.lab_id) // 路径参数得到的是字符串，再转化为数字类型
})

// 点击预约实验室
const handleReserveLab = () => {
  currentEquipment.value = null
  reserveVisible.value = true
}

// 点击预约设备
const handleReserveEquipment = (equipment) => {
  currentEquipment.value = equipment
  reserveVisible.value = true
}


// 将实验室信息加载出来
const loadLab = async () => {
  if (!params.lab_id) {
    ElMessage.error('缺少实验室查询条件 [lab_id]')
    return
  }
  const res = await getLab(params.lab_id)
  if (res.code === 200) {
    lab.value = res.data
  }
}

// 加载设备信息
const loadEquipment = async () => {
  loading.value = true
  try {
    const res = await getEquipmentList(params)
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
  loadEquipment()
}

onMounted(() => {
  loadLab()
  loadEquipment()
})
</script>

<template>
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
    </div>
    <el-row :gutter="15" v-loading="loading">
      <el-col v-for="item in tableData" :key="item.id" style="margin-bottom: 10px" :span="6">
        <el-card shadow="hover">
          <img
            v-if="item.img"
            :src="item.img"
            alt=""
            style="
              display: block;
              width: 100%;
              height: 150px;
              border-radius: 8px;
              object-fit: cover;
            "
          />
          <div style="font-weight: bold; font-size: 16px; margin-bottom: 10px; margin-top: 8px">
            实验室名称：{{ item.name }}
          </div>
          <div style="margin-bottom: 10px">位置：{{ item.location || '-' }}</div>
          <div style="margin-bottom: 10px">容量：{{ item.capacity }} 人</div>
          <div style="margin-bottom: 10px">
            开放时间：{{
              item.open_time && item.close_time ? `${item.open_time} - ${item.close_time}` : '-'
            }}
          </div>
          <div style="display: flex; margin-bottom: 10px; gap: 8px">
            <el-button style="flex: 1" @click="handleViewEquipment(item)">查看设备</el-button>
            <el-button type="primary" style="flex: 1" @click="handleReserve(item)"
              >预约实验室</el-button
            >
          </div>
        </el-card>
      </el-col>
    </el-row>
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
  <!-- 组件内需要传入哪些变量就绑定哪些变量 -->
  <reserve-dialog
    v-model:visible="reserveVisible"
    :lab-id="currentLab?.id"
    :lab-name="currentLab?.name"
  ></reserve-dialog>
</template>

<script setup>
import ReserveDialog from '@/components/ReserveDialog.vue'
import { getLabList } from '@/api/lab'
import router from '@/router'
import { ElMessage } from 'element-plus'
import { ref, reactive, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'

const total = ref(0)
const loading = ref(false)
const tableData = ref([])

const reserveVisible = ref(false)
const currentLab = ref(null)

const params = reactive({
  keyword: '',
  page: 1,
  page_size: 10
})

// 点击查看设备 query就是路径参数
const handleViewEquipment = (lab) => {
  router.push({ path: '/manager/lab-equipment', query: { lab_id: lab.id } })
}

// 点击预约实验室
const handleReserve = (lab) => {
  currentLab.value = lab
  reserveVisible.value = true
}

// 加载数据
const load = async () => {
  loading.value = true
  try {
    const res = await getLabList(params)
    if (res.code === 200) {
      tableData.value = res.data?.list
      total.value = res.data?.total
    }
  } finally {
    loading.value = false
  }
}

// 点击查询
const handleSearch = () => {
  params.page = 1
  load()
}

onMounted(() => {
  load()
})
</script>

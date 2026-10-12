<template>
  <div>
    <!-- @open="FormRef.resetFields()" 表示在打开时重新加载表单中的数据 -->
    <el-dialog
      :model-value="visible"
      title="预约"
      @open="FormRef.resetFields()"
      @close="emit('update:visible', false)"
      width="500"
    >
      <el-form
        ref="FormRef"
        :model="form"
        :rules="rules"
        label-width="90px"
        style="width: 100%; padding-right: 30px; margin-top: 10px"
      >
        <el-form-item label="实验室">
          <el-input :model-value="labName" disabled />
        </el-form-item>
        <el-form-item label="设备名称">
          <el-input :model-value="equipmentName" disabled />
        </el-form-item>
        <el-form-item label="预约日期" prop="date">
          <el-date-picker
            style="width: 100%"
            v-model="form.date"
            type="date"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            placeholer="请选择日期"
          />
        </el-form-item>
        <el-form-item label="开始时间" prop="startTime">
          <el-time-picker
            style="width: 100%"
            v-model="form.startTime"
            format="HH:mm"
            value-format="HH:mm"
            placeholer="请选择开始时间"
          />
        </el-form-item>
        <el-form-item label="结束时间" prop="endTime">
          <el-time-picker
            style="width: 100%"
            v-model="form.endTime"
            format="HH:mm"
            value-format="HH:mm"
            placeholer="请选择结束时间"
          />
        </el-form-item>
        <el-form-item label="备注信息">
          <el-input type="textarea" v-model="form.remark" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="emit('update:visible', false)">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handlesubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { CreateReservationApi } from '@/api/reservation'
import { ElMessage } from 'element-plus'
import { ref, reactive } from 'vue'

// 用来接收组件外边传输进来的数据
const props = defineProps({
  visible: Boolean,
  labId: Number,
  labName: String,
  equipmentId: Number,
  equipmentName: String
})

const FormRef = ref()
const submitLoading = ref(false)
// 定义发送出去的内容
const emit = defineEmits(['update:visible'])

const form = reactive({
  date: '',
  startTime: '09:00',
  endTime: '15:00',
  remark: ''
})

const rules = {
  date: [{ required: true, message: '请输入预约日期', trigger: 'change' }],
  startTime: [{ required: true, message: '请输入预约开始时间', trigger: 'change' }],
  endTime: [{ required: true, message: '请输入预约结束时间', trigger: 'change' }]
}

const handlesubmit = async () => {
  const valid = await FormRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    const res = await CreateReservationApi({
      lab_id: props.labId,
      equipment_id: props.equipmentId,
      date: form.date,
      start_time: form.startTime,
      end_time: form.endTime,
      remark: form.remark
    })
    if (res.code === 200) {
      ElMessage.success('预约成功，请等待审核')
      emit('update:visible', false)
    }
  } finally {
    submitLoading.value = false
  }
}
</script>

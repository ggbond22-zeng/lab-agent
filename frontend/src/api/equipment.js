import request from '@/utils/request'

// 获取用户列表请求
export function getEquipmentList(params) {
  return request({
    url: '/api/equipment/list',
    method: 'get',
    params
  })
}

// 新增用户请求
export function createEquipmentApi(data) {
  return request({
    url: '/api/equipment',
    method: 'post',
    data
  })
}

// 管理员更新用户请求
export function updateEquipmentApi(equipmentId, data) {
  return request({
    url: `/api/equipment/${equipmentId}`,
    method: 'put',
    data
  })
}

// 管理员删除用户请求
export function deleteEquipmentApi(equipmentId) {
  return request({
    url: `/api/equipment/${equipmentId}`,
    method: 'delete'
  })
}

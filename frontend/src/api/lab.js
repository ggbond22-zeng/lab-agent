import request from '@/utils/request'


// 获取对应实验室信息
export function getLab(lab_id) {
  return request({
    url: `/api/lab/${lab_id}`,
    method: 'get'
  })
}

// 获取实验室列表请求
export function getLabList(params) {
  return request({
    url: '/api/lab/list',
    method: 'get',
    params
  })
}

// 新增实验室请求
export function createLabApi(data) {
  return request({
    url: '/api/lab',
    method: 'post',
    data
  })
}

// 管理员更新实验室请求
export function updateLabApi(labId, data) {
  return request({
    url: `/api/lab/${labId}`,
    method: 'put',
    data
  })
}

// 管理员删除实验室请求
export function deleteLabApi(labId) {
  return request({
    url: `/api/lab/${labId}`,
    method: 'delete'
  })
}

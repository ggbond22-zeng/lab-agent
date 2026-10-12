import request from '@/utils/request'

// 创建预约信息
export function CreateReservationApi(data) {
  return request({
    url: '/api/reservation',
    method: 'post',
    data
  })
}

// 获取预约分页信息
export function ReservationPageListApi(params) {
  return request({
    url: '/api/reservation/list',
    method: 'get',
    params
  })
}

// 获取预约分页信息，用于主页展示
export function ReservationPageListHomeApi(params) {
  return request({
    url: '/api/reservation/list/home',
    method: 'get',
    params
  })
}

// 用户修改预约状态
export function cancelReservationApi(id) {
  return request({
    url: `/api/reservation/${id}/cancel`,
    method: 'put'
  })
}

// 管理员审核预约状态
export function auditReservationApi(id, status) {
  return request({
    url: `/api/reservation/${id}/audit`,
    method: 'put',
    data: { status }
  })
}


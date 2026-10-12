import request from '@/utils/request'

// 获取用户信息请求  与django中的ajax请求类似
export function getUserInfo() {
  return request({
    url: '/api/user/info',
    method: 'get'
  })
}

// 更新用户信息请求  与django中的ajax请求类似
export function updateUserInfo(data) {
  return request({
    url: '/api/user/update',
    method: 'put',
    data: data
  })
}

// 修改用户密码请求
export function updatePassword(data) {
  return request({
    url: '/api/user/password',
    method: 'put',
    data: data
  })
}

// 获取用户列表请求
export function getUserList(params) {
  return request({
    url: '/api/user/list',
    method: 'get',
    params
  })
}

// 新增用户请求
export function createUserApi(data) {
  return request({
    url: '/api/user',
    method: 'post',
    data
  })
}

// 管理员更新用户请求
export function updateUserApi(userId, data) {
  return request({
    url: `/api/user/${userId}`,
    method: 'put',
    data
  })
}

// 管理员删除用户请求
export function deleteUserApi(userId) {
  return request({
    url: `/api/user/${userId}`,
    method: 'delete'
  })
}

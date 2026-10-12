import request from '@/utils/request'


// 登录请求  与django中的ajax请求类似
export function loginApi(data) {
    return request({
        url: '/api/auth/login',
        method: 'post',
        data: data  // 登录请求数据
    })
}

// 注册请求  与django中的ajax请求类似
export function registerApi(data) {
    return request({
      url: '/api/auth/register',
      method: 'post',
      data: data // 登录请求数据
    })
}



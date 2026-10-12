import request from '@/utils/request'

// 更新用户头像请求  与django中的ajax请求类似
export function uploadFileApi(file) {
  const formData = new FormData()  // 在上传文件时要使用 FormData 
  formData.append('file', file)   // 在formData 中添加 名为 file 的键 当中添加的值为 file
  return request({
    url: '/api/files/upload',
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' }  // 该请求头在 Apipost 中测试时可以看到
  })
}



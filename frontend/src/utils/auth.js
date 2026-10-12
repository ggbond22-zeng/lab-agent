// 获取、存储、删除，token 及 用户信息

const TOKEN_KEY = 'token'
const USER_KEY = 'userInfo'

// 从浏览器本地存储中获取token
export function getToken() {
    return localStorage.getItem(TOKEN_KEY)
}

//  将 token 保存到浏览器本地存储中
export function setToken(token) {
    localStorage.setItem(TOKEN_KEY, token)
}

// 删除浏览器本地存储的 token
export function removeToken() {
    localStorage.removeItem(TOKEN_KEY)
}

export function getUserInfo() {
    const str = localStorage.getItem(USER_KEY)
    return str ? JSON.parse(str) : str
}

export function setUserInfo(userInfo) {
  localStorage.setItem(USER_KEY, JSON.stringify(userInfo))
}

export function removeUserInfo() {
  localStorage.removeItem(USER_KEY)
}

// 退出登录，将本地的用户信息和token全部清除
export function logout() {
    removeToken()
    removeUserInfo()
}



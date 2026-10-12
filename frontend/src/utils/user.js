// 对用户 user 的数据进行操作，当用户对其个人信息进行操作时，getUserInfo得到的是静态数据，不是动态的，使用ref让其变成响应式的动态数据
// 只能用于 setup 函数使用

import { ref } from "vue"
import { getUserInfo, setToken, setUserInfo } from "./auth"

const userInfo = ref(getUserInfo())   // 响应式对象，可以随时更新最新的值

// 定义 Hook 函数，Hook 函数的规定是统一用use开头
export function useUser() {
    // 保存登录数据
    function saveLoginData(data) {
        setToken(data.token)
        setUserInfo(data.user)
        userInfo.value = data.user
    }

    // 当用户对其信息进行更新时，响应式对象也要同步进行更新
    function updateData(user) {
        setUserInfo(user)
        userInfo.value = user
    }

    // 当用户重新加载信息时，响应式对象内容重新加载用户信息
    function reloadData() {
        userInfo.value = getUserInfo()
    }

    // 将 Hook 函数中规定的函数进行返回，并且返回响应式对象
    return {
      userInfo,
      saveLoginData,
      updateData,
      reloadData
    }
}




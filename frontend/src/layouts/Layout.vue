<template>
  <div class="common-layout">
    <!-- style="min-height: 100vh;" 表示最小高度为视口高度 -->
    <el-container style="min-height: 100vh">
      <!-- display: flex 让元素水平排列 font-weight: bold 加粗字体-->
      <el-header style="display: flex; background-color: #fff; border-bottom: 1px solid #fff">
        <div
          style="flex: 1; display: flex; align-items: center; font-size: 25px; font-weight: bold"
        >
          <img src="@/assets/imgs/logo.png" style="width: 30px; margin-right: 15px" />
          实验室预约系统
        </div>
        <div style="display: flex; align-items: center">
          <el-dropdown @command="handleCommand">
            <div style="display: flex; align-items: center; cursor: pointer">
              <img
                :src="userInfo?.avatar"
                style="width: 30px; margin-right: 10px; border-radius: 50%"
              />
              <div style="font-weight: bold">{{ userInfo?.name }}</div>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="password">修改密码</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-container>
        <el-aside width="200px">
          <!-- default-active="/home" 给指定菜单设置高亮 -->
          <el-menu router style="height: 100%" :default-active="router.currentRoute.value.path">
            <el-menu-item index="/manager/home">
              <el-icon><icon-menu /></el-icon>
              <span>系统首页</span>
            </el-menu-item>
            <el-menu-item index="/manager/ai-chat">
              <el-icon><ChatDotRound /></el-icon>
              <span>智能体预约</span>
            </el-menu-item>
            <el-menu-item index="/manager/lablist" v-if="userInfo?.role === 'student'">
              <el-icon><OfficeBuilding /></el-icon>
              <span>实验室列表</span>
            </el-menu-item>
            <el-menu-item index="/manager/my-reservation" v-if="userInfo?.role === 'student'">
              <el-icon><List /></el-icon>
              <span>我的预约</span>
            </el-menu-item>
            <el-menu-item index="/manager/lab" v-if="userInfo?.role === 'admin'">
              <el-icon><House /></el-icon>
              <span>实验室管理</span>
            </el-menu-item>
            <el-menu-item index="/manager/equipment" v-if="userInfo?.role === 'admin'">
              <el-icon><Setting /></el-icon>
              <span>设备列表管理</span>
            </el-menu-item>
            <el-menu-item index="/manager/audit-reservation" v-if="userInfo?.role === 'admin'">
              <el-icon><OfficeBuilding /></el-icon>
              <span>预约审核</span>
            </el-menu-item>
            <el-menu-item index="/manager/user" v-if="userInfo?.role === 'admin'">
              <el-icon><User /></el-icon>
              <span>用户管理</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import router from '@/router'
import { logout } from '@/utils/auth'
import { House, Menu as IconMenu, User, Setting, OfficeBuilding, ChatDotRound, List } from '@element-plus/icons-vue'
import { useUser } from '@/utils/user'

const { userInfo } = useUser()

const handleCommand = (command) => {
  if (command === 'profile') {
    router.push('/manager/profile')
  } else if (command === 'password') {
    router.push('/manager/password')
  } else if (command === 'logout') {
    logout()
    router.push('/login')
  }
}
</script>

<template>
  <div class="common-layout">
    <!-- style="min-height: 100vh;" 表示最小高度为视口高度 -->
    <el-container style="min-height: 100vh">
      <!-- display: flex 让元素水平排列 font-weight: bold 加粗字体-->
      <el-header class="app-header" style="display: flex; background-color: #fff; border-bottom: 1px solid #fff">
        <div class="header-title">
          <!-- 移动端：汉堡按钮唤出抽屉菜单 -->
          <el-icon v-if="isMobile" class="menu-btn" @click="menuOpen = true"><icon-menu /></el-icon>
          <img src="@/assets/imgs/logo.png" class="logo" />
          <span class="title-text">实验室预约系统</span>
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
        <!-- 桌面端：常驻侧边栏；移动端（<768px）隐藏，改用抽屉 -->
        <el-aside width="200px" v-if="!isMobile">
          <SideMenu />
        </el-aside>
        <el-drawer
          v-if="isMobile"
          v-model="menuOpen"
          direction="ltr"
          size="200px"
          :with-header="false"
        >
          <SideMenu />
        </el-drawer>
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import router from '@/router'
import { logout } from '@/utils/auth'
import { Menu as IconMenu } from '@element-plus/icons-vue'
import { useUser } from '@/utils/user'
import SideMenu from './SideMenu.vue'

const { userInfo } = useUser()

// 移动端判定：视口宽 < 768px 视为手机，侧边栏收进抽屉
const isMobile = ref(window.innerWidth < 768)
const menuOpen = ref(false)

const onResize = () => {
  isMobile.value = window.innerWidth < 768
  // 切回桌面端时确保抽屉关闭
  if (!isMobile.value) menuOpen.value = false
}

onMounted(() => window.addEventListener('resize', onResize))
onUnmounted(() => window.removeEventListener('resize', onResize))

// 路由切换后自动关闭移动端抽屉菜单
watch(
  () => router.currentRoute.value.path,
  () => {
    menuOpen.value = false
  }
)

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

<style scoped>
/* 头部样式从内联抽出，便于做移动端媒体查询 */
.app-header {
  display: flex;
  align-items: center;
  background-color: #fff;
  border-bottom: 1px solid #fff;
}
.header-title {
  flex: 1;
  display: flex;
  align-items: center;
  font-size: 25px;
  font-weight: bold;
  min-width: 0;
}
.logo {
  width: 30px;
  margin-right: 15px;
}
.title-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.menu-btn {
  font-size: 22px;
  margin-right: 12px;
  cursor: pointer;
}
/* 手机端：标题字号收紧，避免挤压用户名 */
@media (max-width: 768px) {
  .app-header {
    height: 50px;
  }
  .header-title {
    font-size: 18px;
  }
  .logo {
    width: 24px;
    margin-right: 8px;
  }
}
</style>

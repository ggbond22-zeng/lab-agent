<template>
  <!-- 侧边菜单：桌面端在 el-aside 中，移动端在 el-drawer 中复用 -->
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
</template>

<script setup>
import router from '@/router'
import {
  House,
  Menu as IconMenu,
  User,
  Setting,
  OfficeBuilding,
  ChatDotRound,
  List
} from '@element-plus/icons-vue'
import { useUser } from '@/utils/user'

const { userInfo } = useUser()
</script>

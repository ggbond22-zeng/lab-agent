import { getToken } from '@/utils/auth'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/manager/home' },
    {
      path: '/manager',
      name: 'Layout',
      component: () => import('@/layouts/Layout.vue'),
      children: [
        { path: 'home', name: 'Home', component: () => import('@/views/Home.vue') },
        { path: 'lab', name: 'Lab', component: () => import('@/views/Lab.vue') },
        { path: 'profile', name: 'Profile', component: () => import('@/views/Profile.vue') },
        { path: 'password', name: 'Password', component: () => import('@/views/Password.vue') },
        { path: 'user', name: 'User', component: () => import('@/views/User.vue') },
        { path: 'equipment', name: 'Equipment', component: () => import('@/views/Equipment.vue') },
        { path: 'lablist', name: 'LabList', component: () => import('@/views/LabList.vue') },
        {
          path: 'lab-equipment',
          name: 'LabEquipment',
          component: () => import('@/views/LabEquipment.vue')
        },
        {
          path: 'my-reservation',
          name: 'MyReservation',
          component: () => import('@/views/MyReservation.vue')
        },
        {
          path: 'audit-reservation',
          name: 'AuditReservation',
          component: () => import('@/views/AuditReservation.vue')
        },
        {
          path: 'ai-chat',
          name: 'AiChat',
          component: () => import('@/views/AiChat.vue')
        }
      ]
    },
    { path: '/login', name: 'Login', component: () => import('@/views/Login.vue') },
    { path: '/register', name: 'Register', component: () => import('@/views/Register.vue') }
  ]
})

// 路由保卫：验证token     to 表示去哪个路由 from 表示来自哪个路由
router.beforeEach((to, from) => {
  const token = getToken() // 先获取token，如果有token 说明用户已经登录过了，就可以访问登录后的链接
  // 如果没有进行登录，强制返回到登录页面

  if (to.path === '/login' || to.path === '/register') {
    return true // 返回true 表示对以上两个链接进行放行，在这两个页面中不会被强制重定向
  } else {
    // 如果token存在 就返回true，如果token不存在 就强制跳转到/login页面
    return token ? true : '/login'
  }
})

export default router

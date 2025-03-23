import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'
import { useUserStore } from '../stores/user'

const service = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 5000
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    const userStore = useUserStore()
    if (userStore.token && config.url !== '/users/login/') {
      config.headers['Authorization'] = `Bearer ${userStore.token}`
    }
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error instanceof Error ? error : new Error(error))
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('Response error:', error.response || error)
    const message = error.response?.data?.message
      || error.response?.data?.detail
      || error.message
      || '请求失败'

    if (error.config.url !== '/users/login/') {
      ElMessage.error(message)
    }

    if (error.response?.status === 401) {
      const userStore = useUserStore()
      userStore.clearUserInfo()
      if (router.currentRoute.value.path !== '/auth') {
        router.push('/auth')
      }
    }
    return Promise.reject(error instanceof Error ? error : new Error(message))
  }
)

export default service
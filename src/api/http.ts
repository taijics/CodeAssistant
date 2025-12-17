// src/api/http.ts
import axios from 'axios'

const http = axios.create({
  baseURL: 'http://localhost:8081', // 后端项目管理模块地址
  timeout: 10000,
})

// 这里可以加拦截器，如需要的话
http.interceptors.response.use(
  (res) => res,
  (error) => {
    console.error('API error:', error)
    return Promise.reject(error)
  },
)

export default http
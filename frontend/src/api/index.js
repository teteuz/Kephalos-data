import axios from 'axios'
import { supabase } from '../lib/supabase'

// Axios instance
const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '',
  timeout: 300000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor — attach Supabase JWT to every request
service.interceptors.request.use(
  async (config) => {
    const { data } = await supabase.auth.getSession()
    const token = data.session?.access_token
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor
service.interceptors.response.use(
  response => {
    const res = response.data
    if (!res.success && res.success !== undefined) {
      console.error('API Error:', res.error || res.message || 'Unknown error')
      return Promise.reject(new Error(res.error || res.message || 'Error'))
    }
    return res
  },
  error => {
    const status = error.response?.status

    if (status === 401) {
      window.location.href = '/login'
      return Promise.reject(error)
    }

    if (status === 402 || status === 403) {
      window.location.href = '/pricing?upgrade=1'
      return Promise.reject(error)
    }

    if (status === 429) {
      const msg = error.response?.data?.error || 'Muitas requisições. Aguarde um momento e tente novamente.'
      return Promise.reject(new Error(msg))
    }

    if (error.code === 'ECONNABORTED') {
      return Promise.reject(new Error('A requisição demorou muito. Verifique sua conexão e tente novamente.'))
    }

    if (error.message === 'Network Error') {
      return Promise.reject(new Error('Sem conexão com o servidor. Verifique se o backend está rodando.'))
    }

    return Promise.reject(error)
  }
)

export const requestWithRetry = async (requestFn, maxRetries = 3, delay = 1000) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await requestFn()
    } catch (error) {
      if (i === maxRetries - 1) throw error
      console.warn(`Request failed, retrying (${i + 1}/${maxRetries})...`)
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)))
    }
  }
}

export default service

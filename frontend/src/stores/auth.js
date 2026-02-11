import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter()
  // 로컬 스토리지에서 토큰 꺼내오기 (새로고침 해도 유지됨)
  const token = ref(localStorage.getItem('token'))
  const user = ref(null)
  const username = ref(localStorage.getItem('username'))

  const isAuthenticated = computed(() => token.value !== null)

  // 1. 회원가입
  const signUp = async (payload) => {
    try {
      await axios.post('http://127.0.0.1:8000/accounts/signup/', payload)
      alert('가입 성공! WALLET.GG에 온 걸 환영해 🎉')
      router.push('/auth') // 로그인 페이지로 이동
    } catch (err) {
      console.error(err)
      alert('가입 실패... 정보를 다시 확인해줘.')
    }
  }
  // 2. 로그인
  const logIn = async (payload) => {
    const { username: user, password } = payload
    try {
      const res = await axios.post('http://127.0.0.1:8000/accounts/login/', {
        username: user,
        password: password
      })
      
      // 2. 로그인 성공 시 저장소에 저장!
      token.value = res.data.key
      username.value = user
      
      localStorage.setItem('token', res.data.key)
      localStorage.setItem('username', user) // ★ 이름도 저장!

      axios.defaults.headers.common['Authorization'] = `Token ${res.data.key}`
    } catch (err) {
      console.error(err)
      throw err
    }
  }

  const logOut = () => {
    // 3. 로그아웃 시 삭제
    token.value = null
    username.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('username') // ★ 이름도 삭제!
    
    // 헤더 초기화
    delete axios.defaults.headers.common['Authorization']
    // 메인으로 이동 (필요 시)
    window.location.href = '/' 
  }

  return { token, username, logIn, logOut, isAuthenticated, }
})
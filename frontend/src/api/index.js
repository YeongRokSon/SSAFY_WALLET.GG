import axios from 'axios'

// 1. 기본 axios 인스턴스 (로그인 안 해도 되는 요청)
const local = axios.create({
  baseURL: 'http://127.0.0.1:8000/' 
})

// 2. 인증이 필요한 axios 인스턴스 (로그인 후 토큰 실어 보낼 때)
// 나중에 auth 스토어랑 연결해서 토큰 자동으로 넣게 설정해야 함
const localAuth = axios.create({
  baseURL: 'http://127.0.0.1:8000/',
  headers: {
    'Content-Type': 'application/json',
    // 'Authorization': 'Token ...' (나중에 Pinia에서 토큰 가져와서 설정)
  }
})

export { local, localAuth } 
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const store = useAuthStore()
const isLogin = ref(true) 

const username = ref('')
const password = ref('')
const email = ref('')
const nickname = ref('') 
const phone_number = ref('')
const birth_date = ref('')

const submitForm = async () => {
  try {
    if (isLogin.value) {
      await store.logIn({ username: username.value, password: password.value })
      router.push('/') 
    } else {
      const sendData = {
        username: username.value,
        password1: password.value,
        password2: password.value,
        email: email.value,
        nickname: nickname.value, // 비어있으면 서버에서 랜덤 닉네임을 만들어줄 거야!
        phone_number: phone_number.value,
        birth_date: birth_date.value
      }
      await axios.post('http://127.0.0.1:8000/accounts/signup/', sendData)
      alert('가입 성공! 🎉 이제 로그인해줘.')
      isLogin.value = true 
    }
  } catch (err) {
    const errorMsg = err.response?.data ? JSON.stringify(err.response.data) : err.message
    alert('실패 ㅠㅠ: ' + errorMsg)
  }
}
</script>

<template>
  <div class="auth-container">
    <h1>💰 WALLET.GG {{ isLogin ? '로그인' : '회원가입' }}</h1>
    
    <div class="card shadow-lg">
      <form @submit.prevent="submitForm">
        <div class="form-group">
          <label>아이디 <span class="required">*</span></label>
          <input type="text" v-model="username" placeholder="아이디를 입력해줘" required>
        </div>
        <div class="form-group">
          <label>비밀번호 <span class="required">*</span></label>
          <input type="password" v-model="password" placeholder="비밀번호를 입력해줘" required>
        </div>

        <transition name="fade-slide">
          <div v-if="!isLogin" class="signup-extra">
            <div class="form-group">
              <label>닉네임 (선택)</label>
              <input type="text" v-model="nickname" placeholder="안 적으면 랜덤으로 지어줄게!">
            </div>
            <div class="form-group">
              <label>이메일</label>
              <input type="email" v-model="email" placeholder="wallet@example.com">
            </div>
            <div class="form-group">
              <label>휴대폰 번호</label>
              <input type="text" v-model="phone_number" placeholder="010-0000-0000">
            </div>
            <div class="form-group">
              <label>생년월일</label>
              <input type="date" v-model="birth_date">
            </div>
          </div>
        </transition>

        <button type="submit" class="btn-submit">
          {{ isLogin ? '로그인하기' : '가입하기' }}
        </button>
      </form>
    </div>

    <p class="toggle-text" @click="isLogin = !isLogin">
      {{ isLogin ? '계정이 없으신가요? 회원가입' : '이미 계정이 있나요? 로그인' }}
    </p>
  </div>
</template>

<style scoped>
/* 기존 스타일은 그대로야! */
.auth-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: linear-gradient(to top, #dfe9f3 0%, white 100%);
  padding: 20px;
  font-family: 'Pretendard', sans-serif;
}
.card {
  background: #ffffff;
  padding: 40px;
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  max-width: 450px;
  width: 100%;
}
.form-group { margin-bottom: 20px; text-align: left; }
.form-group label { display: block; font-size: 0.9rem; font-weight: 700; color: #495057; margin-bottom: 8px; }
.required { color: #fa5252; }
input {
  width: 100%;
  padding: 14px;
  border: 2px solid #edf2f7;
  border-radius: 12px;
  background-color: #f8f9fa;
  box-sizing: border-box;
}
input:focus { outline: none; border-color: #37b24d; background-color: #fff; }
.btn-submit {
  width: 100%;
  padding: 16px;
  margin-top: 10px;
  background: linear-gradient(135deg, #37b24d 0%, #2b8a3e 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
}
.toggle-text { margin-top: 25px; color: #636e72; cursor: pointer; }
.fade-slide-enter-active { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>
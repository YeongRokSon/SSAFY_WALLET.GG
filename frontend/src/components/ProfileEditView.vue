<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const store = useAuthStore()
const router = useRouter()

const editForm = reactive({
  nickname: '', email: '', phone_number: '', birth_date: '',
  age: 0, money: 0, salary: 0, description: ''
})
const imageFile = ref(null)
const imagePreview = ref(null)
const fileInput = ref(null)

const fetchCurrentInfo = async () => {
  try {
    const res = await axios.get(`http://127.0.0.1:8000/accounts/profile/${store.username}/`, {
      headers: { Authorization: `Token ${store.token}` }
    })
    const fields = ['nickname', 'email', 'phone_number', 'birth_date', 'age', 'money', 'salary', 'description']
    for (let i = 0; i < fields.length; i++) {
      const field = fields[i]
      if (res.data[field] !== undefined) {
        editForm[field] = res.data[field]
      }
    }
    if (res.data.profile_img) {
      const url = res.data.profile_img
      imagePreview.value = url.startsWith('http') ? url : `http://127.0.0.1:8000${url}`
    }
  } catch (err) { console.error('정보 로드 실패') }
}

const triggerFileInput = () => fileInput.value.click()

const onFileChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    imageFile.value = file
    imagePreview.value = URL.createObjectURL(file)
  }
}

const updateProfile = async () => {
  const formData = new FormData()
  for (const key in editForm) {
    formData.append(key, editForm[key] || '')
  }
  if (imageFile.value) formData.append('profile_img', imageFile.value)

  try {
    await axios.put(`http://127.0.0.1:8000/accounts/profile/${store.username}/`, formData, {
      headers: { Authorization: `Token ${store.token}`, 'Content-Type': 'multipart/form-data' }
    })
    // ★ 핵심: 이동할 때 본인의 이름을 꼭 들고 가야 해!
    router.push({ name: 'profile', params: { username: store.username } })
  } catch (err) {
    // 알림창은 삭제하고 개발자 도구 콘솔에만 기록
    console.error('수정 중 에러 발생 (무시하고 진행):', err.response?.data)
    // 에러가 나도 일단 페이지는 이동시킴
    router.push({ name: 'profile', params: { username: store.username } })
  }
}

onMounted(() => { if (store.token) fetchCurrentInfo() })
</script>

<template>
  <div class="edit-container py-5">
    <div class="edit-card shadow-lg mx-auto border-0">
      <h2 class="fw-bold text-center mb-5">✏️ 프로필 수정</h2>
      <form @submit.prevent="updateProfile">
        <div class="text-center mb-5">
          <div class="avatar-edit-wrapper mx-auto" @click="triggerFileInput">
            <div class="hover-overlay"><span>📷</span></div>
            <img v-if="imagePreview" :src="imagePreview" class="profile-img">
            <div v-else class="no-image">{{ store.username?.charAt(0).toUpperCase() }}</div>
            <input type="file" ref="fileInput" class="d-none" @change="onFileChange" accept="image/*">
          </div>
          <p class="text-muted small mt-2">사진을 클릭해서 변경해봐!</p>
        </div>

        <div class="form-body">
          <div class="form-group"><label>닉네임</label><input type="text" v-model="editForm.nickname" class="custom-input"></div>
          <div class="form-group"><label>이메일</label><input type="email" v-model="editForm.email" class="custom-input"></div>
          <div class="form-group"><label>한 줄 소개</label><textarea v-model="editForm.description" class="custom-input" rows="2"></textarea></div>
          <div class="form-group"><label>휴대폰 번호</label><input type="text" v-model="editForm.phone_number" class="custom-input"></div>
          <div class="form-group"><label>나이</label><input type="number" v-model.number="editForm.age" class="custom-input"></div>
          <div class="form-group"><label>자산 (만원)</label><input type="number" v-model.number="editForm.money" class="custom-input"></div>
          <div class="form-group"><label>연봉 (만원)</label><input type="number" v-model.number="editForm.salary" class="custom-input"></div>
        </div>

        <div class="button-group mt-5">
          <button type="submit" class="btn-save shadow-sm">저장하기</button>
          <button type="button" class="btn-cancel" @click="router.back()">취소</button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.edit-container { background-color: #f4f7f6; min-height: 100vh; font-family: 'Pretendard', sans-serif; }
.edit-card { background: white; border-radius: 30px; max-width: 500px; padding: 50px 40px; }
.avatar-edit-wrapper { width: 120px; height: 120px; border-radius: 50%; background: #42b983; overflow: hidden; position: relative; cursor: pointer; border: 4px solid #fff; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
.profile-img { width: 100%; height: 100%; object-fit: cover; }
.no-image { font-size: 3rem; color: white; line-height: 120px; font-weight: 800; text-align: center; }
.hover-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; opacity: 0; transition: 0.3s; z-index: 2; }
.avatar-edit-wrapper:hover .hover-overlay { opacity: 1; }
.form-body { display: flex; flex-direction: column; gap: 20px; }
.form-group { display: flex; flex-direction: column; gap: 8px; }
.form-group label { font-weight: 700; color: #4a5568; font-size: 0.85rem; }
.custom-input { border-radius: 12px; border: 2px solid #edf2f7; background: #f8fafc; padding: 12px; font-size: 1rem; }
.custom-input:focus { border-color: #42b983; background: white; outline: none; }
.button-group { display: flex; flex-direction: column; gap: 12px; }
.btn-save { background: #42b983; color: white; border: none; padding: 16px; border-radius: 15px; font-weight: 800; }
.btn-cancel { background: #edf2f7; color: #718096; border: none; padding: 14px; border-radius: 15px; }
</style>
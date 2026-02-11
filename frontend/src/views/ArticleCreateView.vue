<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const store = useAuthStore()
const router = useRouter()

const title = ref('')
const content = ref('')
const imageFile = ref(null) // ★ 이미지를 담을 변수 추가

// 파일이 선택되었을 때 실행되는 함수
const onFileChange = (event) => {
  imageFile.value = event.target.files[0] // 선택한 파일을 변수에 쏙!
}

const createArticle = async () => {
  if (!title.value.trim() || !content.value.trim()) {
    alert('제목과 내용을 모두 채워줘! 빈 칸이 있으면 글을 올릴 수 없어 😅')
    return
  }

  // ★ 중요: 이미지를 보낼 때는 FormData라는 큰 바구니를 만들어야 해!
  const formData = new FormData()
  formData.append('title', title.value)
  formData.append('content', content.value)
  
  // 이미지가 선택되었다면 바구니에 추가해줘
  if (imageFile.value) {
    formData.append('image', imageFile.value) 
  }

  try {
    await axios.post('http://127.0.0.1:8000/articles/articles/', 
      formData, // JSON 대신 바구니(FormData)를 보내!
      { 
        headers: { 
          Authorization: `Token ${store.token}`,
          // 파일을 보낼 때는 이 형식이 필수야!
          'Content-Type': 'multipart/form-data'
        } 
      }
    )
    alert('작성 완료! 멋진 사진과 함께 글이 올라갔어 😎')
    router.push({ name: 'articles' }) 
  } catch (err) {
    console.error(err)
    if (err.response?.status === 401) {
      alert('로그인이 풀린 것 같아. 다시 로그인해주겠니? 🔐')
    } else {
      alert('글을 올리는 중에 오류가 났어. 이미지 용량이 너무 큰 건 아닌지 확인해봐!')
    }
  }
}
</script>

<template>
  <div class="create-page py-5">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-lg-7 col-md-10">
          
          <div class="text-center mb-4">
            <h2 class="fw-bold title-text">🖊️ 커뮤니티에 글 남기기</h2>
            <p class="text-secondary">사진과 함께 자유롭게 생각을 나눠봐요!</p>
          </div>
          
          <div class="card form-card shadow-lg border-0">
            <div class="card-body p-4 p-md-5">
              
              <div class="mb-4">
                <label class="form-label fw-bold">제목</label>
                <input 
                  v-model="title" 
                  type="text"
                  class="form-control custom-input" 
                  placeholder="제목은 30자 이내가 좋아요."
                >
              </div>

              <div class="mb-4">
                <label class="form-label fw-bold">이미지 첨부 (캡처 이미지 등)</label>
                <input 
                  type="file" 
                  class="form-control custom-input" 
                  accept="image/*"
                  @change="onFileChange"
                >
                <small class="text-muted mt-1 d-block">💡 사진이나 화면 캡처 파일을 올려보세요.</small>
              </div>
              
              <div class="mb-4">
                <label class="form-label fw-bold">내용</label>
                <textarea 
                  v-model="content" 
                  class="form-control custom-textarea" 
                  rows="10" 
                  placeholder="내용을 적어주세요."
                ></textarea>
                <div class="text-end mt-2">
                  <span class="char-count text-muted">{{ content.length }}자 작성 중...</span>
                </div>
              </div>

              <div class="d-flex gap-3">
                <button @click="router.go(-1)" class="btn btn-light-custom flex-grow-1">취소</button>
                <button @click="createArticle" class="btn btn-submit flex-grow-1 fw-bold">글 올리기 🚀</button>
              </div>

            </div>
          </div>

          <div class="mt-4 p-3 tips-box text-center">
            <small class="text-muted">💡 따뜻한 말 한마디가 우리 커뮤니티를 더 즐겁게 만들어요!</small>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 기존 스타일 그대로 유지했어! */
.create-page { background-color: #f8f9fa; min-height: 100vh; font-family: 'Pretendard', sans-serif; }
.title-text { color: #2c3e50; letter-spacing: -1px; }
.form-card { border-radius: 25px; background: white; }
.custom-input, .custom-textarea {
  border: 2px solid #edf2f7; border-radius: 12px; padding: 12px 15px;
  background-color: #f8f9fa; transition: all 0.2s;
}
.custom-input:focus, .custom-textarea:focus {
  background-color: white; border-color: #42b983;
  box-shadow: 0 0 0 4px rgba(66, 185, 131, 0.1); outline: none;
}
.btn-submit {
  background: linear-gradient(135deg, #42b983 0%, #34a873 100%);
  color: white; border: none; border-radius: 12px; padding: 15px;
  transition: transform 0.2s, box-shadow 0.2s;
}
.btn-submit:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(52, 168, 115, 0.3); color: white; }
.btn-light-custom { background: #f1f3f5; border: none; border-radius: 12px; color: #495057; padding: 15px; }
.char-count { font-size: 0.85rem; }
.tips-box { background: rgba(0, 0, 0, 0.03); border-radius: 15px; }
</style>
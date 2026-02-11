<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const store = useAuthStore()
const route = useRoute()
const router = useRouter()

const title = ref('')
const content = ref('')
const existingImage = ref('') // ★ 기존 이미지를 보여주기 위한 변수
const imageFile = ref(null)   // ★ 새로 선택한 이미지 파일을 담을 변수
const articleId = route.params.id

// 1. 기존 내용 불러오기
const fetchArticle = async () => {
  try {
    const res = await axios.get(`http://127.0.0.1:8000/articles/articles/${articleId}/`)
    title.value = res.data.title
    content.value = res.data.content
    existingImage.value = res.data.image // ★ 기존 이미지 경로 저장
  } catch (err) {
    alert('글을 불러오지 못했어 😥')
    router.back()
  }
}

// 2. 파일 선택 시 실행되는 함수 (★ 추가)
const onFileChange = (event) => {
  imageFile.value = event.target.files[0]
}

// 3. 수정 내용 저장하기 (FormData 사용)
const updateArticle = async () => {
  if (!title.value.trim() || !content.value.trim()) {
    alert('제목과 내용을 모두 채워줘!')
    return
  }

  // ★ 중요: 이미지 파일을 보낼 때는 FormData 바구니를 써야 해!
  const formData = new FormData()
  formData.append('title', title.value)
  formData.append('content', content.value)
  
  // 새 이미지를 선택했다면 바구니에 추가!
  if (imageFile.value) {
    formData.append('image', imageFile.value)
  }

  try {
    await axios.put(`http://127.0.0.1:8000/articles/articles/${articleId}/`, 
      formData, 
      { 
        headers: { 
          Authorization: `Token ${store.token}`,
          // ★ 파일 보낼 때 꼭 필요한 설정
          'Content-Type': 'multipart/form-data' 
        } 
      }
    )
    alert('수정 완료! 멋진 글로 다시 태어났어 ✨')
    router.push({ name: 'article-detail', params: { id: articleId } })
  } catch (err) {
    alert('수정 실패! 본인의 글이 맞는지 다시 한번 확인해줘.')
  }
}

onMounted(fetchArticle)
</script>

<template>
  <div class="update-page py-5">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-lg-7 col-md-10">
          
          <div class="text-center mb-4">
            <h2 class="fw-bold title-text">✏️ 게시글 수정하기</h2>
            <p class="text-secondary">기존의 생각을 더 멋지게 다듬어보세요.</p>
          </div>

          <div class="card update-card shadow-lg border-0">
            <div class="card-body p-4 p-md-5">
              
              <div class="mb-4">
                <label class="form-label fw-bold">제목 수정</label>
                <input v-model="title" type="text" class="form-control custom-input">
              </div>

              <div class="mb-4">
                <label class="form-label fw-bold">이미지 변경</label>
                
                <div v-if="existingImage && !imageFile" class="mb-2">
                  <p class="small text-muted mb-1">현재 등록된 사진:</p>
                  <img :src="`http://127.0.0.1:8000${existingImage}`" class="img-preview rounded shadow-sm">
                </div>

                <input type="file" @change="onFileChange" class="form-control custom-input" accept="image/*">
                <small class="text-muted mt-1 d-block">💡 새로운 사진을 선택하면 기존 사진이 교체돼요.</small>
              </div>
              
              <div class="mb-4">
                <label class="form-label fw-bold">내용 수정</label>
                <textarea v-model="content" class="form-control custom-textarea" rows="10"></textarea>
                <div class="text-end mt-2">
                  <span class="text-muted small">수정 중인 글자 수: {{ content.length }}자</span>
                </div>
              </div>

              <div class="d-flex gap-3">
                <button @click="router.go(-1)" class="btn btn-cancel flex-grow-1">취소</button>
                <button @click="updateArticle" class="btn btn-update flex-grow-1 fw-bold">수정 완료 🚀</button>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 기존 스타일 그대로 유지하면서 미리보기 스타일만 추가했어 */
.update-page { background-color: #f0f4f8; min-height: 100vh; font-family: 'Pretendard', sans-serif; }
.title-text { color: #2c3e50; letter-spacing: -1px; }
.update-card { border-radius: 24px; background-color: #ffffff; }
.custom-input, .custom-textarea {
  border: 2px solid #e9ecef; border-radius: 12px; padding: 14px 18px;
  background-color: #f8f9fa; font-size: 1rem; transition: all 0.2s ease;
}
.custom-input:focus, .custom-textarea:focus {
  background-color: #ffffff; border-color: #339af0; outline: none;
  box-shadow: 0 0 0 4px rgba(51, 154, 240, 0.1);
}

/* ★ 추가된 미리보기 스타일 */
.img-preview {
  max-width: 200px;
  max-height: 150px;
  object-fit: cover;
}

.btn-update {
  background: linear-gradient(135deg, #339af0 0%, #228be6 100%);
  color: white; border: none; border-radius: 12px; padding: 16px;
  font-size: 1.05rem; transition: transform 0.2s, box-shadow 0.2s;
}
.btn-update:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(34, 139, 230, 0.3); color: white; }
.btn-cancel { background-color: #e9ecef; border: none; border-radius: 12px; color: #495057; padding: 16px; font-weight: 600; }
</style>
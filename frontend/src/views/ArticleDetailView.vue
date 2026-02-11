<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const store = useAuthStore()
const route = useRoute()
const router = useRouter()

const article = ref(null)
const commentContent = ref('') 

// --- [추가] 댓글 수정 관련 상태 변수 ---
const editingCommentId = ref(null) // 현재 수정 중인 댓글의 ID
const editingContent = ref('')    // 수정 중인 내용

// 1. 게시글 및 댓글 가져오기
const fetchArticle = async () => {
  try {
    const articleId = route.params.id
    const res = await axios.get(`http://127.0.0.1:8000/articles/articles/${articleId}/`)
    article.value = res.data
  } catch (err) {
    alert('게시글을 찾을 수 없어 ㅠㅠ')
    router.push({ name: 'articles' }) 
  }
}

// 2. 게시글 수정/삭제 로직 (기존 유지)
const goUpdate = () => router.push({ name: 'article-update', params: { id: route.params.id } })
const deleteArticle = async () => {
  if (!confirm('정말 삭제할까? 🗑️')) return
  try {
    await axios.delete(`http://127.0.0.1:8000/articles/articles/${route.params.id}/`, {
      headers: { Authorization: `Token ${store.token}` }
    })
    router.push({ name: 'articles' }) 
  } catch (err) { alert('권한이 없어!') }
}

// 3. 댓글 작성
const createComment = async () => {
  if (!commentContent.value.trim()) return alert('내용을 입력해!')
  try {
    await axios.post(`http://127.0.0.1:8000/articles/articles/${route.params.id}/comments/`, 
      { content: commentContent.value },
      { headers: { Authorization: `Token ${store.token}` } }
    )
    commentContent.value = ''
    fetchArticle()
  } catch (err) { alert('로그인이 필요해!') }
}

// 4. [신규] 댓글 수정 시작하기
const startEdit = (comment) => {
  editingCommentId.value = comment.id
  editingContent.value = comment.content
}

// 5. [신규] 댓글 수정 취소
const cancelEdit = () => {
  editingCommentId.value = null
  editingContent.value = ''
}

// 6. [신규] 댓글 수정 저장 (Backend PUT 요청)
const updateComment = async (commentId) => {
  if (!editingContent.value.trim()) return alert('내용을 입력해!')
  try {
    await axios.put(`http://127.0.0.1:8000/articles/comments/${commentId}/`, 
      { content: editingContent.value },
      { headers: { Authorization: `Token ${store.token}` } }
    )
    editingCommentId.value = null // 수정 모드 종료
    fetchArticle() // 목록 새로고침
  } catch (err) { alert('수정 권한이 없거나 오류가 발생했어!') }
}

// 7. 댓글 삭제
const deleteComment = async (commentId) => {
  if(!confirm('댓글을 삭제할까?')) return
  try {
    await axios.delete(`http://127.0.0.1:8000/articles/comments/${commentId}/`, {
      headers: { Authorization: `Token ${store.token}` }
    })
    fetchArticle()
  } catch (err) { alert('본인 댓글만 삭제 가능해!') }
}

onMounted(() => { fetchArticle() })
</script>

<template>
  <div class="board-container py-5" v-if="article">
    <div class="container content-wrapper">
      
      <nav class="d-flex justify-content-between align-items-center mb-4">
        <button @click="router.push({ name: 'articles' })" class="btn-back">⬅️ 목록으로</button>
        <div v-if="store.username === article.user" class="d-flex gap-2">
          <button @click="goUpdate" class="btn-edit-main">✏️ 수정하기</button>
          <button @click="deleteArticle" class="btn-delete-main">🗑️ 삭제하기</button>
        </div>
      </nav>

      <article class="detail-card shadow-sm mb-5">
        <header class="card-header">
          <div class="badge-custom mb-3">ARTICLE 🗒️</div>
          <h1 class="display-6 fw-bold text-dark">{{ article.title }}</h1>
          <div class="meta-info d-flex gap-3 text-muted small mt-3">
            <span>👤 <strong>{{ article.nickname || article.user }}</strong></span>
            <span>📅 {{ new Date(article.created_at).toLocaleString() }}</span>
          </div>
        </header>
        <div class="card-body p-4 p-md-5">
          <div v-if="article.image" class="article-image-wrapper mb-4 text-center">
            <img :src="`http://127.0.0.1:8000${article.image}`" class="img-fluid rounded-3 shadow-sm">
          </div>
          <div class="content-text">{{ article.content }}</div>
        </div>
      </article>

      <section class="comment-section mt-5 pb-5">
        <h3 class="fw-bold mb-4">💬 댓글 ({{ article.comments?.length || 0 }})</h3>

        <div class="comment-list mb-4">
          <div v-for="comment in article.comments" :key="comment.id" class="mb-3">
            <div class="comment-bubble p-3 shadow-sm border bg-white rounded-4">
              
              <div v-if="editingCommentId !== comment.id">
                <div class="d-flex justify-content-between align-items-center mb-1">
                  <span class="fw-bold text-primary">👤 {{ comment.nickname || comment.user }}</span>
                  <div v-if="store.username === comment.user" class="d-flex gap-2">
                    <button @click="startEdit(comment)" class="btn-action-small">수정</button>
                    <button @click="deleteComment(comment.id)" class="btn-action-small text-danger">삭제</button>
                  </div>
                </div>
                <p class="m-0 text-dark" style="white-space: pre-line;">{{ comment.content }}</p>
                <div class="text-muted mt-2" style="font-size: 0.7rem;">{{ new Date(comment.created_at).toLocaleString() }}</div>
              </div>

              <div v-else>
                <textarea v-model="editingContent" class="form-control border-0 mb-2 p-0" rows="2"></textarea>
                <div class="d-flex justify-content-end gap-2">
                  <button @click="cancelEdit" class="btn btn-sm btn-light rounded-pill">취소</button>
                  <button @click="updateComment(comment.id)" class="btn btn-sm btn-success rounded-pill px-3">저장</button>
                </div>
              </div>

            </div>
          </div>
        </div>

        <div class="comment-form bg-white p-4 rounded-4 shadow-sm border" v-if="store.token">
          <textarea v-model="commentContent" class="form-control border-0 mb-2 no-focus" rows="3" placeholder="따뜻한 댓글을 남겨주세요!"></textarea>
          <div class="d-flex justify-content-end">
            <button @click="createComment" class="btn-submit">댓글 등록</button>
          </div>
        </div>
      </section>

    </div>
  </div>
</template>

<style scoped>
.board-container { background-color: #f8f9fa; min-height: 90vh; }
.content-wrapper { max-width: 850px; }
.btn-back { background: none; border: none; color: #888; font-weight: bold; cursor: pointer; }
.btn-edit-main { background-color: #e6fcf5; color: #0ca678; border: 1px solid #96f2d7; padding: 6px 18px; border-radius: 50px; font-weight: bold; }
.btn-delete-main { background-color: #fff5f5; color: #ff6b6b; border: 1px solid #ffc9c9; padding: 6px 18px; border-radius: 50px; font-weight: bold; }
.detail-card { background: white; border-radius: 25px; overflow: hidden; border: none; }
.card-header { padding: 45px 45px 0; background: white; }
.content-text { font-size: 1.15rem; line-height: 1.9; color: #333; white-space: pre-line; }

/* 댓글 버튼 스타일 */
.btn-action-small { background: none; border: none; color: #adb5bd; font-size: 0.8rem; cursor: pointer; }
.btn-action-small:hover { text-decoration: underline; color: #495057; }
.text-danger:hover { color: #fa5252 !important; }

.btn-submit { background: #2c3e50; color: white; border-radius: 50px; padding: 10px 30px; border: none; font-weight: bold; }
.btn-submit:hover { background: #42b983; }
.no-focus:focus { box-shadow: none; outline: none; }
</style>
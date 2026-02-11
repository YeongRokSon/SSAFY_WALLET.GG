<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import axios from 'axios'

const store = useAuthStore()
const router = useRouter()
const articles = ref([])
const isLoading = ref(false)

const fetchArticles = async () => {
  isLoading.value = true
  try {
    const res = await axios.get('http://127.0.0.1:8000/articles/articles/')
    articles.value = res.data
  } catch (err) {
    console.error(err)
  } finally {
    isLoading.value = false
  }
}

const goDetail = (id) => {
  router.push({ name: 'article-detail', params: { id } })
}

const goCreate = () => {
  router.push({ name: 'article-create' })
}

onMounted(() => {
  fetchArticles()
})
</script>

<template>
  <div class="board-container py-5">
    <div class="header-section text-center mb-5">
      <span class="badge-custom">COMMUNITY 📢</span>
      <h1 class="fw-bold mt-2">자유 게시판</h1>
      <p class="text-muted">사용자들과 자유롭게 금융 지식을 나누어 보세요.</p>
    </div>

    <div class="container content-wrapper">
      <div class="d-flex justify-content-end mb-4">
        <button v-if="store.token" @click="goCreate" class="btn-create shadow-sm">
          ✏️ 새로운 글 작성하기
        </button>
      </div>

      <div v-if="isLoading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
        <p class="mt-3 text-muted">게시글을 불러오고 있어요...</p>
      </div>

      <div v-else-if="articles.length === 0" class="empty-state card shadow-sm text-center py-5 border-0">
        <div class="fs-1 mb-3">📭</div>
        <p class="text-muted">아직 등록된 게시글이 없어요.<br>첫 번째 주인공이 되어보세요!</p>
      </div>

      <div v-else class="row g-4">
        <div class="col-12" v-for="article in articles" :key="article.id">
          <div class="article-card shadow-sm" @click="goDetail(article.id)">
            <div class="card-body p-4">
              <div class="d-flex gap-4 align-items-center">
                
                <div class="flex-grow-1">
                  <div class="d-flex justify-content-between align-items-start mb-2">
                    <div class="title-group">
                      <h3 class="article-title">{{ article.title }}</h3>
                      <div class="author-info text-muted small mt-1">
                        <span class="nickname">👤 {{ article.nickname || article.user }}</span>
                        <span class="divider">|</span>
                        <span class="date">{{ new Date(article.created_at).toLocaleDateString() }}</span>
                      </div>
                    </div>
                  </div>
                  
                  <p class="article-preview text-secondary mb-3">
                    {{ article.content?.length > 100 ? article.content.substring(0, 100) + '...' : article.content }}
                  </p>

                  <div class="comment-badge d-inline-block">
                    <span>💬 댓글 {{ article.comments?.length || 0 }}</span>
                  </div>
                </div>

                <div v-if="article.image" class="thumbnail-wrapper">
                  <img 
                    :src="`http://127.0.0.1:8000${article.image}`" 
                    alt="미리보기" 
                    class="article-thumbnail"
                  >
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 배경과 컨테이너 */
.board-container {
  background-color: #f8f9fa;
  min-height: 90vh;
}

.content-wrapper {
  max-width: 900px;
}

/* 상단 헤더 디자인 (AI 분석결과 페이지 스타일 참고) */
.badge-custom {
  background: #e7f5ff;
  color: #1971c2;
  padding: 6px 16px;
  border-radius: 20px;
  font-weight: bold;
  font-size: 0.85rem;
  display: inline-block;
}

.header-section h1 {
  font-size: 2.5rem;
  color: #2c3e50;
}

/* 글쓰기 버튼 (AI 버튼 스타일 참고) */
.btn-create {
  background: linear-gradient(135deg, #42b983 0%, #2c3e50 100%);
  color: white;
  border: none;
  padding: 12px 25px;
  border-radius: 50px;
  font-weight: bold;
  transition: transform 0.2s, box-shadow 0.2s;
}

.btn-create:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.2) !important;
}

/* 게시글 카드 디자인 (AnalysisResultView 카드 스타일 참고) */
.article-card {
  background: white;
  border-radius: 20px;
  border: 1px solid #f0f0f0;
  cursor: pointer;
  transition: all 0.3s ease;
}

.article-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.08) !important;
  border-color: #42b983;
}

.article-title {
  font-size: 1.3rem;
  font-weight: 700;
  color: #333;
  margin: 0;
}

.author-info .divider {
  margin: 0 8px;
  color: #ddd;
}

.comment-badge {
  background: #f1f3f5;
  padding: 5px 12px;
  border-radius: 12px;
  font-size: 0.9rem;
  color: #495057;
  font-weight: 600;
}

.article-preview {
  line-height: 1.6;
  font-size: 1rem;
  word-break: break-all;
}

.empty-state {
  border-radius: 20px;
}

/* 애니메이션 */
.row {
  animation: fadeInUp 0.5s ease-out;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.article-card {
  background: white;
  border-radius: 20px;
  border: 1px solid #f0f0f0;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden; /* 사진이 삐져나가지 않게 */
}

/* ★ 추가된 썸네일 스타일 */
.thumbnail-wrapper {
  width: 120px;
  height: 120px;
  flex-shrink: 0; /* 사진 크기가 고정되도록 */
}

.article-thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover; /* 사진 비율을 유지하면서 꽉 채우기 */
  border-radius: 15px;
  border: 1px solid #eee;
}

.article-preview {
  display: -webkit-box;
  -webkit-line-clamp: 2; /* 두 줄까지만 보여주기 */
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.6;
}

/* 기존 스타일들 (이미 있는 것들) */
.board-container { background-color: #f8f9fa; min-height: 90vh; }
.content-wrapper { max-width: 900px; }
.badge-custom { background: #e7f5ff; color: #1971c2; padding: 6px 16px; border-radius: 20px; font-weight: bold; font-size: 0.85rem; display: inline-block; }
.btn-create { background: linear-gradient(135deg, #42b983 0%, #2c3e50 100%); color: white; border: none; padding: 12px 25px; border-radius: 50px; font-weight: bold; }
.article-title { font-size: 1.2rem; font-weight: 700; color: #333; }
.comment-badge { background: #f1f3f5; padding: 4px 10px; border-radius: 10px; font-size: 0.85rem; color: #495057; }
</style>

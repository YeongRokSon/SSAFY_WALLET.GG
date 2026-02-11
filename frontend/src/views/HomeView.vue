<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useFinanceStore } from '@/stores/finance'
import axios from 'axios'

const router = useRouter()
const authStore = useAuthStore()
const financeStore = useFinanceStore()

const myPortfolio = ref(null)
const isLoading = ref(false)

onMounted(async () => {
  if (authStore.token) {
    isLoading.value = true
    try {
      const res = await axios.get('http://127.0.0.1:8000/api/products/portfolio/latest/', {
        headers: { Authorization: `Token ${authStore.token}` }
      })
      if (res.data.exists) {
        myPortfolio.value = res.data
      }
    } catch (err) {
      console.error("기록 불러오기 실패:", err)
    } finally {
      isLoading.value = false
    }
  }
})

const startNewAnalysis = () => router.push({ name: 'asset-input' })
const goRecommendDirectly = () => {
  if (!myPortfolio.value) return
  financeStore.userInfo = myPortfolio.value.user_info
  financeStore.analysisResult = myPortfolio.value.analysis_result
  router.push({ name: 'product-recommend' })
}
</script>

<template>
  <div class="home-wrapper">
    <section class="hero-section text-center py-5">
      <div class="container fade-in">
        <div class="emoji-main mb-3">💰</div>
        <h1 class="display-4 fw-bold mb-3">똑똑한 자산 관리의 시작</h1>
        <p class="lead text-secondary mb-5">
          AI 비서가 당신의 데이터를 분석하여<br>
          최적의 금융 포트폴리오를 제안합니다.
        </p>
        
        <div class="d-flex justify-content-center gap-3">
          <button @click="startNewAnalysis" class="btn-main-start shadow">
            ✨ AI 분석 시작하기
          </button>
          <button v-if="!authStore.token" @click="router.push({ name: 'auth' })" class="btn btn-outline-dark btn-lg px-4 rounded-pill">
            로그인 / 회원가입
          </button>
        </div>
      </div>
    </section>

    <section v-if="authStore.token && myPortfolio" class="recent-record-section py-5 bg-light">
      <div class="container">
        <div class="record-card p-4 shadow-sm bg-white d-flex justify-content-between align-items-center">
          <div>
            <h4 class="fw-bold m-0">최근 분석 결과: <span class="text-primary">{{ myPortfolio.analysis_result.type }}</span></h4>
            <p class="text-muted m-0 small">{{ new Date(myPortfolio.created_at || Date.now()).toLocaleDateString() }} 분석됨</p>
          </div>
          <div class="btn-group gap-2">
            <button @click="goRecommendDirectly" class="btn btn-sm btn-success fw-bold">추천 상품 보기</button>
          </div>
        </div>
      </div>
    </section>

    <section class="features-section py-5">
      <div class="container">
        <div class="row g-4 text-center">
          <div class="col-md-4">
            <div class="feature-item p-4">
              <div class="fs-1 mb-3">🏦</div>
              <h5 class="fw-bold">최신 금리 비교</h5>
              <p class="text-muted small">금융감독원 데이터를 기반으로 가장 높은 금리를 찾아드려요.</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-item p-4">
              <div class="fs-1 mb-3">🤖</div>
              <h5 class="fw-bold">AI 맞춤 추천</h5>
              <p class="text-muted small">당신의 투자 성향을 완벽하게 분석하는 금융 인공지능.</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-item p-4">
              <div class="fs-1 mb-3">📊</div>
              <h5 class="fw-bold">포트폴리오 관리</h5>
              <p class="text-muted small">복잡한 자산 현황을 한눈에 보기 쉽게 정리해 드립니다.</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.hero-section { background: white; min-height: 60vh; display: flex; align-items: center; }
.emoji-main { font-size: 5rem; }

/* AI 버튼 스타일 계승 */
.btn-main-start {
  background: linear-gradient(135deg, #00c6ff 0%, #0072ff 100%);
  color: white; border: none; padding: 15px 40px; border-radius: 50px;
  font-size: 1.2rem; font-weight: bold; transition: transform 0.2s;
}
.btn-main-start:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0, 114, 255, 0.3); }

/* 레코드 카드 스타일 */
.record-card { border-radius: 20px; border: 1px solid #eee; }

.feature-item { transition: transform 0.3s; }
.feature-item:hover { transform: translateY(-10px); }

.fade-in { animation: fadeIn 0.8s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>
<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useFinanceStore } from '@/stores/finance'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'
import ProductDetail from '@/components/ProductDetail.vue'

const router = useRouter()
const store = useFinanceStore()
const authStore = useAuthStore()

const recommendations = ref([])
const isLoading = ref(true)
const selectedProduct = ref(null)
const myLikedIds = ref([]) // 찜한 목록 상태 관리

// 1. 내 상태 로드 (하트 색깔용)
const fetchMyStatus = async () => {
    if (!authStore.token) return
    try {
        const headers = { Authorization: `Token ${authStore.token}` }
        const res = await axios.get('http://127.0.0.1:8000/api/products/liked-list/', { headers })
        myLikedIds.value = res.data.map(p => p.id || p.fin_prdt_cd)
    } catch (err) { console.error(err) }
}

// 2. 추천 데이터 가져오기
const fetchRecommendations = async () => {
    try {
        const res = await axios.post(
            'http://127.0.0.1:8000/api/products/ai-recommend/', 
            { user_info: store.userInfo, analysis_result: store.analysisResult },
            { headers: { Authorization: `Token ${authStore.token}` } }
        )
        recommendations.value = res.data.recommendations || res.data
    } catch (e) { alert("추천 실패!") }
    finally { isLoading.value = false }
}

// 3. 기능 함수들
const openDetail = async (item) => {
    const productId = item.id || item.fin_prdt_cd
    try {
        const res = await axios.get(`http://127.0.0.1:8000/api/products/${productId}/`, {
            headers: { Authorization: `Token ${authStore.token}` }
        })
        selectedProduct.value = { ...res.data, reason: item.reason } 
    } catch (e) { alert("상세 정보 로드 실패") }
}

const toggleLike = async (product, event) => {
    event.stopPropagation()
    const productId = product.id || product.fin_prdt_cd
    try {
        const res = await axios.post(`http://127.0.0.1:8000/api/products/${productId}/like/`, {}, {
            headers: { Authorization: `Token ${authStore.token}` }
        })
        if (res.data.is_liked) myLikedIds.value.push(productId)
        else myLikedIds.value = myLikedIds.value.filter(id => id !== productId)
    } catch (err) { alert('찜하기 실패') }
}

// 이동 함수 3종 세트
const goHome = () => router.push({ name: 'home' })
const goProductList = () => router.push({ name: 'products' })
const goProfile = () => {
    const username = authStore.username || localStorage.getItem('username')
    router.push({ name: 'profile', params: { username: username } })
}

onMounted(() => {
    fetchMyStatus()
    fetchRecommendations()
})
</script>

<template>
  <div class="liked-container py-5">
    <div class="container">
      <ProductDetail v-if="selectedProduct" :product="selectedProduct" @close="selectedProduct = null" />

      <div class="title-section text-center mb-5">
        <h1 class="fw-bold">💎 WALLET.GG 프리미엄 추천</h1>
        <p class="text-muted mt-2">당신만을 위한 최적의 금융 포트폴리오가 완성되었습니다.</p>
      </div>

      <div v-if="isLoading" class="text-center py-5">
        <div class="spinner">🪄</div>
        <p>AI가 보물을 찾는 중...</p>
      </div>

      <div v-else class="row g-4 justify-content-center">
        <div v-for="(item, idx) in recommendations" :key="idx" class="col-md-4">
          <div class="card h-100 product-item shadow-sm" @click="openDetail(item)">
            <div class="card-body p-4 position-relative">
              <button class="like-btn" @click="toggleLike(item, $event)">
                <span>{{ myLikedIds.includes(item.id || item.fin_prdt_cd) ? '❤️' : '🤍' }}</span>
              </button>
              <div class="badge-custom mb-3">BEST {{ idx + 1 }}</div>
              <h4 class="fw-bold text-dark mb-1">{{ item.fin_prdt_nm || item.name }}</h4>
              <p class="text-success small">{{ item.kor_co_nm || item.bank }}</p>
              <hr>
              <p class="card-text small text-secondary">{{ item.reason }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="button-section text-center mt-5 pt-5">
        <div class="d-flex justify-content-center gap-4 flex-wrap">
          <button @click="goHome" class="btn-luxury btn-home">홈으로</button>
          <button @click="goProductList" class="btn-luxury btn-list">다른 상품 보기</button>
          <button @click="goProfile" class="btn-luxury btn-profile">내 프로필 👤</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.liked-container { background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%); min-height: 100vh; }

/* 카드 스타일 */
.product-item {
  border: none; border-radius: 24px; cursor: pointer;
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
  background: rgba(255, 255, 255, 0.9);
}
.product-item:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(0,0,0,0.08) !important;
}

/* 버튼 섹션 */
.button-section { border-top: 1px solid #e2e8f0; width: 100%; }

/* 럭셔리 버튼 스타일 */
.btn-luxury {
  border: none; padding: 16px 45px; border-radius: 16px;
  font-weight: 800; font-size: 1rem; transition: all 0.3s;
  color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

.btn-home { background: #64748b; } /* 차분한 그레이 */
.btn-list { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); } /* 선명한 블루 */
.btn-profile { background: linear-gradient(135deg, #10b981 0%, #059669 100%); } /* 산뜻한 그린 */

.btn-luxury:hover {
  transform: translateY(-3px) scale(1.03);
  filter: brightness(1.1);
  box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}

.like-btn { position: absolute; top: 20px; right: 20px; background: none; border: none; font-size: 1.6rem; z-index: 5; }
.badge-custom { display: inline-block; padding: 6px 14px; background: #f1f5f9; color: #475569; border-radius: 10px; font-weight: 800; font-size: 0.75rem; border: 1px solid #e2e8f0; }

.spinner { font-size: 3.5rem; animation: bounce 1s infinite alternate; }
@keyframes bounce { from { transform: translateY(0); } to { transform: translateY(-15px); } }
</style>
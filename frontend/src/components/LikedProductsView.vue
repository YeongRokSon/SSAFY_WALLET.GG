<template>
  <div class="liked-container py-5">
    <div class="container">
      
      <!-- 상세 모달 -->
      <ProductDetail 
        v-if="selectedProduct" 
        :product="selectedProduct" 
        @close="selectedProduct = null" 
      />

      <div class="card shadow-lg border-0 rounded-lg overflow-hidden">
        <div class="card-header bg-white p-4 border-0">
          <h3 class="fw-bold mb-0">❤️ 내가 찜한 금융 상품</h3>
          <p class="text-muted mb-0">관심 있는 상품들을 한눈에 모아보세요.</p>
        </div>
        
        <div class="card-body p-4">
          <div v-if="likedProducts.length > 0" class="row">
            <div v-for="product in likedProducts" :key="product.id" class="col-md-6 mb-3">
              <div @click="openDetail(product)" class="product-item shadow-sm">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <div class="fw-bold fs-5 text-primary">{{ product.fin_prdt_nm }}</div>
                    <div class="text-muted small">{{ product.kor_co_nm }}</div>
                  </div>
                  <span class="badge rounded-pill">상세보기 ></span>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="text-center py-5 text-muted">
            <div class="fs-1 mb-3">📭</div>
            <p>아직 찜한 상품이 없어요!<br>나에게 맞는 상품을 먼저 찾아볼까요?</p>
            <button @click="router.push({name: 'products'})" class="btn btn-primary mt-2">상품 찾으러 가기</button>
          </div>
        </div>
      </div>
      
      <div class="text-center mt-4">
        <!-- 프로필로 돌아가기 버튼 -->
        <button @click="goProfile" class="btn btn-outline-secondary">내 프로필로 돌아가기</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'
import ProductDetail from '@/components/ProductDetail.vue' 

const store = useAuthStore()
const router = useRouter()
const likedProducts = ref([])
const selectedProduct = ref(null) 

const fetchLikedProducts = async () => {
  try {
    const headers = { Authorization: `Token ${store.token}` }
    const res = await axios.get('http://127.0.0.1:8000/api/products/liked-list/', { headers })
    likedProducts.value = res.data
  } catch (err) {
    console.error(err)
    // 500 에러는 DB 테이블 없음 문제일 수 있음 (이전 단계에서 해결됨)
  }
}

const openDetail = (product) => {
    selectedProduct.value = product
}

// [수정] 프로필 이동 함수 강화 (API 조회 추가)
const goProfile = async () => {
    // 1. 스토어 또는 로컬스토리지에서 1차 확인
    let username = store.user?.username || store.username || localStorage.getItem('username')
    
    // 2. 없으면 서버 API로 내 정보 다시 조회 (새로고침 대비)
    if (!username && store.token) {
        try {
            console.log("유저 정보 재조회 중...")
            const res = await axios.get('http://127.0.0.1:8000/accounts/user/', {
                headers: { Authorization: `Token ${store.token}` }
            })
            username = res.data.username
        } catch (e) {
            console.error("사용자 정보 조회 실패:", e)
        }
    }

    // 3. username이 확보되었으면 이동, 아니면 로그인 페이지로
    if (username) {
        router.push({ 
            name: 'profile', 
            params: { username: username } 
        })
    } else {
        alert("로그인 정보가 만료되었습니다. 다시 로그인해주세요.")
        router.push({ name: 'login' })
    }
}

onMounted(() => {
    if (!store.token) {
        alert('로그인이 필요합니다.')
        router.push({ name: 'login' })
        return
    }
    fetchLikedProducts()
})
</script>

<style scoped>
.liked-container { background-color: #f4f7f6; min-height: 100vh; }
.product-item {
  background: white; border-radius: 20px; padding: 25px; cursor: pointer;
  transition: all 0.2s; border: 1px solid #f1f3f5;
}
.product-item:hover {
  transform: translateY(-5px); border-color: #42b983; background-color: #f8fbf9;
}
.badge { background-color: #e7f5ff; color: #1971c2; padding: 8px 12px; }
</style>
<template>
  <div class="liked-container py-5">
    <div class="container">
      
      <!-- 상세 모달 (클릭 시에만 표시) -->
      <ProductDetail 
        v-if="selectedProduct" 
        :product="selectedProduct" 
        @close="selectedProduct = null" 
      />

      <div class="card shadow-lg border-0 rounded-lg overflow-hidden">
        <div class="card-header bg-white p-4 border-0">
          <h3 class="fw-bold mb-0">💼 내가 가입한 금융 상품</h3>
          <p class="text-muted mb-0">나의 자산 포트폴리오를 관리해보세요.</p>
        </div>
        
        <div class="card-body p-4">
          <div v-if="joinedProducts.length > 0" class="row">
            <div v-for="product in joinedProducts" :key="product.id" class="col-md-6 mb-3">
              <!-- 클릭 시 모달 열기 함수 호출 -->
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
            <p>아직 가입한 상품이 없어요!<br>나에게 맞는 상품을 찾아 가입해볼까요?</p>
            <button @click="router.push({name: 'products'})" class="btn btn-primary mt-2">상품 찾으러 가기</button>
          </div>
        </div>
      </div>
      
      <div class="text-center mt-4">
        <!-- [수정] goProfile 함수 호출 -->
        <button @click="goProfile" class="btn btn-outline-secondary">
          내 프로필로 돌아가기
        </button>
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
const joinedProducts = ref([])
const selectedProduct = ref(null) 

// 가입 상품 목록 가져오기
const fetchJoinedProducts = async () => {
  try {
    const headers = { Authorization: `Token ${store.token}` }
    const res = await axios.get('http://127.0.0.1:8000/api/products/joined-list/', { headers })
    joinedProducts.value = res.data
  } catch (err) {
    console.error(err)
    alert('가입 상품 목록을 불러오지 못했어요.')
  }
}

// 상세 정보 모달 열기
const openDetail = (product) => {
    selectedProduct.value = product
}

// [추가] 프로필 이동 함수 (username 파라미터 포함)
const goProfile = () => {
    // 스토어 또는 로컬스토리지에서 username 확인
    const username = store.user?.username || store.username || localStorage.getItem('username')
    
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
    fetchJoinedProducts()
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
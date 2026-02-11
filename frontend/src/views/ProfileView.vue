<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'
import YoutubeDetail from '@/components/YoutubeDetail.vue' 
import ProductDetail from '@/components/ProductDetail.vue' 
const store = useAuthStore()
const router = useRouter()

const userInfo = ref(null)
const joinedProducts = ref([])
const userPortfolio = ref(null) 
const likedProducts = ref([])
const bookmarkedVideos = ref([])
const isLoading = ref(false)
const selectedVideo = ref(null)
const fileInput = ref(null)
const selectedProduct = ref(null)

const formatNumber = (num) => num?.toLocaleString() || '0'
const getAnimalImage = (code) => code ? `/images/animals/${code}.png` : ''
const goAnalysis = () => router.push({ name: 'asset-input' })
const goProductDetail = (id) => router.push({ name: 'product-detail', params: { product_pk: id } })

// 데이터 가져오기
const fetchAllData = async () => {
  isLoading.value = true
  const headers = { Authorization: `Token ${store.token}` }
  try {
    const userRes = await axios.get(`http://127.0.0.1:8000/accounts/profile/${store.username}/`, { headers })
    userInfo.value = userRes.data

    // (2) 가입한 상품
    try {
        const joinRes = await axios.get('http://127.0.0.1:8000/api/products/joined-list/', { headers })
        joinedProducts.value = joinRes.data
    } catch(e) {}

    // (3) AI 분석 결과
    try {
        const portRes = await axios.get('http://127.0.0.1:8000/api/products/portfolio/latest/', { headers })
        if (portRes.data.exists) {
            // 백엔드에서 { animal, name, description, stats } 형태로 줌
            userPortfolio.value = portRes.data.analysis_result
        }
    } catch (e) {
        console.log("AI 분석 기록 없음")
    }

    // (4) 찜 & 북마크
    try {
        const likeRes = await axios.get('http://127.0.0.1:8000/api/products/liked-list/', { headers })
        likedProducts.value = likeRes.data
        const videoRes = await axios.get('http://127.0.0.1:8000/youtube/bookmark/list/', { headers })
        bookmarkedVideos.value = videoRes.data
    } catch(e) {}

    const [joinRes, portRes, likeRes, videoRes] = await Promise.allSettled([
        axios.get('http://127.0.0.1:8000/api/products/joined-list/', { headers }),
        axios.get('http://127.0.0.1:8000/api/products/portfolio/latest/', { headers }),
        axios.get('http://127.0.0.1:8000/api/products/liked-list/', { headers }),
        axios.get('http://127.0.0.1:8000/youtube/bookmark/list/', { headers })
    ])

    if (joinRes.status === 'fulfilled') joinedProducts.value = joinRes.value.data
    if (portRes.status === 'fulfilled' && portRes.value.data.exists) userPortfolio.value = portRes.value.data.analysis_result
    if (likeRes.status === 'fulfilled') likedProducts.value = likeRes.value.data
    if (videoRes.status === 'fulfilled') bookmarkedVideos.value = videoRes.value.data

  } catch (err) {
    console.error("데이터 로딩 중 에러 발생:", err)
  } finally {
    isLoading.value = false
  }
}

// [수정] 상세보기 열기 함수: 서버에서 금리 등 진짜 정보를 가져오도록 업그레이드!
const openDetail = async (product) => {
  try {
    // 상품 고유 번호(id)를 써서 백엔드에 상세 정보를 물어봐
    const res = await axios.get(`http://127.0.0.1:8000/api/products/${product.id}/`, {
      headers: { Authorization: `Token ${store.token}` }
    })
    // 서버가 보내준 진짜 꽉 찬 정보를 팝업창에 넣어줘!
    selectedProduct.value = res.data
  } catch (e) {
    alert("상세 정보를 가져오는 데 실패했어 ㅠㅠ")
  }
}

// 모달 닫을 때 다시 내 정보를 새로고침해서 찜 상태 등을 맞춤
const handleModalClose = () => {
    selectedProduct.value = null
    fetchAllData()
}

// [기타 함수들 유지]
const triggerFileInput = () => fileInput.value.click()
const handleImageUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  const formData = new FormData()
  formData.append('profile_img', file)
  try {
    await axios.put(`http://127.0.0.1:8000/accounts/profile/${store.username}/`, formData, {
      headers: { Authorization: `Token ${store.token}`, 'Content-Type': 'multipart/form-data' }
    })
    fetchAllData()
  } catch (err) { alert('업로드 실패') }
}
const handleLogout = () => { if (confirm('로그아웃 할까?')) { store.logOut(); router.push({ name: 'login' }) } }
const goEdit = () => router.push({ name: 'profile-edit' })
const goJoinedProducts = () => router.push({ name: 'joined-products' }) // [확인] 가입상품 전체보기
// 상품 클릭 시 상세 모달 열기


onMounted(() => {
  if (!store.token) return router.push({ name: 'login' })
  fetchAllData()
})
</script>

<template>
  <div class="profile-dashboard py-5">
    <YoutubeDetail v-if="selectedVideo" :video="selectedVideo" @close="selectedVideo = null" />
    
    <div class="container">
      <div class="user-summary-card shadow-lg mb-4">
        <div class="card-body p-4">
            <div class="user-info-header">
              <div class="avatar clickable" @click="triggerFileInput">
                <div class="hover-overlay">📷</div>
                <img v-if="userInfo?.profile_img" :src="`http://127.0.0.1:8000${userInfo.profile_img}`" class="profile-img-fit">
                <span v-else>{{ userInfo?.username?.charAt(0).toUpperCase() }}</span>
                <input type="file" ref="fileInput" class="d-none" @change="handleImageUpload" accept="image/*">
              </div>
              <div class="text-group">
                <h3>{{ userInfo?.nickname }}님</h3>
                <p class="email">{{ userInfo?.email }}</p>
              </div>
              <button @click="handleLogout" class="btn-logout">로그아웃</button>
            </div>
            
            <div class="quick-stats row text-center">
              <div class="col-4 stat-item">
                <span class="label">나이</span>
                <span class="value">{{ userInfo?.age || 0 }}세</span>
              </div>
              <div class="col-4 stat-item border-start border-end">
                <span class="label">내 자산</span>
                <span class="value">{{ formatNumber(userInfo?.money) }}만원</span>
              </div>
              <div class="col-4 stat-item">
                <span class="label">내 연봉</span>
                <span class="value">{{ formatNumber(userInfo?.salary) }}만원</span>
              </div>
            </div>
        </div>
      </div>

      <div class="row mb-5 g-3">
        <div class="col-md-6">
            <div class="card shadow-sm border-0 rounded-4 h-100 ai-card overflow-hidden">
                <div class="card-body p-4 d-flex flex-column justify-content-between position-relative">
                    <div class="z-1">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <h5 class="fw-bold text-white mb-1">🤖 AI 투자 성향</h5>
                                <p class="text-white-50 small">나의 투자 DNA 분석 리포트</p>
                            </div>
                            <div v-if="userPortfolio" class="animal-icon-sm">
                                <img :src="getAnimalImage(userPortfolio.animal)" alt="animal" />
                            </div>
                        </div>
                        <div v-if="userPortfolio" class="mt-3">
                            <h2 class="fw-bold text-white mb-2">{{ userPortfolio.name }}</h2>
                            <p class="text-white-50 mb-3 small description-text">{{ userPortfolio.description }}</p>
                            <button @click="goAnalysis" class="btn btn-light btn-sm fw-bold rounded-pill px-3">다시 분석하기</button>
                        </div>
                        <div v-else class="mt-4 text-center">
                            <p class="text-white-50 mb-3">아직 분석 기록이 없어요.</p>
                            <button @click="goAnalysis" class="btn btn-light fw-bold rounded-pill px-4">분석 시작하기</button>
                        </div>
                    </div>
                    <div class="ai-bg-icon">📊</div>
                </div>
            </div>
        </div>
        <ProductDetail 
        v-if="selectedProduct" 
        :product="selectedProduct" 
        @close="selectedProduct = null" 
      />  
        <!-- B. 나의 가입 상품 요약 -->
        <div class="col-md-6">
            <div class="card shadow-sm border-0 rounded-4 h-100">
                <div class="card-body p-4">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5 class="fw-bold mb-0 text-dark">
                            💼 가입한 상품 
                            <span class="badge bg-primary-subtle text-primary ms-1 rounded-pill">{{ joinedProducts.length }}</span>
                        </h5>
                        <button v-if="joinedProducts.length > 0" @click="goJoinedProducts" class="btn btn-link btn-sm text-decoration-none p-0 text-muted">전체보기 ></button>
                    </div>

                    <div v-if="joinedProducts.length > 0" class="joined-list">
                        <div 
                            v-for="product in joinedProducts.slice(0, 3)" 
                            :key="product.id" 
                            class="joined-item p-3 mb-2 rounded border border-light"
                            @click="openDetail(product)" 
                        >
                            <div class="d-flex justify-content-between align-items-center">
                                <div class="text-truncate pe-2">
                                    <span class="d-block fw-bold text-dark text-truncate">{{ product.fin_prdt_nm }}</span>
                                    <small class="text-muted">{{ product.kor_co_nm }}</small>
                                </div>
                                <span class="badge bg-secondary-subtle text-secondary-emphasis rounded-pill">가입중</span>
                            </div>
                        </div>
                    </div>
                    
                    <div v-else class="text-center py-4 text-muted h-100 d-flex flex-column justify-content-center align-items-center">
                        <div class="fs-2 mb-2">📭</div>
                        <p class="small mb-2">가입한 상품이 없습니다.</p>
                        <button @click="router.push({name: 'products'})" class="btn btn-sm btn-outline-primary rounded-pill px-3">상품 찾으러 가기</button>
                    </div>
                </div>
            </div>
        </div>
      </div>

      <h4 class="mb-4 fw-bold ps-2 border-start border-4 border-success">나의 활동 메뉴</h4>
      <div class="menu-grid">
        <div @click="goEdit" class="menu-card">
          <div class="menu-icon">✏️</div>
          <div class="menu-text"><h5>내 정보 수정</h5><p>정보 수정하기</p></div>
          <span class="arrow">></span>
        </div>
        <div @click="router.push({name:'liked-products'})" class="menu-card">
          <div class="menu-icon">❤️</div>
          <div class="menu-text"><h5>찜 목록</h5><p>관심 상품 보기</p></div>
          <span class="arrow">></span>
        </div>
        <div @click="router.push({name:'profile-youtube'})" class="menu-card">
          <div class="menu-icon">📺</div>
          <div class="menu-text"><h5>영상 북마크</h5><p>저장한 영상 보기</p></div>
          <span class="arrow">></span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 기존 스타일 그대로 유지 */
.profile-dashboard { background-color: #f4f7f6; min-height: 100vh; }
.user-summary-card { background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); border-radius: 30px; padding: 40px; color: white; }
.user-info-header { display: flex; align-items: center; margin-bottom: 40px; gap: 20px; }
.avatar { width: 70px; height: 70px; background: #42b983; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: 800; overflow: hidden; position: relative; }
.profile-img-fit { width: 100%; height: 100%; object-fit: cover; }
.hover-overlay { position: absolute; width: 100%; height: 100%; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; opacity: 0; transition: 0.3s; }
.avatar:hover .hover-overlay { opacity: 1; cursor: pointer; }
.text-group h3 { margin: 0; font-weight: 700; }
.email { color: #bdc3c7; margin: 0; }
.btn-logout { margin-left: auto; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: white; border-radius: 10px; padding: 5px 15px; font-size: 0.8rem; }
.stat-item .label { display: block; color: #bdc3c7; font-size: 0.9rem; }
.stat-item .value { font-size: 1.3rem; font-weight: 700; }
.ai-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
.animal-icon-sm img { width: 60px; height: 60px; border-radius: 50%; border: 2px solid rgba(255,255,255,0.5); object-fit: cover; }
.ai-bg-icon { position: absolute; right: -10px; bottom: -10px; font-size: 5rem; opacity: 0.2; }
.joined-item { cursor: pointer; transition: 0.2s; background: white; }
.joined-item:hover { transform: scale(1.02); border-color: #42b983 !important; }
.menu-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
.menu-card { background: white; border-radius: 20px; padding: 25px; display: flex; align-items: center; cursor: pointer; transition: 0.3s; border: 1px solid #eee; }
.menu-card:hover { transform: translateY(-5px); border-color: #42b983; }
.menu-icon { font-size: 2.5rem; margin-right: 20px; }
.arrow { margin-left: auto; color: #ccc; font-weight: bold; }
</style>
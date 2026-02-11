<template>
  <div class="wallet-container">
    <div class="header">
        <h1>💰 금융 상품 라운지</h1>
        <p>나에게 딱 맞는 최고의 금융 상품을 찾아보세요.</p>
    </div>

    <!-- 1. 메인 카테고리 탭 -->
    <div class="main-tabs">
        <button @click="changeCategory('recommend')" :class="{ active: currentCategory === 'recommend' }">🔥 AI 추천</button>
        
        <!-- [추가] ETF 탭 -->
        <button @click="changeCategory('etf')" :class="{ active: currentCategory === 'etf' }">⚡ 주식/ETF</button>
        
        <button @click="changeCategory('deposit')" :class="{ active: currentCategory === 'deposit' }">정기예금</button>
        <button @click="changeCategory('saving')" :class="{ active: currentCategory === 'saving' }">적금</button>
        <button @click="changeCategory('annuity')" :class="{ active: currentCategory === 'annuity' }">연금저축</button>
        <button @click="changeCategory('loan')" :class="{ active: isLoanCategory }">대출</button>
    </div>

    <!-- 2. 대출 하위 탭 -->
    <div class="sub-tabs" v-if="isLoanCategory && currentCategory !== 'recommend'">
        <button @click="changeCategory('loan')" :class="{ active: currentCategory === 'loan' }">전체 대출</button>
        <button @click="changeCategory('mortgage')" :class="{ active: currentCategory === 'mortgage' }">주택담보</button>
        <button @click="changeCategory('rent')" :class="{ active: currentCategory === 'rent' }">전세자금</button>
        <button @click="changeCategory('credit')" :class="{ active: currentCategory === 'credit' }">개인신용</button>
    </div>

    <!-- 3. 필터 및 컨트롤 -->
    <div class="controls-bar" v-if="currentCategory !== 'recommend'">
        <select v-model="selectedBank" @change="fetchProducts(currentCategory)" class="custom-select">
            <option :value="null">모든 금융사</option>
            <option v-for="bank in bankList" :key="bank" :value="bank">
                {{ bank }}
            </option>
        </select>

        <!-- ETF와 대출은 기간 필터 제외 -->
        <select v-model="selectedTerm" @change="fetchProducts(currentCategory)" class="custom-select" v-if="!isLoanCategory && currentCategory !== 'etf'">
            <option :value="null">전체 기간</option>
            <option :value="6">6개월</option>
            <option :value="12">12개월</option>
            <option :value="24">24개월</option>
            <option :value="36">36개월</option>
        </select>

        <select v-model="sortOrder" @change="fetchProducts(currentCategory)" class="custom-select">
            <option value="top_rate">
                <!-- [수정] 정렬 기준 텍스트 분기 처리 -->
                <template v-if="currentCategory === 'etf'">1년 수익률순</template>
                <template v-else-if="isLoanCategory">금리 낮은순 (추천)</template>
                <template v-else-if="currentCategory === 'annuity'">수령액 높은순 (추천)</template>
                <template v-else>금리 높은순 (추천)</template>
            </option>
            <option value="popular">인기순</option>
        </select>
    </div>

    <!-- 로딩 & 에러 -->
    <div v-if="loading" class="loading-state">
      <div class="loader"></div>
      <p>최신 금융 데이터를 불러오고 있습니다...</p>
    </div>

    <!-- 결과 없음 -->
    <div v-else-if="displayProducts.length === 0" class="empty-state">
        <p>조건에 맞는 상품이 없습니다 😢</p>
    </div>

    <!-- 상품 리스트 -->
    <div v-else class="product-grid">
      <div 
        v-for="product in displayProducts" 
        :key="product.id" 
        class="card"
        @click="openDetail(product)"
      >
        <div class="card-header">
            <div class="bank-info">
                <img 
                    :src="getBankLogo(product.kor_co_nm)" 
                    @error="handleImageError"
                    alt="bank logo" 
                    class="bank-logo" 
                />
                <span class="bank-name">{{ product.kor_co_nm }}</span>
            </div>
            
            <!-- [수정] 배지 표시 로직 (ETF 추가) -->
            <span class="rate-badge" 
                  :class="{ 
                      'loan-badge': isLoanProduct(product), 
                      'annuity-badge': isAnnuityProduct(product),
                      'etf-badge': product.product_type === 'etf' 
                  }" 
                  v-if="product.options && product.options.length > 0">
                
                <template v-if="product.product_type === 'etf'">
                    1년 수익률 {{ getBestRate(product) }}%
                </template>
                <template v-else-if="isAnnuityProduct(product)">
                    월 {{ formatNumber(getBestRate(product)) }}원 수령
                </template>
                <template v-else-if="isLoanProduct(product)">
                    최저 {{ getBestRate(product) }}%
                </template>
                <template v-else>
                    최고 {{ getBestRate(product) }}%
                </template>
            </span>
        </div>
        
        <h3 class="product-title">{{ product.fin_prdt_nm }}</h3>
        
        <div class="card-info">
            <span v-if="isLoanProduct(product)">{{ getLoanTypeName(product) }}</span>
            <span v-else-if="product.product_type === 'etf'">미국 주식/ETF</span>
            <span v-else>가입기간: {{ getTermRange(product) }}</span>
        </div>

        <div class="card-actions" @click.stop>
            <button 
                class="action-btn like" 
                :class="{ active: isLiked(product.id) }"
                @click="toggleLike(product)"
                title="찜하기"
            >
                {{ isLiked(product.id) ? '❤️' : '🤍' }}
            </button>
            <button 
                class="action-btn join" 
                :class="{ active: isJoined(product.id) }"
                @click="toggleJoin(product)"
            >
                {{ isJoined(product.id) ? '가입완료' : '가입하기' }}
            </button>
        </div>
      </div>
    </div>

    <ProductDetail 
        v-if="selectedProduct" 
        :product="selectedProduct" 
        @close="handleModalClose" 
    />

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import ProductDetail from '@/components/ProductDetail.vue' 

const products = ref([])
const recommendedProducts = ref([])
const currentCategory = ref('deposit') 
const loading = ref(false)
const selectedProduct = ref(null)
const store = useAuthStore()

const myLikedIds = ref([])
const myJoinedIds = ref([])

const selectedBank = ref(null)
const selectedTerm = ref(null)
const sortOrder = ref('top_rate')

const isLoanCategory = computed(() => ['loan', 'mortgage', 'rent', 'credit'].includes(currentCategory.value))
const isLoanProduct = (product) => ['mortgage', 'rent', 'credit'].includes(product.product_type)
const isAnnuityProduct = (product) => product.product_type === 'annuity'

const bankList = computed(() => {
    const banks = new Set(products.value.map(p => p.kor_co_nm))
    return Array.from(banks).sort()
})

const displayProducts = computed(() => {
    if (currentCategory.value === 'recommend') {
        return recommendedProducts.value
    }
    return products.value
})

const isLiked = (id) => myLikedIds.value.includes(id)
const isJoined = (id) => myJoinedIds.value.includes(id)

const fetchMyStatus = async () => {
    if (!store.token) return
    try {
        const headers = { Authorization: `Token ${store.token}` }
        const [likeRes, joinRes] = await Promise.all([
            axios.get('http://127.0.0.1:8000/api/products/liked-list/', { headers }),
            axios.get('http://127.0.0.1:8000/api/products/joined-list/', { headers })
        ])
        myLikedIds.value = likeRes.data.map(p => p.id)
        myJoinedIds.value = joinRes.data.map(p => p.id)
    } catch (err) {
        console.error('내 상태 로드 실패:', err)
    }
}

const toggleLike = async (product) => {
    if (!store.token) return alert('로그인이 필요합니다.')
    try {
        const res = await axios.post(`http://127.0.0.1:8000/api/products/${product.id}/like/`, {}, {
            headers: { Authorization: `Token ${store.token}` }
        })
        if (res.data.is_liked) {
            myLikedIds.value.push(product.id)
        } else {
            myLikedIds.value = myLikedIds.value.filter(id => id !== product.id)
        }
    } catch (err) {
        alert('오류가 발생했습니다.')
    }
}

const toggleJoin = async (product) => {
    if (!store.token) return alert('로그인이 필요합니다.')
    try {
        const res = await axios.post(`http://127.0.0.1:8000/api/products/${product.id}/join/`, {}, {
            headers: { Authorization: `Token ${store.token}` }
        })
        if (res.data.is_joined) {
            myJoinedIds.value.push(product.id)
        } else {
            myJoinedIds.value = myJoinedIds.value.filter(id => id !== product.id)
        }
    } catch (err) {
        alert('오류가 발생했습니다.')
    }
}

const changeCategory = (category) => {
    currentCategory.value = category
    selectedBank.value = null
    selectedTerm.value = null
    sortOrder.value = 'top_rate'
    
    if (category === 'recommend') {
        getRecommendation()
    } else {
        fetchProducts(category)
    }
}

const fetchProducts = async (type) => {
    loading.value = true
    products.value = []
    
    try {
        const params = {
            type: type,
            sort: sortOrder.value,
            bank: selectedBank.value,
            term: selectedTerm.value
        }
        
        // [수정] 대출 및 ETF는 기간 필터 제거
        if (['loan','mortgage','rent','credit', 'etf'].includes(type)) {
            delete params.term
        }

        const cleanParams = Object.fromEntries(Object.entries(params).filter(([_, v]) => v != null))
        const res = await axios.get('http://127.0.0.1:8000/api/products/', { params: cleanParams })
        products.value = res.data
    } catch (err) {
        console.error('데이터 로드 실패:', err)
    } finally {
        loading.value = false
    }
}

const getRecommendation = async () => {
    loading.value = true
    try {
        const res = await axios.get('http://127.0.0.1:8000/api/products/recommend/', {
            headers: { Authorization: `Token ${store.token}` }
        })
        recommendedProducts.value = res.data
    } catch (err) {
        alert('로그인이 필요한 기능입니다!')
        currentCategory.value = 'deposit' 
        fetchProducts('deposit')
    } finally {
        loading.value = false
    }
}

const getBestRate = (product) => {
    if (!product.options || product.options.length === 0) return 0
    
    // [추가] ETF: intr_rate(1년 수익률) 사용 (높을수록 좋음)
    if (product.product_type === 'etf') {
        return product.options[0].intr_rate
    }
    else if (isAnnuityProduct(product)) {
        const amounts = product.options.map(opt => opt.intr_rate).filter(r => r > 0)
        return amounts.length > 0 ? Math.max(...amounts) : 0
    }
    else if (isLoanProduct(product)) {
        const rates = product.options.map(opt => opt.intr_rate).filter(r => r > 0)
        return rates.length > 0 ? Math.min(...rates) : 0
    } 
    else {
        const rates = product.options.map(opt => opt.intr_rate2).filter(r => r > 0)
        return rates.length > 0 ? Math.max(...rates) : 0
    }
}

const getTermRange = (product) => {
    if (!product.options) return '-'
    const terms = product.options.map(opt => opt.save_trm).filter(t => t > 0)
    if (terms.length === 0) return '-'
    const min = Math.min(...terms)
    const max = Math.max(...terms)
    return min === max ? `${min}개월` : `${min}~${max}개월`
}

const getLoanTypeName = (product) => {
    const map = { 'mortgage': '주택담보대출', 'rent': '전세자금대출', 'credit': '개인신용대출', 'annuity': '연금저축' }
    return map[product.product_type] || '대출'
}

const formatNumber = (num) => {
    return num ? num.toLocaleString() : '0'
}

const openDetail = (product) => {
    selectedProduct.value = product
}

const handleModalClose = () => {
    selectedProduct.value = null
    fetchMyStatus()
}

const getBankLogo = (bankName) => {
    // ETF/주식 로고 처리 (미국주식 등)
    if (bankName === '미국 주식/ETF') return '/images/chart/usd.png' // 적절한 아이콘 필요
    return `/images/logos/${bankName}.png`
}

const handleImageError = (e) => {
    const fallback = 'https://via.placeholder.com/40x40?text=Bank'
    if (!e.target.src.includes('placeholder')) {
        e.target.src = fallback
    }
}

onMounted(() => {
    fetchProducts('deposit') 
    fetchMyStatus() 
})
</script>

<style scoped src="./ProductView.css"></style>

<style scoped>
/* 탭 및 배지 스타일 */
.main-tabs { display: flex; gap: 10px; margin-bottom: 15px; flex-wrap: wrap; }
.main-tabs button { padding: 10px 20px; border: none; background: #f1f3f5; color: #495057; border-radius: 8px; font-weight: bold; cursor: pointer; transition: all 0.2s; }
.main-tabs button.active { background: #2c3e50; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
.sub-tabs { display: flex; gap: 8px; margin-bottom: 20px; padding-left: 10px; border-left: 3px solid #2c3e50; }
.sub-tabs button { padding: 6px 14px; border: 1px solid #dee2e6; background: white; border-radius: 20px; font-size: 0.9rem; color: #868e96; cursor: pointer; }
.sub-tabs button.active { border-color: #2c3e50; color: #2c3e50; font-weight: bold; background: #eef2ff; }

/* 배지 색상 */
.rate-badge.loan-badge { background: #fff0f6; color: #c026d3; }
.rate-badge.annuity-badge { background: #ecfdf5; color: #059669; }
.rate-badge.etf-badge { background: #fff5f5; color: #ff6b6b; } /* [추가] ETF 배지 */

.card-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 15px;
    margin-top: auto; 
    border-top: 1px solid #f1f3f5;
}

.action-btn {
    border: none;
    background: transparent;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 600;
    transition: all 0.2s;
    padding: 6px 12px;
    border-radius: 6px;
}

.action-btn.like { color: #868e96; font-size: 1.2rem; }
.action-btn.like.active { color: #ff6b6b; transform: scale(1.1); }

.action-btn.join { background-color: #f1f3f5; color: #495057; }
.action-btn.join:hover { background-color: #e9ecef; }
.action-btn.join.active { background-color: #2c3e50; color: white; }
</style>
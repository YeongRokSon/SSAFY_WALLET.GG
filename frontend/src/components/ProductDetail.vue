<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content" v-if="product">
      <header>
        <span class="bank-badge">{{ product.kor_co_nm }}</span>
        <h2>{{ product.fin_prdt_nm }}</h2>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </header>

      <div class="modal-body">
        <!-- 1. 기본 정보 섹션 -->
        <div class="info-section">
          <h3>📌 상품 설명</h3>
          <p class="description">{{ product.etc_note || '상세 설명이 없습니다.' }}</p>
        </div>

        <!-- 2. 금리/옵션/수익률 테이블 -->
        <div class="info-section">
            <h3>
                <span v-if="isEtf">💰 투자 수익률 정보</span>
                <span v-else-if="isAnnuity">💰 연금 수령 정보</span>
                <span v-else-if="isLoan">💰 대출 금리 정보</span>
                <span v-else>💰 금리 및 기간</span>
            </h3>
            
            <div class="rate-table">
                <div class="rate-header" :class="{ 'loan-header': isLoan, 'annuity-header': isAnnuity, 'etf-header': isEtf }">
                    <!-- ETF 헤더 -->
                    <template v-if="isEtf">
                        <span>기준</span>
                        <span>섹터</span>
                        <span>1년 수익률</span>
                        <span>배당률</span>
                    </template>
                    <!-- 연금 헤더 -->
                    <template v-else-if="isAnnuity">
                         <span>유형</span>
                         <span>월 납입액</span>
                         <span>월 수령액</span>
                    </template>
                     <!-- 대출 헤더 -->
                    <template v-else-if="isLoan">
                        <span>금리유형</span>
                        <span>최저금리</span>
                        <span>최고금리</span>
                    </template>
                    <!-- 예적금 헤더 -->
                    <template v-else>
                        <span>기간</span>
                        <span>금리유형</span>
                        <span>기본금리</span>
                        <span>최고우대</span>
                    </template>
                </div>
                
                <div v-for="opt in product.options" :key="opt.id" class="rate-row">
                    <!-- ETF 데이터 -->
                    <template v-if="isEtf">
                        <span>1년</span>
                        <span class="type-badge">{{ opt.etc_info?.sector || 'ETF' }}</span>
                        <span class="highlight" :class="{ 'plus': opt.intr_rate > 0, 'minus': opt.intr_rate < 0 }">
                            {{ opt.intr_rate }}%
                        </span>
                        <span class="highlight max">{{ opt.intr_rate2 }}%</span>
                    </template>
                    
                    <!-- 연금 데이터 -->
                    <template v-else-if="isAnnuity">
                        <span>{{ opt.intr_rate_type_nm }}</span>
                        <span class="type-badge">{{ opt.etc_info?.mon_paym_atm_nm || '-' }}</span>
                        <span class="highlight">{{ formatNumber(opt.intr_rate) }}원</span>
                    </template>

                    <!-- 대출/예적금 데이터 -->
                    <template v-else>
                        <span v-if="!isLoan">{{ opt.save_trm }}개월</span>
                        <span class="type-badge">{{ opt.intr_rate_type_nm }}</span>
                        <span class="highlight">{{ opt.intr_rate }}%</span>
                        <span class="highlight max">{{ opt.intr_rate2 }}%</span>
                    </template>
                </div>
            </div>
        </div>

        <!-- 3. 추가 상세 정보 (JSONField 내용 표시) -->
        <div class="info-section" v-if="hasEtcInfo">
            <h3>📋 상세 정보</h3>
            <ul class="etc-list">
                <li v-for="(value, key) in etcInfoDisplay" :key="key">
                    <span class="label">{{ key }}</span>
                    <span class="value">{{ value }}</span>
                </li>
            </ul>
        </div>

        <!-- 4. 가입/우대 조건 (ETF는 제외) -->
        <div class="info-section" v-if="!isEtf">
          <h3>🎁 우대 조건 및 가입 대상</h3>
          <p v-if="product.spcl_cnd" class="sub-text"><strong>우대조건:</strong> {{ product.spcl_cnd }}</p>
          <p class="sub-text"><strong>가입대상:</strong> {{ product.join_member }}</p>
          <p class="sub-text"><strong>가입방법:</strong> {{ product.join_way }}</p>
        </div>
      </div>

      <footer>
        <button class="action-btn web" @click="openBankSite">🏦 홈페이지 방문</button>
        <button 
          class="action-btn like" 
          :class="{ active: isLiked }"
          @click="toggleLike"
        >
          {{ isLiked ? '♥ 찜 취소' : '♡ 찜하기' }}
        </button>
        <button 
          class="action-btn join" 
          :class="{ active: isJoined }"
          @click="toggleJoin"
        >
          {{ isJoined ? (isEtf ? '보유중' : '가입완료') : (isEtf ? '포트폴리오 추가' : '가입하기') }}
        </button>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const props = defineProps({
  product: Object,
})

const emit = defineEmits(['close'])
const store = useAuthStore()
const isLiked = ref(false)
const isJoined = ref(false)

// 상품 타입 확인
const isLoan = computed(() => ['mortgage', 'rent', 'credit'].includes(props.product.product_type))
const isAnnuity = computed(() => props.product.product_type === 'annuity')
const isEtf = computed(() => props.product.product_type === 'etf')

const hasEtcInfo = computed(() => props.product.options && props.product.options.some(opt => opt.etc_info))

// 상세 정보 매핑
const etcInfoDisplay = computed(() => {
    if (!props.product.options || props.product.options.length === 0) return {}
    const info = props.product.options[0].etc_info || {}
    const displayMap = {}

    // ETF 정보 매핑
    if (isEtf.value) {
        if (info.current_price) displayMap['현재가'] = '$' + info.current_price
        if (info.sector) displayMap['섹터'] = info.sector
    } else {
        // 기존 상품 정보 매핑
        if (info.rpay_type_nm) displayMap['상환방식'] = info.rpay_type_nm
        if (info.mrtg_type_nm) displayMap['담보유형'] = info.mrtg_type_nm
        if (info.lend_rate_type_nm) displayMap['금리방식'] = info.lend_rate_type_nm
        if (info.pnsn_entr_age_nm) displayMap['가입나이'] = info.pnsn_entr_age_nm
        if (info.mon_paym_atm_nm) displayMap['월납입액'] = info.mon_paym_atm_nm
    }

    return displayMap
})

const formatNumber = (num) => {
    return num ? num.toLocaleString() : '0'
}

const fetchDetailStatus = async () => {
    if (!store.token) return
    try {
        const res = await axios.get(`http://127.0.0.1:8000/api/products/${props.product.id}/`, {
             headers: { Authorization: `Token ${store.token}` }
        })
        isLiked.value = res.data.is_liked
        isJoined.value = res.data.is_joined
    } catch (e) {
        console.error("상태 조회 실패", e)
    }
}

const toggleLike = async () => {
  if (!store.token) return alert('로그인이 필요한 기능입니다.')
  try {
    const res = await axios.post(`http://127.0.0.1:8000/api/products/${props.product.id}/like/`, {}, {
      headers: { Authorization: `Token ${store.token}` }
    })
    isLiked.value = res.data.is_liked
    if (isLiked.value) alert('관심 상품에 등록되었습니다!')
  } catch (err) {
    alert('오류가 발생했습니다.')
  }
}

const toggleJoin = async () => {
  if (!store.token) return alert('로그인이 필요한 기능입니다.')
  try {
    const res = await axios.post(`http://127.0.0.1:8000/api/products/${props.product.id}/join/`, {}, {
      headers: { Authorization: `Token ${store.token}` }
    })
    isJoined.value = res.data.is_joined
    if (isJoined.value) alert(isEtf.value ? '포트폴리오에 추가되었습니다!' : '가입 상품으로 등록되었습니다!')
  } catch (err) {
    alert('오류가 발생했습니다.')
  }
}

const openBankSite = () => {
    window.open(`https://www.google.com/search?q=${props.product.kor_co_nm} ${props.product.fin_prdt_nm}`, '_blank')
}

onMounted(() => {
    fetchDetailStatus()
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(2px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  width: 90%;
  max-width: 650px;
  max-height: 85vh;
  overflow-y: auto;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 20px 50px rgba(0,0,0,0.3);
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
    from { transform: translateY(20px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}

header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
}

.bank-badge {
    background: #eff6ff;
    color: #2563eb;
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 700;
    margin-bottom: 8px;
    display: inline-block;
}

h2 { margin: 5px 0 0; font-size: 1.5rem; color: #1e293b; line-height: 1.3; }

.close-btn {
  background: none;
  border: none;
  font-size: 1.8rem;
  color: #94a3b8;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.modal-body { flex: 1; overflow-y: auto; padding-right: 5px; }
.modal-body::-webkit-scrollbar { width: 6px; }
.modal-body::-webkit-scrollbar-thumb { background-color: #cbd5e1; border-radius: 3px; }

.info-section { margin-bottom: 30px; }
.info-section h3 { 
    font-size: 1.1rem; 
    color: #334155; 
    margin-bottom: 12px; 
    font-weight: 700;
    border-left: 4px solid #42b883;
    padding-left: 10px;
}

.description { color: #64748b; line-height: 1.6; font-size: 0.95rem; white-space: pre-line; }
.sub-text { margin: 8px 0; color: #475569; font-size: 0.95rem; line-height: 1.5; }

.rate-table {
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    overflow: hidden;
}
.rate-header, .rate-row {
    display: flex;
    text-align: center;
    padding: 12px;
}
.rate-header span, .rate-row span {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
}
.rate-header { background: #f8fafc; font-weight: 700; font-size: 0.9rem; color: #475569; border-bottom: 1px solid #e2e8f0; }

/* 헤더 색상 */
.rate-header.loan-header { background: #fff0f6; color: #be185d; } 
.rate-header.annuity-header { background: #ecfdf5; color: #047857; }
.rate-header.etf-header { background: #fff5f5; color: #e03131; }

.rate-row { border-top: 1px solid #f1f5f9; font-size: 0.95rem; color: #334155; }
.rate-row:first-child { border-top: none; }

.type-badge { background: #f1f5f9; color: #475569; padding: 2px 8px; border-radius: 4px; font-size: 0.85rem; }
.highlight { font-weight: 500; }
.highlight.max { color: #e11d48; font-weight: 800; }
.highlight.plus { color: #e03131; font-weight: 700; }
.highlight.minus { color: #228be6; font-weight: 700; }

.etc-list { list-style: none; padding: 0; display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.etc-list li { background: #f8fafc; padding: 10px; border-radius: 8px; font-size: 0.9rem; }
.etc-list .label { display: block; font-weight: bold; color: #64748b; margin-bottom: 4px; font-size: 0.8rem; }
.etc-list .value { color: #334155; font-weight: 600; }

footer {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.action-btn {
  flex: 1;
  padding: 14px;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
}

.action-btn.web { background: #f1f5f9; color: #475569; }
.action-btn.web:hover { background: #e2e8f0; }

.action-btn.like { background: #fff5f5; color: #ff6b6b; border: 1px solid #ffc9c9; }
.action-btn.like:hover { background: #ffe3e3; }
.action-btn.like.active { background: #ff6b6b; color: white; border-color: #ff6b6b; }

.action-btn.join { background: #2c3e50; color: white; }
.action-btn.join:hover { background: #1e293b; transform: translateY(-1px); }
.action-btn.join.active { background: #42b883; border: 1px solid #42b883; }
</style>
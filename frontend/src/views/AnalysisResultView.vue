<script setup>
import { computed } from 'vue'
import { useFinanceStore } from '@/stores/finance'
import { useRouter } from 'vue-router'

const store = useFinanceStore()
const router = useRouter()

// 안전장치: 분석 결과가 없으면 입력 페이지로 돌려보냄
if (!store.analysisResult) {
  router.replace({ name: 'asset-input' })
}

const result = computed(() => store.analysisResult || {})
const userInfo = computed(() => store.userInfo || {})
// [신규] 스탯 데이터 (없을 경우 기본값 처리)
const animalStats = computed(() => result.value.stats || { '위험감수': 50, '수익지향': 50, '분석력': 50, '인내심': 50 })

// 동물 이미지 경로 생성 함수
const getAnimalImage = (code) => {
    if (!code) return '' 
    return `/images/animals/${code}.png`
}

// 금액 포맷팅
const formatMoney = (val) => {
    return Number(val).toLocaleString() + '만원'
}

// 목표 라벨 변환
const goalLabel = (val) => {
    const map = {
        'housing': '내 집 마련 🏡',
        'car': '드림카 구매 🚗',
        'marriage': '결혼 자금 💍',
        'rich': '경제적 자유 🤑'
    }
    return map[val] || val
}

const goRecommend = () => router.push({ name: 'product-recommend' })
</script>

<template>
  <div class="container py-5">
    <div class="result-container">
        
      <!-- 1. 기본 정보 요약 카드 -->
      <div class="info-card shadow-sm mb-4">
        <h3 class="card-title">📋 나의 자산 프로필</h3>
        <div class="info-grid">
            <div class="info-item">
                <span class="label">나이</span>
                <span class="value">{{ userInfo.age }}세</span>
            </div>
            <div class="info-item">
                <span class="label">연봉</span>
                <span class="value">{{ formatMoney(userInfo.salary) }}</span>
            </div>
            <div class="info-item">
                <span class="label">자산</span>
                <span class="value">{{ formatMoney(userInfo.assets) }}</span>
            </div>
            <div class="info-item">
                <span class="label">목표</span>
                <span class="value">{{ goalLabel(userInfo.goal) }}</span>
            </div>
        </div>
      </div>

      <!-- 2. 동물 성향 분석 결과 -->
      <div class="result-card shadow-lg">
        
        <div class="header-section mb-4">
          <span class="badge-custom">AI 투자 성향 분석 완료 ✨</span>
        </div>

        <!-- 동물 이미지 섹션 -->
        <div class="animal-display">
            <div class="image-wrapper">
                <img 
                    :src="getAnimalImage(result.animal)" 
                    alt="Animal Type" 
                    class="animal-img"
                    @error="$event.target.src='https://via.placeholder.com/200?text=Animal'" 
                />
            </div>
            <h1 class="animal-title">
                당신은 <span class="highlight">{{ result.name }}</span> 입니다!
            </h1>
        </div>

        <!-- [신규] 투자 능력치 (Stats) 섹션 -->
        <div class="stats-box mb-4">
            <h4 class="stats-title">📊 투자 능력치</h4>
            <div class="stats-grid">
                <div v-for="(score, key) in animalStats" :key="key" class="stat-row">
                    <div class="stat-label">
                        <span>{{ key }}</span>
                        <span class="stat-score">{{ score }}</span>
                    </div>
                    <div class="progress-bg">
                        <div class="progress-fill" :style="{ width: score + '%' }"></div>
                    </div>
                </div>
            </div>
        </div>

        <div class="description-box">
          <h3>💡 투자 스타일 분석</h3>
          <p class="desc-text">{{ result.description }}</p>
        </div>

        <div class="action-section">
            <p class="guide-text">
                <strong>{{ userInfo.age }}세 {{ result.name }}</strong>님을 위한<br>
                맞춤 금융 상품 포트폴리오가 준비되었습니다.
            </p>
            <button @click="goRecommend" class="btn-action">
                AI 추천 상품 보러가기 🎁
            </button>
        </div>

      </div>
      
    </div>
  </div>
</template>

<style scoped>
.result-container { max-width: 600px; margin: 0 auto; }

/* 1. 기본 정보 카드 */
.info-card {
    background: white; border-radius: 20px; padding: 25px;
    border: 1px solid #f0f0f0;
}
.card-title { font-size: 1.1rem; font-weight: 700; color: #495057; margin-bottom: 15px; border-bottom: 2px solid #f8f9fa; padding-bottom: 10px; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
.info-item { display: flex; flex-direction: column; }
.info-item .label { font-size: 0.85rem; color: #888; margin-bottom: 2px; }
.info-item .value { font-size: 1.1rem; font-weight: 700; color: #2c3e50; }

/* 2. 결과 카드 */
.result-card {
  background: white;
  border-radius: 24px;
  padding: 50px 30px;
  text-align: center;
  border: 1px solid #f0f0f0;
  margin-top: 20px;
  position: relative;
  overflow: hidden;
}

/* 배경 장식 */
.result-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 150px;
    background: linear-gradient(180deg, #f8f9fa 0%, rgba(255,255,255,0) 100%);
    z-index: 0;
}

.header-section, .animal-display, .description-box, .action-section, .stats-box {
    position: relative; z-index: 1;
}

.badge-custom {
  background: #e7f5ff;
  color: #1971c2;
  padding: 8px 16px;
  border-radius: 30px;
  font-weight: 700;
  font-size: 0.9rem;
  display: inline-block;
  letter-spacing: 0.5px;
}

/* 동물 이미지 스타일 */
.image-wrapper {
  width: 200px; 
  height: 200px;
  border-radius: 50%;
  margin: 0 auto 25px;
  border: 8px solid white;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  overflow: hidden;
  background-color: #fff;
  animation: pop 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.animal-img {
    width: 100%;
    height: 100%;
    object-fit: cover; 
    display: block;
}

.animal-title {
    font-size: 1.8rem;
    font-weight: 800;
    color: #333;
    line-height: 1.4;
    margin-bottom: 30px;
}

.highlight { color: #0061f2; }

/* [신규] 스탯 박스 스타일 */
.stats-box {
    background: white;
    border: 1px solid #eee;
    border-radius: 20px;
    padding: 25px;
    margin-bottom: 30px;
    text-align: left;
    box-shadow: 0 4px 10px rgba(0,0,0,0.02);
}
.stats-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #333;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.stat-row { margin-bottom: 12px; }
.stat-row:last-child { margin-bottom: 0; }
.stat-label {
    display: flex;
    justify-content: space-between;
    font-size: 0.9rem;
    font-weight: 600;
    color: #555;
    margin-bottom: 5px;
}
.stat-score { color: #0061f2; font-weight: 800; }
.progress-bg {
    width: 100%;
    height: 8px;
    background-color: #f1f3f5;
    border-radius: 10px;
    overflow: hidden;
}
.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #0061f2, #6900f2);
    border-radius: 10px;
    transition: width 1s ease-out;
}

.description-box {
  background: #f8f9fa;
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 30px;
  text-align: left;
  border: 1px solid #eee;
}
.description-box h3 { font-size: 1.2rem; font-weight: 700; color: #343a40; margin-bottom: 12px; }
.desc-text { font-size: 1.05rem; line-height: 1.7; color: #495057; white-space: pre-line; margin: 0; }

.action-section { margin-top: 20px; }
.guide-text { font-size: 1rem; color: #666; margin-bottom: 20px; line-height: 1.5; }

.btn-action {
  background: linear-gradient(45deg, #0061f2, #6900f2);
  color: white;
  border: none;
  padding: 18px 40px;
  font-size: 1.1rem;
  font-weight: 700;
  border-radius: 50px;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(105, 0, 242, 0.3);
  transition: transform 0.2s, box-shadow 0.2s;
  width: 100%;
}
.btn-action:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(105, 0, 242, 0.4); }

@keyframes pop { from { transform: scale(0.5); opacity: 0; } to { transform: scale(1); opacity: 1; } }
</style>
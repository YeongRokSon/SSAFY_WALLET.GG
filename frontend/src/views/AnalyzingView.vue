<script setup>
import { onMounted, ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useFinanceStore } from '@/stores/finance'
import { useAuthStore } from '@/stores/auth' 
import axios from 'axios'

const router = useRouter()
const store = useFinanceStore()
const authStore = useAuthStore()

// 로딩 문구 관련 상태
const currentMessage = ref('자산 데이터를 꼼꼼히 살펴보고 있어요 🔍')
const messages = [
  '금융 감독원 최신 금리 정보를 대조 중이에요 🏦',
  '사용자분의 투자 성향을 분석하고 있어요 🧠',
  '최적의 포트폴리오 구성을 계산 중이에요 🧮',
  '거의 다 됐어요! 결과 리포트를 작성 중... 📝'
]
let msgInterval = null

onMounted(async () => {
  // 1. 안전장치
  if (!store.userInfo || Object.keys(store.userInfo).length === 0) {
    alert('입력된 정보가 없습니다. 다시 시작해주세요!')
    router.replace({ name: 'asset-input' })
    return
  }

  // 2. 문구 변경 타이머 시작 (1.5초마다 변경)
  let msgIndex = 0
  msgInterval = setInterval(() => {
    if (msgIndex < messages.length) {
      currentMessage.value = messages[msgIndex]
      msgIndex++
    }
  }, 1500)

  try {
    // 3. AI 분석 요청
    const res = await axios.post(
      'http://127.0.0.1:8000/api/products/analyze/', 
      { user_info: store.userInfo }, 
      { headers: { Authorization: `Token ${authStore.token}` } }
    )
    
    store.analysisResult = res.data
    
    // 분석 완료 후 잠시 대기 (완료 메시지 보여주기 위함)
    setTimeout(() => {
      clearInterval(msgInterval)
      router.replace({ name: 'analysis-result' })
    }, 1000)

  } catch (err) {
    console.error(err)
    alert('로그인이 필요한 기능입니다.')
    router.go(-1)
  }
})

onUnmounted(() => {
  if (msgInterval) clearInterval(msgInterval)
})
</script>

<template>
  <div class="loading-container">
    <div class="content-card">
      
      <div class="icon-wrapper">
        <span class="emoji-bounce">🤖</span>
        <div class="shadow-pulse"></div>
      </div>

      <h2 class="title">AI 금융 비서가<br>포트폴리오를 분석 중입니다</h2>
      
      <div class="progress-bar-container">
        <div class="progress-bar-fill"></div>
      </div>

      <p class="status-text fade-in-out" :key="currentMessage">
        {{ currentMessage }}
      </p>

    </div>
  </div>
</template>

<style scoped>
/* 전체 컨테이너 */
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  background: #f8f9fa;
}

/* 카드 디자인 */
.content-card {
  background: white;
  padding: 50px 40px;
  border-radius: 24px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0,0,0,0.08);
  max-width: 500px;
  width: 90%;
}

/* 아이콘 애니메이션 */
.icon-wrapper { position: relative; height: 100px; margin-bottom: 20px; }
.emoji-bounce {
  font-size: 5rem;
  display: block;
  animation: bounce 1.5s infinite ease-in-out;
  position: relative;
  z-index: 2;
}
.shadow-pulse {
  width: 60px; height: 10px;
  background: rgba(0,0,0,0.1);
  border-radius: 50%;
  margin: 0 auto;
  animation: shadowScale 1.5s infinite ease-in-out;
}

/* 텍스트 스타일 */
.title { font-size: 1.5rem; font-weight: 800; color: #2c3e50; margin-bottom: 30px; line-height: 1.4; }
.status-text { color: #007bff; font-weight: 600; font-size: 1.1rem; min-height: 1.5rem; }

/* 프로그레스 바 */
.progress-bar-container {
  width: 100%; height: 8px;
  background: #e9ecef;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 20px;
}
.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #0061f2, #6900f2);
  width: 30%;
  border-radius: 10px;
  animation: loadingProgress 3s infinite ease-in-out;
}

/* 키프레임 애니메이션 */
@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}
@keyframes shadowScale {
  0%, 100% { transform: scale(1); opacity: 0.2; }
  50% { transform: scale(0.6); opacity: 0.1; }
}
@keyframes loadingProgress {
  0% { width: 0%; margin-left: 0; }
  50% { width: 100%; margin-left: 0; }
  100% { width: 0%; margin-left: 100%; }
}
.fade-in-out { animation: fadeIn 0.5s ease-in-out; }
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
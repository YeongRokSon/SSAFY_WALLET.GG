<script setup>
import { ref, computed, onMounted } from 'vue' // onMounted 추가
import { useRouter } from 'vue-router'
import { useFinanceStore } from '@/stores/finance'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios' // axios 추가

const router = useRouter()
const store = useFinanceStore()
const authStore = useAuthStore()

const step = ref(0)
const totalSteps = 4

const info = ref({
  age: '',
  salary: '',
  assets: '',
  goal: '',
  tendency: ''
})

const goalOptions = [
  { value: 'housing', label: '🏡 내 집 마련', desc: '안정적인 자산 증식이 필요해요' },
  { value: 'car', label: '🚗 드림카 구매', desc: '단기간에 목돈을 모아야 해요' },
  { value: 'marriage', label: '💍 결혼 자금', desc: '2~3년 내에 쓸 돈이에요' },
  { value: 'rich', label: '🤑 경제적 자유', desc: '공격적인 투자가 필요해요' }
]

const tendencyOptions = [
  { value: 'stable', label: '🐢 안정형', desc: '원금 손실은 절대 안 돼요!' },
  { value: 'moderate', label: '⚖️ 중립형', desc: '적당한 수익과 위험을 감수해요' },
  { value: 'aggressive', label: '🐅 공격형', desc: 'High Risk, High Return!' }
]

// [신규] 기존 데이터 불러오기 함수
const fetchExistingData = async () => {
  if (!authStore.token) return

  try {
    const headers = { Authorization: `Token ${authStore.token}` }
    
    // 1. 유저 기본 정보 (나이, 연봉, 자산-money)
    // accounts/profile/{username}/ 엔드포인트 사용 (ProfileView와 동일)
    const userRes = await axios.get(`http://127.0.0.1:8000/accounts/profile/${authStore.username}/`, { headers })
    const u = userRes.data

    // 2. 이전 포트폴리오 분석 기록 (목표, 성향)
    let p = {}
    try {
        const portRes = await axios.get('http://127.0.0.1:8000/api/products/portfolio/latest/', { headers })
        if (portRes.data.exists && portRes.data.user_info) {
            p = portRes.data.user_info
        }
    } catch (e) {
        // 이전 기록이 없으면 패스
    }

    // 3. 데이터 병합하여 폼 채우기
    // DB에 값이 0이거나 없으면 빈 문자열로 두어 입력을 유도
    info.value = {
        age: u.age || p.age || '',
        salary: u.salary || p.salary || '',
        assets: u.money || p.assets || '', // User 모델엔 money, 여기 폼엔 assets
        goal: p.goal || '',
        tendency: p.tendency || ''
    }

  } catch (err) {
    console.error("데이터 로드 중 오류:", err)
  }
}

const handleStart = () => {
  if (!authStore.isAuthenticated) {
    alert('🔐로그인이 필요한 기능입니다🔐')
    router.push({ name: 'auth' })
    return
  }
  step.value++
}

const nextStep = () => { if (step.value < totalSteps) step.value++ }
const prevStep = () => { if (step.value > 1) step.value-- }

const submitForm = () => {
  if (!info.value.age || !info.value.salary || !info.value.assets) {
    alert('모든 정보를 입력해주세요!')
    return
  }
  store.userInfo = info.value
  router.push({ name: 'animal-survey' }) 
}

const progress = computed(() => (step.value / totalSteps) * 100)

// 페이지 로드 시 기존 데이터 가져오기
onMounted(() => {
    fetchExistingData()
})
</script>

<template>
  <div class="input-container py-5">
    
    <div v-if="step === 0" class="start-screen text-center">
      <div class="emoji-bounce">🤖</div>
      <h1 class="display-5 fw-bold mb-3">AI 자산 분석 도우미</h1>
      <p class="text-secondary fs-5 mb-5">
        몇 가지 질문에 답해주시면<br>당신에게 딱 맞는 금융 포트폴리오를 짜드릴게요.
        <!-- 안내 문구 추가 -->
        <br><span v-if="authStore.isAuthenticated" class="small text-primary">(기존 정보가 있다면 자동으로 입력됩니다)</span>
      </p>
      <button @click="handleStart" class="btn-main-gradient">분석 시작하기 🚀</button>
    </div>

    <div v-else class="form-card shadow-lg">
      
      <div class="progress-wrapper mb-5">
        <div class="d-flex justify-content-between mb-2">
          <span class="step-text fw-bold">STEP {{ step }}</span>
          <span class="total-text text-muted">{{ step }} / {{ totalSteps }}</span>
        </div>
        <div class="progress-bg">
          <div class="progress-fill" :style="{ width: progress + '%' }"></div>
        </div>
      </div>

      <div class="question-section min-vh-40">
        
        <div v-if="step === 1" class="step-content fade-in">
          <h2 class="section-title">기본 정보를 알려주세요</h2>
          <div class="input-floating mb-4">
            <label>나이</label>
            <input v-model="info.age" type="number" placeholder="만 나이를 입력하세요 (예: 25)">
          </div>
          <div class="input-floating">
            <label>연봉 (만원)</label>
            <input v-model="info.salary" type="number" placeholder="세전 연봉을 입력하세요 (예: 3500)">
          </div>
        </div>

        <div v-if="step === 2" class="step-content fade-in">
          <h2 class="section-title">현재 자산 규모는 얼마인가요? 💰</h2>
          <p class="sub-desc mb-4">예금, 적금, 주식 등을 모두 합친 총 금액을 적어주세요.</p>
          <div class="input-floating">
            <label>총 자산 (만원)</label>
            <input v-model="info.assets" type="number" placeholder="예: 5000">
          </div>
        </div>

        <div v-if="step === 3" class="step-content fade-in">
          <h2 class="section-title">투자의 가장 큰 목표는?</h2>
          <div class="option-grid">
            <div 
              v-for="opt in goalOptions" :key="opt.value"
              class="option-card"
              :class="{ active: info.goal === opt.value }"
              @click="info.goal = opt.value"
            >
              <div class="option-check"></div>
              <h3>{{ opt.label }}</h3>
              <p>{{ opt.desc }}</p>
            </div>
          </div>
        </div>

        <div v-if="step === 4" class="step-content fade-in">
          <h2 class="section-title">당신의 투자 성향은?</h2>
          <div class="option-grid vertical">
            <div 
              v-for="opt in tendencyOptions" :key="opt.value"
              class="option-card-horizontal"
              :class="{ active: info.tendency === opt.value }"
              @click="info.tendency = opt.value"
            >
              <div class="check-circle"></div>
              <div class="text-group">
                <h3>{{ opt.label }}</h3>
                <p>{{ opt.desc }}</p>
              </div>
            </div>
          </div>
        </div>

      </div>

      <div class="btn-group-footer mt-5">
        <button @click="prevStep" class="btn-prev">이전</button>
        
        <button v-if="step < totalSteps" @click="nextStep" class="btn-next" :disabled="step===3 && !info.goal">
          다음 단계로
        </button>
        
        <button v-else @click="submitForm" class="btn-submit-final" :disabled="!info.tendency">
          상세 성향 분석하러 가기 🦁
        </button>
      </div>

    </div>
  </div>
</template>

<style scoped>
.input-container { max-width: 700px; margin: 0 auto; }

.emoji-bounce { font-size: 5rem; animation: bounce 2s infinite; }
@keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-20px); } }

.form-card {
  background: white;
  border-radius: 30px;
  padding: 50px 40px;
  border: 1px solid #f0f0f0;
}

.progress-bg { height: 8px; background: #e9ecef; border-radius: 10px; overflow: hidden; }
.progress-fill { height: 100%; background: #2c3e50; transition: width 0.4s ease; }
.step-text { color: #2c3e50; font-size: 0.9rem; }

.section-title { font-size: 1.8rem; font-weight: 800; color: #2c3e50; margin-bottom: 25px; }
.sub-desc { color: #888; font-size: 1rem; }

.input-floating label { display: block; font-weight: 700; color: #495057; margin-bottom: 8px; }
.input-floating input {
  width: 100%; padding: 15px 20px;
  border: 2px solid #eee; border-radius: 15px;
  font-size: 1.1rem; transition: all 0.2s;
}
.input-floating input:focus { border-color: #2c3e50; outline: none; background: #fcfcfc; }

.option-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
.option-card {
  border: 2px solid #f1f3f5; border-radius: 20px;
  padding: 25px 15px; cursor: pointer; text-align: center;
  transition: all 0.2s ease; position: relative;
}
.option-card.active { border-color: #42b983; background: #f2fbf7; }
.option-card h3 { font-size: 1.15rem; font-weight: 700; margin-bottom: 8px; }

.option-grid.vertical { grid-template-columns: 1fr; }
.option-card-horizontal {
  display: flex; align-items: center; gap: 20px;
  padding: 20px 25px; border: 2px solid #f1f3f5; border-radius: 20px;
  cursor: pointer; transition: all 0.2s;
}
.option-card-horizontal.active { border-color: #007bff; background: #f0f7ff; }
.check-circle { width: 20px; height: 20px; border: 2px solid #ddd; border-radius: 50%; }
.active .check-circle { background: #007bff; border-color: #007bff; }

.btn-group-footer { display: flex; gap: 15px; }
.btn-prev { background: #f1f3f5; border: none; padding: 15px 30px; border-radius: 15px; font-weight: 700; color: #666; }
.btn-next { flex-grow: 1; background: #2c3e50; color: white; border: none; border-radius: 15px; font-weight: 700; }
.btn-submit-final {
  flex-grow: 1; padding: 15px; border: none; border-radius: 15px;
  font-weight: 700; font-size: 1.1rem;
  background: linear-gradient(135deg, #00c6ff 0%, #0072ff 100%);
  color: white; box-shadow: 0 4px 15px rgba(0, 114, 255, 0.3);
}
.btn-main-gradient {
  background: linear-gradient(135deg, #2c3e50 0%, #42b983 100%);
  color: white; border: none; padding: 18px 50px; border-radius: 50px;
  font-size: 1.2rem; font-weight: 800; box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}

.fade-in { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>
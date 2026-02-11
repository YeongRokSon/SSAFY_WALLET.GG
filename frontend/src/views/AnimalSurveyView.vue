<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useFinanceStore } from '@/stores/finance' // 스토어 사용
import axios from 'axios'

const router = useRouter()
const store = useAuthStore()
const financeStore = useFinanceStore() // 스토어 연결

const questions = ref([])
const currentIdx = ref(0)
const answers = ref([])
const loading = ref(false)

// 1. 질문 가져오기
const fetchQuestions = async () => {
    try {
        const res = await axios.get('http://127.0.0.1:8000/api/animals/questions/')
        questions.value = res.data
    } catch (err) {
        console.error(err)
        alert('질문을 불러오는데 실패했습니다.')
    }
}

// 2. 답변 선택 시
const selectAnswer = async (optionIndex) => {
    answers.value.push(optionIndex)

    if (currentIdx.value < questions.value.length - 1) {
        currentIdx.value++
    } else {
        await submitSurvey()
    }
}

// 3. 결과 제출 및 이동
const submitSurvey = async () => {
    loading.value = true
    try {
        // [변경] 스토어에 있는 자산 정보(userInfo)도 함께 백엔드로 전송하도록 payload 구성
        // AssetInputView에서 입력했던 나이, 연봉, 자산 정보가 여기서 DB로 넘어갑니다.
        const payload = {
            answers: answers.value,
            user_info: financeStore.userInfo // { age, salary, assets, ... }
        }

        const res = await axios.post(
            'http://127.0.0.1:8000/api/animals/submit/', 
            payload, // [변경] 기존 객체 대신 user_info가 포함된 payload 전송
            { headers: { Authorization: `Token ${store.token}` } }
        )
        
        // [변경] 결과 데이터를 스토어에 저장 (AnalysisResultView에서 사용하기 위해)
        financeStore.analysisResult = res.data
        
        // 결과 종합 페이지로 이동
        router.push({ name: 'analysis-result' })
        
    } catch (err) {
        console.error(err)
        alert('결과 분석 중 오류가 발생했습니다.')
        answers.value = []
        currentIdx.value = 0
    } finally {
        loading.value = false
    }
}

const progress = computed(() => {
    if (questions.value.length === 0) return 0
    return ((currentIdx.value + 1) / questions.value.length) * 100
})

onMounted(() => {
    if (!store.token) {
        alert('로그인이 필요합니다.')
        router.push({ name: 'login' })
        return
    }
    fetchQuestions()
})
</script>

<template>
  <div class="survey-container py-5">
    
    <div v-if="loading" class="loading-screen text-center">
        <div class="spinner-border text-primary mb-3" role="status"></div>
        <h3>AI가 당신의 투자 성향을 분석하고 있어요... 🧠</h3>
        <p class="text-muted">자산 정보와 답변을 종합하는 중입니다.</p>
    </div>

    <div v-else-if="questions.length > 0" class="question-card shadow">
        <div class="progress-area mb-4">
            <div class="d-flex justify-content-between mb-2 small text-muted">
                <span>질문 {{ currentIdx + 1 }}</span>
                <span>{{ questions.length }}</span>
            </div>
            <div class="progress" style="height: 6px;">
                <div class="progress-bar bg-success" :style="{ width: progress + '%' }"></div>
            </div>
        </div>

        <h3 class="question-text mb-4">
            Q{{ currentIdx + 1 }}. <br>
            {{ questions[currentIdx].question }}
        </h3>

        <div class="options-list">
            <button 
                v-for="(option, idx) in questions[currentIdx].options" 
                :key="idx"
                class="option-btn"
                @click="selectAnswer(idx)"
            >
                {{ option.text }}
            </button>
        </div>
    </div>

  </div>
</template>

<style scoped>
.survey-container { max-width: 600px; margin: 0 auto; min-height: 80vh; display: flex; flex-direction: column; justify-content: center; }

.question-card {
    background: white;
    border-radius: 24px;
    padding: 40px 30px;
    border: 1px solid #f0f0f0;
}

.question-text {
    font-weight: 800;
    color: #2c3e50;
    line-height: 1.4;
    font-size: 1.2rem;
}

.options-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.option-btn {
    background: #f8f9fa;
    border: 2px solid #e9ecef;
    padding: 16px 20px;
    border-radius: 16px;
    text-align: left;
    font-size: 1rem;
    font-weight: 600;
    color: #495057;
    transition: all 0.2s ease;
}

.option-btn:hover {
    background: #e6fcf5;
    border-color: #20c997;
    color: #0ca678;
    transform: translateY(-2px);
}

.loading-screen { padding: 50px; }
</style>
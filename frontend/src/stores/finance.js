import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useFinanceStore = defineStore('finance', () => {
  const userInfo = ref(null)       // 사용자 입력 정보
  const analysisResult = ref(null) // AI 분석 결과

  return { userInfo, analysisResult }
}, { persist: true }) // persist가 없다면 이 부분 지워도 됨
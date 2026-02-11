import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'

export const useServiceStore = defineStore('services', () => {
  const goldPrice = ref([])
  const youtubeVideos = ref([])
  
  // 1. 금/은 시세 가져오기
  const getExchangeRates = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:8000/services/gold-silver/')
      goldPrice.value = res.data.gold
    } catch (err) {
      console.error(err)
    }
  }

  // 2. 유튜브 검색
  const searchYoutube = async (keyword) => {
    try {
      const res = await axios.get('http://127.0.0.1:8000/services/youtube/', {
        params: { keyword }
      })
      youtubeVideos.value = res.data.items
    } catch (err) {
      console.error(err)
    }
  }

  return { goldPrice, youtubeVideos, getExchangeRates, searchYoutube }
})
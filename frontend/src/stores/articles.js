import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { useAuthStore } from './auth'

export const useArticleStore = defineStore('articles', () => {
  const articles = ref([])
  const authStore = useAuthStore()

  // 1. 게시글 목록 가져오기
  const getArticles = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:8000/articles/articles/')
      articles.value = res.data
    } catch (err) {
      console.error(err)
    }
  }

  // 2. 글 쓰기
  const createArticle = async (payload) => {
    if (!authStore.token) {
      alert('로그인이 필요해!')
      return
    }
    try {
      await axios.post('http://127.0.0.1:8000/articles/articles/', payload, {
        headers: {
          Authorization: `Token ${authStore.token}`
        }
      })
      // 글 쓰고 나서 목록 다시 불러오기
      await getArticles()
    } catch (err) {
      console.error(err)
    }
  }

  return { articles, getArticles, createArticle }
})
import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'

export const useProductStore = defineStore('products', () => {
  const products = ref([]) // 전체 상품 리스트
  const product = ref(null) // 상세 상품 정보

  // 1. 데이터 저장 (관리자용, 혹은 버튼 눌러서 갱신)
  const saveProducts = async () => {
    try {
      await axios.get('http://127.0.0.1:8000/products/save-deposit-products/')
      alert('금융감독원 데이터 저장 완료!')
    } catch (err) {
      console.error(err)
    }
  }

  // 2. 전체 상품 조회
  const getProducts = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:8000/products/deposit-products/')
      products.value = res.data
    } catch (err) {
      console.error(err)
    }
  }

  // 3. 상품 상세 조회
  const getProductDetail = async (id) => {
    try {
      const res = await axios.get(`http://127.0.0.1:8000/products/deposit-products/${id}/`)
      product.value = res.data
    } catch (err) {
      console.error(err)
    }
  }

  return { products, product, saveProducts, getProducts, getProductDetail }
})
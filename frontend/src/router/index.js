import { createRouter, createWebHistory } from 'vue-router'

// [1] 기본 페이지 및 인증
import HomeView from '@/views/HomeView.vue'
import AuthView from '@/views/AuthView.vue'
import ProfileView from '@/views/ProfileView.vue'
import ProfileEditView from '@/components/ProfileEditView.vue'
import LikedProductsView from '@/components/LikedProductsView.vue'
import JoinedProductsView from '@/components/JoinedProductsView.vue'
import ProfileYoutube from '@/components/ProfileYoutube.vue'

// [2] 금융 기능
import ProductView from '@/views/ProductView.vue'
import BankMapView from '@/views/BankMapView.vue'
import ExchangeView from '@/views/ExchangeView.vue'
import YoutubeView from '@/views/YoutubeView.vue'

// [3] 게시판 기능
import ArticleView from '@/views/ArticleView.vue'
import ArticleCreateView from '@/views/ArticleCreateView.vue'
import ArticleDetailView from '@/views/ArticleDetailView.vue'
import ArticleUpdateView from '@/views/ArticleUpdateView.vue'

// [4] AI 자산 분석
import AssetInputView from '@/views/AssetInputView.vue'
import AnimalSurveyView from '@/views/AnimalSurveyView.vue'
import AnalyzingView from '@/views/AnalyzingView.vue'
import AnalysisResultView from '@/views/AnalysisResultView.vue'
import ProductRecommendView from '@/views/ProductRecommendView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // === 메인 및 인증 ===
    { path: '/', name: 'home', component: HomeView },
    { path: '/auth', name: 'auth', component: AuthView },
    
    // === 프로필 관련 (상세 주소를 위로!) ===
    { path: '/profile/edit', name: 'profile-edit', component: ProfileEditView },
    { path: '/profile/liked-products',name: 'liked-products',component: LikedProductsView},
    { path: '/profile/joined-products',name: 'joined-products',component: JoinedProductsView},
    { path: '/profile/youtube', name: 'profile-youtube', component: ProfileYoutube },
    { path: '/profile/:username', name: 'profile', component: ProfileView },

    // === 금융 기능 ===
    { path: '/products', name: 'products', component: ProductView }, 
    { path: '/bank-map', name: 'bank-map', component: BankMapView },
    { path: '/exchange', name: 'exchange', component: ExchangeView },
    { path: '/youtube', name: 'youtube', component: YoutubeView },

    // === 게시판 기능 ===
    { path: '/articles', name: 'articles', component: ArticleView },
    { path: '/articles/create', name: 'article-create', component: ArticleCreateView },
    { path: '/articles/:id', name: 'article-detail', component: ArticleDetailView },
    { path: '/articles/:id/update', name: 'article-update', component: ArticleUpdateView },

    // 알고리즘 분석
    { path: '/asset-input', name: 'asset-input', component: AssetInputView },
    // 동물 성향 분석 페이지
    { path: '/animals/animal', name: 'animal-survey', component: AnimalSurveyView},

    // AI분석
    { path: '/analyzing', name: 'analyzing', component: AnalyzingView },
    { path: '/analysis-result', name: 'analysis-result', component: AnalysisResultView },
    { path: '/recommend', name: 'product-recommend', component: ProductRecommendView },
  ]
})

export default router
<script setup>
import { computed } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const store = useAuthStore()
const myUsername = computed(() => store.user?.username || store.username || localStorage.getItem('username'))

const logOut = () => {
  store.logOut()
}
</script>

<template>
  <header class="navbar">
    <div class="container">
      
      <RouterLink :to="{ name: 'home' }" class="brand-logo">
        💰 WALLET.GG
      </RouterLink>

      <nav class="nav-links">
        <RouterLink :to="{ name: 'products' }" class="nav-item">상품 조회</RouterLink>
        <RouterLink :to="{ name: 'exchange' }" class="nav-item">유동 자산</RouterLink>
        <RouterLink :to="{ name: 'youtube' }" class="nav-item">관심 종목</RouterLink>
        <RouterLink :to="{ name: 'bank-map' }" class="nav-item">주변 은행</RouterLink>
        <RouterLink :to="{ name: 'articles' }" class="nav-item">게시판</RouterLink>
        
        <RouterLink :to="{ name: 'asset-input' }" class="nav-item ai-btn">
          ✨ AI 자산 분석
        </RouterLink>

        <div class="divider"></div>

        <div v-if="!store.token" class="auth-menu">
          <RouterLink :to="{ name: 'auth' }" class="auth-btn login">로그인</RouterLink>
        </div>

        <div v-else class="auth-menu">
          <RouterLink 
            v-if="myUsername"
            :to="{ name: 'profile', params: { username: myUsername } }" 
            class="nav-item profile-link"
          >
            👤 내 프로필
          </RouterLink>
          <a href="#" @click.prevent="logOut" class="auth-btn logout">로그아웃</a>
        </div>
      </nav>
    </div>
  </header>

  <main>
    <RouterView />
  </main>

  <footer class="site-footer">
    <div class="footer-container">
      <div class="footer-section brand">
        <h3>💰 WALLET.GG</h3>
        <p>데이터 기반의 스마트한 자산 관리 솔루션.</p>
      </div>
      <div class="footer-section">
        <h4>Service</h4>
        <ul>
          <li><RouterLink :to="{ name: 'products' }">예적금 조회</RouterLink></li>
          <li><RouterLink :to="{ name: 'exchange' }">유동 자산</RouterLink></li>
        </ul>
      </div>
      <div class="footer-section">
        <h4>Contact</h4>
        <ul>
          <li>help@wallet.gg</li>
        </ul>
      </div>
    </div>
    <div class="copyright-bar">
      <p>&copy; 2025 WALLET.GG. All rights reserved.</p>
    </div>
  </footer>
</template>

<style scoped>
/* 헤더 스타일 (Dark Theme) */
.navbar {
  background-color: #2c3e50; /* 짙은 네이비 */
  color: white;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
  padding: 0.8rem 0;
}

.container {
  max-width: 1280px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 25px;
}

.brand-logo {
  font-size: 1.6rem;
  font-weight: 800;
  color: #fff; /* 흰색 로고 */
  text-decoration: none;
}

.nav-links { display: flex; align-items: center; gap: 25px; }

.nav-item {
  text-decoration: none;
  color: rgba(255, 255, 255, 0.7); /* 살짝 투명한 흰색 */
  font-weight: 500;
  transition: color 0.2s;
}

.nav-item:hover, .nav-item.router-link-active {
  color: #ffffff; /* 활성화 시 완전 흰색 */
  font-weight: 700;
}

/* AI 버튼 스타일 */
.ai-btn {
  background: linear-gradient(135deg, #00c6ff 0%, #0072ff 100%);
  color: white !important;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: bold;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}
.ai-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.3);
}

.divider { width: 1px; height: 15px; background-color: rgba(255,255,255,0.2); }

/* 인증 버튼 */
.auth-btn { text-decoration: none; padding: 6px 15px; border-radius: 5px; font-weight: bold; font-size: 0.9rem; }
.login { background: white; color: #2c3e50; }
.logout { color: #ff6b6b; font-size: 0.9rem; }

/* 푸터 스타일 (App.vue 하단에 추가했던 것과 동일) */
.site-footer { background-color: #2c3e50; color: #ecf0f1; padding-top: 60px; margin-top: auto; }
.footer-container { max-width: 1280px; margin: 0 auto; padding: 0 25px 40px; display: flex; justify-content: space-between; gap: 40px; }
.footer-section h3 { color: white; margin-bottom: 10px; }
.footer-section h4 { color: #3498db; margin-bottom: 15px; }
.footer-section ul { list-style: none; padding: 0; }
.footer-section ul li a { color: #bdc3c7; text-decoration: none; }
.copyright-bar { background-color: #243342; padding: 20px 0; text-align: center; color: #7f8c8d; font-size: 0.85rem; }
main { min-height: calc(100vh - 300px); padding-bottom: 40px; }
</style>
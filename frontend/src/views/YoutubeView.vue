<template>
  <div class="wallet-container">
    <div class="header-section">
      <h1>📺 금융 인사이트 (Media)</h1>
      <p>투자 전문가들의 최신 영상으로 시장의 흐름을 읽어보세요.</p>
    </div>

    <!-- 검색 섹션 -->
    <div class="search-section">
      <div class="search-bar">
        <input 
          v-model="searchQuery" 
          @keyup.enter="searchVideos(searchQuery)"
          type="text" 
          placeholder="관심 있는 투자 키워드를 입력해보세요" 
        />
        <button @click="searchVideos(searchQuery)" class="search-btn">
          <span>🔍</span>
        </button>
      </div>

      <!-- 추천 키워드 (태그) -->
      <div class="keyword-tags">
        <span class="tag-label">추천 검색어:</span>
        <button 
          v-for="keyword in keywords" 
          :key="keyword" 
          class="tag-chip"
          @click="searchVideos(keyword)"
        >
          #{{ keyword }}
        </button>
      </div>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="loading" class="state-container">
      <div class="loader"></div>
      <p>최신 영상을 불러오고 있습니다...</p>
    </div>

    <!-- 결과 없음 -->
    <div v-else-if="videos.length === 0 && searched" class="state-container">
      <div class="empty-icon">📭</div>
      <p>검색 결과가 없습니다.<br>다른 키워드로 다시 시도해보세요!</p>
    </div>

    <!-- 비디오 리스트 -->
    <div v-else class="video-grid">
      <div 
        v-for="video in videos" 
        :key="video.id.videoId" 
        class="video-card"
        @click="openDetail(video)"
      >
        <div class="thumbnail-wrapper">
            <img :src="video.snippet.thumbnails.high.url" alt="thumbnail" />
            <div class="play-overlay">
              <span class="play-icon">▶</span>
            </div>
            
            <!-- [추가] 북마크 버튼 -->
            <button 
              class="bookmark-btn" 
              :class="{ active: isBookmarked(video.id.videoId) }"
              @click.stop="toggleBookmark(video)"
              title="북마크에 저장"
            >
              <span v-if="isBookmarked(video.id.videoId)">♥</span>
              <span v-else>♡</span>
            </button>
        </div>
        
        <div class="card-content">
            <h3 class="video-title" v-html="decodeHtml(video.snippet.title)"></h3>
            <div class="channel-info">
              <div class="channel-profile"></div> 
              <div class="text-info">
                <span class="channel-name">{{ video.snippet.channelTitle }}</span>
                <span class="upload-date">{{ formatDate(video.snippet.publishTime) }}</span>
              </div>
            </div>
        </div>
      </div>
    </div>

    <!-- 상세 모달 -->
    <YoutubeDetail 
      v-if="selectedVideo" 
      :video="selectedVideo" 
      @close="selectedVideo = null" 
    />

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth' // 토큰 사용을 위해 추가
import YoutubeDetail from '@/components/YoutubeDetail.vue' 

const store = useAuthStore()
const searchQuery = ref('')
const videos = ref([])
const loading = ref(false)
const searched = ref(false)
const selectedVideo = ref(null)
const bookmarkedIds = ref([]) // 저장된 영상 ID 목록

// 추천 검색어 리스트
const keywords = ['삼성전자', '2차전지', '미국주식', 'ETF추천', '부동산전망', '비트코인']

const searchVideos = async (query) => {
  if (!query || !query.trim()) {
      alert('검색어를 입력해주세요!')
      return
  }

  searchQuery.value = query
  loading.value = true
  searched.value = true
  videos.value = []

  try {
    const res = await axios.get('http://127.0.0.1:8000/youtube/search/', {
        params: { q: query }
    })
    videos.value = res.data.items || []
  } catch (err) {
    console.error(err)
    alert('영상 정보를 불러오는데 실패했습니다.')
  } finally {
    loading.value = false
  }
}

// [추가] 북마크 여부 확인 함수
const isBookmarked = (videoId) => {
  return bookmarkedIds.value.includes(videoId)
}

// [추가] 북마크 토글 기능
const toggleBookmark = async (video) => {
  if (!store.token) {
    alert('로그인이 필요한 기능입니다!')
    return
  }

  const videoData = {
    videoId: video.id.videoId,
    title: video.snippet.title,
    thumbnail: video.snippet.thumbnails.high.url,
    channelTitle: video.snippet.channelTitle,
    publishTime: video.snippet.publishTime
  }

  try {
    const res = await axios.post('http://127.0.0.1:8000/youtube/bookmark/', videoData, {
      headers: { Authorization: `Token ${store.token}` }
    })
    
    if (res.data.bookmarked) {
      bookmarkedIds.value.push(video.id.videoId)
    } else {
      bookmarkedIds.value = bookmarkedIds.value.filter(id => id !== video.id.videoId)
    }
  } catch (err) {
    console.error('북마크 오류:', err)
    alert('북마크 처리에 실패했습니다.')
  }
}

// [추가] 내 북마크 목록 ID 가져오기 (초기 로딩 시)
const fetchMyBookmarks = async () => {
  if (!store.token) return
  try {
    const res = await axios.get('http://127.0.0.1:8000/youtube/bookmark/list/', {
      headers: { Authorization: `Token ${store.token}` }
    })
    // 가져온 목록에서 ID만 추출해서 저장
    bookmarkedIds.value = res.data.map(v => v.id.videoId)
  } catch (err) {
    console.error('북마크 로드 실패:', err)
  }
}

const openDetail = (video) => {
    selectedVideo.value = video
}

const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString()
}

const decodeHtml = (html) => {
    const txt = document.createElement("textarea");
    txt.innerHTML = html;
    return txt.value;
}

onMounted(() => {
  fetchMyBookmarks() // 내 북마크 상태 확인
  searchVideos('재테크 기초')
})
</script>

<style scoped>
.wallet-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
  font-family: 'Pretendard', sans-serif;
}

.header-section {
  text-align: center;
  margin-bottom: 40px;
}
.header-section h1 { font-size: 2.2rem; font-weight: 800; color: #1a1a1a; margin-bottom: 10px; }
.header-section p { color: #666; font-size: 1.1rem; }

/* 검색 섹션 스타일 */
.search-section {
  max-width: 700px;
  margin: 0 auto 50px;
}

.search-bar {
  display: flex;
  background: white;
  border-radius: 50px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.08);
  padding: 5px;
  border: 1px solid #eee;
  transition: box-shadow 0.3s;
}
.search-bar:focus-within {
  box-shadow: 0 4px 20px rgba(44, 62, 80, 0.15);
  border-color: #2c3e50;
}

.search-bar input {
  flex: 1;
  border: none;
  background: transparent;
  padding: 15px 25px;
  font-size: 1rem;
  outline: none;
}

.search-btn {
  background: #2c3e50;
  color: white;
  border: none;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  font-size: 1.2rem;
  cursor: pointer;
  transition: transform 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.search-btn:hover { transform: scale(1.05); background: #34495e; }

/* 키워드 태그 */
.keyword-tags {
  margin-top: 15px;
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}
.tag-label { font-size: 0.9rem; color: #888; margin-right: 5px; }
.tag-chip {
  padding: 6px 14px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 20px;
  color: #495057;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}
.tag-chip:hover {
  background: #eef2ff;
  color: #2c3e50;
  border-color: #2c3e50;
}

/* 상태 표시 (로딩/빈 결과) */
.state-container {
  text-align: center;
  padding: 80px 0;
  color: #888;
}
.loader {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #ff0000; /* Youtube Red point */
  border-radius: 50%;
  width: 40px; height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 15px;
}
.empty-icon { font-size: 3rem; margin-bottom: 10px; opacity: 0.5; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* 비디오 그리드 */
.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 30px;
}

.video-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
  display: flex;
  flex-direction: column;
  position: relative; /* 북마크 버튼 위치 기준점 */
}
.video-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.12);
}

/* 썸네일 & 호버 효과 */
.thumbnail-wrapper {
  position: relative;
  width: 100%;
  padding-top: 56.25%; /* 16:9 비율 유지 */
  overflow: hidden;
  background: #000;
}
.thumbnail-wrapper img {
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
  object-fit: cover;
  opacity: 0.9;
  transition: opacity 0.3s;
}
.play-overlay {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.3);
  display: flex;
  justify-content: center;
  align-items: center;
  opacity: 0;
  transition: opacity 0.3s;
}
.play-icon {
  font-size: 3rem;
  color: white;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5));
}
.video-card:hover .play-overlay { opacity: 1; }
.video-card:hover img { opacity: 1; transform: scale(1.05); transition: transform 0.5s; }

/* [추가] 북마크 버튼 스타일 */
.bookmark-btn {
  position: absolute;
  top: 10px; right: 10px;
  background: rgba(0,0,0,0.6);
  border: none;
  border-radius: 50%;
  width: 36px; height: 36px;
  display: flex; justify-content: center; align-items: center;
  color: white; font-size: 1.3rem;
  cursor: pointer;
  transition: all 0.2s;
  z-index: 10;
}
.bookmark-btn:hover { transform: scale(1.1); background: rgba(0,0,0,0.8); }
.bookmark-btn.active { color: #ff4081; background: white; }

/* 카드 내용 */
.card-content {
  padding: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
}
.video-title {
  font-size: 1rem;
  font-weight: bold;
  color: #333;
  margin: 0 0 12px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.channel-info {
  display: flex;
  align-items: center;
  margin-top: auto;
}
.channel-profile {
  width: 32px; height: 32px;
  border-radius: 50%;
  background: #eee;
  margin-right: 10px;
}
.text-info { display: flex; flex-direction: column; }
.channel-name { font-size: 0.85rem; font-weight: 600; color: #555; }
.upload-date { font-size: 0.75rem; color: #999; }
</style>
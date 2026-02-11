<template>
  <div class="wallet-container">
    <div class="header-section">
      <h1>📺 내가 저장한 동영상</h1>
      <p>북마크한 금융/경제 영상을 모아보세요.</p>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="loading" class="state-container">
      <div class="loader"></div>
      <p>저장한 영상을 불러오는 중입니다...</p>
    </div>

    <!-- 결과 없음 -->
    <div v-else-if="videos.length === 0" class="state-container">
      <div class="empty-icon">📭</div>
      <p>저장된 영상이 없습니다.<br>관심 영상을 검색해서 북마크해보세요!</p>
      <button @click="router.push({ name: 'youtube' })" class="btn-link">
        영상 검색하러 가기 →
      </button>
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
            
            <!-- 삭제 버튼 (북마크 해제) -->
            <button 
              class="remove-btn" 
              @click.stop="removeBookmark(video.id.videoId)"
              title="북마크 삭제"
            >
              🗑️
            </button>
        </div>
        
        <div class="card-content">
            <h3 class="video-title" v-html="decodeHtml(video.snippet.title)"></h3>
            <div class="channel-info">
              <div class="text-info">
                <span class="channel-name">{{ video.snippet.channelTitle }}</span>
                <span class="upload-date">{{ formatDate(video.snippet.publishTime) }}</span>
              </div>
            </div>
        </div>
      </div>
    </div>

    <!-- 상세 모달 (기존 컴포넌트 재사용) -->
    <YoutubeDetail 
      v-if="selectedVideo" 
      :video="selectedVideo" 
      @close="selectedVideo = null" 
    />

    <!-- [추가] 프로필로 돌아가기 버튼 -->
    <div class="text-center mt-5">
      <button @click="goProfile" class="btn-back">
        내 프로필로 돌아가기
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import YoutubeDetail from '@/components/YoutubeDetail.vue' 

const store = useAuthStore()
const router = useRouter()

const videos = ref([])
const loading = ref(false)
const selectedVideo = ref(null)

// 1. 내 북마크 목록 가져오기
const fetchMyBookmarks = async () => {
  if (!store.token) {
    alert('로그인이 필요합니다.')
    router.push({ name: 'login' })
    return
  }

  loading.value = true
  try {
    // [수정] api/ 경로 추가
    const res = await axios.get('http://127.0.0.1:8000/youtube/bookmark/list/', {
      headers: { Authorization: `Token ${store.token}` }
    })
    videos.value = res.data
  } catch (err) {
    console.error('북마크 로드 실패:', err)
    alert('목록을 불러오지 못했습니다.')
  } finally {
    loading.value = false
  }
}

// 2. 북마크 삭제
const removeBookmark = async (videoId) => {
  if (!confirm('이 영상을 저장 목록에서 삭제할까요?')) return

  try {
    // [수정] api/ 경로 추가
    await axios.post('http://127.0.0.1:8000/youtube/bookmark/', 
      { videoId }, 
      { headers: { Authorization: `Token ${store.token}` } }
    )
    
    videos.value = videos.value.filter(v => v.id.videoId !== videoId)
    
  } catch (err) {
    console.error('삭제 오류:', err)
    alert('삭제 처리에 실패했습니다.')
  }
}

// [추가] 프로필 이동 함수
const goProfile = () => {
    const username = store.user?.username || store.username || localStorage.getItem('username')
    
    if (username) {
        router.push({ 
            name: 'profile', 
            params: { username: username } 
        })
    } else {
        alert("로그인 정보가 만료되었습니다. 다시 로그인해주세요.")
        router.push({ name: 'login' })
    }
}

const openDetail = (video) => {
    selectedVideo.value = video
}

const formatDate = (dateString) => {
    if (!dateString) return ''
    const date = new Date(dateString)
    return date.toLocaleDateString()
}

const decodeHtml = (html) => {
    const txt = document.createElement("textarea");
    txt.innerHTML = html;
    return txt.value;
}

onMounted(() => {
  fetchMyBookmarks()
})
</script>

<style scoped src="@/views/ProductView.css"></style>

<style scoped>
/* YoutubeView.css의 스타일을 가져오되, 일부 수정 */
.header-section { text-align: center; margin-bottom: 40px; }
.header-section h1 { font-size: 2rem; font-weight: 800; color: #1a1a1a; margin-bottom: 10px; }
.header-section p { color: #666; font-size: 1rem; }

.state-container { text-align: center; padding: 80px 0; color: #888; }
.empty-icon { font-size: 3rem; margin-bottom: 15px; opacity: 0.5; }
.btn-link {
    margin-top: 15px;
    padding: 10px 20px;
    background: #2c3e50;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: bold;
    transition: background 0.2s;
}
.btn-link:hover { background: #34495e; }

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
  position: relative;
}
.video-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.12);
}

.thumbnail-wrapper {
  position: relative;
  width: 100%;
  padding-top: 56.25%;
  overflow: hidden;
  background: #000;
}
.thumbnail-wrapper img {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; opacity: 0.9;
}
.play-overlay {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.3);
  display: flex; justify-content: center; align-items: center; opacity: 0; transition: opacity 0.3s;
}
.play-icon { font-size: 3rem; color: white; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5)); }
.video-card:hover .play-overlay { opacity: 1; }

/* 삭제 버튼 스타일 */
.remove-btn {
  position: absolute;
  top: 10px; right: 10px;
  background: rgba(0,0,0,0.6);
  border: none;
  border-radius: 50%;
  width: 36px; height: 36px;
  display: flex; justify-content: center; align-items: center;
  color: #fff;
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.2s;
  z-index: 10;
}
.remove-btn:hover { background: #ef4444; transform: scale(1.1); }

.card-content { padding: 16px; flex: 1; display: flex; flex-direction: column; }
.video-title {
  font-size: 1rem; font-weight: bold; color: #333; margin: 0 0 12px; line-height: 1.4;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.channel-info { margin-top: auto; }
.channel-name { font-size: 0.85rem; font-weight: 600; color: #555; display: block; }
.upload-date { font-size: 0.75rem; color: #999; }

/* [추가] 돌아가기 버튼 스타일 */
.btn-back {
  padding: 10px 24px;
  background-color: transparent;
  color: #6c757d;
  border: 1px solid #6c757d;
  border-radius: 50px;
  font-weight: 600;
  transition: all 0.2s;
  cursor: pointer;
}
.btn-back:hover {
  background-color: #6c757d;
  color: white;
}
</style>
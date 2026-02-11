<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content" v-if="video">
      <header>
        <div class="title-area">
            <h2>{{ decodeHtml(video.snippet.title) }}</h2>
        </div>
        
        <div class="header-actions">
            <!-- 북마크 버튼 -->
            <button 
                class="bookmark-btn" 
                :class="{ active: isBookmarked }" 
                @click="toggleBookmark"
                title="북마크"
            >
                <span v-if="isBookmarked">♥</span>
                <span v-else>♡</span>
            </button>
            <button class="close-btn" @click="$emit('close')">✕</button>
        </div>
      </header>

      <div class="video-container">
        <iframe 
          :src="`https://www.youtube.com/embed/${video.id.videoId}?autoplay=1`" 
          frameborder="0" 
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
          allowfullscreen
        ></iframe>
      </div>

      <div class="modal-body">
        <!-- 채널 정보 및 게시일 -->
        <div class="channel-info">
            <span class="channel-name">📺 {{ video.snippet.channelTitle }}</span>
            <span class="date">{{ formatDate(video.snippet.publishTime) }}</span>
        </div>

        <!-- [신규] 통계 정보 (조회수, 좋아요) -->
        <div class="stats-bar" v-if="videoStats">
            <span class="stat-item" v-if="videoStats.viewCount">
                👁️ 조회수 {{ formatCount(videoStats.viewCount) }}회
            </span>
            <span class="stat-item" v-if="videoStats.likeCount">
                👍 좋아요 {{ formatCount(videoStats.likeCount) }}개
            </span>
            <span class="stat-item" v-if="videoStats.commentCount">
                💬 댓글 {{ formatCount(videoStats.commentCount) }}개
            </span>
        </div>

        <!-- [신규] 태그 목록 -->
        <div class="tags-container" v-if="videoTags && videoTags.length > 0">
            <span v-for="tag in videoTags.slice(0, 5)" :key="tag" class="tag-badge">#{{ tag }}</span>
        </div>

        <hr class="divider">

        <!-- 상세 설명 (기본 정보가 없으면 상세 조회한 것으로 대체) -->
        <div class="description-box">
            <h4>📝 영상 설명</h4>
            <p class="description">
                {{ fullDescription || video.snippet.description || '상세 설명이 없습니다.' }}
            </p>
        </div>
      </div>

      <footer>
        <button class="action-btn close" @click="$emit('close')">닫기</button>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  video: Object
})
const emit = defineEmits(['close'])
const store = useAuthStore()

const isBookmarked = ref(false)

// 상세 정보 상태 변수
const fullDescription = ref('')
const videoStats = ref(null) // { viewCount, likeCount, ... }
const videoTags = ref([])

// [신규] 영상 상세 정보(통계, 전체설명) 가져오기
const fetchVideoDetail = async () => {
    try {
        // 백엔드에 새로 만들 API 엔드포인트 호출
        const res = await axios.get('http://127.0.0.1:8000/youtube/video/', {
            params: { id: props.video.id.videoId }
        })
        
        if (res.data.items && res.data.items.length > 0) {
            const detail = res.data.items[0]
            fullDescription.value = detail.snippet.description
            videoStats.value = detail.statistics
            videoTags.value = detail.snippet.tags
        }
    } catch (err) {
        console.error('상세 정보 로드 실패:', err)
    }
}

// 1. 북마크 상태 확인
const checkBookmarkStatus = async () => {
    if (!store.token) return
    try {
        const res = await axios.get('http://127.0.0.1:8000/youtube/bookmark/list/', {
            headers: { Authorization: `Token ${store.token}` }
        })
        const myBookmarks = res.data.map(v => v.id.videoId)
        isBookmarked.value = myBookmarks.includes(props.video.id.videoId)
    } catch (err) {
        console.error('북마크 확인 실패:', err)
    }
}

// 2. 북마크 토글
const toggleBookmark = async () => {
    if (!store.token) {
        alert('로그인이 필요한 기능입니다!')
        return
    }

    const videoData = {
        videoId: props.video.id.videoId,
        title: props.video.snippet.title,
        thumbnail: props.video.snippet.thumbnails.high.url,
        channelTitle: props.video.snippet.channelTitle,
        publishTime: props.video.snippet.publishTime
    }

    try {
        const res = await axios.post('http://127.0.0.1:8000/youtube/bookmark/', videoData, {
            headers: { Authorization: `Token ${store.token}` }
        })
        isBookmarked.value = res.data.bookmarked
    } catch (err) {
        console.error('북마크 오류:', err)
        alert('북마크 처리에 실패했습니다.')
    }
}

const decodeHtml = (html) => {
    const txt = document.createElement("textarea");
    txt.innerHTML = html;
    return txt.value;
}

const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString()
}

const formatCount = (num) => {
    return Number(num).toLocaleString()
}

onMounted(() => {
    checkBookmarkStatus()
    fetchVideoDetail() // 상세 정보 호출
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.modal-content {
  background: white;
  width: 90%;
  max-width: 800px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
  display: flex;
  flex-direction: column;
}

header {
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border-bottom: 1px solid #eee;
}

.title-area { flex: 1; margin-right: 15px; }
h2 { margin: 0; font-size: 1.2rem; line-height: 1.4; color: #333; }

.header-actions { display: flex; align-items: center; gap: 10px; }

.close-btn {
  background: none; border: none; font-size: 1.5rem; cursor: pointer; line-height: 1; color: #999;
}
.close-btn:hover { color: #333; }

/* 북마크 버튼 스타일 */
.bookmark-btn {
    background: #f1f3f5; border: none; border-radius: 50%;
    width: 40px; height: 40px; display: flex; justify-content: center; align-items: center;
    font-size: 1.5rem; color: #ccc; cursor: pointer; transition: all 0.2s;
}
.bookmark-btn:hover { background: #e9ecef; transform: scale(1.1); }
.bookmark-btn.active { color: #ff4081; background: #fff0f6; }

.video-container {
  position: relative; padding-bottom: 56.25%; height: 0; background: black;
}
.video-container iframe {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
}

.modal-body { padding: 20px; max-height: 40vh; overflow-y: auto; }

.channel-info {
    display: flex; justify-content: space-between; margin-bottom: 15px;
    color: #666; font-size: 0.9rem;
}
.channel-name { font-weight: bold; color: #d32f2f; }

/* [신규 스타일] 통계 및 태그 */
.stats-bar {
    display: flex; gap: 15px; margin-bottom: 12px;
    color: #555; font-size: 0.9rem; font-weight: 600;
}
.tags-container {
    display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 15px;
}
.tag-badge {
    background: #f1f3f5; color: #495057; padding: 4px 10px;
    border-radius: 12px; font-size: 0.8rem;
}
.divider { margin: 15px 0; border: 0; border-top: 1px solid #eee; }

.description-box h4 {
    font-size: 1rem; font-weight: bold; margin-bottom: 8px; color: #333;
}
.description {
    line-height: 1.6; color: #555; font-size: 0.95rem; white-space: pre-wrap;
}

footer { padding: 15px 20px; background: #f9f9f9; text-align: right; }

.action-btn {
  padding: 10px 20px; border: none; border-radius: 8px;
  cursor: pointer; font-weight: bold;
}
.action-btn.close { background: #eee; color: #333; }
.action-btn.close:hover { background: #ddd; }
</style>


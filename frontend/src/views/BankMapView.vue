<template>
  <div class="map-page-container">
    
    <!-- 1. 플로팅 컨트롤 패널 (지도 위에 뜸) -->
    <div class="floating-panel">
      <div class="panel-header">
        <h2>🏦 은행 찾기 & 길찾기</h2>
        <p>가까운 은행을 찾고 최적의 경로를 확인하세요.</p>
      </div>

      <!-- 경로 설정 영역 -->
      <div class="route-inputs">
        <!-- 출발지 설정 -->
        <div 
          class="input-group" 
          :class="{ active: currentMode === 'start', filled: startInfo }"
          @click="setMode('start')"
        >
          <div class="icon-area">
            <!-- 동물 이미지가 있으면 그것을, 없으면 기본 점 표시 -->
            <img v-if="userAnimal" :src="`/images/animals/${userAnimal}.png`" class="animal-dot" alt="start">
            <span v-else class="dot start"></span>
            <div class="line"></div>
          </div>
          <div class="text-area">
            <label>출발지</label>
            <div class="value text-truncate">
              {{ startInfo ? startInfo.address : '지도를 클릭해 위치를 설정하세요' }}
            </div>
          </div>
          <span v-if="currentMode === 'start'" class="badge">설정중</span>
        </div>

        <!-- 도착지 설정 -->
        <div 
          class="input-group" 
          :class="{ active: currentMode === 'end', filled: endInfo }"
          @click="setMode('end')"
        >
          <div class="icon-area">
            <span class="dot end"></span>
          </div>
          <div class="text-area">
            <label>도착지 (은행)</label>
            <div class="value text-truncate">
              {{ endInfo ? endInfo.place_name : '지도에서 은행을 선택하세요' }}
            </div>
          </div>
          <span v-if="currentMode === 'end'" class="badge">설정중</span>
        </div>
      </div>

      <!-- 주소 필터 -->
      <div class="filter-section">
        <select v-model="selectedSido" @change="onSidoChange" class="custom-select">
          <option value="">시/도 선택</option>
          <option v-for="sido in sidoList" :key="sido" :value="sido">{{ sido }}</option>
        </select>
        <select v-model="selectedSigugun" @change="moveMapToAddress" class="custom-select">
          <option value="">시/군/구 선택</option>
          <option v-for="sigugun in sigugunList" :key="sigugun" :value="sigugun">{{ sigugun }}</option>
        </select>
      </div>

      <!-- 액션 버튼 -->
      <button 
        class="action-btn" 
        :class="{ ready: startInfo && endInfo }"
        @click="runRouteGuide" 
        :disabled="!startInfo || !endInfo"
      >
        🚗 경로 계산하기
      </button>

      <!-- 결과 카드 -->
      <transition name="slide-fade">
        <div v-if="routeResult" class="result-card">
            <div class="result-header">
                <span class="icon">🏁</span> 경로 안내 결과
            </div>
            <div class="result-body">
                <div class="result-item">
                    <span class="label">소요 시간</span>
                    <span class="data highlight">{{ routeResult.duration }}분</span>
                </div>
                <div class="divider"></div>
                <div class="result-item">
                    <span class="label">총 거리</span>
                    <span class="data">{{ formatDistance(routeResult.distance) }}</span>
                </div>
            </div>
        </div>
      </transition>
    </div>

    <!-- 2. 지도 영역 -->
    <div id="map" class="full-map"></div>

  </div>
</template>

<script setup>
import { onMounted, ref, computed, watch } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth' // [추가] 인증 스토어
import regionData from '@/assets/data.json'
import myMarkerImg from '@/assets/11.gif'    
import bankMarkerImg from '@/assets/bank.png' 

const store = useAuthStore()
const userAnimal = ref(null) // [추가] 사용자 동물 성향 저장

// 상태 변수
const currentMode = ref('start')
const selectedSido = ref('')
const selectedSigugun = ref('')

const startInfo = ref(null) 
const endInfo = ref(null)   
const routeResult = ref(null)

let map = null
let geocoder = null
let startMarker = null   
let searchMarker = null  
let bankMarkers = []     
let currentPolyline = null

const sidoList = computed(() => regionData.mapInfo.map(item => item.name))
const sigugunList = computed(() => {
  if (!selectedSido.value) return []
  const target = regionData.mapInfo.find(item => item.name === selectedSido.value)
  return target ? target.countries : []
})

// [추가] 사용자 동물 성향 가져오기
const fetchUserAnimal = async () => {
  if (!store.token) return
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/products/portfolio/latest/', {
      headers: { Authorization: `Token ${store.token}` }
    })
    if (res.data.exists && res.data.analysis_result) {
      userAnimal.value = res.data.analysis_result.animal
    }
  } catch (e) {
    console.error("동물 정보 로드 실패", e)
  }
}

// [추가] 동물 정보가 로드되면 마커 이미지 업데이트
watch(userAnimal, () => {
    if (startMarker) {
        // 현재 위치 유지하면서 마커 이미지만 갱신
        const pos = startMarker.getPosition()
        setStartPoint(pos.getLat(), pos.getLng())
    }
})

onMounted(() => {
  fetchUserAnimal() // [추가] 실행
  
  if (!window.kakao || !window.kakao.maps) {
    const script = document.createElement('script')
    const jsKey = import.meta.env.VITE_KAKAO_JS_KEY 
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?autoload=false&appkey=${jsKey}&libraries=services`
    script.onload = () => kakao.maps.load(initMap)
    document.head.appendChild(script)
  } else {
    initMap()
  }
})

const initMap = () => {
  const container = document.getElementById('map')
  const options = {
    center: new kakao.maps.LatLng(37.5012743, 127.039585),
    level: 5
  }
  map = new kakao.maps.Map(container, options)
  geocoder = new kakao.maps.services.Geocoder()

  setStartPoint(37.5012743, 127.039585)

  kakao.maps.event.addListener(map, 'click', function(mouseEvent) {
      const lat = mouseEvent.latLng.getLat()
      const lng = mouseEvent.latLng.getLng()

      if (currentMode.value === 'start') {
          setStartPoint(lat, lng)
      } else {
          setSearchPoint(lat, lng)
      }
  })
}

const setMode = (mode) => {
    currentMode.value = mode
}

const onSidoChange = () => { selectedSigugun.value = '' }

const moveMapToAddress = () => {
  if (!selectedSido.value || !selectedSigugun.value) return
  const fullAddress = `${selectedSido.value} ${selectedSigugun.value}`
  
  geocoder.addressSearch(fullAddress, (result, status) => {
     if (status === kakao.maps.services.Status.OK) {
        const newLat = parseFloat(result[0].y)
        const newLng = parseFloat(result[0].x)
        
        map.setCenter(new kakao.maps.LatLng(newLat, newLng))
        map.setLevel(5)

        if (currentMode.value === 'start') {
            setStartPoint(newLat, newLng)
        } else {
            setSearchPoint(newLat, newLng)
        }
     }
  })
}

// [수정] 출발지 마커 설정 (동물 이미지 적용)
const setStartPoint = (lat, lng) => {
    geocoder.coord2Address(lng, lat, (result, status) => {
        let addr = '위치 정보 없음'
        if (status === kakao.maps.services.Status.OK) {
            addr = result[0].address ? result[0].address.address_name : result[0].road_address.address_name
        }
        startInfo.value = { lat, lng, address: addr }
    })

    const pos = new kakao.maps.LatLng(lat, lng)
    
    // 이미지 결정: 동물이면 동물 이미지, 없으면 기본 이미지
    let markerImageSrc = myMarkerImg
    let markerSize = new kakao.maps.Size(40, 40)

    if (userAnimal.value) {
        markerImageSrc = `/images/animals/${userAnimal.value}.png`
        markerSize = new kakao.maps.Size(50, 50) // 동물은 조금 더 크게
    }

    const img = new kakao.maps.MarkerImage(markerImageSrc, markerSize)
    
    if (startMarker) {
        startMarker.setPosition(pos)
        startMarker.setImage(img) // 이미지 업데이트
    } else {
        startMarker = new kakao.maps.Marker({ position: pos, map: map, image: img, title: '출발지' })
    }

    if (currentPolyline) currentPolyline.setMap(null)
    routeResult.value = null
}

const setSearchPoint = (lat, lng) => {
    const pos = new kakao.maps.LatLng(lat, lng)
    
    if (searchMarker) {
        searchMarker.setPosition(pos)
        searchMarker.setMap(map)
    } else {
        searchMarker = new kakao.maps.Marker({ position: pos, map: map })
    }
    fetchNearbyBanks(lat, lng)
}

const fetchNearbyBanks = async (lat, lng) => {
  try {
    bankMarkers.forEach(m => m.setMap(null))
    bankMarkers = []

    const response = await axios.get('http://127.0.0.1:8000/services/bank-search/', {
      params: { keyword: '은행', x: lng, y: lat }
    })

    if (response.data.documents) {
        const imageSize = new kakao.maps.Size(35, 35)
        const img = new kakao.maps.MarkerImage(bankMarkerImg, imageSize)

        response.data.documents.forEach(place => {
            const pLat = parseFloat(place.y)
            const pLng = parseFloat(place.x)
            
            const marker = new kakao.maps.Marker({
                map: map,
                position: new kakao.maps.LatLng(pLat, pLng),
                title: place.place_name,
                image: img
            })
            bankMarkers.push(marker)

            const safeName = place.place_name.replace(/'/g, "\\'")
            
            const iwContent = `
                <div style="padding:15px; min-width:200px; border-radius:8px; background:white;">
                    <h4 style="margin:0 0 5px; font-size:14px; font-weight:bold; color:#333;">${place.place_name}</h4>
                    <p style="margin:0 0 10px; font-size:11px; color:#888;">${place.road_address_name || place.address_name}</p>
                    <button onclick="window.selectDestination(${pLng}, ${pLat}, '${safeName}')"
                        style="width:100%; background:#2c3e50; color:white; border:none; padding:8px 0; border-radius:6px; font-size:12px; font-weight:bold; cursor:pointer; transition:0.2s;">
                        🚩 도착지로 설정
                    </button>
                </div>
            `
            const infowindow = new kakao.maps.InfoWindow({ content: iwContent, removable: true })

            kakao.maps.event.addListener(marker, 'click', () => {
                infowindow.open(map, marker)
            })
        })
    }
  } catch (error) {
    console.error(error)
  }
}

window.selectDestination = (lng, lat, name) => {
    endInfo.value = { lat, lng, place_name: name }
    alert(`도착지가 [${name}]으로 설정되었습니다!`)
    currentMode.value = null
}

const runRouteGuide = async () => {
    if (!startInfo.value || !endInfo.value) return

    try {
        if (currentPolyline) currentPolyline.setMap(null)

        const sp = `${startInfo.value.lng},${startInfo.value.lat}`
        const ep = `${endInfo.value.lng},${endInfo.value.lat}`

        const response = await axios.get('http://127.0.0.1:8000/services/route/', {
            params: { sp, ep }
        })

        const result = response.data
        if (result.code && result.code < 0) {
            alert(`[오류] ${result.msg}`)
            return
        }

        if (result.routes && result.routes.length > 0) {
            drawPath(result.routes[0])
            const summary = result.routes[0].summary
            routeResult.value = {
                duration: Math.round(summary.duration / 60),
                distance: summary.distance
            }
        } else {
            alert("경로를 찾을 수 없습니다.")
        }
    } catch (e) {
        console.error(e)
        alert("경로 요청 실패")
    }
}

const drawPath = (routeData) => {
    const linePath = []
    routeData.sections.forEach(section => {
        section.roads.forEach(road => {
            const vertexes = road.vertexes
            for (let i = 0; i < vertexes.length; i += 2) {
                linePath.push(new kakao.maps.LatLng(vertexes[i + 1], vertexes[i]))
            }
        })
    })
    currentPolyline = new kakao.maps.Polyline({
        path: linePath,
        strokeWeight: 7,
        strokeColor: '#3b82f6', 
        strokeOpacity: 0.8,
        strokeStyle: 'solid'
    })
    currentPolyline.setMap(map)
}

const formatDistance = (dist) => {
    if (dist >= 1000) return `${(dist / 1000).toFixed(1)}km`
    return `${dist}m`
}
</script>

<style scoped>
.map-page-container {
  position: relative;
  width: 100%;
  max-width: 1200px; 
  height: 700px;     
  margin: 40px auto; 
  overflow: hidden;
  background-color: #f8f9fa;
  border-radius: 24px; 
  box-shadow: 0 10px 40px rgba(0,0,0,0.1); 
}

/* 지도 전체 채우기 */
.full-map {
  width: 100%;
  height: 100%;
  z-index: 0;
}

/* 플로팅 패널 스타일 */
.floating-panel {
  position: absolute;
  top: 20px;
  left: 20px;
  width: 360px;
  max-width: calc(100% - 40px);
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 5px 20px rgba(0,0,0,0.08);
  z-index: 10;
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: calc(100% - 40px);
  overflow-y: auto;
}

.floating-panel::-webkit-scrollbar { width: 6px; }
.floating-panel::-webkit-scrollbar-thumb { background-color: #ddd; border-radius: 3px; }

.panel-header h2 { margin: 0; font-size: 1.4rem; font-weight: 800; color: #2c3e50; }
.panel-header p { margin: 5px 0 0; font-size: 0.9rem; color: #7f8c8d; }

.route-inputs {
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 16px;
  border: 1px solid #eee;
  overflow: hidden;
}

.input-group {
  display: flex;
  align-items: center;
  padding: 15px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.input-group:hover { background-color: #f8f9fa; }
.input-group.active { background-color: #eef2ff; }
.input-group:not(:last-child) { border-bottom: 1px solid #f0f0f0; }

.icon-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-right: 15px;
  width: 24px; /* 조금 넓혀서 동물 이미지 들어갈 공간 확보 */
}

/* 동물 이미지 스타일 (추가됨) */
.animal-dot {
    width: 30px;
    height: 30px;
    object-fit: contain;
    border-radius: 50%;
    border: 2px solid #3b82f6;
    background: white;
}

.dot { width: 10px; height: 10px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 0 2px #ccc; }
.dot.start { background-color: #3b82f6; box-shadow: 0 0 0 2px #3b82f6; }
.dot.end { background-color: #ef4444; box-shadow: 0 0 0 2px #ef4444; }

.line {
  width: 2px;
  height: 25px; 
  background: #e0e0e0;
  margin-top: 5px;
  position: absolute;
  top: 25px;
}

.text-area { flex: 1; overflow: hidden; }
.text-area label { display: block; font-size: 0.75rem; color: #888; margin-bottom: 2px; }
.text-area .value { font-size: 0.95rem; font-weight: 600; color: #333; }

.badge {
  background: #2c3e50;
  color: white;
  font-size: 0.7rem;
  padding: 4px 8px;
  border-radius: 12px;
}

.filter-section { display: flex; gap: 10px; }
.custom-select {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 0.9rem;
  outline: none;
  cursor: pointer;
  background: white;
}

.action-btn {
  width: 100%;
  padding: 14px;
  border: none;
  border-radius: 12px;
  background-color: #e0e0e0;
  color: #888;
  font-weight: 700;
  font-size: 1rem;
  cursor: not-allowed;
  transition: all 0.3s;
}
.action-btn.ready {
  background-color: #2c3e50;
  color: white;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(44, 62, 80, 0.3);
}
.action-btn.ready:hover { background-color: #1e293b; transform: translateY(-2px); }

.result-card {
  background: #f0fdf4;
  border: 1px solid #dcfce7;
  border-radius: 12px;
  padding: 15px;
}
.result-header { font-size: 0.9rem; font-weight: 700; color: #166534; margin-bottom: 10px; }
.result-body { display: flex; align-items: center; justify-content: space-around; }
.result-item { display: flex; flex-direction: column; align-items: center; }
.result-item .label { font-size: 0.8rem; color: #15803d; margin-bottom: 4px; }
.result-item .data { font-size: 1.2rem; font-weight: 800; color: #14532d; }
.result-item .data.highlight { color: #d97706; }
.divider { width: 1px; height: 30px; background: #bbf7d0; }

.text-truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

@media (max-width: 768px) {
  .map-page-container {
    display: flex;
    flex-direction: column;
    height: calc(100vh - 60px);
    max-width: 100%;
    margin: 0;
    border-radius: 0;
  }
  .full-map { height: 55%; order: 1; }
  .floating-panel {
    position: relative;
    top: 0; left: 0;
    width: 100%;
    max-width: 100%;
    height: 45%;
    border-radius: 20px 20px 0 0;
    box-shadow: 0 -5px 20px rgba(0,0,0,0.1);
    order: 2;
    overflow-y: auto;
    max-height: none;
    gap: 12px;
    padding: 20px;
  }
}

.slide-fade-enter-active { transition: all 0.3s ease-out; }
.slide-fade-leave-active { transition: all 0.3s cubic-bezier(1, 0.5, 0.8, 1); }
.slide-fade-enter-from, .slide-fade-leave-to { transform: translateY(-10px); opacity: 0; }
</style>
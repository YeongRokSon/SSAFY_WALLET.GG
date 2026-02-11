<template>
  <div class="dashboard-container">
    <!-- 헤더 섹션 -->
    <header class="header-section">
      <div>
        <h1 class="page-title">Global Market</h1>
        <p class="page-subtitle">실시간 암호화폐, 환율 및 귀금속 정보를 확인하세요.</p>
      </div>
      <div class="market-status">
        <span class="status-dot"></span> Real-time
      </div>
    </header>

    <div class="dashboard-grid">
      <!-- [왼쪽] 메인 차트 영역 -->
      <div class="main-card chart-section">
        <div v-if="selectedAsset" class="chart-header">
          <div class="asset-info">
            <div class="icon-wrapper">
                <!-- 이미지 아이콘으로 변경 -->
                <img 
                    :src="getAssetIcon(selectedAsset)" 
                    @error="handleImageError"
                    class="asset-image-large"
                    alt="icon"
                />
            </div>
            <div>
              <h2 class="asset-name">{{ selectedAsset.name }}</h2>
              <p class="asset-code">{{ selectedAsset.code }}</p>
            </div>
          </div>
          <div class="price-info">
            <h3 class="current-price">{{ formatPrice(selectedAsset.currentPrice, selectedAsset.type) }}</h3>
            <span 
              class="change-badge"
              :class="getChangeColor(selectedAsset.change)"
              v-if="selectedAsset.change !== undefined && selectedAsset.change !== 0"
            >
              {{ selectedAsset.change > 0 ? '▲' : '▼' }} {{ Math.abs(selectedAsset.change) }}%
            </span>
          </div>
        </div>

        <div class="chart-container">
          <Line 
            v-if="chartData" 
            :data="chartData" 
            :options="chartOptions" 
          />
          <div v-else class="loading-chart">
            <div v-if="loading" class="spinner-border text-primary" role="status"></div>
            <p v-else>차트 데이터가 없습니다.</p>
          </div>
        </div>
      </div>

      <!-- [오른쪽] 자산 리스트 영역 -->
      <div class="side-card list-section">
        <h3 class="list-title">Market Watch</h3>
        
        <!-- [추가] 카테고리 탭 -->
        <div class="category-tabs">
            <button 
                v-for="tab in categories" 
                :key="tab.value"
                @click="currentCategory = tab.value"
                :class="{ active: currentCategory === tab.value }"
            >
                {{ tab.label }}
            </button>
        </div>

        <div v-if="loading && assets.length === 0" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
        </div>
        
        <div v-else class="asset-list">
          <!-- 필터링된 자산 목록 표시 -->
          <div 
            v-for="asset in filteredAssets" 
            :key="asset.code"
            class="asset-item"
            :class="{ active: selectedAsset?.code === asset.code }"
            @click="selectAsset(asset)"
          >
            <div class="item-left">
              <div class="item-icon-box">
                  <img 
                    :src="getAssetIcon(asset)" 
                    @error="handleImageError"
                    class="asset-image-small"
                    alt="icon"
                  />
              </div>
              <div>
                <p class="item-name">{{ asset.name }}</p>
                <p class="item-code">{{ asset.code }}</p>
              </div>
            </div>
            <div class="item-right">
              <p class="item-price">{{ formatPrice(asset.currentPrice, asset.type) }}</p>
              <p class="item-change" :class="getChangeColor(asset.change)" v-if="asset.change !== undefined">
                {{ asset.change > 0 ? '+' : '' }}{{ asset.change }}%
              </p>
            </div>
          </div>
          
          <!-- 데이터 없을 때 -->
          <div v-if="filteredAssets.length === 0" class="no-data">
              해당 카테고리의 데이터가 없습니다.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Line } from 'vue-chartjs'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const assets = ref([])
const selectedAsset = ref(null)
const loading = ref(false)

// 카테고리 관리
const currentCategory = ref('all')
const categories = [
    { label: '전체', value: 'all' },
    { label: '코인', value: 'crypto' },
    { label: '환율', value: 'forex' },
    { label: '원자재', value: 'commodity' },
]

// 카테고리에 따라 자산 필터링
const filteredAssets = computed(() => {
    if (currentCategory.value === 'all') return assets.value
    return assets.value.filter(asset => asset.type === currentCategory.value)
})

// 차트 옵션
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { 
    legend: { display: false },
    tooltip: {
      mode: 'index',
      intersect: false,
      backgroundColor: 'rgba(0,0,0,0.8)',
      titleFont: { size: 14 },
      bodyFont: { size: 14, weight: 'bold' },
      padding: 10,
      displayColors: false,
      callbacks: {
        label: (context) => {
            const val = context.parsed.y;
            return val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        }
      }
    }
  },
  scales: {
    x: { 
        grid: { display: false }, 
        ticks: { maxTicksLimit: 8, color: '#999' } 
    }, 
    y: { 
        grid: { color: '#f0f0f0' }, 
        // [수정] 차트 위아래 여유 공간 추가 (그래프 완만하게 보기)
        grace: '80%', 
        beginAtZero: false 
    }
  },
  elements: { point: { radius: 0, hitRadius: 10, hoverRadius: 5 } },
  interaction: {
    mode: 'nearest',
    axis: 'x',
    intersect: false
  }
}

// 차트 데이터 생성
const chartData = computed(() => {
  if (!selectedAsset.value || !selectedAsset.value.data || selectedAsset.value.data.length === 0) return null
  
  const labels = selectedAsset.value.data.map(item => item.date)
  const data = selectedAsset.value.data.map(item => item.price)

  let color = '#228be6'; 
  if (data.length >= 2) {
      const first = data[0];
      const last = data[data.length - 1];
      if (last >= first) color = '#fa5252'; 
  } else if (selectedAsset.value.change >= 0) {
      color = '#fa5252';
  }

  return {
    labels,
    datasets: [{
      label: selectedAsset.value.name,
      data,
      borderColor: color,
      backgroundColor: (ctx) => {
        const gradient = ctx.chart.ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, color + '40'); 
        gradient.addColorStop(1, color + '00'); 
        return gradient;
      },
      borderWidth: 2,
      fill: true,
      tension: 0.4
    }]
  }
})

// 데이터 가져오기
const fetchData = async () => {
  loading.value = true
  try {
    const res = await axios.get('http://127.0.0.1:8000/services/gold-silver/')
    const { crypto, forex, gold, silver } = res.data

    const newAssets = []

    crypto.forEach(c => {
        newAssets.push({
            code: c.code,
            name: c.name,
            currentPrice: c.price,
            change: c.change,
            type: 'crypto',
            // icon은 이제 사용하지 않고 이미지 로드 함수 사용
            data: generateDummyChartData(c.price) 
        })
    })

    forex.forEach(f => {
        newAssets.push({
            code: f.code,
            name: f.name,
            currentPrice: f.price,
            change: f.change, 
            type: 'forex',
            data: generateDummyChartData(f.price) 
        })
    })

    if (gold && gold.length > 0) {
        const latestGold = gold[gold.length - 1]
        const prevGold = gold.length >= 2 ? gold[gold.length - 2] : latestGold
        const changeRate = prevGold['Close/Last'] ? ((latestGold['Close/Last'] - prevGold['Close/Last']) / prevGold['Close/Last'] * 100) : 0
        
        newAssets.push({
            code: 'GOLD',
            name: '국제 금',
            currentPrice: latestGold['Close/Last'],
            change: Number(changeRate.toFixed(2)),
            type: 'commodity',
            data: gold.map(item => ({ date: item.Date, price: item['Close/Last'] }))
        })
    }

    if (silver && silver.length > 0) {
        const latestSilver = silver[silver.length - 1]
        const prevSilver = silver.length >= 2 ? silver[silver.length - 2] : latestSilver
        const changeRate = prevSilver['Close/Last'] ? ((latestSilver['Close/Last'] - prevSilver['Close/Last']) / prevSilver['Close/Last'] * 100) : 0

        newAssets.push({
            code: 'SILVER',
            name: '국제 은',
            currentPrice: latestSilver['Close/Last'],
            change: Number(changeRate.toFixed(2)),
            type: 'commodity',
            data: silver.map(item => ({ date: item.Date, price: item['Close/Last'] }))
        })
    }

    assets.value = newAssets
    
    if (!selectedAsset.value && assets.value.length > 0) {
        selectedAsset.value = assets.value[0]
    } else if (selectedAsset.value) {
        const updated = assets.value.find(a => a.code === selectedAsset.value.code)
        if (updated) selectedAsset.value = updated
    }

  } catch (err) {
    console.error("데이터 로드 실패:", err)
  } finally {
    loading.value = false
  }
}

const generateDummyChartData = (basePrice) => {
    const data = []
    const now = new Date()
    for (let i = 29; i >= 0; i--) {
        const d = new Date(now)
        d.setDate(d.getDate() - i)
        const randomFluctuation = (Math.random() - 0.5) * 0.1 
        data.push({
            date: d.toISOString().split('T')[0],
            price: basePrice * (1 + randomFluctuation)
        })
    }
    if(data.length > 0) data[data.length-1].price = basePrice
    return data
}

const selectAsset = (asset) => {
  selectedAsset.value = asset
}

const formatPrice = (price, type) => {
    if (price === undefined || price === null) return '-'
    
    let options = {}
    let suffix = ' 원' 

    if (type === 'commodity') {
        options = { style: 'currency', currency: 'USD', minimumFractionDigits: 2 }
        return Number(price).toLocaleString('en-US', options)
    } else if (type === 'crypto') {
        options = { maximumFractionDigits: 0 }
    } else {
        options = { minimumFractionDigits: 2, maximumFractionDigits: 2 }
    }
    
    return Number(price).toLocaleString(undefined, options) + (type !== 'commodity' ? suffix : '')
}

const getChangeColor = (change) => {
    if (change > 0) return 'up'
    if (change < 0) return 'down'
    return ''
}

// [추가] 이미지 경로 생성 함수
// public/images/chart 폴더에 btc.png, gold.png 등으로 저장되어 있어야 함
// USD/KRW 같은 경우 슬래시가 있으므로 처리 필요 (usd_krw.png 등으로 매핑하거나 앞글자만 따기)
const getAssetIcon = (asset) => {
    let filename = asset.code.toLowerCase()
    
    // 특수문자 처리 (USD/KRW -> usd)
    if (filename.includes('/')) {
        filename = filename.split('/')[0] 
    }
    
    return `/images/chart/${filename}.png`
}

// 이미지 로드 실패 시 기본 아이콘 표시 (fallback)
const handleImageError = (e) => {
    // 이미 대체 이미지로 변경된 상태라면 중단 (무한루프 방지)
    if (e.target.src.includes('placeholder')) return
    e.target.src = 'https://via.placeholder.com/60/f0f0f0/888888?text=' + e.target.alt
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.dashboard-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px;
  color: #333;
  font-family: 'Helvetica Neue', 'Arial', sans-serif;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 30px;
}
.page-title { font-size: 2rem; font-weight: 800; margin: 0; color: #111; }
.page-subtitle { color: #666; margin-top: 5px; font-size: 1rem; }
.market-status {
  background: #e6fcf5; color: #0ca678; padding: 6px 12px;
  border-radius: 20px; font-weight: 600; font-size: 0.9rem;
  display: flex; align-items: center;
}
.status-dot {
  width: 8px; height: 8px; background-color: #0ca678;
  border-radius: 50%; margin-right: 6px; display: inline-block;
  animation: blink 2s infinite;
}
@keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }

.dashboard-grid {
  display: grid; grid-template-columns: 2.5fr 1fr; gap: 24px; height: 600px;
}

.main-card, .side-card {
  background: #fff; border-radius: 24px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.04);
  border: 1px solid #f1f3f5;
  overflow: hidden; display: flex; flex-direction: column;
}

/* 차트 섹션 */
.chart-section { padding: 30px; }
.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.asset-info { display: flex; align-items: center; gap: 15px; }

/* 이미지 아이콘 스타일 */
.icon-wrapper {
  width: 60px; height: 60px;
  border-radius: 16px; overflow: hidden;
  background: white; border: 1px solid #f1f3f5;
  display: flex; justify-content: center; align-items: center;
}
.asset-image-large { width: 100%; height: 100%; object-fit: contain; padding: 5px; }

.asset-name { margin: 0; font-size: 1.5rem; font-weight: 700; }
.asset-code { margin: 0; color: #868e96; font-size: 0.9rem; font-weight: 600; }

.price-info { text-align: right; }
.current-price { margin: 0; font-size: 1.8rem; font-weight: 800; color: #212529; }
.change-badge {
  display: inline-block; padding: 4px 10px; border-radius: 8px;
  font-size: 0.9rem; font-weight: 700; margin-top: 5px;
}
.change-badge.up { background: #fff5f5; color: #fa5252; }
.change-badge.down { background: #e7f5ff; color: #228be6; }

.chart-container { flex: 1; position: relative; min-height: 0; }
.loading-chart {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  height: 100%; color: #adb5bd;
}

/* 리스트 섹션 */
.list-title { padding: 20px 24px 10px; margin: 0; font-size: 1.1rem; font-weight: 700; }

/* 카테고리 탭 스타일 */
.category-tabs {
    padding: 0 24px 15px;
    border-bottom: 1px solid #f1f3f5;
    display: flex; gap: 8px;
}
.category-tabs button {
    border: 1px solid #dee2e6; background: white;
    padding: 6px 12px; border-radius: 20px;
    font-size: 0.85rem; color: #868e96; cursor: pointer;
    transition: all 0.2s;
}
.category-tabs button.active {
    background: #228be6; color: white; border-color: #228be6; font-weight: 600;
}

.asset-list { flex: 1; overflow-y: auto; }
.asset-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 24px; cursor: pointer; transition: all 0.2s; border-bottom: 1px solid #f8f9fa;
}
.asset-item:hover { background-color: #f8f9fa; }
.asset-item.active { background-color: #f1f3f5; border-left: 4px solid #228be6; }

.item-left { display: flex; align-items: center; gap: 12px; }
.item-icon-box {
    width: 36px; height: 36px; border-radius: 10px;
    background: white; border: 1px solid #eee;
    overflow: hidden; display: flex; justify-content: center; align-items: center;
}
.asset-image-small { width: 100%; height: 100%; object-fit: contain; padding: 4px; }

.item-name { margin: 0; font-weight: 600; font-size: 0.95rem; color: #343a40; }
.item-code { margin: 0; font-size: 0.8rem; color: #adb5bd; }

.item-right { text-align: right; }
.item-price { margin: 0; font-weight: 600; font-size: 0.95rem; color: #212529; }
.item-change { margin: 0; font-size: 0.8rem; font-weight: 600; }
.item-change.up { color: #fa5252; }
.item-change.down { color: #228be6; }

.no-data { text-align: center; padding: 40px 0; color: #adb5bd; font-size: 0.9rem; }

@media (max-width: 992px) {
  .dashboard-grid { grid-template-columns: 1fr; height: auto; }
  .chart-section { height: 500px; }
  .list-section { height: 400px; }
}
</style>
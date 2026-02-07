<template>
  <div class="pack-page">
    <header
      class="pack-header"
      :style="{ backgroundImage: packBackgroundStyle }"
      role="region"
      aria-label="Pack banner"
    >
      <div class="overlay">
        <div class="header-content">
          <div class="title-block">
            <h1 class="pack-title">{{ packInfo.name }}</h1>

            <div class="header-meta">
                <div class="meta-item">
                    <strong>{{ packInfo.beatmapset_count ?? '—' }}</strong>
                    <span> beatmapsets</span>
                </div>

                <div class="meta-item">
                    <strong>{{ packInfo.downloads ?? 0 }}</strong>
                    <span> downloads</span>
                </div>

                <div class="meta-item modes">
                <template v-for="m in packModes" :key="m">
                  <span class="mode-pill">{{ m }}</span>
                </template>
                </div>
            </div>

            <div class="timestamp">
              <small>created: {{ createdAt }}</small>
              <small>Last update: {{ updatedAt }}</small>
            </div>
          </div>

          <div class="actions">
            <button 
              class="download-btn" 
              :class="{ 'downloading': isDownloading }"
              @click="handleDownloadClick" 
              :disabled="isDownloading"
            >
              <div v-if="isDownloading" class="download-progress">
                <span class="progress-text">
                  <template v-if="downloadProgress.waiting">
                    ⏳ Rate limited, waiting {{ downloadProgress.waitSeconds }}s...
                  </template>
                  <template v-else>
                    Downloading {{ downloadProgress.current }} / {{ downloadProgress.total }}
                    <span class="progress-size">({{ downloadProgress.downloadedMB.toFixed(1) }} MB)</span>
                  </template>
                </span>
                <div class="progress-bar-container">
                  <div 
                    class="progress-bar-fill" 
                    :style="{ width: `${(downloadProgress.current / downloadProgress.total) * 100}%` }"
                  ></div>
                </div>
              </div>
              <span v-else>Download Pack</span>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Download confirmation modal -->
    <DownloadConfirmModal 
      :show="showModal" 
      @close="showModal = false" 
      @confirm="handleDownload"
    />

    <main class="container">
        <!-- Loading state -->
        <div v-if="bmsetLoading" class="loading-state">
          <div class="loading-emoji">৻( •̀ ᗜ •́ ৻)</div>
          <p class="loading-message">Fetching database</p>
          <p class="loading-hint">Please wait for a moment...</p>
        </div>

        <div class="grid-beatmapsets">
            <BeatmapsetCard
            v-for="beatmapset in bmsetInfo"
            :key="beatmapset.id"
            :beatmapset="beatmapset"
            />
        </div>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref, computed, watch } from 'vue'
import BeatmapsetCard from './components/BeatmapsetCard.vue';
import DownloadConfirmModal from './components/DownloadConfirmModal.vue';
import api from './api'
import { useRoute } from 'vue-router'
import { usePacksStore } from './stores/packs'
import { usePackDownload } from '@/composables/usePackDownload'

const route = useRoute();
const packsStore = usePacksStore()

const bmsetInfo = ref([])
const bmsetLoading = ref(false)

const packInfo = ref(null)
const packInfoLoading = ref(false)

// pack-level info (title, source, background image, download url)
const loadPackInfo = async () => {
  const packId = route.params.packId
  const packFromStore = packsStore.getPackById(packId)

  if (packFromStore) {
    packInfo.value = packFromStore
    return
  }

  packInfoLoading.value = true
  try {
    const packData = await api.packs.get(packId)
    packsStore.setPack(packData)
    packInfo.value = packData
  } catch (err) {
    console.error("Failed to fetch pack data:", err)
    packInfo.value = null
  } finally {
    packInfoLoading.value = false
  }
}

watch(
  () => route.params.packId,
  () => loadPackInfo(),
  { immediate: true }
)

// Use the reusable composable for download logic
const {
  showModal,
  isPackDownloading,
  getPackDownloadProgress,
  handleDownloadClick: _handleDownloadClick,
  handleDownload: _handleDownload
} = usePackDownload({
  incrementDownloadCount: async (packId) => {
    try {
      await api.packs.incrementDownloads(packId)
    } catch (err) {
      console.error('Failed to increment download count:', err)
    }
  },
  refreshPackData: async (packId) => {
    try {
      await packsStore.fetchPacks() // refresh store
    } catch (err) {
      console.error('Failed to refresh pack data:', err)
    }
  }
})

// Computed properties for this specific pack's download status
const isDownloading = computed(() => packInfo.value?.id ? isPackDownloading(packInfo.value.id) : false)
const downloadProgress = computed(() => packInfo.value?.id ? getPackDownloadProgress(packInfo.value.id) : { current: 0, total: 0, downloadedMB: 0, waiting: false, waitSeconds: 0 })

// Wrap the composable handlers to pass pack from packInfo
const handleDownloadClick = () => _handleDownloadClick({ disabled: false, pack: packInfo.value })
const handleDownload = () => _handleDownload(packInfo.value)

const packBackgroundStyle = computed(() => {
  const url = packInfo.value.image_link
  return url ? `url('${url}')` : 'none'
})

const packModes = computed(() => {
  const mapping = { '-1': 'ALL', 0: 'Standard', 1: 'Taiko', 2: 'Catch the Beat', 3: 'Mania' }
  const modes = packInfo.value.mode || []
  // ensure array
  return Array.isArray(modes) ? modes.map(m => mapping[m] ?? String(m)) : []
})

const packStatuses = computed(() => {
  const mapping = { 1: 'Ranked', 2: 'Loved' }
  const statuses = packInfo.value.status || []
  return Array.isArray(statuses) ? statuses.map(s => mapping[s] ?? String(s)) : []
})

const createdAt = computed(() => {
  const v = packInfo.value.created_at || packInfo.value.createdAt
  if (!v) return '—'
  try { return new Date(v).toLocaleDateString() } catch (e) { return String(v) }
})

const updatedAt = computed(() => {
  const v = packInfo.value.updated_at || packInfo.value.updatedAt
  if (!v) return '—'
  try { return new Date(v).toLocaleDateString() } catch (e) { return String(v) }
})

const getBeatmapsets = async (id) => {
  try {
    bmsetLoading.value = true;
    // this returns an Array so we need to make props array too
    const bmsets = await api.packs.get_bmsets(id);
    bmsetInfo.value = bmsets;
  } catch (err) {
    console.error("Failed to reach the server.");
  } finally {
    bmsetLoading.value = false;
  }
}

onMounted(() => {
  const id = route.params.packId
  getBeatmapsets(id)
})

</script>

<style scoped>
.header-meta {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}
.timestamp {
  margin-top: 12px;
  color: #d1d5db;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.pack-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  padding: 1rem;
}
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.loading-state p {
  margin: 16px 0 0;
  color: #4a5568;
  font-size: 16px;
}

.loading-emoji {
  color:#d8cc6e;
  font-size: 64px;
  margin-bottom: 24px;
  animation: bounce 1s ease-in-out infinite;
}
@keyframes bounce {
  0%, 100% {
    transform: translateY(0) scale(1);
  }
  50% {
    transform: translateY(-15px) scale(1.05);
  }
}
.container {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.grid-beatmapsets {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
    max-width: 64rem;
    width: 100%;
    gap: 20px;
    padding: 1rem;
}

.pack-header {
    max-width: 80rem;
    width: 100%;
    height: 360px;
    background-size: cover;
    background-position: center;
    position: relative;
    color: #fff;
    border-radius: 2rem;
}
.pack-header .overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(17,24,28,0.55) 0%, rgba(17,24,28,0.85) 100%);
  display: flex;
  align-items: flex-end;
  border-radius: 2rem;
}

.header-content {
  width: 100%;
  padding: 28px 48px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
}

.title-block {
  display: flex;
  flex-direction: column;
}
.pack-title {
  margin: 0;
  font-size: 2.25rem;
  font-weight: 700;
  line-height: 1;
}

@media (max-width: 600px) {
  .pack-title {
    font-size: 1.75rem;
  }
}

.pack-meta {
  margin-top: 8px;
  color: #d1d5db;
}
.actions {
  display: flex;
  align-items: center;
}
.download-btn {
  background: #1f9bf0;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  min-width: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.download-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.download-btn.downloading {
  cursor: wait;
  min-width: 220px;
}

.download-progress {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 100%;
}
.progress-text {
  font-size: 13px;
  font-weight: 600;
  text-align: center;
}
.progress-size {
  font-size: 12px;
  font-weight: 500;
  opacity: 0.9;
  margin-left: 4px;
}
.progress-bar-container {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
  overflow: hidden;
}
.progress-bar-fill {
  height: 100%;
  background: white;
  border-radius: 3px;
  transition: width 0.3s ease;
  box-shadow: 0 0 8px rgba(255, 255, 255, 0.5);
}

</style>
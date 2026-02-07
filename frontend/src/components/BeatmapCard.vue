<template>
  <article class="card" @mouseenter="mouseHover = true" @mouseleave="mouseHover = false">
    <router-link :to="{ name: 'PackDetail', params: { packId: pack.id } }" class="card-content">
    <div class="cover" :style="coverStyle">
      <div class="gradient-overlay"></div>
      <div class="modes-overlay">
        <!-- Future place for mode icons -->
      </div>
      <!-- use pack.image_link for the cover image and ensure to center -->
      <img v-if="proxySrc" :src="proxySrc" class="cover-image" />
    </div>
    <div class="content">
      <div class="pack-name">
        {{ pack.name }}
      </div>
      <div class="header">
        <div class="title-section">
          <span class="anime-badge">{{ pack.anime_title }}</span>
        </div>
      </div>
      <div class="meta-info">
        <div class="stat">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
          </svg>
          <span>{{ pack.beatmapset_count }} beatmapset{{ pack.beatmapset_count !== 1 ? 's' : '' }}</span>

        </div>
        <div class="stat downloads">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
          <span>{{ formatNumber(pack.downloads) }}</span>
        </div>
      </div>
    </div>
    <!-- only show actions on hover -->
      <div class="actions" v-show="mouseHover || isDownloading">
        <button 
          @click.stop.prevent="handleDownloadClick" 
          class="download-btn primary"
          :class="{ 'downloading': isDownloading }"
          :disabled="isDownloading || disabled"
        >
          <div v-if="isDownloading" class="download-progress">
            <div class="progress-content">
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
          </div>
          <div v-else class="download-content">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7 10 12 15 17 10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            Download
          </div>
        </button>
      </div> 
    </router-link>
    <DownloadConfirmModal 
      :show="showModal" 
      @close="showModal = false" 
      @confirm="handleDownload"
    />
  </article>
</template>

<script setup>
import { ref, computed } from 'vue'
import DownloadConfirmModal from './DownloadConfirmModal.vue'
import api from '../api'
import { usePackDownload } from '@/composables/usePackDownload'

const props = defineProps({
  pack: { type: Object, required: true },
  disabled: { type: Boolean, default: false }
})

const mouseHover = ref(false)

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
      const updatedPack = await api.packs.get(packId)
      // Note: this won't reactively update props, but the store or parent should handle refresh
      props.pack.downloads = updatedPack.downloads
    } catch (err) {
      console.error('Failed to refresh pack data:', err)
    }
  }
})

import { API_BASE_URL } from '../api/index'

// Computed properties for this specific pack's download status
const isDownloading = computed(() => isPackDownloading(props.pack?.id))
const downloadProgress = computed(() => getPackDownloadProgress(props.pack?.id))

const proxySrc = computed(() => {
  const raw = props.pack?.image_link
  if (!raw) return ''
  return `${API_BASE_URL}/packs/img?url=${encodeURIComponent(raw)}`
})

// Wrap the composable's handleDownloadClick to pass pack and disabled
const handleDownloadClick = () => _handleDownloadClick({ disabled: props.disabled, pack: props.pack })

// Wrap handleDownload so modal @confirm can call it without args
const handleDownload = () => _handleDownload(props.pack)

const coverStyle = computed(() => {
  if (props.pack.image_link) return {}

  const label = (props.pack.anime_title || props.pack.name || '').toString()
  const safeLabel = label
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300">
    <defs>
      <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#667eea"/>
        <stop offset="100%" stop-color="#764ba2"/>
      </linearGradient>
    </defs>
    <rect width="100%" height="100%" fill="url(#grad)"/>
    <text x="50%" y="50%" fill="white" font-size="22" font-weight="600"
      font-family="Arial" dominant-baseline="middle" text-anchor="middle"
      opacity="0.9">${safeLabel}</text>
  </svg>`

  return {
    backgroundImage: `url("data:image/svg+xml;utf8,${encodeURIComponent(svg)}")`
  }
})


const shortSynopsis = computed(() => {
  if (!props.pack.synopsis) return ''
  return props.pack.synopsis.length > 100 ? props.pack.synopsis.slice(0, 97) + '…' : props.pack.synopsis
})

const formatNumber = (num) => {
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num.toString()
}
</script>

<style scoped>

/* gradient from bottom right */
.gradient-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 50%;
  background: linear-gradient(
    to top,
    rgba(0, 0, 0, 0.80),
    transparent
  );
}
.link {
  display: flex;
  color: inherit;
  text-decoration: none;
  height: 100%;
}
.link:hover {
  cursor: pointer;
  background-color: unset;
}
.cover-image {
  width: 160px;
  aspect-ratio: 2 / 3;
  object-fit: cover;
}

.modes-overlay {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  gap: 6px;
  /* Future styles for mode icons */
}

.card-content {
  display: flex;
  height: 100%;
}

.card-content:hover {
  background-color: unset;
}

.card {
  display: flex;
  flex-direction: column; 
  position: relative;
  background: white;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  height: 10rem;
}
/* shadow inner from left  to right with primary color*/
.card:hover {
  box-shadow: inset 0 12px 28px rgba(102, 126, 234, 0.12), inset 0 4px 8px rgba(102, 126, 234, 0.08);
}

.cover {
  position: relative;
  width: 35%;
  height: 100%;
  overflow: hidden;
}

.cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
}

.overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 50%;
  background: linear-gradient(
    to top,
    rgba(0, 0, 0, 0.35),
    transparent
  );
}

.content {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
}

.header {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.title-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.pack-name {
  font-size: 14px;
  font-weight: 700;
  margin: 0;
  color: #1a202c;
  line-height: 1.3;
}

.pack-name:hover {
  background-color:unset;
  color: #667eea;
}

.anime-badge {
  display: inline-block;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 600;
  align-self: flex-start;
  box-shadow: 0 2px 4px rgba(102, 126, 234, 0.2);
}

.synopsis {
  color: #4a5568;
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
}

.meta-info {
  display: flex;
  gap: 16px;
  margin-top: auto;
}

.stat {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #718096;
  font-size: 10px;
  font-weight: 500;
}

.stat svg {
  flex-shrink: 0;
}

.stat.downloads {
  color: #667eea;
}

.actions {
  display: flex;
  gap: 8px;
}

.download-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 0.1rem 0.3rem;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  border: none;
}

.download-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.download-btn.primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.download-btn.primary:active {
  transform: translateY(0);
}

.download-btn.downloading {
  cursor: wait;
  opacity: 0.8;
}

.download-btn.downloading:hover {
  transform: none;
}

.download-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.download-progress {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.progress-content {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 6px;
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

.spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.download-btn.disabled {
  background: #e2e8f0;
  color: #a0aec0;
  cursor: not-allowed;
}

.download-btn svg {
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .cover {
    height: 160px;
  }

  .content {
    padding: 16px;
  }

  .pack-name {
    font-size: 16px;
  }
}
</style>

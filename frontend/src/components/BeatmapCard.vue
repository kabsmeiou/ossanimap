<template>
  <article class="card">
    <div class="cover" :style="coverStyle">
      <div class="overlay"></div>
    </div>
    <div class="content">
      <div class="header">
        <div class="title-section">
          <h3 class="pack-name">{{ pack.name }}</h3>
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
      <div class="actions">
        <button 
          @click="handleDownloadClick" 
          class="download-btn primary"
          :class="{ 'downloading': isDownloading }"
          :disabled="isDownloading"
        >
          <div v-if="isDownloading" class="download-progress">
            <div class="progress-content">
              <span class="progress-text">Downloading {{ downloadProgress.current }} / {{ downloadProgress.total }}</span>
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
    </div>

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
import JSZip from 'jszip';
import { saveAs } from 'file-saver'; // Optional helper, or use <a> tag

const props = defineProps({
  pack: { type: Object, required: true }
})

const showModal = ref(false)
const isDownloading = ref(false)
const downloadProgress = ref({ current: 0, total: 0 })
const rateLimitWarning = ref('')

// Check rate limits before download
const checkRateLimits = async () => {
  try {
    const response = await fetch('https://catboy.best/api/ratelimits')
    if (!response.ok) throw new Error('Failed to fetch rate limits')
    
    const data = await response.json()
    const remaining = data.daily.remaining.downloads
    const total = data.daily.limit.downloads
    const needed = props.pack.beatmapset_ids.length
    
    if (remaining === 0) {
      return {
        allowed: false,
        message: '⚠️ Daily download quota exceeded. Please try again tomorrow.'
      }
    }
    
    if (remaining < needed) {
      return {
        allowed: false,
        message: `⚠️ Insufficient daily downloads remaining. You need ${needed} downloads but only have ${remaining} remaining (${total} daily limit).`
      }
    }
    
    if (remaining < needed * 2) {
      return {
        allowed: true,
        warning: `⚠️ Warning: Only ${remaining} downloads remaining today (${total} daily limit). This pack needs ${needed} downloads.`
      }
    }
    
    return { allowed: true }
  } catch (err) {
    console.error('Failed to check rate limits:', err)
    // Allow download to proceed if rate limit check fails
    return { allowed: true }
  }
}

const handleDownloadClick = async () => {
  // Check rate limits first
  const rateLimitCheck = await checkRateLimits()
  
  if (!rateLimitCheck.allowed) {
    alert(rateLimitCheck.message)
    return
  }
  
  if (rateLimitCheck.warning) {
    const proceed = confirm(rateLimitCheck.warning + '\n\nDo you want to proceed?')
    if (!proceed) return
  }
  
  // Check if user has opted to skip the modal for this session
  const skipModal = sessionStorage.getItem('skipDownloadModal') === 'true'
  
  if (skipModal) {
    // Proceed directly to download
    handleDownload()
  } else {
    // Show confirmation modal
    showModal.value = true
  }
}

const handleDownload = async () => {
  const ids = props.pack.beatmapset_ids;
  if (!confirm(`Download and pack ${ids.length} beatmaps into a ZIP?`)) return;

  isDownloading.value = true
  downloadProgress.value = { current: 0, total: ids.length }

  const zip = new JSZip();
  const folder = zip.folder("beatmap_pack");

  // Use Promise.all to fetch files in parallel
  const downloadPromises = ids.map(async (id, index) => {
    try {
      const response = await fetch(`https://catboy.best/d/${id}`);
      if (!response.ok) throw new Error(`Failed to fetch ${id}`);
      
      const blob = await response.blob();
      // Add to zip: filename usually comes from headers, 
      // but you can default to id.osz
      folder.file(`${id}.osz`, blob);
      
      // Update progress
      downloadProgress.value.current += 1
    } catch (err) {
      console.error(`Error downloading map ${id}:`, err);
      // Still increment progress even on error
      downloadProgress.value.current += 1
    }
  });

  await Promise.all(downloadPromises);

  // Generate the ZIP and trigger a single download
  const content = await zip.generateAsync({ type: "blob" });
  saveAs(content, `${props.pack.name || 'osu_pack'}.zip`);
  
  // Reset state
  isDownloading.value = false
  downloadProgress.value = { current: 0, total: 0 }
};


const coverStyle = computed(() => {
  const label = (props.pack.anime_title || props.pack.name || '').toString()
  const safeLabel = label.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300"><defs><linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#667eea;stop-opacity:1" /><stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" /></linearGradient></defs><rect width="100%" height="100%" fill="url(#grad)"/><text x="50%" y="50%" fill="white" font-size="22" font-weight="600" font-family="Arial" dominant-baseline="middle" text-anchor="middle" opacity="0.9">${safeLabel}</text></svg>`
  const encoded = encodeURIComponent(svg)
  return {
    backgroundImage: `url("data:image/svg+xml;utf8,${encoded}")`
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
.card {
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08), 0 2px 4px rgba(0, 0, 0, 0.04);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  height: 100%;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.12), 0 4px 8px rgba(0, 0, 0, 0.08);
}

.cover {
  position: relative;
  width: 100%;
  height: 100px;
  background-size: cover;
  background-position: center;
  overflow: hidden;
}

.overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 0%, rgba(0, 0, 0, 0.3) 100%);
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
  font-size: 18px;
  font-weight: 700;
  margin: 0;
  color: #1a202c;
  line-height: 1.3;
}

.anime-badge {
  display: inline-block;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 12px;
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
  font-size: 13px;
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
  margin-top: 8px;
  padding-top: 12px;
  border-top: 1px solid #e2e8f0;
}

.download-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 10px;
  font-size: 14px;
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

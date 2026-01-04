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
      <p class="synopsis" v-if="pack.synopsis">{{ shortSynopsis }}</p>
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
        <a v-if="pack.artifact_url" :href="pack.artifact_url" class="download-btn primary">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
          Download
        </a>
        <button v-else class="download-btn disabled">
          No Artifact
        </button>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({
  pack: { type: Object, required: true }
})

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
  height: 180px;
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
  padding-top: 8px;
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

<template>
  <main>
    <div class="page">
      <div class="links">
        <a class="link-text" href="https://github.com/kabsmeiou/ossanimap" target="_blank" rel="noopener noreferrer">Github</a>
        <!-- <a class="link-text" href="https://api.kabsmeiou.space/docs" target="_blank" rel="noopener noreferrer">API Docs</a> -->
        <a class="link-text" href="https://catboy.best" target="_blank" rel="noopener noreferrer">Chimu</a>
        <a class="link-text" href="https://animethemes.moe" target="_blank" rel="noopener noreferrer">Animethemes</a>
      </div>
      <header class="top">
        <div class="brand"> 
          <div class="logo">
            <!-- use favicon.ico -->
            <img src="/favicon.ico" alt="ossanimap Logo" width="34" height="34" />
          </div>
          <div class="header-text">
            <h1>ossanimap</h1>
            <p class="tagline">your favorite anime beatmaps in one place</p>
          </div>
        </div>
        
        <!-- Rate Limit Counters -->
        <div class="rate-limits" v-if="rateLimits">
          <div class="limit-group">
            <span class="limit-label">Per Minute</span>
            <div class="limit-values">
              <span class="limit-value" :class="getPerMinuteClass">
                {{ rateLimits.perMinute.remaining }}/{{ rateLimits.perMinute.limit }}
              </span>
            </div>
          </div>
          <button class="refresh-btn" @click="refreshRateLimits" :disabled="isRefreshing" title="Refresh rate limits">
            <svg :class="{ 'spinning': isRefreshing }" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M23 4v6h-6"></path>
              <path d="M1 20v-6h6"></path>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
            </svg>
          </button>
        </div>
      </header>
      <router-view></router-view>
    </div>
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchRateLimits } from '@/services/packDownload'

const rateLimits = ref(null)
const isRefreshing = ref(false)

const refreshRateLimits = async () => {
  if (isRefreshing.value) return
  isRefreshing.value = true
  try {
    rateLimits.value = await fetchRateLimits()
  } catch (err) {
    console.error('Failed to fetch rate limits:', err)
  } finally {
    isRefreshing.value = false
  }
}

const getPerMinuteClass = computed(() => {
  if (!rateLimits.value) return ''
  const { remaining, limit } = rateLimits.value.perMinute
  const ratio = remaining / limit
  if (ratio <= 0.1) return 'limit-critical'
  if (ratio <= 0.3) return 'limit-warning'
  return 'limit-good'
})


onMounted(() => {
  refreshRateLimits()
  setInterval(refreshRateLimits, 30000)
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  padding : 0px 0px 32px 0px ;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
.links {
  position: absolute;
  top: 16px;
  right: 16px;
  display: flex;
  gap: 12px;
  z-index: 200;
}

.link-text{
  font-size: 14px;
  color: #4a5568;
  text-decoration: none;
  font-weight: 500;
  transition: background-color 0.2s ease;
  border-radius: 1rem;
  padding: 4px 8px;
}
.link-text:hover {
  background-color: #c5cbe2;
}
@media screen and (max-width: 1100px) {
  .links {
    padding: 1rem;
    position: static;
    justify-content: center;
  }
}
.top {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  align-items: center;
}
.brand {
  display: flex;
  align-items: center;
  gap: 16px;
}

.tagline {
  font-size: 14px;
  color: #718096;
  margin: 0;
  font-weight: 500;
}

.brand .logo {
  width: 3rem;
  height: 3rem;
  border-radius: 12px;
  border-color: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* apply gradient to text */
.brand h1 {
  font-size: 28px;
  font-weight: 700;
  margin: 0;
  letter-spacing: -0.5px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* Rate limit status */
.rate-limits {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(102, 126, 234, 0.15);
  font-size: 13px;
  border: 1px solid rgba(102, 126, 234, 0.1);
}

.limit-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.limit-label {
  font-size: 11px;
  font-weight: 500;
  color: #718096;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.limit-value {
  font-weight: 700;
  font-size: 15px;
  color: #2d3748;
}

.limit-value.good {
  color: #38a169;
}

.limit-value.warning {
  color: #dd6b20;
}

.limit-value.danger {
  color: #e53e3e;
}

.limit-divider {
  width: 1px;
  height: 32px;
  background: linear-gradient(180deg, transparent, #cbd5e0, transparent);
}

.refresh-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-left: 4px;
}

.refresh-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.refresh-btn svg.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
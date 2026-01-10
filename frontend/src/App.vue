<script setup>
import { ref, computed, onMounted } from 'vue'
import BeatmapCard from './components/BeatmapCard.vue'
import api from './api'

// State
const query = ref('')
const sortBy = ref('downloads')
const packs = ref([])
const loading = ref(false)
const error = ref(null)

// Search suggestions state
const searchSuggestions = ref([])
const showSuggestions = ref(false)
const searchLoading = ref(false)
const searchInput = ref(null)
const showSearchIndicator = ref(false)
const requestingPackSlug = ref(null) // Track which suggestion is being processed

// Rate limit state
const rateLimitInfo = ref(null)
const showRateLimitWarning = ref(false)
const rateLimitError = ref(false) // Track if rate limit fetch failed


// Fetch rate limits
const fetchRateLimits = async () => {
  try {
    const response = await fetch('https://catboy.best/api/ratelimits')
    console.log('Rate limits response:', response)
    if (!response.ok) throw new Error('Failed to fetch rate limits')
    
    const data = await response.json()
    rateLimitInfo.value = data
    rateLimitError.value = false
    
    // Show warning if downloads are getting low
    const remaining = data.daily.remaining.downloads
    const total = data.daily.limit.downloads
    const percentRemaining = (remaining / total) * 100
    
    showRateLimitWarning.value = percentRemaining <= 20 || remaining === 0
  } catch (err) {
    console.error('Failed to fetch rate limits:', err)
    rateLimitError.value = true // Set error state
    rateLimitInfo.value = null
    showRateLimitWarning.value = false
  }
}

// Handle Enter key press to trigger search
const handleSearchKeyPress = async (event) => {
  if (rateLimitError.value) {
    return; // Prevent search when service is unreachable
  }
  
  if (event.key === 'Enter' && query.value.trim().length >= 3) {
    await fetchSearchSuggestions(query.value)
  }
}

// Fetch search suggestions from anime API
const fetchSearchSuggestions = async (searchQuery) => {
  searchLoading.value = true
  showSearchIndicator.value = false
  
  try {
    const results = await api.anime.search(searchQuery)
    searchSuggestions.value = results
    showSuggestions.value = results.length > 0
  } catch (err) {
    console.error('Failed to fetch search suggestions:', err)
    searchSuggestions.value = []
    showSuggestions.value = false
  } finally {
    searchLoading.value = false
  }
}

// Handle suggestion click
const handleSuggestionClick = async (suggestion) => {
  requestingPackSlug.value = suggestion.slug
  
  const data = {
    anime_name: suggestion.name,
    status: 1,
  }

  try {
    await api.packs.create(data).then(() => {
      fetchPacks()
    })
    alert(`Request for pack "${suggestion.name}" has been submitted!`)
    showSuggestions.value = false
    query.value = ''
  } catch (err) {
    console.error('Failed to submit request:', err)
    alert('Failed to submit request. Please try again later.')
  } finally {
    requestingPackSlug.value = null
  }
}

// Close suggestions when clicking outside
const handleClickOutside = (event) => {
  if (searchInput.value && !searchInput.value.contains(event.target)) {
    showSuggestions.value = false
  }
}

onMounted(() => {
  fetchRateLimits()
  fetchPacks()
  document.addEventListener('click', handleClickOutside)
})

// Cleanup
onMounted(() => {
  return () => {
    document.removeEventListener('click', handleClickOutside)
  }
})


// Fetch packs from the backend
const fetchPacks = async () => {
  loading.value = true
  error.value = null
  
  try {
    const data = await api.packs.list()
    packs.value = data
  } catch (err) {
    error.value = err.message
    // get response code
    if (err.response) {
      console.log('Response code:', err.response.status)
    }
    console.error('Failed to fetch packs:', err)
    // Fallback to dummy data on error
    packs.value = [
      {
        id: 1,
        name: 'Renge Hanabi Pack',
        anime_title: 'Renge Hanabi',
        anime_slug: 'renge-hanabi',
        synopsis: 'A dreamy collection of melodic beatmapsets inspired by Renge Hanabi.',
        beatmapset_ids: [101, 102, 103],
        beatmapset_count: 3,
        downloads: 1240,
        created_at: '2023-10-01T12:00:00Z',
        updated_at: '2024-02-01T12:00:00Z'
      },
      {
        id: 2,
        name: 'Out of Place Pack',
        anime_title: 'Out of Place',
        anime_slug: 'out-of-place',
        synopsis: 'Upbeat pack with fast-paced osu! maps.',
        beatmapset_ids: [201, 202],
        beatmapset_count: 2,
        downloads: 980,
        created_at: '2024-01-10T09:00:00Z',
        updated_at: '2024-12-01T09:00:00Z'
      },
      {
        id: 3,
        name: 'Various Artists Collection',
        anime_title: 'Ms. VICTORIA',
        anime_slug: 'ms-victoria',
        synopsis: null,
        beatmapset_ids: [301, 302, 303, 304],
        beatmapset_count: 4,
        downloads: 760,
        created_at: '2022-06-05T10:00:00Z',
        updated_at: '2023-07-01T11:00:00Z'
      }
    ]
  } finally {
    loading.value = false
  }
}

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  let list = packs.value.filter(p => {
    if (!q) return true
    return (
      p.name.toLowerCase().includes(q) ||
      p.anime_title.toLowerCase().includes(q) ||
      (p.synopsis && p.synopsis.toLowerCase().includes(q))
    )
  })
  if (sortBy.value === 'downloads') list = list.slice().sort((a, b) => b.downloads - a.downloads)
  if (sortBy.value === 'title') list = list.slice().sort((a, b) => a.name.localeCompare(b.name))
  return list
})
</script>

<template>
  <div class="page">
    <div class="container">
      <header class="top">
        <div class="brand">
          <div class="logo">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="16" cy="16" r="14" stroke="currentColor" stroke-width="2.5"/>
              <circle cx="16" cy="16" r="6" fill="currentColor"/>
            </svg>
          </div>
          <h1>ossanimap</h1>
          <p class="tagline">your favorite anime beatmap packs in one place</p>
        </div>

        <div class="controls">
          <div class="search-container" ref="searchInput">
            <div class="search-box" :class="{ 'disabled': rateLimitError }">
              <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8"></circle>
                <path d="m21 21-4.35-4.35"></path>
              </svg>
              <input 
                v-model="query" 
                @keypress="handleSearchKeyPress"
                placeholder="Search or create packs here..." 
                aria-label="search"
                :disabled="rateLimitError"
              />
            </div>

            <!-- Search indicator message -->
            <div v-if="query.trim().length >= 3 && !showSuggestions" class="search-indicator">
              <div v-if="searchLoading" class="search-indicator-loading">
                <div class="small-spinner"></div>
                <span>Searching for anime...</span>
              </div>
              <div v-else class="search-indicator-message">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="12" y1="16" x2="12" y2="12"></line>
                  <line x1="12" y1="8" x2="12.01" y2="8"></line>
                </svg>
                <span>Can't find your anime? Press <kbd>Enter</kbd> to search and click to request pack</span>
              </div>
            </div>

            <!-- Search suggestions dropdown -->
            <div v-if="showSuggestions" class="search-suggestions">
              <div v-if="searchLoading" class="suggestions-loading">
                <div class="small-spinner"></div>
                <span>Searching...</span>
              </div>
              <div v-else>
                <div class="suggestions-header">Request for packs</div>
                <ul class="suggestions-list">
                  <li 
                    v-for="suggestion in searchSuggestions" 
                    :key="suggestion.slug"
                    @click="handleSuggestionClick(suggestion)"
                    class="suggestion-item"
                    :class="{ 'requesting': requestingPackSlug === suggestion.slug }"
                  >
                    <div class="suggestion-content">
                      <span class="suggestion-name">{{ suggestion.name }}</span>
                      <div class="suggestion-meta">
                        <span v-if="suggestion.year" class="suggestion-year">{{ suggestion.year }}</span>
                        <div v-if="requestingPackSlug === suggestion.slug" class="suggestion-loading">
                          <div class="small-spinner"></div>
                          <span>Requesting...</span>
                        </div>
                      </div>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- chimu.moe Unreachable Warning Banner -->
      <div v-if="rateLimitError" class="rate-limit-banner error-banner">
        <div class="banner-content">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <div class="banner-text">
            <strong>(｡•́ㅁ•̀｡) Service Unavailable:</strong>
            <span>
              chimu.moe is currently unreachable. Downloads and search requests are temporarily disabled.
            </span>
          </div>
        </div>
      </div>

      <!-- Rate Limit Warning Banner -->
      <div v-if="showRateLimitWarning && rateLimitInfo" class="rate-limit-banner">
        <div class="banner-content">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
            <line x1="12" y1="9" x2="12" y2="13"></line>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
          </svg>
          <div class="banner-text">
            <strong>Download Limit Warning:</strong>
            <span v-if="rateLimitInfo.daily.remaining.downloads === 0">
              Daily download quota exhausted. Please try again tomorrow.
            </span>
            <span v-else>
              Only {{ rateLimitInfo.daily.remaining.downloads }} of {{ rateLimitInfo.daily.limit.downloads }} 
              daily downloads remaining. Use wisely!
            </span>
          </div>
        </div>
      </div>

      <main>
        <div class="results-header">
          <h2>{{ filtered.length }} Pack{{ filtered.length !== 1 ? 's' : '' }}</h2>
          <div class="sort-labels">
            <span @click="sortBy = 'title'" :class="{ active: sortBy === 'title' }">Title</span>
            <span class="divider">·</span>
            <span @click="sortBy = 'downloads'" :class="{ active: sortBy === 'downloads' }">Downloads</span>
          </div>
        </div>

        <!-- Loading state -->
        <div v-if="loading" class="loading-state">
          <div class="loading-emoji">৻( •̀ ᗜ •́ ৻)</div>
          <p class="loading-message">Fetching database.</p>
          <p class="loading-hint">Please wait for a moment, it can take about 30 seconds if the server was idle</p>
        </div>

        <!-- Error state -->
        <div v-else-if="error" class="error-state">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <p>{{ error }}</p>
          <button @click="fetchPacks" class="retry-btn">Retry</button>
        </div>

        <!-- Empty state -->
        <div v-else-if="filtered.length === 0" class="empty-state">
          <div class="empty-emoji">૮(˶ㅠ︿ㅠ)ა</div>
          <p class="empty-message">There are no packs yet.</p>
          <p class="empty-hint">You may request for packs of your desired anime through the search bar</p>
        </div>

        <!-- Packs list -->
        <section v-else class="cards">
          <BeatmapCard 
            v-for="pack in filtered" 
            :key="pack.id" 
            :pack="pack" 
            :disabled="rateLimitError" 
          />
        </section>
      </main>
    </div>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  padding: 32px 24px;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.container {
  width: 100%;
}

.top {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
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
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.brand h1 {
  font-size: 28px;
  font-weight: 700;
  margin: 0;
  color: #1a202c;
  letter-spacing: -0.5px;
}

.controls {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  flex-wrap: wrap;
}

.search-container {
  position: relative;
  flex: 1;
  min-width: 280px;
  max-width: 500px;
}

.search-box {
  display: flex;
  align-items: center;
  background: white;
  padding: 10px 16px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06), 0 1px 2px rgba(0, 0, 0, 0.04);
  gap: 10px;
  transition: all 0.2s ease;
}

.search-box.disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: #f7fafc;
}

.search-box.disabled input {
  cursor: not-allowed;
}

.search-box:focus-within {
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.2), 0 2px 4px rgba(0, 0, 0, 0.06);
  transform: translateY(-1px);
}

.search-box.disabled:focus-within {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06), 0 1px 2px rgba(0, 0, 0, 0.04);
  transform: none;
}

.search-icon {
  color: #a0aec0;
  flex-shrink: 0;
}

.search-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #e2e8f0;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  flex-shrink: 0;
}

.search-box input {
  background: transparent;
  border: 0;
  color: #2d3748;
  outline: none;
  padding: 0;
  font-size: 15px;
  flex: 1;
  min-width: 0;
}

.search-box input::placeholder {
  color: #a0aec0;
}

/* Search Indicator */
.search-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  padding: 10px 12px;
  background: #f7fafc;
  border-radius: 8px;
  font-size: 13px;
  color: #4a5568;
  border-left: 3px solid #667eea;
}

.search-indicator-message,
.search-indicator-loading {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.search-indicator-message svg {
  color: #667eea;
  flex-shrink: 0;
}

.search-indicator-loading {
  color: #667eea;
  font-weight: 500;
}

.search-indicator kbd {
  background: white;
  border: 1px solid #cbd5e0;
  border-radius: 4px;
  padding: 2px 6px;
  font-family: monospace;
  font-size: 12px;
  font-weight: 600;
  color: #2d3748;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

/* Search Suggestions Dropdown */
.search-suggestions {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12), 0 2px 6px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  z-index: 1000;
  max-height: 400px;
  overflow-y: auto;
}

.suggestions-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 20px;
  color: #718096;
}

.small-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #e2e8f0;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

.suggestions-header {
  padding: 12px 16px;
  font-size: 12px;
  font-weight: 600;
  color: #718096;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: #f7fafc;
  border-bottom: 1px solid #e2e8f0;
}

.suggestions-list {
  list-style: none;
  margin: 0;
  padding: 0;
  max-height: 300px;
  overflow-y: auto;
}

.suggestion-item {
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.15s ease;
  border-bottom: 1px solid #f7fafc;
}

.suggestion-item:last-child {
  border-bottom: none;
}

.suggestion-item:hover {
  background: #f7fafc;
}

.suggestion-item.requesting {
  background: #f7fafc;
  cursor: wait;
  opacity: 0.7;
}

.suggestion-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.suggestion-name {
  color: #2d3748;
  font-size: 14px;
  font-weight: 500;
  flex: 1;
}

.suggestion-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.suggestion-year {
  color: #a0aec0;
  font-size: 13px;
  font-weight: 400;
}

.suggestion-loading {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #667eea;
  font-size: 13px;
  font-weight: 500;
}

/* Dropdown transition */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* Rate Limit Warning Banner */
.rate-limit-banner {
  background: linear-gradient(135deg, #fed7aa 0%, #fbbf24 100%);
  border: 1px solid #f59e0b;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.2);
}

.error-banner {
  background: linear-gradient(135deg, #fecaca 0%, #f87171 100%);
  border: 1px solid #dc2626;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
}

.error-banner .banner-content svg {
  color: #7f1d1d;
}

.error-banner .banner-text {
  color: #7f1d1d;
}

.banner-content {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.banner-content svg {
  color: #92400e;
  flex-shrink: 0;
  margin-top: 2px;
}

.banner-text {
  flex: 1;
  color: #78350f;
  font-size: 14px;
  line-height: 1.5;
}

.banner-text strong {
  font-weight: 700;
  margin-right: 4px;
}

.sort-box {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sort-box label {
  font-size: 12px;
  font-weight: 600;
  color: #718096;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.sort-box select {
  background: white;
  color: #2d3748;
  border: 1px solid #e2e8f0;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.sort-box select:hover {
  border-color: #cbd5e0;
}

.sort-box select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

main {
  margin-top: 0;
}

.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.results-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #2d3748;
}

.sort-labels {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.sort-labels span {
  color: #718096;
  cursor: pointer;
  transition: color 0.2s ease;
  font-weight: 500;
}

.sort-labels span:not(.divider):hover {
  color: #667eea;
}

.sort-labels span.active {
  color: #667eea;
  font-weight: 600;
}

.sort-labels .divider {
  cursor: default;
  user-select: none;
}

.cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.loading-state p,
.error-state p {
  margin: 16px 0 0;
  color: #4a5568;
  font-size: 16px;
}

.loading-emoji {
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

.loading-message {
  margin: 0 0 12px !important;
  color: #2d3748 !important;
  font-size: 20px !important;
  font-weight: 600;
}

.loading-hint {
  margin: 0 !important;
  color: #718096 !important;
  font-size: 15px !important;
  max-width: 500px;
  line-height: 1.6;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #e2e8f0;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-state svg {
  color: #f56565;
}

.retry-btn {
  margin-top: 20px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.retry-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.retry-btn:active {
  transform: translateY(0);
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.empty-emoji {
  font-size: 64px;
  color: #1a202c;
  margin-bottom: 24px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.empty-message {
  margin: 0 0 12px;
  color: #2d3748;
  font-size: 20px;
  font-weight: 600;
}

.empty-hint {
  margin: 0;
  color: #718096;
  font-size: 15px;
  max-width: 500px;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .container {
    padding: 24px 16px;
  }

  .top {
    margin-bottom: 32px;
  }

  .brand h1 {
    font-size: 24px;
  }

  .controls {
    width: 100%;
  }

  .search-container {
    flex: 1;
    min-width: 0;
    max-width: 100%;
  }

  .search-box {
    min-width: 0;
  }

  .search-indicator {
    font-size: 11px;
    padding: 6px 10px;
  }

  .search-indicator kbd {
    padding: 2px 6px;
    font-size: 10px;
  }

  .cards {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .results-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .rate-limit-banner,
  .error-banner {
    padding: 12px 16px;
  }

  .banner-text {
    font-size: 13px;
  }

  .loading-emoji {
    font-size: 56px;
  }

  .loading-message {
    font-size: 18px !important;
  }

  .loading-hint {
    font-size: 14px !important;
  }

  .empty-emoji {
    font-size: 56px;
  }

  .empty-message {
    font-size: 18px;
  }

  .empty-hint {
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .brand h1 {
    font-size: 20px;
  }

  .brand .logo {
    width: 40px;
    height: 40px;
  }

  .search-container {
    min-width: 0;
  }

  .search-indicator {
    font-size: 10px;
    padding: 5px 8px;
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .search-indicator kbd {
    padding: 2px 5px;
    font-size: 9px;
  }

  .rate-limit-banner,
  .error-banner {
    padding: 10px 14px;
    margin-bottom: 16px;
  }

  .banner-text {
    font-size: 12px;
  }

  .loading-emoji {
    font-size: 48px;
  }

  .loading-message {
    font-size: 16px !important;
  }

  .loading-hint {
    font-size: 13px !important;
    padding: 0 16px;
  }

  .empty-emoji {
    font-size: 48px;
  }

  .empty-message {
    font-size: 16px;
  }

  .empty-hint {
    font-size: 13px;
    padding: 0 16px;
  }
}
</style>

<script setup>
import { ref, computed } from 'vue'
import BeatmapCard from './components/BeatmapCard.vue'

// Dummy data for packs (following the Pack schema)
const query = ref('')
const sortBy = ref('downloads')

const packs = ref([
  {
    id: 1,
    name: 'Renge Hanabi Pack',
    anime_title: 'Renge Hanabi',
    anime_slug: 'renge-hanabi',
    synopsis: 'A dreamy collection of melodic beatmapsets inspired by Renge Hanabi.',
    beatmapset_ids: [101, 102, 103],
    beatmapset_count: 3,
    downloads: 1240,
    artifact_url: null,
    created_at: '2023-10-01T12:00:00Z',
    updated_at: '2024-02-01T12:00:00Z'
  },
  {
    id: 2,
    name: 'Out of Place Pack',
    anime_title: 'Out of Place',
    anime_slug: 'out-of-place',
    synopsis: 'Upbeat pack with fast-paced osu! maps.',
    beatmapset_ids: [201,202],
    beatmapset_count: 2,
    downloads: 980,
    artifact_url: null,
    created_at: '2024-01-10T09:00:00Z',
    updated_at: '2024-12-01T09:00:00Z'
  },
  {
    id: 3,
    name: 'Various Artists Collection',
    anime_title: 'Ms. VICTORIA',
    anime_slug: 'ms-victoria',
    synopsis: null,
    beatmapset_ids: [301,302,303,304],
    beatmapset_count: 4,
    downloads: 760,
    created_at: '2022-06-05T10:00:00Z',
    updated_at: '2023-07-01T11:00:00Z'
  }
])

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
          <div class="search-box">
            <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"></circle>
              <path d="m21 21-4.35-4.35"></path>
            </svg>
            <input v-model="query" placeholder="Search packs..." aria-label="search" />
          </div>
        </div>
      </header>

      <main>
        <div class="results-header">
          <h2>{{ filtered.length }} Pack{{ filtered.length !== 1 ? 's' : '' }}</h2>
          <div class="sort-labels">
            <span @click="sortBy = 'title'" :class="{ active: sortBy === 'title' }">Title</span>
            <span class="divider">·</span>
            <span @click="sortBy = 'downloads'" :class="{ active: sortBy === 'downloads' }">Downloads</span>
          </div>
        </div>

        <section class="cards">
          <BeatmapCard v-for="pack in filtered" :key="pack.id" :pack="pack" />
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
  margin-bottom: 48px;
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
  align-items: center;
  flex-wrap: wrap;
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
  min-width: 280px;
}

.search-box:focus-within {
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.2), 0 2px 4px rgba(0, 0, 0, 0.06);
  transform: translateY(-1px);
}

.search-icon {
  color: #a0aec0;
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

  .search-box {
    flex: 1;
    min-width: 0;
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
}

@media (max-width: 480px) {
  .brand h1 {
    font-size: 20px;
  }

  .brand .logo {
    width: 40px;
    height: 40px;
  }

  .search-box {
    min-width: 200px;
  }
}
</style>

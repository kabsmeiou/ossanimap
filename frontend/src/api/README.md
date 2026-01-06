# API Service

This module provides a clean interface for communicating with the ossanimap backend API.

## Setup

1. Create a `.env` file in the frontend root directory:
```bash
cp .env.example .env
```

2. Configure the API base URL (defaults to `http://localhost:8000`):
```env
VITE_API_BASE_URL=http://localhost:8000
```

## Usage

### Import the API

```javascript
import api from './api'
```

### Available Methods

#### Packs

```javascript
// Get all packs
const packs = await api.packs.list()

// Get a specific pack
const pack = await api.packs.get(1)

// Create a new pack
const newPack = await api.packs.create({
  anime_name: "Sword Art Online",
  status: 1,
  mode: 0
})

// Delete a pack
await api.packs.delete(1)

// Increment pack downloads
await api.packs.incrementDownloads(1)
```

#### Stats

```javascript
// Get global statistics
const stats = await api.stats.getGlobal()
// Returns: { total_packs, total_beatmapsets, total_downloads, total_redirects }
```

#### Anime

```javascript
// Search for anime
const results = await api.anime.search("naruto")

// Get anime by slug
const anime = await api.anime.getBySlug("naruto-shippuden")
```

### Error Handling

The API throws `ApiError` objects with the following properties:

```javascript
try {
  const packs = await api.packs.list()
} catch (error) {
  console.error(error.message)  // Error message
  console.error(error.status)   // HTTP status code
  console.error(error.data)     // Response data if available
}
```

### Example in Vue Component

```vue
<script setup>
import { ref, onMounted } from 'vue'
import api from './api'

const packs = ref([])
const loading = ref(false)
const error = ref(null)

const fetchPacks = async () => {
  loading.value = true
  error.value = null
  
  try {
    packs.value = await api.packs.list()
  } catch (err) {
    error.value = err.message
    console.error('Failed to fetch packs:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchPacks()
})
</script>
```

## Development

### Backend CORS Configuration

Make sure your FastAPI backend has CORS enabled for the frontend origin:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Testing

You can test API calls in the browser console:

```javascript
// In browser console
import('/src/api/index.js').then(async ({ api }) => {
  const stats = await api.stats.getGlobal()
  console.log(stats)
})
```

// src/services/packDownload.js

// Per-minute rate limit tracking
const RATE_LIMIT_PER_MINUTE = 120
const RATE_LIMIT_WINDOW_MS = 60 * 1000 // 1 minute
const SAFETY_BUFFER = 5 // Leave some buffer to avoid hitting exact limit

// Track download timestamps for local rate limiting
let downloadTimestamps = []
// Track the last known server remaining count
let lastServerRemaining = RATE_LIMIT_PER_MINUTE
let lastServerCheck = 0

/**
 * Get remaining downloads in the current minute window (local tracking)
 */
function getLocalRemainingDownloads() {
  const now = Date.now()
  // Remove timestamps older than 1 minute
  downloadTimestamps = downloadTimestamps.filter(ts => now - ts < RATE_LIMIT_WINDOW_MS)
  return RATE_LIMIT_PER_MINUTE - downloadTimestamps.length
}

/**
 * Get effective remaining downloads (considers both local and server tracking)
 */
function getEffectiveRemaining() {
  const localRemaining = getLocalRemainingDownloads()
  // Use the more conservative estimate
  return Math.min(localRemaining, lastServerRemaining) - SAFETY_BUFFER
}

/**
 * Record a download timestamp for local rate limiting
 */
function recordDownload() {
  downloadTimestamps.push(Date.now())
  // Also decrement our cached server remaining
  if (lastServerRemaining > 0) {
    lastServerRemaining--
  }
}

/**
 * Update server remaining count from API response
 */
function updateServerRemaining(remaining) {
  lastServerRemaining = remaining
  lastServerCheck = Date.now()
}

/**
 * Calculate how long to wait before the next download is allowed
 * @returns {number} milliseconds to wait (0 if no wait needed)
 */
function getWaitTimeMs() {
  const now = Date.now()
  downloadTimestamps = downloadTimestamps.filter(ts => now - ts < RATE_LIMIT_WINDOW_MS)
  
  // Check if we have remaining capacity (with safety buffer)
  const effectiveRemaining = getEffectiveRemaining()
  if (effectiveRemaining > 0) {
    return 0
  }
  
  // If no local timestamps, but server says we're out, wait a bit
  if (downloadTimestamps.length === 0) {
    return 5000 // Wait 5 seconds and try again
  }
  
  // Find the oldest timestamp and calculate when it will expire
  const oldestTimestamp = Math.min(...downloadTimestamps)
  const waitTime = (oldestTimestamp + RATE_LIMIT_WINDOW_MS) - now + 500 // Add 500ms buffer
  return Math.max(0, waitTime)
}

/**
 * Sleep for a given number of milliseconds
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * Fetch current rate limits from catboy.best API and update local tracking
 * @returns {{ perMinute: { remaining: number, limit: number }, daily: { remaining: number, limit: number }, count: { downloads: number, limited: number, blocked: number } }}
 */
export async function fetchRateLimits() {
  const response = await fetch('https://catboy.best/api/ratelimits')
  if (!response.ok) throw new Error('Failed to fetch rate limits')
  
  const data = await response.json()
  
  // Update our local tracking with server's current remaining count
  const serverRemaining = data.remaining?.download ?? RATE_LIMIT_PER_MINUTE
  updateServerRemaining(serverRemaining)
  
  return {
    perMinute: {
      remaining: serverRemaining,
      limit: data.types?.download ?? RATE_LIMIT_PER_MINUTE
    },
    daily: {
      remaining: data.daily?.remaining?.downloads ?? Infinity,
      limit: data.daily?.limit?.downloads ?? Infinity
    },
    count: {
      downloads: data.count?.downloads ?? 0,
      limited: data.count?.limited ?? 0,
      blocked: data.count?.blocked ?? 0
    }
  }
}

/**
 * Check rate limits from catboy.best API (both per-minute and daily).
 * @param {number} neededDownloads – how many beatmapset downloads you need.
 * @returns {{ allowed: boolean, message?: string, warning?: string }}
 */
export async function checkRateLimits(neededDownloads = 1) {
  try {
    const limits = await fetchRateLimits()
    const { perMinute, daily, count } = limits

    // Check if user has been limited or blocked (indicates potential ban risk)
    if (count.blocked > 0) {
      return {
        allowed: false,
        message: '🚫 Your IP has been temporarily blocked due to excessive requests. Please wait and try again later.'
      }
    }

    if (count.limited > 50) {
      return {
        allowed: false,
        message: '⚠️ Too many rate-limited requests detected. Please wait a few minutes before downloading to avoid an IP ban.'
      }
    }

    // Check daily limits first
    if (daily.remaining === 0) {
      return {
        allowed: false,
        message: '⚠️ Daily download quota exceeded. Please try again tomorrow.'
      }
    }

    if (daily.remaining < neededDownloads) {
      return {
        allowed: false,
        message: `⚠️ Insufficient daily downloads remaining. You need ${neededDownloads} downloads but only have ${daily.remaining} remaining (${daily.limit} daily limit).`
      }
    }

    // Check per-minute limits with safety buffer
    const effectiveRemaining = getEffectiveRemaining()

    let warning = null

    // Warn if daily limit is getting low
    if (daily.remaining < neededDownloads * 2) {
      warning = `⚠️ Warning: Only ${daily.remaining} downloads remaining today (${daily.limit} daily limit). This pack needs ${neededDownloads} downloads.`
    }

    // Warn about rate limiting for large packs
    if (neededDownloads > RATE_LIMIT_PER_MINUTE - SAFETY_BUFFER) {
      const estimatedMinutes = Math.ceil(neededDownloads / (RATE_LIMIT_PER_MINUTE - SAFETY_BUFFER))
      const additionalWarning = `⏱️ This pack has ${neededDownloads} beatmaps and will take approximately ${estimatedMinutes} minute(s) due to rate limits (${RATE_LIMIT_PER_MINUTE}/min).`
      warning = warning ? `${warning}\n\n${additionalWarning}` : additionalWarning
    } else if (effectiveRemaining < neededDownloads) {
      const waitMinutes = Math.ceil((neededDownloads - effectiveRemaining) / RATE_LIMIT_PER_MINUTE)
      warning = warning 
        ? `${warning}\n\n⏱️ Per-minute rate limit low (${Math.max(0, effectiveRemaining)}/${RATE_LIMIT_PER_MINUTE}). Download will be throttled and may take ~${waitMinutes} extra minute(s).`
        : `⏱️ Per-minute rate limit low (${Math.max(0, effectiveRemaining)}/${RATE_LIMIT_PER_MINUTE}). Download will be throttled and may take ~${waitMinutes} extra minute(s).`
    }

    // Warn if there have been rate-limited requests
    if (count.limited > 10) {
      const limitWarning = `⚠️ You've hit ${count.limited} rate limits recently. Downloads will be paced carefully to avoid an IP ban.`
      warning = warning ? `${warning}\n\n${limitWarning}` : limitWarning
    }

    return { allowed: true, warning }
  } catch (err) {
    console.error('Failed to check rate limits:', err)
    // Allow download to proceed if rate limit check fails
    return { allowed: true }
  }
}

/**
 * Download a beatmapset with rate limiting.
 * Will wait if per-minute rate limit is exhausted.
 * @param {number|string} id - Beatmapset ID
 * @param {function} onWaiting - Optional callback when waiting for rate limit (receives wait time in seconds)
 * @param {function} onDownloadProgress - Optional callback for download progress (receives { loaded, total } in bytes)
 * @returns {Promise<Blob>}
 */
export async function downloadWithoutVideo(id, onWaiting = null, onDownloadProgress = null) {
  // Check if we need to wait for rate limit
  let waitTime = getWaitTimeMs()
  if (waitTime > 0) {
    if (onWaiting) {
      onWaiting(Math.ceil(waitTime / 1000))
    }
    console.log(`Rate limit reached. Waiting ${Math.ceil(waitTime / 1000)}s before downloading ${id}...`)
    await sleep(waitTime)
  }

  const tryFetch = async (url, retryCount = 0) => {
    const res = await fetch(url)
    
    // Handle 429 Too Many Requests
    if (res.status === 429) {
      if (retryCount >= 3) {
        throw new Error('Too many rate limit retries. Please try again later.')
      }
      
      const retryAfter = res.headers.get('Retry-After')
      // Use longer wait time to be safe, minimum 10 seconds
      const waitMs = retryAfter ? Math.max(parseInt(retryAfter) * 1000, 10000) : 15000
      
      // Refresh rate limits from server to sync our local tracking
      try {
        await fetchRateLimits()
      } catch (e) {
        console.warn('Failed to refresh rate limits:', e)
      }
      
      if (onWaiting) {
        onWaiting(Math.ceil(waitMs / 1000))
      }
      console.log(`Received 429, waiting ${Math.ceil(waitMs / 1000)}s... (retry ${retryCount + 1}/3)`)
      await sleep(waitMs)
      
      // Retry the request
      return tryFetch(url, retryCount + 1)
    }
    
    if (!res.ok) throw res
    return readResponseWithProgress(res, onDownloadProgress)
  }

  // Record the download before making the request
  recordDownload()

  try {
    return await tryFetch(`https://catboy.best/d/${id}n`)
  } catch (err) {
    // If it's not a 404, treat as a real failure
    if (err instanceof Response && err.status !== 404) {
      throw new Error(`No-video download failed (${err.status})`)
    }
    // Fallback to normal download
    return await tryFetch(`https://catboy.best/d/${id}`)
  }
}

/**
 * Read response body with progress tracking
 * @param {Response} response - Fetch response
 * @param {function} onProgress - Progress callback ({ loaded, total })
 * @returns {Promise<Blob>}
 */
async function readResponseWithProgress(response, onProgress) {
  const contentLength = response.headers.get('Content-Length')
  const total = contentLength ? parseInt(contentLength, 10) : 0
  
  // If no content-length or no progress callback, just return blob directly
  if (!total || !onProgress) {
    return response.blob()
  }

  const reader = response.body.getReader()
  const chunks = []
  let loaded = 0

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    
    chunks.push(value)
    loaded += value.length
    onProgress({ loaded, total })
  }

  return new Blob(chunks)
}

/**
 * Download multiple beatmapsets with rate limiting.
 * Processes downloads sequentially to respect rate limits.
 * @param {Array<number|string>} ids - Array of beatmapset IDs
 * @param {function} onProgress - Callback for progress updates ({ current, total, currentId, waiting, waitSeconds, downloadedMB, currentDownloadMB })
 * @returns {Promise<Array<{ id: number|string, blob?: Blob, error?: Error }>>}
 */
export async function downloadBeatmapsetsWithRateLimit(ids, onProgress = null) {
  const results = []
  let totalDownloadedBytes = 0 // Track total bytes downloaded across all beatmaps
  let downloadsSinceLastCheck = 0 // Track downloads since last rate limit refresh
  const REFRESH_INTERVAL = 20 // Refresh rate limits every 20 downloads
  
  // Initial rate limit check
  try {
    await fetchRateLimits()
  } catch (e) {
    console.warn('Failed to fetch initial rate limits:', e)
  }
  
  for (let i = 0; i < ids.length; i++) {
    const id = ids[i]
    let currentFileBytes = 0 // Bytes downloaded for current file
    
    // Periodically refresh rate limits to stay in sync with server
    if (downloadsSinceLastCheck >= REFRESH_INTERVAL) {
      try {
        await fetchRateLimits()
        downloadsSinceLastCheck = 0
      } catch (e) {
        console.warn('Failed to refresh rate limits:', e)
      }
    }
    
    if (onProgress) {
      onProgress({ 
        current: i, 
        total: ids.length, 
        currentId: id, 
        waiting: false,
        downloadedMB: totalDownloadedBytes / (1024 * 1024),
        currentDownloadMB: 0
      })
    }
    
    try {
      const blob = await downloadWithoutVideo(
        id, 
        // onWaiting callback
        (waitSeconds) => {
          if (onProgress) {
            onProgress({ 
              current: i, 
              total: ids.length, 
              currentId: id, 
              waiting: true, 
              waitSeconds,
              downloadedMB: totalDownloadedBytes / (1024 * 1024),
              currentDownloadMB: currentFileBytes / (1024 * 1024)
            })
          }
        },
        // onDownloadProgress callback
        ({ loaded, total }) => {
          currentFileBytes = loaded
          if (onProgress) {
            onProgress({ 
              current: i, 
              total: ids.length, 
              currentId: id, 
              waiting: false,
              downloadedMB: (totalDownloadedBytes + loaded) / (1024 * 1024),
              currentDownloadMB: loaded / (1024 * 1024),
              currentFileTotal: total / (1024 * 1024)
            })
          }
        }
      )
      
      totalDownloadedBytes += blob.size
      downloadsSinceLastCheck++
      results.push({ id, blob })
    } catch (err) {
      console.error(`Error downloading map ${id}:`, err)
      results.push({ id, error: err })
      
      // If we hit a rate limit error, refresh and wait before continuing
      if (err.message?.includes('429') || err.message?.includes('rate limit')) {
        try {
          await fetchRateLimits()
          downloadsSinceLastCheck = 0
        } catch (e) {
          console.warn('Failed to refresh rate limits after error:', e)
        }
        // Wait a bit before continuing
        await sleep(5000)
      }
    }
    
    if (onProgress) {
      onProgress({ 
        current: i + 1, 
        total: ids.length, 
        currentId: id, 
        waiting: false,
        downloadedMB: totalDownloadedBytes / (1024 * 1024),
        currentDownloadMB: 0
      })
    }
  }
  
  return results
}

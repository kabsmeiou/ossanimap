// src/services/packDownload.js

// Per-minute rate limit tracking
const RATE_LIMIT_PER_MINUTE = 120
const RATE_LIMIT_WINDOW_MS = 60 * 1000 // 1 minute

// Track download timestamps for local rate limiting
let downloadTimestamps = []

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
 * Record a download timestamp for local rate limiting
 */
function recordDownload() {
  downloadTimestamps.push(Date.now())
}

/**
 * Calculate how long to wait before the next download is allowed
 * @returns {number} milliseconds to wait (0 if no wait needed)
 */
function getWaitTimeMs() {
  const now = Date.now()
  downloadTimestamps = downloadTimestamps.filter(ts => now - ts < RATE_LIMIT_WINDOW_MS)
  
  if (downloadTimestamps.length < RATE_LIMIT_PER_MINUTE) {
    return 0
  }
  
  // Find the oldest timestamp and calculate when it will expire
  const oldestTimestamp = Math.min(...downloadTimestamps)
  const waitTime = (oldestTimestamp + RATE_LIMIT_WINDOW_MS) - now + 100 // Add 100ms buffer
  return Math.max(0, waitTime)
}

/**
 * Sleep for a given number of milliseconds
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * Fetch current rate limits from catboy.best API
 * @returns {{ perMinute: { remaining: number, limit: number }, daily: { remaining: number, limit: number } }}
 */
export async function fetchRateLimits() {
  const response = await fetch('https://catboy.best/api/ratelimits')
  if (!response.ok) throw new Error('Failed to fetch rate limits')
  
  const data = await response.json()
  return {
    perMinute: {
      remaining: data.remaining?.download ?? RATE_LIMIT_PER_MINUTE,
      limit: data.types?.download ?? RATE_LIMIT_PER_MINUTE
    },
    daily: {
      remaining: data.daily?.remaining?.downloads ?? Infinity,
      limit: data.daily?.limit?.downloads ?? Infinity
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
    const { perMinute, daily } = limits

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

    // Check per-minute limits (informational - we'll handle throttling during download)
    const localRemaining = getLocalRemainingDownloads()
    const effectivePerMinute = Math.min(perMinute.remaining, localRemaining)

    let warning = null

    if (daily.remaining < neededDownloads * 2) {
      warning = `⚠️ Warning: Only ${daily.remaining} downloads remaining today (${daily.limit} daily limit). This pack needs ${neededDownloads} downloads.`
    }

    if (neededDownloads > RATE_LIMIT_PER_MINUTE) {
      const estimatedMinutes = Math.ceil(neededDownloads / RATE_LIMIT_PER_MINUTE)
      const additionalWarning = `⏱️ This pack has ${neededDownloads} beatmaps and will take approximately ${estimatedMinutes} minute(s) due to rate limits (${RATE_LIMIT_PER_MINUTE}/min).`
      warning = warning ? `${warning}\n\n${additionalWarning}` : additionalWarning
    } else if (effectivePerMinute < neededDownloads) {
      warning = warning 
        ? `${warning}\n\n⏱️ Per-minute rate limit low (${effectivePerMinute}/${RATE_LIMIT_PER_MINUTE}). Download may be throttled.`
        : `⏱️ Per-minute rate limit low (${effectivePerMinute}/${RATE_LIMIT_PER_MINUTE}). Download may be throttled.`
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

  const tryFetch = async (url) => {
    const res = await fetch(url)
    
    // Handle 429 Too Many Requests
    if (res.status === 429) {
      const retryAfter = res.headers.get('Retry-After')
      const waitMs = retryAfter ? parseInt(retryAfter) * 1000 : 5000
      if (onWaiting) {
        onWaiting(Math.ceil(waitMs / 1000))
      }
      console.log(`Received 429, waiting ${Math.ceil(waitMs / 1000)}s...`)
      await sleep(waitMs)
      // Retry the request
      const retryRes = await fetch(url)
      if (!retryRes.ok) throw retryRes
      return readResponseWithProgress(retryRes, onDownloadProgress)
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
  
  for (let i = 0; i < ids.length; i++) {
    const id = ids[i]
    let currentFileBytes = 0 // Bytes downloaded for current file
    
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
      results.push({ id, blob })
    } catch (err) {
      console.error(`Error downloading map ${id}:`, err)
      results.push({ id, error: err })
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

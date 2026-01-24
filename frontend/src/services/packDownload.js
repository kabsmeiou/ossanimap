// src/services/packDownload.js

/**
 * Check rate limits from catboy.best API.
 * @param {number} neededDownloads – how many beatmapset downloads you need.
 * @returns {{ allowed: boolean, message?: string, warning?: string }}
 */
export async function checkRateLimits(neededDownloads = 1) {
  try {
    const response = await fetch('https://catboy.best/api/ratelimits')
    if (!response.ok) throw new Error('Failed to fetch rate limits')

    const data = await response.json()
    const remaining = data.daily.remaining.downloads
    const total = data.daily.limit.downloads

    if (remaining === 0) {
      return {
        allowed: false,
        message: '⚠️ Daily download quota exceeded. Please try again tomorrow.'
      }
    }

    if (remaining < neededDownloads) {
      return {
        allowed: false,
        message: `⚠️ Insufficient daily downloads remaining. You need ${neededDownloads} downloads but only have ${remaining} remaining (${total} daily limit).`
      }
    }

    if (remaining < neededDownloads * 2) {
      return {
        allowed: true,
        warning: `⚠️ Warning: Only ${remaining} downloads remaining today (${total} daily limit). This pack needs ${neededDownloads} downloads.`
      }
    }

    return { allowed: true }
  } catch (err) {
    console.error('Failed to check rate limits:', err)
    // Allow download to proceed if rate limit check fails
    return { allowed: true }
  }
}

export async function downloadWithoutVideo(id) {
  const tryFetch = async (url) => {
    const res = await fetch(url)
    if (!res.ok) throw res
    return res.blob()
  }

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

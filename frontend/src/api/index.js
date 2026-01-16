// Base API configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

/**
 * Custom error class for API errors
 */
class ApiError extends Error {
  constructor(message, status, data) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.data = data
  }
}

/**
 * Makes an HTTP request to the API
 * @param {string} endpoint - API endpoint path
 * @param {object} options - Fetch options
 * @returns {Promise<any>} Response data
 */
async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  }

  try {
    const response = await fetch(url, config)
    
    // Parse response body
    const data = await response.json().catch(() => null)
    
    // Handle errors
    if (!response.ok) {
      throw new ApiError(
        data?.detail || `HTTP ${response.status}: ${response.statusText}`,
        response.status,
        data
      )
    }
    
    return data
  } catch (error) {
    if (error instanceof ApiError) {
      throw error
    }
    // Network or other errors
    throw new ApiError(
      error.message || 'Network error occurred',
      0,
      null
    )
  }
}

/**
 * API service object with methods for all backend endpoints
 */
export const api = {
  /**
   * Packs endpoints
   */
  packs: {
    /**
     * Get all packs
     * @returns {Promise<Array>} List of packs
     */
    list: () => request('/packs/'),

    /**
     * Get a specific pack by ID
     * @param {number} id - Pack ID
     * @returns {Promise<Object>} Pack details
     */
    get: (id) => request(`/packs/${id}`),

    /**
     * Create a new pack
     * @param {Object} data - Pack creation data
     * @returns {Promise<Object>} Created pack response
     */
    create: (data) =>
      request('/packs/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),

    /**
     * Delete a pack
     * @param {number} id - Pack ID
     * @returns {Promise<Object>} Deletion response
     */
    delete: (id) =>
      request(`/packs/${id}`, {
        method: 'DELETE',
      }),

    /**
     * Increment pack downloads
     * @param {number} id - Pack ID
     * @returns {Promise<Object>} Response
     * GET /packs/{id}/downloads
     */
    incrementDownloads: (id) =>
      request(`/packs/${id}/increment-downloads`),
  },

  /**
   * Stats endpoints
   */
  stats: {
    /**
     * Get global statistics
     * @returns {Promise<Object>} Global stats
     */
    getGlobal: () => request('/stats/'),
  },

  /**
   * Anime endpoints
   */
  anime: {
    /**
     * Search for anime
     * @param {string} query - Search query
     * @returns {Promise<Array>} Search results
     */
    search: (query) => request(`/anime/search?anime_name=${encodeURIComponent(query)}`),
  },

  health: {
    /**
     * Check health status of external services
     * @returns {Promise<Object>} Health status
     */
    check: () => request('/health/'),
    checkChimu: () => request('/health/chimu'),
    checkAnimethemes: () => request('/health/animethemes'),
  },

  job: {
    /**
     * Get job status by job ID
     * @param {string} job_id - Job ID
     * @returns {Promise<Object>} Job status
     */
    getStatus: (job_id) => request(`/job/${job_id}`),
  },
}

export default api

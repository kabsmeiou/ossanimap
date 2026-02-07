// stores/packs.js
import g from 'file-saver'
import { defineStore } from 'pinia'

const DOWNLOADING_STORAGE_KEY = 'ossanimap_downloading_packs'

// Load downloading state from localStorage
function loadDownloadingState() {
  try {
    const saved = localStorage.getItem(DOWNLOADING_STORAGE_KEY)
    return saved ? JSON.parse(saved) : {}
  } catch {
    return {}
  }
}

// Save downloading state to localStorage
function saveDownloadingState(state) {
  try {
    localStorage.setItem(DOWNLOADING_STORAGE_KEY, JSON.stringify(state))
  } catch {
    // Ignore storage errors
  }
}

export const usePacksStore = defineStore('packs', {
  state: () => ({
    packsById: {}, // { [id]: pack }
    downloadingPacks: loadDownloadingState(), // { [packId]: { current, total, downloadedMB, waiting, waitSeconds } }
  }),
  getters: {
    isPackDownloading: (state) => (packId) => {
      return !!state.downloadingPacks[packId]
    },
    getDownloadProgress: (state) => (packId) => {
      return state.downloadingPacks[packId] || { current: 0, total: 0, downloadedMB: 0, waiting: false, waitSeconds: 0 }
    },
  },
  actions: {
    setPacks(packs) {
      for (const p of packs) this.packsById[p.id] = p
    },
    setPack(pack) {
      this.packsById[pack.id] = pack
    },
    getPackById(packId) {
      return this.packsById[packId]
    },
    
    // Download state management
    startDownload(packId, total) {
      this.downloadingPacks[packId] = { 
        current: 0, 
        total, 
        downloadedMB: 0, 
        waiting: false, 
        waitSeconds: 0,
        startedAt: Date.now()
      }
      saveDownloadingState(this.downloadingPacks)
    },
    updateDownloadProgress(packId, progress) {
      if (this.downloadingPacks[packId]) {
        this.downloadingPacks[packId] = {
          ...this.downloadingPacks[packId],
          ...progress
        }
        saveDownloadingState(this.downloadingPacks)
      }
    },
    finishDownload(packId) {
      // Create a new object without the packId to ensure reactivity
      const { [packId]: removed, ...rest } = this.downloadingPacks
      this.downloadingPacks = rest
      saveDownloadingState(this.downloadingPacks)
    },
    // Clean up stale downloads (e.g., from page crashes) - older than 1 hour
    cleanupStaleDownloads() {
      const oneHourAgo = Date.now() - (60 * 60 * 1000)
      const keysToRemove = []
      for (const packId of Object.keys(this.downloadingPacks)) {
        const download = this.downloadingPacks[packId]
        if (download.startedAt && download.startedAt < oneHourAgo) {
          keysToRemove.push(packId)
        }
      }
      if (keysToRemove.length > 0) {
        // Create new object without stale keys
        const newState = { ...this.downloadingPacks }
        for (const key of keysToRemove) {
          delete newState[key]
        }
        this.downloadingPacks = newState
        saveDownloadingState(this.downloadingPacks)
      }
    }
  }
})

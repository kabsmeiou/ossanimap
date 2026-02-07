// src/composables/usePackDownload.js
import { ref, computed } from 'vue'
import JSZip from 'jszip'
import { saveAs } from 'file-saver'
import { downloadBeatmapsetsWithRateLimit, checkRateLimits as defaultCheckRateLimits } from '@/services/packDownload'
import { usePacksStore } from '@/stores/packs'

export function usePackDownload(options = {}) {
  const {
    checkRateLimits = defaultCheckRateLimits,
    incrementDownloadCount = async () => {},
    refreshPackData = async () => {},
    sessionKey = 'skipDownloadModal',
  } = options

  const packsStore = usePacksStore()
  
  // Clean up any stale downloads on init
  packsStore.cleanupStaleDownloads()

  const showModal = ref(false)
  
  // Rate limit modal state
  const rateLimitModal = ref({
    show: false,
    type: 'info', // 'info', 'warning', 'error'
    title: '',
    message: '',
    showConfirm: false,
    showCancel: false,
    showOk: true
  })

  // Track the current pack being downloaded in this instance
  const currentPackId = ref(null)

  // Computed properties that read from store for the current pack
  const isDownloading = computed(() => {
    return currentPackId.value ? packsStore.isPackDownloading(currentPackId.value) : false
  })

  const downloadProgress = computed(() => {
    return currentPackId.value 
      ? packsStore.getDownloadProgress(currentPackId.value)
      : { current: 0, total: 0, downloadedMB: 0, waiting: false, waitSeconds: 0 }
  })

  // Check if a specific pack is downloading (for card components)
  const isPackDownloading = (packId) => packsStore.isPackDownloading(packId)
  const getPackDownloadProgress = (packId) => packsStore.getDownloadProgress(packId)

  // Rate limit modal helpers
  const showRateLimitError = (message) => {
    rateLimitModal.value = {
      show: true,
      type: 'error',
      title: 'Download Blocked',
      message,
      showConfirm: false,
      showCancel: false,
      showOk: true
    }
  }

  const showRateLimitWarning = (message) => {
    return new Promise((resolve) => {
      rateLimitModal.value = {
        show: true,
        type: 'warning',
        title: 'Rate Limit Warning',
        message,
        showConfirm: true,
        showCancel: true,
        showOk: false,
        onConfirm: () => resolve(true),
        onClose: () => resolve(false)
      }
    })
  }

  const closeRateLimitModal = () => {
    const onClose = rateLimitModal.value.onClose
    rateLimitModal.value = { ...rateLimitModal.value, show: false }
    if (onClose) onClose()
  }

  const confirmRateLimitModal = () => {
    const onConfirm = rateLimitModal.value.onConfirm
    rateLimitModal.value = { ...rateLimitModal.value, show: false }
    if (onConfirm) onConfirm()
  }

  // pendingPack is stored so the modal confirm can call handleDownload(pendingPack)
  let pendingPack = null

  const handleDownloadClick = async ({ disabled, pack }) => {
    if (disabled) return
    
    // Check if this pack is already being downloaded
    if (packsStore.isPackDownloading(pack?.id)) {
      showRateLimitError('This pack is already being downloaded.')
      return
    }

    const needed = pack?.beatmapset_ids?.length || 1
    const rateLimitCheck = await checkRateLimits(needed)
    if (!rateLimitCheck.allowed) {
      showRateLimitError(rateLimitCheck.message)
      return
    }

    if (rateLimitCheck.warning) {
      const proceed = await showRateLimitWarning(rateLimitCheck.warning)
      if (!proceed) return
    }

    const skipModal = sessionStorage.getItem(sessionKey) === 'true'
    if (skipModal) {
      await handleDownload(pack)
    } else {
      pendingPack = pack
      showModal.value = true
    }
  }

  // Called by modal confirm — uses pendingPack if pack not supplied
  const handleDownload = async (pack) => {
    const target = pack || pendingPack
    pendingPack = null
    showModal.value = false

    const ids = target?.beatmapset_ids ?? []
    if (!ids.length) return

    const packId = target?.id
    currentPackId.value = packId

    // Start download in store
    packsStore.startDownload(packId, ids.length)

    const zip = new JSZip()
    const folder = zip.folder('beatmap_pack')

    try {
      // Use rate-limited sequential downloads
      const results = await downloadBeatmapsetsWithRateLimit(ids, (progress) => {
        packsStore.updateDownloadProgress(packId, {
          current: progress.current,
          total: progress.total,
          waiting: progress.waiting || false,
          waitSeconds: progress.waitSeconds || 0,
          downloadedMB: progress.downloadedMB || 0
        })
      })

      // Add successful downloads to zip
      for (const result of results) {
        if (result.blob) {
          folder.file(`${result.id}.osz`, result.blob)
        }
      }

      const content = await zip.generateAsync({ type: 'blob' })
      saveAs(content, `${target?.name || 'osu_pack'}.zip`)

      await incrementDownloadCount(packId)
      // Small delay to allow background task to complete before refreshing
      await new Promise(resolve => setTimeout(resolve, 500))
      await refreshPackData(packId)
    } finally {
      // Always finish download in store
      packsStore.finishDownload(packId)
      currentPackId.value = null
    }
  }

  return {
    // state
    showModal,
    isDownloading,
    downloadProgress,
    rateLimitModal,
    
    // helpers for checking any pack's download status
    isPackDownloading,
    getPackDownloadProgress,

    // actions
    handleDownloadClick,
    handleDownload,
    closeRateLimitModal,
    confirmRateLimitModal,
  }
}

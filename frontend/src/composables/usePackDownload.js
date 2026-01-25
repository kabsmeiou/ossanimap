// src/composables/usePackDownload.js
import { ref } from 'vue'
import JSZip from 'jszip'
import { saveAs } from 'file-saver'
import { downloadBeatmapsetsWithRateLimit, checkRateLimits as defaultCheckRateLimits } from '@/services/packDownload'

export function usePackDownload(options = {}) {
  const {
    checkRateLimits = defaultCheckRateLimits,
    incrementDownloadCount = async () => {},
    refreshPackData = async () => {},
    confirmFn = (msg) => window.confirm(msg),
    alertFn = (msg) => window.alert(msg),
    sessionKey = 'skipDownloadModal',
  } = options

  const showModal = ref(false)
  const isDownloading = ref(false)
  const downloadProgress = ref({ current: 0, total: 0, downloadedMB: 0, waiting: false, waitSeconds: 0 })

  // pendingPack is stored so the modal confirm can call handleDownload(pendingPack)
  let pendingPack = null

  const handleDownloadClick = async ({ disabled, pack }) => {
    if (disabled) return

    const needed = pack?.beatmapset_ids?.length || 1
    const rateLimitCheck = await checkRateLimits(needed)
    if (!rateLimitCheck.allowed) {
      alertFn(rateLimitCheck.message)
      return
    }

    if (rateLimitCheck.warning) {
      const proceed = confirmFn(rateLimitCheck.warning + '\n\nDo you want to proceed?')
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

    isDownloading.value = true
    downloadProgress.value = { current: 0, total: ids.length, downloadedMB: 0, waiting: false, waitSeconds: 0 }

    const zip = new JSZip()
    const folder = zip.folder('beatmap_pack')

    // Use rate-limited sequential downloads
    const results = await downloadBeatmapsetsWithRateLimit(ids, (progress) => {
      downloadProgress.value = {
        current: progress.current,
        total: progress.total,
        waiting: progress.waiting || false,
        waitSeconds: progress.waitSeconds || 0,
        downloadedMB: progress.downloadedMB || 0
      }
    })

    // Add successful downloads to zip
    for (const result of results) {
      if (result.blob) {
        folder.file(`${result.id}.osz`, result.blob)
      }
    }

    const content = await zip.generateAsync({ type: 'blob' })
    saveAs(content, `${target?.name || 'osu_pack'}.zip`)

    isDownloading.value = false
    downloadProgress.value = { current: 0, total: 0, downloadedMB: 0, waiting: false, waitSeconds: 0 }

    await incrementDownloadCount(target?.id)
    await refreshPackData(target?.id)
  }

  return {
    // state
    showModal,
    isDownloading,
    downloadProgress,

    // actions
    handleDownloadClick,
    handleDownload,
  }
}

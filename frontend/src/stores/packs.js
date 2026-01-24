// stores/packs.js
import g from 'file-saver'
import { defineStore } from 'pinia'

export const usePacksStore = defineStore('packs', {
  state: () => ({
    packsById: {}, // { [id]: pack }
  }),
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
  }
})

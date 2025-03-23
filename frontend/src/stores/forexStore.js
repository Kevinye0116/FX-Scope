import { loadForexData } from '@/utils/csvParser'
import { updateFavoriteRates } from '@/utils/exchangeRateApi'
import { defineStore } from 'pinia'

export const useForexStore = defineStore('forex', {
    state: () => ({
        forexData: {
            all: [],
            major: [],
            minor: [],
            exotic: [],
            usd: [],
            eur: [],
            aud: [],
            cny: []
        },
        isLoaded: false
    }),

    actions: {
        async loadAllForexData() {
            if (this.isLoaded) return

            try {
                const fileTypes = ['all', 'major', 'minor', 'exotic', 'usd', 'eur', 'aud', 'cny']
                const results = await Promise.all(
                    fileTypes.map(async (type) => {
                        const data = await loadForexData(`/forex/${type}.csv`)
                        if (!data || data.length === 0) {
                            console.error(`No data loaded for type: ${type}`)
                        }
                        return { type, data }
                    })
                )

                results.forEach(({ type, data }) => {
                    this.forexData[type] = data
                })

                this.isLoaded = true
            } catch (error) {
                console.error('Failed to load forex data:', error)
                throw error
            }
        },

        getForexData(type) {
            if (!this.isLoaded) {
                console.warn('Store not loaded yet, loading data...')
                return this.loadAllForexData().then(() => this.forexData[type] || [])
            }
            return this.forexData[type] || []
        },

        async updateFavoriteStocksData(favoriteStocks) {
            const updatedStocks = await updateFavoriteRates(favoriteStocks)

            // Update the stocks in all relevant categories
            Object.keys(this.forexData).forEach(category => {
                this.forexData[category] = this.forexData[category].map(stock => {
                    const updatedStock = updatedStocks.find(s => s.symbol === stock.symbol)
                    return updatedStock || stock
                })
            })
        }
    }
})
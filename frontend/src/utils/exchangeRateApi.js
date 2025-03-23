const VITE_API_KEY = import.meta.env.VITE_EXCHANGE_RATE_API_KEY

export async function fetchExchangeRate(baseCurrency, targetCurrency) {
    try {
        const response = await fetch(
            `https://v6.exchangerate-api.com/v6/${VITE_API_KEY}/pair/${baseCurrency}/${targetCurrency}`
        )
        const data = await response.json()
        return data.conversion_rate
    } catch (error) {
        console.error('Error fetching exchange rate:', error)
        return null
    }
}

export async function updateFavoriteRates(favoriteStocks) {
    const updatedStocks = await Promise.all(
        favoriteStocks.map(async (stock) => {
            const [base, target] = stock.symbol.split(' / ')
            const newPrice = await fetchExchangeRate(base, target)

            if (newPrice) {
                // 获取昨日汇率数据
                const yesterday = new Date()
                yesterday.setDate(yesterday.getDate() - 1)
                const year = yesterday.getFullYear()
                const month = String(yesterday.getMonth() + 1).padStart(2, '0')
                const day = String(yesterday.getDate()).padStart(2, '0')

                try {
                    const response = await fetch(
                        `https://v6.exchangerate-api.com/v6/${VITE_API_KEY}/history/${base}/${year}/${month}/${day}`
                    )
                    const data = await response.json()
                    const yesterdayRate = data.conversion_rates[target]
                    const formattedNewPrice = parseFloat(newPrice.toFixed(5))

                    // 基于昨日收盘价计算涨跌额和涨跌幅
                    const priceChange = parseFloat((formattedNewPrice - yesterdayRate).toFixed(5))
                    const percentChange = parseFloat(((priceChange / yesterdayRate) * 100).toFixed(4))

                    return {
                        ...stock,
                        price: formattedNewPrice.toFixed(5),
                        change: priceChange,
                        changePercent: percentChange
                    }
                } catch (error) {
                    console.error('Error fetching historical rate:', error)
                    return stock
                }
            }
            return stock
        })
    )
    return updatedStocks
}
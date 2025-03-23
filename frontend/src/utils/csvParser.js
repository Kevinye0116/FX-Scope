import Papa from 'papaparse'

export async function loadForexData(filePath) {
    try {
        // 确保路径以 / 开头
        const fullPath = filePath.startsWith('/') ? filePath : `/${filePath}`
        const response = await fetch(fullPath)

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
        }

        const csvData = await response.text()

        const results = Papa.parse(csvData, {
            header: true,
            skipEmptyLines: true
        })

        if (!results.data || results.data.length === 0) {
            throw new Error('No data found in CSV file')
        }

        return results.data.map(record => ({
            symbol: record.Ticker,
            name: record.Description,
            price: record.Price,
            change: parseFloat(parseFloat(record.Change).toFixed(6)),
            changePercent: parseFloat(parseFloat(record['Change %']).toFixed(2)),
            high: parseFloat(record.High),
            low: parseFloat(record.Low),
            bid: parseFloat(record.Bid),
            ask: parseFloat(record.Ask),
            isFollowed: false
        }))
    } catch (error) {
        console.error('Error loading forex data:', error)
        console.error('Failed path:', filePath)
        return []
    }
}

<template>
  <div class="search-container">
    <div class="search-wrapper">
      <el-icon class="search-icon"><Search /></el-icon>
      <input
        type="text"
        class="search-input"
        v-model="query"
        @input="handleInput"
        @keydown.down="selectNext"
        @keydown.up="selectPrev"
        @keydown.enter="confirmSelection"
        placeholder="输入货币对（如 CNY / USD 或 人民币 / 美元）"
      />
      <ul v-show="showSuggestions" class="suggestions">
        <li
          v-for="(suggestion, index) in suggestions"
          :key="suggestion"
          @click="selectSuggestion(suggestion)"
          :class="{ active: index === selectedIndex }"
        >
          <div class="suggestion-item">
            <div class="stock-symbol">
              <div class="currency-pair">
                <div class="flag-container">
                  <img
                    :src="`/flagList/${getCountryCode(suggestion.slice(0, 3))}.svg`"
                    class="country-flag first"
                    alt=""
                  />
                  <img
                    :src="`/flagList/${getCountryCode(suggestion.slice(6, 9))}.svg`"
                    class="country-flag second"
                    alt=""
                  />
                </div>
                <span class="symbol-tag">{{ suggestion }}</span>
                <span class="company-name">{{ getCurrencyName(suggestion) }}</span>
              </div>
            </div>
            <div class="stock-price">
              <span class="price">{{ formatNumber(exchangeRates[suggestion]) }}</span>
              <div class="percentWrapper">
                <span class="change-percent" :class="getChangeClass(suggestion)">
                  {{ getChangePercent(suggestion) }}
                </span>
              </div>
            </div>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { useForexStore } from '@/stores/forexStore'
import { Search } from '@element-plus/icons-vue'
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const forexStore = useForexStore()

const query = ref('')
const suggestions = ref([])
const selectedIndex = ref(-1)
const exchangeRates = ref({})
const VITE_API_KEY = import.meta.env.VITE_EXCHANGE_RATE_API_KEY

const showSuggestions = computed(() => {
  return query.value.length > 0 && suggestions.value.length > 0
})

const fetchRate = async (pair) => {
  try {
    const [base, target] = pair.split('/').map((curr) => curr.trim())
    const response = await fetch(
      `https://v6.exchangerate-api.com/v6/${VITE_API_KEY}/pair/${base}/${target}`
    )
    const data = await response.json()
    exchangeRates.value[`${base} / ${target}`] = data.conversion_rate.toFixed(4)
  } catch (error) {
    console.error('汇率获取失败:', error)
  }
}

const generateSuggestions = (input) => {
  const allForexData = forexStore.getForexData('all')
  if (!allForexData || allForexData.length === 0) return []

  const hasSlash = input.includes('/')

  if (hasSlash) {
    // 如果输入包含斜杠，分别匹配左右两部分
    const [leftPart, rightPart = ''] = input.split('/')
    const trimmedLeft = leftPart.trim()
    const trimmedRight = rightPart.trim()

    return allForexData
      .map((stock) => {
        // 分别获取货币对的代码和名称的左右部分
        const [symbolLeft, symbolRight] = stock.symbol.split('/')
        const [nameLeft, nameRight] = (stock.name || '').split('/')

        // 计算左右两边的匹配度
        const leftMatchSymbol = symbolLeft.trim().toUpperCase().includes(trimmedLeft.toUpperCase())
        const leftMatchName = (nameLeft || '').includes(trimmedLeft)
        const rightMatchSymbol = rightPart
          ? symbolRight.trim().toUpperCase().includes(trimmedRight.toUpperCase())
          : true
        const rightMatchName = rightPart ? (nameRight || '').includes(trimmedRight) : true

        // 综合判断左右两边的匹配情况
        const leftMatch = leftMatchSymbol || leftMatchName
        const rightMatch = rightMatchSymbol || rightMatchName

        let distance = 2
        if (leftMatch && rightMatch) distance = 0
        else if (leftMatch) distance = 1

        return {
          symbol: stock.symbol,
          distance,
          exactMatchLeft: leftMatch,
          exactMatchRight: rightMatch,
          // 给予代码匹配更高的优先级
          symbolMatchLeft: leftMatchSymbol,
          symbolMatchRight: rightMatchSymbol,
        }
      })
      .sort((a, b) => {
        // 优先考虑左边的代码匹配
        if (a.symbolMatchLeft !== b.symbolMatchLeft) {
          return a.symbolMatchLeft ? -1 : 1
        }
        // 然后考虑左边的名称匹配
        if (a.exactMatchLeft !== b.exactMatchLeft) {
          return a.exactMatchLeft ? -1 : 1
        }
        // 然后考虑右边的代码匹配
        if (a.symbolMatchRight !== b.symbolMatchRight) {
          return a.symbolMatchRight ? -1 : 1
        }
        // 最后考虑右边的名称匹配
        if (a.exactMatchRight !== b.exactMatchRight) {
          return a.exactMatchRight ? -1 : 1
        }
        return a.distance - b.distance
      })
      .slice(0, 8)
      .map((item) => item.symbol)
  } else {
    // 如果输入不包含斜杠，优先匹配左边部分
    return allForexData
      .map((stock) => {
        const [symbolLeft, symbolRight] = stock.symbol.split('/')
        const [nameLeft, nameRight] = (stock.name || '').split('/')

        // 匹配代码和名称
        const leftMatchSymbol = symbolLeft.trim().toUpperCase().includes(input.toUpperCase())
        const leftMatchName = (nameLeft || '').includes(input)
        const rightMatchSymbol = symbolRight.trim().toUpperCase().includes(input.toUpperCase())
        const rightMatchName = (nameRight || '').includes(input)

        let distance = 2
        if (leftMatchSymbol || leftMatchName) distance = 0
        else if (rightMatchSymbol || rightMatchName) distance = 1

        return {
          symbol: stock.symbol,
          distance,
          exactMatchLeft: leftMatchSymbol || leftMatchName,
          exactMatchRight: rightMatchSymbol || rightMatchName,
          symbolMatchLeft: leftMatchSymbol,
          symbolMatchRight: rightMatchSymbol,
        }
      })
      .sort((a, b) => {
        // 优先考虑左边的代码匹配
        if (a.symbolMatchLeft !== b.symbolMatchLeft) {
          return a.symbolMatchLeft ? -1 : 1
        }
        // 然后考虑左边的名称匹配
        if (a.exactMatchLeft !== b.exactMatchLeft) {
          return a.exactMatchLeft ? -1 : 1
        }
        // 然后考虑右边的代码匹配
        if (a.symbolMatchRight !== b.symbolMatchRight) {
          return a.symbolMatchRight ? -1 : 1
        }
        // 最后考虑右边的名称匹配
        if (a.exactMatchRight !== b.exactMatchRight) {
          return a.exactMatchRight ? -1 : 1
        }
        return a.distance - b.distance
      })
      .slice(0, 8)
      .map((item) => item.symbol)
  }
}

const handleInput = () => {
  if (query.value.length > 0) {
    suggestions.value = generateSuggestions(query.value)
    selectedIndex.value = -1
    suggestions.value.forEach((pair) => {
      if (!exchangeRates.value[pair]) {
        const cleanPair = pair.replace(/\s+/g, '')
        fetchRate(cleanPair)
      }
    })
  } else {
    suggestions.value = []
  }
}

const selectNext = () => {
  selectedIndex.value = Math.min(selectedIndex.value + 1, suggestions.value.length - 1)
}

const selectPrev = () => {
  selectedIndex.value = Math.max(selectedIndex.value - 1, -1)
}

const confirmSelection = () => {
  if (selectedIndex.value >= 0) {
    selectSuggestion(suggestions.value[selectedIndex.value])
  }
}

const selectSuggestion = (pair) => {
  const name = getCurrencyName(pair)
  query.value = ''
  suggestions.value = []
  router.push({
    name: 'detail',
    params: {
      symbol: pair,
    },
    query: {
      name: name,
      from: router.currentRoute.value.fullPath,
    },
    replace: true,
  })
}

const getCountryCode = (currency) => {
  if (currency === 'ANG') return 'CW'
  else if (currency === 'XCD') return 'AG'
  else if (currency === 'XPF') return 'PF'
  else if (currency === 'XAF') return 'CF'
  else if (currency === 'XDR') return 'US'
  else if (currency === 'TWD') return 'CN'
  return currency.slice(0, 2)
}

const getCurrencyName = (pair) => {
  const allForexData = forexStore.getForexData('all')
  if (!allForexData || allForexData.length === 0) return pair

  // 在 forexStore 数据中查找匹配的货币对
  const matchedPair = allForexData.find((item) => item.symbol === pair)
  return matchedPair ? matchedPair.name : pair
}

const getChangeClass = (pair) => {
  const rate = exchangeRates.value[pair]
  if (!rate) return 'neutral'
  const change = (rate - 1) * 100

  let changeClass = 'neutral'
  if (change > 0) changeClass = 'up'
  else if (change < 0) changeClass = 'down'
  return changeClass
}

const getChangePercent = (pair) => {
  const rate = exchangeRates.value[pair]
  if (!rate) return '加载中...'
  const change = ((rate - 1) * 100).toFixed(2)

  let result = '0.00%'
  if (change > 0) result = `▲${change}%`
  else if (change < 0) result = `▼${Math.abs(change)}%`
  return result
}

const formatNumber = (value) => {
  if (!value) return '加载中...'
  return Number(value).toFixed(4)
}

const handleClickOutside = (event) => {
  const searchContainer = document.querySelector('.search-container')
  if (searchContainer && !searchContainer.contains(event.target)) {
    suggestions.value = [] // 只收起下拉框
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.search-container {
  width: 600px;
  margin: 0 auto;
}

.search-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 16px;
  font-size: 20px;
  color: #909399;
}

.search-input {
  width: 100%;
  height: 46px;
  padding: 12px 20px 12px 45px;
  border: 1px solid #ddd;
  border-radius: 24px;
  font-size: 16px;
  outline: none;
  transition: all 0.3s ease;
}

.search-input:focus {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

.search-input:focus + .search-icon {
  color: #409eff;
}

.suggestions {
  position: absolute;
  width: 100%;
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 12px;
  margin-top: 5px;
  background: white;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  z-index: 1000;
  top: 100%;
  padding: 0;
}

.suggestions li {
  padding: 12px 20px;
  cursor: pointer;
  transition: background 0.2s;
  border-bottom: 1px solid #eee;
}

.suggestions li:last-child {
  border-bottom: none;
}

.suggestions li:hover,
.suggestions li.active {
  background: #f0f8ff;
}

.suggestion-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stock-symbol {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.currency-pair {
  display: flex;
  align-items: center;
  gap: 8px;
}

.flag-container {
  position: relative;
  width: 26px;
  height: 26px;
  margin-right: 5px;
}

.country-flag {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  object-fit: cover;
  position: absolute;
}

.country-flag.first {
  bottom: 0;
  left: 0;
  z-index: 2;
  width: 20px;
  height: 20px;
  border: 2px solid white;
}

.country-flag.second {
  top: 0;
  right: 0;
  z-index: 1;
}

.symbol-tag {
  padding: 6px 5px;
  border-radius: 4px;
  background-color: #f0f0f0;
  color: #333;
  font-size: 12px;
  font-weight: 600;
  width: 80px;
  text-align: center;
}

.company-name {
  color: #333;
  font-size: 14px;
  margin-left: 8px;
}

.stock-price {
  display: flex;
  align-items: center;
  gap: 20px;
  min-width: 200px;
  justify-content: flex-end;
}

.price {
  font-weight: 600;
  width: 80px;
  text-align: right;
  font-size: 14px;
}

.percentWrapper {
  display: flex;
  justify-content: flex-end;
  min-width: 100px;
}

.change-percent {
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 14px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.change-percent.up,
.change.up {
  color: #d24646;
}

.change-percent.down,
.change.down {
  color: #1e723a;
}

.change-percent.up {
  background-color: rgba(202, 57, 41, 0.1);
}

.change-percent.down {
  background-color: rgba(25, 165, 83, 0.1);
}

.change-percent.neutral {
  background-color: rgba(108, 110, 114, 0.1);
  color: #444343;
}
</style>

<template>
  <div class="cross-rate-container">
    <!-- 标签按钮 -->
    <div class="tab-buttons">
      <button
        v-for="(tab, index) in tabs"
        :key="index"
        :class="{ active: activeTab === index }"
        @click="switchTab(index)"
      >
        {{ tab }}
      </button>
    </div>

    <div class="description-container" v-if="currentDescription">
      <h2>{{ currentDescription.title }}</h2>
      <p>{{ currentDescription.description }}</p>
    </div>

    <!-- 汇率表格 -->
    <div class="table-container">
      <div v-if="isLoading" class="loading-overlay">
        <div class="loader"></div>
      </div>
      <table class="rate-table">
        <thead>
          <tr>
            <th scope="row"></th>
            <th
              scope="col"
              v-for="(header, hIndex) in currentHeaders"
              :key="hIndex"
              :class="{ hovered: isHovered && hoveredColumn === hIndex }"
            >
              <div class="header-with-flag">
                <img :src="getFlagUrl(header)" alt="" class="flag-icon" />
                <span>{{ header }}</span>
              </div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(country, rIndex) in currentCountries" :key="rIndex">
            <th scope="row" :class="{ hovered: isHovered && hoveredRow === rIndex }">
              <div class="header-with-flag">
                <img :src="getFlagUrl(country)" alt="" class="flag-icon" />
                <span>{{ country }}</span>
              </div>
            </th>
            <td
              v-for="(header, cIndex) in currentHeaders"
              :key="cIndex"
              :class="[
                {
                  hovered: isHovered && hoveredRow === rIndex && hoveredColumn === cIndex,
                  diagonal: rIndex === cIndex,
                  'no-hover': rIndex === cIndex,
                },
              ]"
              :style="getCellStyle(country, header)"
              @mouseover="onCellHover(rIndex, cIndex)"
              @mouseleave="onCellLeave"
              @click="handleCellClick(rIndex, cIndex)"
            >
              <div class="cell-content">
                <span class="percentage">{{ getPercentage(country, header) }}</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CrossRateTables',
  data() {
    return {
      // 标签页名称
      tabs: ['总览', '欧洲 & 美洲', '亚洲 & 非洲'],
      activeTab: 0, // 当前选中的标签页索引

      // 每个标签页对应的数据
      tableData: [
        {
          headers: ['EUR', 'USD', 'CNY', 'AUD', 'GBP', 'NZD', 'CAD', 'CHF'], // 表头
          countries: ['EUR', 'USD', 'CNY', 'AUD', 'GBP', 'NZD', 'CAD', 'CHF'], // 首列
        },
        {
          headers: ['USD', 'EUR', 'CAD', 'GBP', 'CHF', 'DKK', 'BRL', 'NOK'], // 表头
          countries: ['USD', 'EUR', 'CAD', 'GBP', 'CHF', 'DKK', 'BRL', 'NOK'], // 首列
        },
        {
          headers: ['CNY', 'JPY', 'KRW', 'HKD', 'SGD', 'AED'], // 表头
          countries: ['CNY', 'JPY', 'KRW', 'HKD', 'SGD', 'AED'], // 首列
        },
      ],
      isHovered: false, // 是否悬浮在表格方框上
      hoveredRow: -1, // 当前悬浮的行索引
      hoveredColumn: -1, // 当前悬浮的列索引
      heatmapData: {},
      historicalRates: {},
      currentDateRates: {},
      sevenDayAverage: {},
      refreshTimer: null,
      colorThresholds: {
        positive: '#FCCBCD',
        negativeLight: '#E8F7EE',
        negativeDark: '#D8F0E3',
      },
      isLoading: false,
      descriptions: {
        0: {
          title: '总览',
          description:
            '这个热图展示了主要货币对之间的汇率变化强度。颜色深浅代表过去7天平均汇率与当前汇率的偏离程度：红色表示升值，绿色表示贬值。颜色越深表示变化越显著，帮助您直观地把握市场走势。',
        },
        1: {
          title: '欧洲 & 美洲',
          description:
            '这个视图重点展示欧美货币市场的热力变化。通过颜色深浅直观反映欧元、美元等主要西方货币的相对强弱关系，帮助您快速识别市场趋势。绿色区域表明该货币对走强，粉色区域表明走弱。',
        },
        2: {
          title: '亚洲 & 非洲',
          description:
            '这个热图聚焦于亚非地区货币的相对强弱。通过颜色变化展示人民币、日元等亚太货币的市场表现，反映区域经济态势。深色区域代表显著的汇率变动，浅色区域表示相对稳定的走势。',
        },
      },
    }
  },
  computed: {
    // 获取当前标签页的表头
    currentHeaders() {
      return this.tableData[this.activeTab].headers
    },
    // 获取当前标签页的首列
    currentCountries() {
      return this.tableData[this.activeTab].countries
    },
    currentDescription() {
      return this.descriptions[this.activeTab]
    },
  },
  mounted() {
    this.initializeDates()
    this.fetchHistoricalData()
    this.setupAutoRefresh()
  },
  beforeDestroy() {
    clearTimeout(this.refreshTimer)
  },
  methods: {
    // 获取国旗图片路径
    getFlagUrl(country) {
      const flagMap = {
        EUR: 'flags/euro.svg',
        USD: 'flags/usd.svg',
        CNY: '/flags/china.svg',
        AUD: 'flags/aud.svg',
        GBP: 'flags/gbp.svg',
        NZD: 'flags/nzd.svg',
        CAD: 'flags/cad.svg',
        CHF: 'flags/chf.svg',
        DKK: 'flags/dkk.svg',
        NOK: 'flags/nok.svg',
        BRL: 'flags/brl.svg',
        JPY: 'flags/jpy.svg',
        KRW: 'flags/krw.svg',
        HKD: 'flags/hkd.svg',
        SGD: 'flags/sgd.svg',
        AED: 'flags/aed.svg',
      }
      return flagMap[country] || 'flags/default.png'
    },
    // 切换标签页
    switchTab(index) {
      this.activeTab = index
      this.fetchHistoricalData()
    },
    // 当鼠标悬浮在单元格上时
    onCellHover(rowIndex, colIndex) {
      if (rowIndex !== colIndex) {
        this.isHovered = true
        this.hoveredRow = rowIndex
        this.hoveredColumn = colIndex
      }
    },
    // 当鼠标离开单元格时
    onCellLeave() {
      this.isHovered = false
      this.hoveredRow = -1
      this.hoveredColumn = -1
    },

    handleCellClick(rowIndex, colIndex) {
      if (rowIndex != colIndex) {
        const baseCurrency = this.currentCountries[rowIndex]
        const targetCurrency = this.currentHeaders[colIndex]
        const pairName = `${baseCurrency} / ${targetCurrency}`
        const pairNameCN = this.getCurrencyPairName(pairName)

        this.$router.push({
          name: 'detail',
          params: {
            symbol: pairName,
          },
          query: {
            name: pairNameCN,
            from: this.$route.fullPath,
            view: '热图',
          },
        })
      }
    },

    async initializeDates() {
      const today = new Date()
      this.dates = Array.from({ length: 7 }, (_, i) => {
        const d = new Date(today)
        d.setDate(d.getDate() - i - 1)
        return d
      }).reverse()
    },

    async fetchHistoricalData() {
      this.isLoading = true
      const VITE_API_KEY = import.meta.env.VITE_EXCHANGE_RATE_API_KEY
      try {
        // 获取当日数据（使用新API）
        const todayResponse = await fetch(
          `https://v6.exchangerate-api.com/v6/${VITE_API_KEY}/latest/USD`
        )
        if (!todayResponse.ok) throw new Error('当日数据获取失败')
        const todayData = await todayResponse.json()
        this.currentDateRates = todayData.conversion_rates

        // 获取历史数据（过去7天）
        const historicalPromises = this.dates.map((date) => this.fetchDayData(date))
        const historicalResults = await Promise.all(historicalPromises)

        // 处理历史数据
        this.historicalRates = historicalResults.reduce((acc, result) => {
          console.log(result)
          acc[result.date] = result.conversion_rates
          return acc
        }, {})

        this.calculateAverages()
        this.generateHeatmapData()
      } catch (error) {
        this.error = `数据获取失败: ${error.message}`
      } finally {
        this.isLoading = false
      }
    },

    async fetchDayData(date) {
      const today = new Date()
      const isToday =
        date.getDate() === today.getDate() &&
        date.getMonth() === today.getMonth() &&
        date.getFullYear() === today.getFullYear()

      if (isToday) {
        // 当日数据已通过其他接口获取
        return {
          date: today.toISOString().split('T')[0],
          conversion_rates: this.currentDateRates,
        }
      }

      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')

      const VITE_API_KEY = import.meta.env.VITE_EXCHANGE_RATE_API_KEY
      const response = await fetch(
        `https://v6.exchangerate-api.com/v6/${VITE_API_KEY}/history/USD/${year}/${month}/${day}`
      )

      if (!response.ok) throw new Error('历史数据获取失败')
      const data = await response.json()
      return {
        date: `${data.year}-${String(data.month).padStart(2, '0')}-${String(data.day).padStart(
          2,
          '0'
        )}`, // 如果返回的 API 没有 date 字段，看看是否可以用其他字段来代替
        conversion_rates: data.conversion_rates,
      }
    },

    setupAutoRefresh() {
      // 每小时触发一次（3600000 毫秒）
      this.refreshTimer = setInterval(() => {
        this.fetchHistoricalData()
      }, 3600000) // 每小时更新一次
    },

    // 修改平均值计算方法
    calculateAverages() {
      const currencies = [...new Set([...this.currentCountries, ...this.currentHeaders])]

      currencies.forEach((currency) => {
        const values = Object.values(this.historicalRates)
          .map((rates) => rates[currency])
          .filter(Boolean)

        // 只计算前7天的平均值（排除当日）
        this.sevenDayAverage[currency] =
          values.length > 0 ? values.reduce((a, b) => a + b) / values.length : null
      })
    },

    // 修改热力图生成逻辑
    generateHeatmapData() {
      this.heatmapData = {}
      this.currentCountries.forEach((base) => {
        this.currentHeaders.forEach((target) => {
          if (base === target) return

          // 直接使用API返回的汇率（基于USD）
          const currentRate = this.currentDateRates[target] / this.currentDateRates[base]
          const avgRate = this.sevenDayAverage[target] / this.sevenDayAverage[base]

          const change = ((currentRate - avgRate) / avgRate) * 100
          this.heatmapData[`${base}-${target}`] = isNaN(change) ? 0 : change
        })
      })
    },

    getPercentage(base, target) {
      if (base === target) return '-'
      const change = this.heatmapData[`${base}-${target}`]
      return change ? `${change.toFixed(2)}%` : '-'
    },

    // 修改颜色计算方法
    getCellStyle(base, target) {
      if (base === target) return { cursor: 'default' }
      const change = this.heatmapData[`${base}-${target}`] || 0

      // 根据新规则计算颜色
      if (change > 0.1) {
        return { backgroundColor: this.colorThresholds.positive }
      } else if (change >= 0) {
        return
      } else {
        return {
          backgroundColor:
            Math.abs(change) > 0.1
              ? this.colorThresholds.negativeDark
              : this.colorThresholds.negativeLight,
        }
      }
    },

    showTrend(base, target) {
      return base !== target && this.heatmapData[`${base}-${target}`]
    },

    getTrendDirection(base, target) {
      const change = this.heatmapData[`${base}-${target}`] || 0
      return change > 0 ? 'up' : 'down'
    },

    getCurrencyPairName(pairName) {
      const currencyNames = {
        USD: '美元',
        EUR: '欧元',
        JPY: '日元',
        GBP: '英镑',
        AUD: '澳元',
        CAD: '加元',
        CHF: '瑞士法郎',
        CNY: '人民币',
        NZD: '新西兰元',
        DKK: '丹麦克朗',
        NOK: '挪威克朗',
        BRL: '巴西雷亚尔',
        KRW: '韩元',
        HKD: '港币',
        SGD: '新加坡元',
        AED: '阿联酋迪拉姆',
      }

      const [base, target] = pairName.split(' / ')
      return `${currencyNames[base] || base} / ${currencyNames[target] || target}`
    },
  },
}
</script>
<style scoped>
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2em;
  color: #666;
  z-index: 10;
}

.loader {
  border: 8px solid #f3f3f3; /* 浅灰色背景 */
  border-top: 8px solid #3498db; /* 蓝色的旋转部分 */
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.rate-table td {
  transition: background-color 0.5s ease;
  color: rgba(0, 0, 0, 0.87);
  font-weight: 500;
}

/* 深色背景时的文字颜色 */
.rate-table td[style*='background-color: rgb(76, 175, 80)'],
.rate-table td[style*='background-color: rgb(255, 105, 180)'] {
  color: white;
}

.cross-rate-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
}

.tab-buttons {
  display: flex;
  gap: 12px;
  margin-bottom: 10px;
  margin-top: -10px;
  flex-wrap: wrap;
}

.tab-buttons button {
  padding: 8px 22px;
  border-radius: 100px;
  border: none;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  background-color: #f0f0f0;
  color: #000;
  transition: all 0.3s ease;
}

.tab-buttons button:hover {
  background-color: #e0e0e0;
}

.tab-buttons button.active {
  background-color: #000;
  color: #fff;
  font-weight: 600;
}

.cell-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  height: 100%;
}

.percentage {
  font-weight: 500;
  font-size: 0.9em;
}

.table-container {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow-x: auto; /* 启用水平滚动条 */
  overflow-y: hidden; /* 禁用垂直滚动条，保持界面美观 */
}

.rate-table {
  transition: background-color 0.3s ease;
  width: max-content; /* 根据内容调整表格宽度 */
  border-collapse: collapse;
  text-align: center;
}

.rate-table th,
.rate-table td {
  border: 1px solid rgb(239, 241, 243);
  padding: 0; /* 移除 padding 确保单元格大小一致 */
  font-size: 14px;
  background-color: white;
  width: 160px; /* 单元格宽度 */
  height: 60px; /* 单元格高度，比例为1:2 */
  box-shadow: 0 0 2px rgba(0, 0, 0, 0.1);
  line-height: 1; /* 调整行高，保证文字居中 */
}

.rate-table th {
  background-color: #f8f9fa;
  font-weight: bold;
  color: rgb(113, 116, 121);
}

.header-with-flag {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.flag-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%; /* 圆形图片 */
}

.rate-table td.no-hover:hover {
  cursor: default !important; /* 不显示手型鼠标指针 */
  transform: none !important; /* 不进行缩放 */
  background-color: #f2f2f2 !important;
}

.rate-table td:hover {
  background-color: rgb(190, 222, 255) !important; /* 使用rgba，设置蓝色背景和透明度 */
  cursor: pointer; /* 鼠标指针变为手形 */
  transform: scale(1.05); /* 鼠标悬浮时单元格稍微增大 */
  transition: transform 0.2s ease; /* 添加平滑的过渡效果 */
}

.rate-table tr:nth-child(even) {
  background-color: #f9f9f9;
}

.rate-table td.diagonal {
  background-color: #f2f2f2; /* 调整对角线颜色 */
}

/* 当鼠标悬浮在单元格时，修改对应的表头背景颜色 */
.rate-table th.hovered {
  background-color: rgba(137, 194, 251, 0.41) !important; /* 悬浮时变为浅蓝色 */
}

.description-container {
  margin: 0 0 5px;
  padding: 0 5px;
}

.description-container h2 {
  font-size: 26px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #000;
}

.description-container p {
  font-size: 16px;
  line-height: 1.6;
  color: #333;
  max-width: 600px;
}
</style>

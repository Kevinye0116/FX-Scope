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

    <div v-if="error" class="error-message">
      {{ error }}
      <button @click="fetchRates">重试</button>
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
              {{ calculateRate(country, header).rate }}
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
      ratesData: {}, // 存储原始汇率数据
      oldRatesData: {},
      lastUpdated: null, // 最后更新时间
      isLoading: false, // 加载状态
      error: null, // 错误信息
      refreshInterval: null,
      colorThresholds: {
        positive: '#FCCBCD',
        negativeLight: '#E8F7EE',
        negativeDark: '#D8F0E3',
      },
      descriptions: {
        0: {
          title: '总览',
          description:
            '这个视图展示了主要货币之间的交叉汇率关系。包括欧元、美元、人民币等主要货币，让您可以快速了解全球主要货币之间的兑换关系。表格中的颜色变化反映了相比昨日的汇率变动：红色表示上涨，绿色表示下跌。',
        },
        1: {
          title: '欧洲 & 美洲',
          description:
            '这个视图聚焦于欧美地区的主要货币，包括美元、欧元、加元等。这些货币对在全球外汇市场中占据主导地位，具有最高的流动性和交易量。您可以通过此表格详细了解这些西方主要货币之间的汇率关系。',
        },
        2: {
          title: '亚洲 & 非洲',
          description:
            '这个视图展示了亚非地区主要货币的交叉汇率，包括人民币、日元、港元等。这些新兴市场货币反映了亚太地区的经济活力，以及与全球市场的联系。通过此表格，您可以监控亚太地区货币市场的动态。',
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
      this.fetchRates()
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
      if (rowIndex !== colIndex) {
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
            view: '交叉汇率',
          },
        })
      }
    },

    getCellStyle(base, target) {
      if (base === target) return { cursor: 'default' }
      const { rateClass } = this.calculateRate(base, target)
      if (rateClass === 'increase') {
        return { backgroundColor: this.colorThresholds.positive }
      } else if (rateClass === 'decrease') {
        return { backgroundColor: this.colorThresholds.negativeDark }
      } else if (rateClass === 'no-change') {
        return
      } else {
        return { backgroundColor: this.colorThresholds.negativeLight }
      }
    },
    async fetchRates() {
      this.isLoading = true
      const VITE_API_KEY = import.meta.env.VITE_EXCHANGE_RATE_API_KEY
      try {
        const baseCurrency = this.getBaseCurrency()
        // 修改API端点并使用模板字符串动态插入基准货币
        const response = await fetch(
          `https://v6.exchangerate-api.com/v6/${VITE_API_KEY}/latest/${baseCurrency}`
        )

        if (!response.ok) throw new Error('网络响应异常')

        const data = await response.json()
        this.ratesData = data.conversion_rates
        // 根据ExchangeRate-API的响应结构调整数据获取方式
        this.lastUpdated = new Date(data.timestamp)
        let yesterday = new Date()
        yesterday.setDate(yesterday.getDate() - 1)

        const year = yesterday.getFullYear()
        const month = String(yesterday.getMonth() + 1).padStart(2, '0')
        const day = String(yesterday.getDate()).padStart(2, '0')
        const response_old = await fetch(
          `https://v6.exchangerate-api.com/v6/${VITE_API_KEY}/history/${baseCurrency}/${year}/${month}/${day}`
        )

        if (!response_old.ok) throw new Error('网络响应异常')
        const data_old = await response_old.json()
        this.oldRatesData = data_old.conversion_rates
      } catch (err) {
        this.error = `汇率获取失败: ${err.message}`
        console.error(err)
      } finally {
        this.isLoading = false
      }
    },

    getBaseCurrency() {
      // 根据当前标签页确定基准货币
      const baseCurrencies = ['EUR', 'USD', 'CNY']
      return baseCurrencies[this.activeTab]
    },

    calculateRate(base, target) {
      if (base !== target && this.ratesData && this.oldRatesData) {
        const baseCurrency = this.getBaseCurrency()
        let baseRate = 1
        let targetRate = 1
        if (base === baseCurrency) {
          targetRate = this.ratesData[target]
        } else if (target === baseCurrency) {
          baseRate = this.ratesData[base]
        } else {
          baseRate = this.ratesData[base]
          targetRate = this.ratesData[target]
        }
        const currentRate = (targetRate / baseRate).toFixed(4)
        let oldbaseRate = 1
        let oldtargetRate = 1
        if (base === baseCurrency) {
          oldtargetRate = this.oldRatesData[target]
        } else if (target === baseCurrency) {
          oldbaseRate = this.oldRatesData[base]
        } else {
          oldbaseRate = this.oldRatesData[base]
          oldtargetRate = this.oldRatesData[target]
        }
        const oldRate = (oldtargetRate / oldbaseRate).toFixed(4)
        const difference = currentRate - oldRate
        let rateClass = ''
        if (difference > 0) {
          rateClass = 'increase' // 汇率上升
        } else if (difference < 0) {
          rateClass = 'decrease' // 汇率下降
        } else {
          rateClass = 'no-change' // 汇率未变化
        }
        return { rate: currentRate, rateClass: rateClass }
      }
      return { rate: '-', rateClass: 'no-data' }
    },

    setupAutoRefresh() {
      // 每5分钟刷新一次数据
      this.refreshInterval = setInterval(() => {
        if (!this.isLoading) {
          this.fetchRates()
        }
      }, 60 * 60 * 1000)
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

  mounted() {
    this.fetchRates()
    this.setupAutoRefresh()
  },

  beforeDestroy() {
    clearInterval(this.refreshInterval)
  },

  watch: {
    activeTab() {
      this.fetchRates()
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

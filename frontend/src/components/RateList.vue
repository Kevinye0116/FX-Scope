<template>
  <div class="list-container">
    <!-- Filter Buttons -->
    <div class="filter-buttons">
      <button
        v-for="filter in filters"
        :key="filter.value"
        :class="['filter-btn', { active: activeFilter === filter.value }]"
        @click="setFilter(filter.value)"
      >
        {{ filter.label }}
      </button>
    </div>

    <!-- Filter Description -->
    <div class="filter-description">
      <h2>{{ activeFilterTitle }}</h2>
      <p>{{ activeFilterDescription }}</p>
    </div>

    <!-- Favorites Section -->
    <div class="stock-list">
      <h3 :style="{ 'margin-bottom': '10px', 'font-weight': '600' }">我的关注</h3>
      <transition name="fade">
        <div v-if="favoriteStocks.length > 0" class="stock-header">
          <div class="stock-symbol">
            <span class="header-item">货币对</span>
          </div>
          <div class="stock-price">
            <span class="header-item price">价格</span>
            <span class="header-item change">涨跌额</span>
            <div class="percentWrapper">
              <span class="header-item change-percent">涨跌幅</span>
            </div>
            <span class="header-item price">买入价</span>
            <span class="header-item follow-placeholder"></span>
          </div>
        </div>
      </transition>
      <transition-group name="stock-list" tag="div" class="favorites-container">
        <div
          v-if="showEmptyMessage && !favoriteStocks.length"
          :key="'empty-message'"
          class="empty-favorites stock-list-item"
        >
          暂无关注的货币对
        </div>
        <div
          v-for="stock in favoriteStocks"
          :key="stock.symbol"
          class="stock-item"
          @click="handleStockClick(stock)"
        >
          <div class="stock-symbol">
            <div class="currency-pair">
              <div class="flag-container">
                <img
                  :src="`/flagList/${getCountryCode(stock.symbol.slice(0, 3))}.svg`"
                  class="country-flag"
                  alt=""
                />
                <img
                  :src="`/flagList/${getCountryCode(stock.symbol.slice(6, 9))}.svg`"
                  class="country-flag"
                  alt=""
                />
              </div>
              <span class="symbol-tag">{{ stock.symbol }}</span>
            </div>
            <span class="company-name">{{ stock.name }}</span>
          </div>
          <div class="stock-price">
            <span class="price">{{ formatNumber(stock.price) }}</span>
            <span class="change" :class="{ up: stock.change > 0, down: stock.change < 0 }">
              {{ stock.change > 0 ? '+' : '' }}{{ formatNumber(stock.change) }}
            </span>
            <div class="percentWrapper">
              <span
                class="change-percent"
                :class="{
                  up: stock.changePercent > 0,
                  down: stock.changePercent < 0,
                  neutral: stock.changePercent === 0,
                }"
              >
                {{
                  stock.changePercent === 0
                    ? '0.00%'
                    : (stock.changePercent > 0 ? '▲' : '▼') +
                      Math.abs(stock.changePercent).toFixed(2) +
                      '%'
                }}
              </span>
            </div>
            <span class="price">{{ isNaN(stock.bid) ? '—' : formatNumber(stock.bid) }}</span>
            <button
              class="follow-btn is-followed"
              @click.stop="toggleFollow(stock)"
              :class="{ 'fade-out': stock.isRemoving }"
            >
              <el-icon><SelectIcon /></el-icon>
            </button>
          </div>
        </div>
      </transition-group>
    </div>

    <!-- Original Stock List Section -->
    <div class="stock-list">
      <h3 :style="{ 'margin-bottom': '10px', 'font-weight': '600' }">货币对列表</h3>
      <div class="stock-header">
        <div class="stock-symbol">
          <span class="header-item">货币对</span>
        </div>
        <div class="stock-price">
          <span class="header-item price">价格</span>
          <span class="header-item change">涨跌额</span>
          <div class="percentWrapper">
            <span class="header-item change-percent">涨跌幅</span>
          </div>
          <span class="header-item price">买入价</span>
          <span class="header-item follow-placeholder"></span>
        </div>
      </div>
      <div
        v-for="stock in displayedStocks"
        :key="stock.symbol"
        class="stock-item"
        @click="handleStockClick(stock)"
      >
        <div class="stock-symbol">
          <div class="currency-pair">
            <div class="flag-container">
              <img
                :src="`/flagList/${getCountryCode(stock.symbol.slice(0, 3))}.svg`"
                class="country-flag"
                alt=""
              />
              <img
                :src="`/flagList/${getCountryCode(stock.symbol.slice(6, 9))}.svg`"
                class="country-flag"
                alt=""
              />
            </div>
            <span class="symbol-tag">{{ stock.symbol }}</span>
          </div>
          <span class="company-name">{{ stock.name }}</span>
        </div>
        <div class="stock-price">
          <span class="price">{{ formatNumber(stock.price) }}</span>
          <span class="change" :class="{ up: stock.change > 0, down: stock.change < 0 }">
            {{ stock.change > 0 ? '+' : '' }}{{ formatNumber(stock.change) }}
          </span>
          <div class="percentWrapper">
            <span
              class="change-percent"
              :class="{
                up: stock.changePercent > 0,
                down: stock.changePercent < 0,
                neutral: stock.changePercent === 0,
              }"
            >
              {{
                stock.changePercent === 0
                  ? '0.00%'
                  : (stock.changePercent > 0 ? '▲' : '▼') +
                    ' ' +
                    Math.abs(stock.changePercent).toFixed(2) +
                    '%'
              }}
            </span>
          </div>
          <span class="price">{{ isNaN(stock.bid) ? '—' : formatNumber(stock.bid) }}</span>
          <button
            class="follow-btn"
            :class="{ 'is-followed': stock.isFollowed }"
            @click.stop="toggleFollow(stock)"
          >
            <el-icon><component :is="stock.isFollowed ? 'SelectIcon' : 'Plus'" /></el-icon>
          </button>
        </div>
      </div>
    </div>
    <button v-if="hasMoreStocks" class="load-more-btn" @click="loadMore">加载更多</button>
  </div>
</template>

<script>
import { useForexStore } from '@/stores/forexStore'
import { Plus, Select as SelectIcon } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'RateList',
  components: {
    Plus,
    SelectIcon,
  },
  props: {
    stocks: {
      type: Array,
      required: true,
    },
    showEmptyMessage: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      currentPage: 1,
      pageSize: 80,
      activeFilter: 'all',
      filters: [
        { label: '全部货币对', value: 'all' },
        { label: '主要货币对', value: 'major' },
        { label: '次要货币对', value: 'minor' },
        { label: '外来货币对', value: 'exotic' },
        { label: '美元', value: 'usd' },
        { label: '欧元', value: 'eur' },
        { label: '澳元', value: 'aud' },
        { label: '人民币', value: 'cny' },
      ],
    }
  },
  computed: {
    favoriteStocks() {
      return this.stocks.filter((stock) => stock.isFollowed)
    },
    displayedStocks() {
      return this.stocks.slice(0, this.currentPage * this.pageSize)
    },
    hasMoreStocks() {
      return this.displayedStocks.length < this.stocks.length
    },
    activeFilterTitle() {
      const filter = this.filters.find((f) => f.value === this.activeFilter)
      return filter ? filter.label : ''
    },
    activeFilterDescription() {
      switch (this.activeFilter) {
        case 'all':
          return '主要、次要、特殊、欧洲、亚洲及其他货币对将按货币代码的字母顺序排列在此页面上。您可以向下滚动查看完整的货币对列表，您可能会在这个页面上发现一些从未听说过的货币名称。祝您好运！'
        case 'major':
          return '这些货币对基于一组与美元挂钩的热门货币，这些货币对占据了整个外汇市场的大部分交易量，包含全球交易量最大、流动性最强的货币组合。例如，仅欧元兑美元这一货币对就占约 30% 的交易量。这些货币对通常具有最低的点差和最高的市场效率。'
        case 'minor':
          return '这些货币对与美元无关，被称为次要货币对或交叉货币对。这些货币对具有良好的流动性但交易量低于主要货币对。使用主要货币对可以轻松计算交叉汇率。 例如，要计算 EUR / GBP 汇率，只需删除 EUR / USD 和 GBP / USD 汇率中的美元即可。'
        case 'exotic':
          return '外来货币既包括发展中国家的货币，也包括少数特定发达国家的货币。国际货币基金组织等全球性组织的经济统计数据为这组货币对提供了信息。外来货币对通常波动较大，缺乏流动性。这导致交易成本较高，价格波动较大。'
        case 'usd':
          return '美元相关的货币对包含所有以美元（USD）作为基础货币或报价货币的组合，这些是外汇市场中最常见的交易品种。'
        case 'eur':
          return '欧元相关的货币对包含所有以欧元（EUR）作为基础货币或报价货币的组合，这些货币对在欧洲交易时段最活跃。'
        case 'aud':
          return '澳元相关的货币对包含所有以澳元（AUD）作为基础货币或报价货币的组合，反映澳大利亚经济与全球市场的联系。'
        case 'cny':
          return '人民币相关的货币对包含所有以人民币（CNY）作为基础货币或报价货币的组合，反映中国经济与全球市场的联系。'
        default:
          return ''
      }
    },
  },
  watch: {
    activeFilter: {
      immediate: true,
      async handler(newFilter) {
        try {
          let csvPath = 'forex/'
          switch (newFilter) {
            case 'all':
              csvPath += 'all.csv'
              break
            case 'major':
              csvPath += 'major.csv'
              break
            case 'minor':
              csvPath += 'minor.csv'
              break
            case 'exotic':
              csvPath += 'exotic.csv'
              break
            case 'usd':
              csvPath += 'usd.csv'
              break
            case 'eur':
              csvPath += 'eur.csv'
              break
            case 'aud':
              csvPath += 'aud.csv'
              break
            case 'cny':
              csvPath += 'cny.csv'
              break
            default:
              csvPath += 'all.csv'
          }

          // 发出事件通知父组件需要加载新的数据
          this.$emit('change-data-source', csvPath)

          // Update favorite stocks data
          if (this.favoriteStocks.length > 0) {
            const store = useForexStore()
            await store.updateFavoriteStocksData(this.favoriteStocks)
          }
        } catch (error) {
          console.error('Failed to load forex data:', error)
        }
      },
    },
  },
  methods: {
    async loadMore() {
      this.currentPage += 1
      const forexStore = useForexStore()

      try {
        // 获取所有已显示的股票数据（包括新加载的）
        const endIndex = this.currentPage * this.pageSize
        const displayedStocks = this.stocks.slice(0, endIndex)

        // 更新所有已显示的股票数据
        await forexStore.updateFavoriteStocksData(displayedStocks)

        // 从 store 获取更新后的数据
        const type = this.activeFilter
        const updatedData = await forexStore.getForexData(type)

        // 通过事件通知父组件更新数据
        if (updatedData) {
          const favoriteSymbols = this.stocks
            .filter((stock) => stock.isFollowed)
            .map((stock) => stock.symbol)

          const updatedStocks = this.stocks.map((stock, index) => {
            if (index < endIndex) {
              const updatedStock = updatedData.find((s) => s.symbol === stock.symbol)
              return updatedStock
                ? {
                    ...updatedStock,
                    isFollowed: favoriteSymbols.includes(stock.symbol),
                  }
                : stock
            }
            return stock
          })

          // 发出更新事件
          this.$emit('update:stocks', updatedStocks)
        }
      } catch (error) {
        console.error('Failed to update stocks:', error)
        ElMessage.error('更新货币对数据失败')
      }
    },
    formatNumber(value) {
      const num = Number(value)
      if (isNaN(num)) return value
      const formatter = new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 20,
        useGrouping: false,
        notation: 'standard',
      })

      let strValue = formatter.format(Math.abs(num))
      if (num < 0) {
        strValue = '-' + strValue
      }
      if (strValue.includes('.')) {
        const [integer, decimal] = strValue.split('.')
        if (decimal.length < 4) {
          return `${integer}.${decimal.padEnd(4, '0')}`
        }
        return strValue
      }
      return `${strValue}.0000`
    },
    handleStockClick(stock) {
      this.$router.push({
        name: 'detail',
        params: {
          symbol: stock.symbol,
        },
        query: {
          name: stock.name,
          price: stock.price,
          change: stock.change,
          changePercent: stock.changePercent,
          from: this.$route.fullPath,
          view: '汇率',
        },
      })
    },
    toggleFollow(stock) {
      this.$emit('toggle-follow', stock)
    },
    setFilter(filter) {
      this.activeFilter = filter
      // 重置分页
      this.currentPage = 1
    },
    getCountryCode(currency) {
      if (currency === 'ANG') return 'CW'
      else if (currency === 'XCD') return 'AG'
      else if (currency === 'XPF') return 'PF'
      else if (currency === 'XAF') return 'CF'
      else if (currency === 'XDR') return 'US'
      else if (currency === 'TWD') return 'CN'
      return currency.slice(0, 2)
    },
  },
}
</script>

<style scoped>
.list-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
}

.stock-list {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  min-height: 150px;
}

.stock-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 11px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: all 0.3s ease;
}

.stock-item:hover {
  background-color: #f8f9fa;
  transform: translateX(5px);
}

.stock-item:active {
  background-color: #e9ecef;
}

.stock-symbol {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 200px;
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
}

.country-flag {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  object-fit: cover;
  position: absolute;
}

.country-flag:first-child {
  bottom: 0;
  left: 0;
  z-index: 2;
  width: 20px;
  height: 20px;
  border: 2px solid white;
}

.country-flag:last-child {
  top: 0;
  right: 0;
  z-index: 1;
}

.symbol-tag {
  padding: 6px 5px;
  border-radius: 4px;
  border: none;
  background-color: #f0f0f0;
  color: #333;
  font-size: 12px;
  font-weight: 600;
  margin-left: 3px;
  margin-right: 8px;
  width: 80px;
  display: inline-block;
  text-align: center;
  transition: all 0.2s ease;
}

.stock-item:hover .symbol-tag {
  background-color: #409eff;
  color: white;
}

.company-name {
  margin-left: 3px;
  color: #333;
}

.stock-price {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 300px;
  justify-content: flex-end;
}

.price {
  font-weight: 600;
  width: 100px;
  text-align: right;
  font-size: 16px;
}

.change {
  font-weight: 600;
  width: 100px;
  text-align: right;
  font-size: 16px;
  color: inherit;
  margin-left: 15px;
}

.up {
  color: #d24646 !important;
}

.down {
  color: #1e723a !important;
}

.percentWrapper {
  display: flex;
  justify-content: flex-end;
  min-width: 130px;
}

.change-percent {
  font-weight: 600;
  width: auto;
  text-align: right;
  padding: 8px 10px;
  border-radius: 8px;
  display: inline-flex;
  justify-content: flex-end;
  align-items: center;
  font-size: 16px;
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

.follow-btn {
  margin-left: 10px;
  background: transparent;
  border: 1.5px solid #303133;
  cursor: pointer;
  padding: 6px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  width: 22px;
  height: 22px;
}

.follow-btn:hover {
  background-color: #409eff;
  border-color: #409eff;
}

.follow-btn:hover .el-icon {
  color: white;
}

.stock-item .follow-btn[class*='is-followed'] {
  background-color: #808080;
  border-color: #808080;
}

.stock-item .follow-btn[class*='is-followed'] .el-icon {
  color: white;
}

.stock-item .follow-btn[class*='is-followed']:hover {
  background-color: #409eff;
  border-color: #409eff;
}

.stock-list-enter-active {
  transition: all 0.3s ease;
}

.stock-list-leave-active {
  transition: none;
}

.stock-list-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.stock-list-leave-to {
  opacity: 0;
}

.stock-list-move {
  transition: transform 0.3s ease;
}

.empty-favorites {
  text-align: center;
  padding: 20px;
  color: #909399;
  font-size: 14px;
  position: absolute;
  width: 100%;
  left: 0;
}

.favorites-container {
  position: relative;
  min-height: 60px;
}

.stock-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 11px;
  border-top: 1px solid #eee;
  border-bottom: 1px solid #eee;
  color: #666;
  font-size: 14px;
}

.header-item {
  font-weight: 600;
  font-size: 14px;
  color: #6a6a6a;
}

.follow-placeholder {
  width: 22px;
  margin-left: 10px;
}

.stock-price .header-item {
  text-align: right;
}

.stock-price .header-item.price,
.stock-price .header-item.change {
  width: 100px;
  display: inline-block;
}

.stock-price .header-item .high-low {
  min-width: 160px;
  text-align: right;
}

/* 修改为纯淡入淡出动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.load-more-btn {
  width: 100%;
  padding: 15px;
  margin-top: 15px;
  background-color: transparent;
  border: 1px solid #eee;
  border-radius: 13px;
  color: black;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.load-more-btn:hover {
  color: black;
  background-color: #f5f5f5;
  border-color: #e0e0e0;
}

.filter-buttons {
  display: flex;
  gap: 12px;
  margin-bottom: 10px;
  margin-top: -10px;
  flex-wrap: wrap;
}

.filter-btn {
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

.filter-btn:hover {
  background-color: #e0e0e0;
}

.filter-btn.active {
  background-color: #000;
  color: #fff;
  font-weight: 600;
}

.filter-description {
  margin: 0 0 5px;
  padding: 0 5px;
}

.filter-description h2 {
  font-size: 26px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #000;
}

.filter-description p {
  font-size: 16px;
  line-height: 1.6;
  color: #333;
  max-width: 600px;
}
</style>

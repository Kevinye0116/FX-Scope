<template>
  <div class="detail-container">
    <!-- 顶部栏 -->
    <div class="home-container">
      <!-- Logo -->
      <div class="logo">
        <img src="/logo1.png" alt="FX-Scope Logo" class="logo-image" />
      </div>

      <!-- Search Bar -->
      <div class="search-container">
        <Search />
      </div>

      <!-- Avatar -->
      <div class="avatar-container">
        <el-dropdown trigger="click">
          <el-avatar
            :size="40"
            :style="{ backgroundColor: avatarBgColor }"
            v-if="avatarText"
            class="avatar-icon"
          >
            {{ avatarText }}
          </el-avatar>
          <el-avatar :size="40" :icon="UserFilled" class="avatar-icon" v-else />
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="handleAccount">
                <el-icon><User /></el-icon>
                <span style="margin-left: 8px">我的账号</span>
              </el-dropdown-item>
              <el-dropdown-item @click="handleLogout">
                <el-icon><SwitchButton /></el-icon>
                <span style="margin-left: 8px">退出登录</span>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- 返回按钮 -->
    <div class="back-section">
      <el-button @click="goBack" class="back-button">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
    </div>

    <!-- 货币信息 -->
    <div class="detail-content">
      <div class="currency-info">
        <div class="currency-image-container">
          <div class="flag-container">
            <img
              :src="`/flagList/${getCountryCode(baseCurrency)}.svg`"
              class="country-flag primary"
              :alt="`${baseCurrency} flag`"
            />
            <img
              :src="`/flagList/${getCountryCode(targetCurrency)}.svg`"
              class="country-flag secondary"
              :alt="`${targetCurrency} flag`"
            />
          </div>
        </div>
        <div class="currency-details">
          <div class="currency-header">
            <div class="currency-title">
              <h2>{{ symbol }}</h2>
              <div class="currency-name">{{ name }}</div>
            </div>
            <button class="follow-btn" :class="{ 'is-followed': isFollowed }" @click="toggleFollow">
              <el-icon><component :is="isFollowed ? 'Select' : 'Plus'" /></el-icon>
              <span class="follow-text">{{ isFollowed ? '已关注' : '关注' }}</span>
            </button>
          </div>
          <div class="price-section">
            <div class="current-price">{{ price }}</div>
            <div class="change-info" :class="{ up: change > 0, down: change < 0 }">
              <span>{{ change > 0 ? '+' : '' }}{{ change }}</span>
              <span>({{ changePercent }}%)</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Secondary Navigation -->
    <div class="secondary-nav">
      <div
        class="nav-item"
        @click="selectSection('overview')"
        :class="{ active: activeSection === 'overview' }"
      >
        总览
      </div>
      <div
        class="nav-item"
        @click="selectSection('technical')"
        :class="{ active: activeSection === 'technical' }"
      >
        技术
      </div>
    </div>

    <!-- Tertiary Navigation for Overview -->
    <div v-if="activeSection === 'overview'" class="tertiary-nav">
      <div
        class="nav-item"
        @click="selectSubsection('summary')"
        :class="{ active: activeSubsection === 'summary' }"
      >
        概览
      </div>
      <div
        class="nav-item"
        @click="selectSubsection('converter')"
        :class="{ active: activeSubsection === 'converter' }"
      >
        货币转换器
      </div>
    </div>

    <!-- Tertiary Navigation for Technical -->
    <div v-if="activeSection === 'technical'" class="tertiary-nav">
      <div
        class="nav-item"
        @click="selectSubsection('chart')"
        :class="{ active: activeSubsection === 'chart' }"
      >
        K线图
      </div>
      <div
        class="nav-item"
        @click="selectSubsection('risk')"
        :class="{ active: activeSubsection === 'risk' }"
      >
        风险雷达图
      </div>
    </div>

    <!-- Content Area for Overview -->
    <div v-if="activeSection === 'overview'" class="content-area">
      <div v-if="activeSubsection === 'summary'" class="line-chart">
        <!-- TradingView Symbol Overview Widget -->
        <div class="tradingview-widget-container">
          <div class="symbol-chart-container"></div>
        </div>
      </div>

      <div v-if="activeSubsection === 'converter'" class="converter-content">
        <div class="converter-container">
          <!-- 左侧输入框 -->
          <div class="currency-input-group">
            <div class="currency-header">
              <div class="currency-header-left">
                <img
                  :src="`/flagList/${getCountryCode(baseCurrency)}.svg`"
                  class="currency-flag"
                  :alt="`${baseCurrency} flag`"
                />
                <span>{{ baseCurrency }}</span>
              </div>
            </div>
            <input
              type="number"
              v-model="baseAmount"
              class="currency-input"
              @input="handleBaseInput"
              placeholder="输入金额"
            />
          </div>

          <!-- 转换图标 -->
          <div class="swap-icon">
            <el-icon><Refresh /></el-icon>
          </div>

          <!-- 右侧输入框 -->
          <div class="currency-input-group">
            <div class="currency-header">
              <div class="currency-header-right">
                <span>{{ targetCurrency }}</span>
                <img
                  :src="`/flagList/${getCountryCode(targetCurrency)}.svg`"
                  class="currency-flag"
                  :alt="`${targetCurrency} flag`"
                />
              </div>
            </div>
            <input
              type="number"
              v-model="targetAmount"
              class="currency-input right-align"
              @input="handleTargetInput"
              placeholder="输入金额"
            />
          </div>
        </div>

        <!-- 日期选择器 -->
        <div class="date-selector">
          <el-date-picker
            v-model="selectedDate"
            type="date"
            placeholder="选择日期"
            :disabled-date="disabledDate"
            @change="handleDateChange"
            value-format="YYYY-MM-DD"
          />
        </div>

        <div class="rate-info">
          1 {{ baseCurrency }} = {{ price }} {{ targetCurrency }}
          <span v-if="selectedDate" class="date-info"> ({{ selectedDate }}) </span>
        </div>
      </div>
    </div>

    <!-- Content Area for Technical -->
    <div v-if="activeSection === 'technical'" class="content-area">
      <div v-if="activeSubsection === 'chart'" class="chart-container">
        <!-- TradingView Advanced Chart Widget -->
        <div class="tradingview-widget-container" v-show="activeSubsection === 'chart'">
          <div class="advanced-chart-container"></div>
        </div>
      </div>
      <div v-if="activeSubsection === 'risk'" class="risk-chart">
        <RiskChart />
      </div>
    </div>
  </div>

  <!-- Bottom Container -->
  <div class="bottom-container">
    <BottomBar
      :is-about-us-expanded="isAboutUsExpanded"
      :is-copyright-expanded="isCopyrightExpanded"
      @toggle-about="toggleAboutUs"
      @toggle-copyright="toggleCopyright"
    />
  </div>

  <!-- Setting Dialog -->
  <SettingDialog
    v-model:visible="accountDialogVisible"
    v-model:userInfo="userInfo"
    :avatar-bg-color="avatarBgColor"
  />

  <!-- Chat Window -->
  <ChatWindow
    v-model:visible="isChatVisible"
    :position="chatPosition"
    v-model:position="chatPosition"
    :messages="messages"
    :isWaitingResponse="isWaitingResponse"
    :initialMode="savedChatMode"
    @save-mode="saveChatMode"
    @send="handleSendMessage"
  />

  <!-- Chat Button -->
  <div
    class="float-chat-btn"
    :class="{ 'chat-open': isChatVisible, breathing: isBreathing && !isChatVisible }"
  >
    <!-- 添加提示框和箭头 -->
    <div class="chat-tooltip" v-if="showChatTooltip">
      <div class="tooltip-content">
        点击聊天窗口，获取汇率风险信息和研究报告，尽情和FX-Assistant聊天吧！
      </div>
      <div class="tooltip-arrow"></div>
      <el-icon class="tooltip-close" @click.stop="dismissTooltip"><Close /></el-icon>
    </div>
    <el-button type="primary" circle @click="toggleChat">
      <el-icon>
        <ChatDotSquare />
      </el-icon>
    </el-button>
  </div>
</template>

<script>
import {
  ArrowLeft,
  ChatDotSquare,
  Close,
  Plus,
  Refresh,
  Search,
  Select,
  SwitchButton,
  User,
  UserFilled,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { addFavorite, getFavorites, getUserInfo, removeFavorite } from '../api/user'
import BottomBar from '../components/BottomBar.vue'
import ChatWindow from '../components/ChatWindow.vue'
import RiskChart from '../components/RiskChart.vue'
import SettingDialog from '../components/SettingDialog.vue'
import { fetchExchangeRate } from '../utils/exchangeRateApi'

export default {
  name: 'DetailView',
  components: {
    ArrowLeft,
    ChatDotSquare,
    Close,
    Plus,
    Search,
    Select,
    SwitchButton,
    User,
    SettingDialog,
    BottomBar,
    ChatWindow,
    Refresh,
    RiskChart,
  },
  setup() {
    return {
      UserFilled,
    }
  },
  data() {
    return {
      symbol: this.$route.params.symbol || '',
      name: this.$route.query.name || '',
      price: '0',
      change: 0,
      changePercent: 0,
      isFollowed: false,
      isAboutUsExpanded: false,
      isCopyrightExpanded: false,
      searchQuery: '',
      avatarBgColor: this.getRandomColor(),
      avatarText: '',
      accountDialogVisible: false,
      userInfo: {
        username: '',
        email: '',
      },
      baseCurrency: '',
      targetCurrency: '',
      activeSection: 'overview',
      activeSubsection: 'summary',
      baseAmount: '',
      targetAmount: '',
      selectedDate: '',
      isChatVisible: false,
      messages: [],
      isWaitingResponse: false,
      showChatTooltip: true,
      isBreathing: false,
      chatPosition: {
        right: '2.5%',
        bottom: '10%',
      },
      savedChatMode: localStorage.getItem('chatMode') || 'floating',
    }
  },
  computed: {
    avatarText() {
      if (!this.userInfo.username) return ''
      const firstChar = this.userInfo.username.charAt(0)
      return firstChar
    },
  },
  async created() {
    // 获取用户信息
    await this.fetchUserInfo()

    // 继续执行原有的 refreshData
    await this.refreshData()
  },
  beforeDestroy() {
    // 清除定时器
    if (this.rateUpdateInterval) {
      clearInterval(this.rateUpdateInterval)
    }
  },
  mounted() {
    // 监听 activeSection 和 activeSubsection 的变化
    this.$watch(
      () => [this.activeSection, this.activeSubsection],
      ([newSection, newSubsection]) => {
        this.$nextTick(() => {
          if (newSection === 'overview' && newSubsection === 'summary') {
            this.initSymbolOverviewWidget()
          } else if (newSection === 'technical' && newSubsection === 'chart') {
            this.initAdvancedChartWidget()
          }
        })
      },
      { immediate: true }
    )
  },
  watch: {
    '$route.params.symbol': {
      immediate: true,
      handler(newSymbol, oldSymbol) {
        // 只在 symbol 真正改变时才刷新数据
        if (newSymbol !== oldSymbol) {
          this.symbol = newSymbol
          this.refreshData()
        }
      },
    },
    selectedTimeScale(newVal) {
      this.adjustDateRange(newVal)
      this.fetchHistoricalData()
    },
    selectedDateRange() {
      this.fetchHistoricalData()
    },
  },
  methods: {
    async refreshData() {
      // 防止重复调用
      if (this._refreshing) return
      this._refreshing = true

      try {
        this.searchQuery = ''
        // 解析货币对
        const [base, target] = this.symbol.replace(/\s/g, '').split('/')
        this.baseCurrency = base
        this.targetCurrency = target

        // 获取实时汇率
        await this.fetchCurrentRate()

        // 获取用户收藏状态
        await this.fetchUserInfo()
        try {
          const response = await getFavorites()
          const favoriteSymbols = response.map((item) => item.symbol)
          this.isFollowed = favoriteSymbols.includes(this.symbol)
        } catch (error) {
          console.error('Failed to fetch favorites:', error)
        }

        // 只在需要时初始化组件
        if (this.activeSection === 'overview' && this.activeSubsection === 'summary') {
          this.$nextTick(() => {
            this.initSymbolOverviewWidget()
          })
        } else if (this.activeSection === 'technical' && this.activeSubsection === 'chart') {
          this.$nextTick(() => {
            this.initAdvancedChartWidget()
          })
        }
      } catch (error) {
        console.error('Error refreshing data:', error)
        ElMessage.error('刷新数据失败')
      } finally {
        this._refreshing = false
      }
    },
    initSymbolOverviewWidget() {
      // 清除可能存在的旧widget
      const container = document.querySelector('.symbol-chart-container')
      if (container) {
        container.innerHTML = ''
        const script = document.createElement('script')
        script.type = 'text/javascript'
        script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-symbol-overview.js'
        script.async = true
        const [base, target] = this.symbol.replace(/\s/g, '').split('/')
        script.innerHTML = JSON.stringify({
          symbols: [[`FX_IDC:${base}/${target}`, `FX_IDC:${base}${target}|1D`]],
          chartOnly: false,
          width: '100%',
          height: '100%',
          locale: 'zh_CN',
          colorTheme: 'light',
          autosize: true,
          showVolume: false,
          showMA: false,
          hideDateRanges: false,
          hideMarketStatus: false,
          hideSymbolLogo: false,
          scalePosition: 'right',
          scaleMode: 'Normal',
          fontFamily: '-apple-system, BlinkMacSystemFont, Trebuchet MS, Roboto, Ubuntu, sans-serif',
          fontSize: '10',
          noTimeScale: false,
          valuesTracking: '1',
          changeMode: 'price-and-percent',
          chartType: 'area',
          maLineColor: '#2962FF',
          maLineWidth: 1,
          maLength: 9,
          headerFontSize: 'medium',
          lineWidth: 2,
          lineType: 0,
          dateRanges: ['1d|1', '1m|30', '3m|60', '12m|1D', '60m|1W', 'all|1M'],
        })
        container.appendChild(script)
      }
    },
    initAdvancedChartWidget() {
      // 清除可能存在的旧widget
      const container = document.querySelector('.advanced-chart-container')
      if (container) {
        container.innerHTML = ''
        const script = document.createElement('script')
        script.type = 'text/javascript'
        script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js'
        script.async = true
        const [base, target] = this.symbol.replace(/\s/g, '').split('/')

        const config = {
          autosize: true,
          symbol: `${base}${target}`,
          interval: 'D',
          timezone: 'Etc/UTC',
          theme: 'light',
          style: '1',
          locale: 'zh_CN',
          backgroundColor: 'rgba(255, 255, 255, 1)',
          gridColor: 'rgba(255, 255, 255, 0.06)',
          withdateranges: true,
          allow_symbol_change: false,
          save_image: false,
          details: true,
          calendar: false,
          support_host: 'https://www.tradingview.com',
        }

        script.innerHTML = JSON.stringify(config)
        container.appendChild(script)
      }
    },
    toggleAboutUs() {
      this.isCopyrightExpanded = false
      this.isAboutUsExpanded = !this.isAboutUsExpanded
      if (this.isAboutUsExpanded) {
        this.$nextTick(() => {
          window.scrollTo({
            top: document.documentElement.scrollHeight,
            behavior: 'smooth',
          })
        })
      }
    },
    toggleCopyright() {
      this.isAboutUsExpanded = false
      this.isCopyrightExpanded = !this.isCopyrightExpanded
      if (this.isCopyrightExpanded) {
        this.$nextTick(() => {
          window.scrollTo({
            top: document.documentElement.scrollHeight,
            behavior: 'smooth',
          })
        })
      }
    },
    async toggleFollow() {
      try {
        if (this.isFollowed) {
          await removeFavorite(this.symbol)
          this.isFollowed = false
          ElMessage.success('已取消关注')
        } else {
          await addFavorite(this.symbol)
          this.isFollowed = true
          ElMessage.success('已添加到关注')
        }
      } catch (error) {
        ElMessage.error('操作失败，请重试')
        console.error('Failed to toggle favorite:', error)
      }
    },
    handleAccount() {
      this.accountDialogVisible = true
    },
    handleLogout() {
      localStorage.removeItem('token')
      window.location.replace('/auth')
      window.onpopstate = function () {
        window.location.replace('/auth')
      }
    },
    getRandomColor() {
      const colors = [
        '#f56c6c',
        '#e6a23c',
        '#67c23a',
        '#409eff',
        '#9c27b0',
        '#3f51b5',
        '#00bcd4',
        '#009688',
      ]
      return colors[Math.floor(Math.random() * colors.length)]
    },
    async fetchUserInfo() {
      try {
        const response = await getUserInfo()
        this.userInfo = response
      } catch (error) {
        console.error('Failed to fetch user info:', error)
        ElMessage.error('获取用户信息失败')
      }
    },
    async fetchCurrentRate() {
      try {
        // 获取当前汇率
        console.log(this.baseCurrency, this.targetCurrency)
        const currentRate = await fetchExchangeRate(this.baseCurrency, this.targetCurrency)
        if (!currentRate) throw new Error('Failed to fetch current rate')

        // 获取昨天的日期
        let yesterday = new Date()
        yesterday.setDate(yesterday.getDate() - 1)
        const year = yesterday.getFullYear()
        const month = String(yesterday.getMonth() + 1).padStart(2, '0')
        const day = String(yesterday.getDate()).padStart(2, '0')

        // 获取昨天的汇率
        const VITE_API_KEY = import.meta.env.VITE_EXCHANGE_RATE_API_KEY
        const response = await fetch(
          `https://v6.exchangerate-api.com/v6/${VITE_API_KEY}/history/${this.baseCurrency}/${year}/${month}/${day}`
        )
        if (!response.ok) throw new Error('Failed to fetch historical rate')

        const data = await response.json()
        const oldRate = data.conversion_rates[this.targetCurrency]

        // 计算变化
        const formattedNewPrice = parseFloat(currentRate.toFixed(5))
        const priceChange = parseFloat((formattedNewPrice - oldRate).toFixed(5))
        const percentChange = parseFloat(((priceChange / oldRate) * 100).toFixed(4))

        // 更新数据
        this.price = formattedNewPrice.toFixed(5)
        this.change = priceChange
        this.changePercent = percentChange
      } catch (error) {
        console.error('Error updating rates:', error)
        ElMessage.error('获取汇率数据失败')
      }
    },
    getCountryCode(currency) {
      if (!currency) return 'US' // 默认返回

      // 特殊货币代码映射
      const specialCases = {
        ANG: 'CW',
        XCD: 'AG',
        XPF: 'PF',
        XAF: 'CF',
        XDR: 'US',
        TWD: 'CN',
      }

      return specialCases[currency] || currency.slice(0, 2)
    },
    selectSection(section) {
      if (this.activeSection === section) return
      this.activeSection = section
      this.activeSubsection = section === 'overview' ? 'summary' : 'chart'

      // 使用 nextTick 确保 DOM 更新后再初始化组件
      this.$nextTick(() => {
        if (section === 'overview' && this.activeSubsection === 'summary') {
          this.initSymbolOverviewWidget()
        } else if (section === 'technical' && this.activeSubsection === 'chart') {
          this.initAdvancedChartWidget()
        }
      })
    },
    selectSubsection(subsection) {
      if (this.activeSubsection === subsection) return
      this.activeSubsection = subsection

      // 使用 nextTick 确保 DOM 更新后再初始化组件
      this.$nextTick(() => {
        if (this.activeSection === 'overview' && subsection === 'summary') {
          this.initSymbolOverviewWidget()
        } else if (this.activeSection === 'technical' && subsection === 'chart') {
          this.initAdvancedChartWidget()
        }
      })
    },
    formatPrice(value) {
      return parseFloat(value).toFixed(2)
    },
    formatPercentage(value) {
      return `${parseFloat(value).toFixed(2)}%`
    },
    priceChangeClass({ row }) {
      return {
        'price-up': parseFloat(row.changePercent) > 0,
        'price-down': parseFloat(row.changePercent) < 0,
      }
    },
    handleBaseInput() {
      if (this.baseAmount === '') {
        this.targetAmount = ''
        return
      }
      this.targetAmount = (parseFloat(this.baseAmount) * parseFloat(this.price)).toFixed(4)
    },
    handleTargetInput() {
      if (this.targetAmount === '') {
        this.baseAmount = ''
        return
      }
      this.baseAmount = (parseFloat(this.targetAmount) / parseFloat(this.price)).toFixed(4)
    },
    swapCurrencies() {
      // 交换货币金额
      const temp = this.baseAmount
      this.baseAmount = this.targetAmount
      this.targetAmount = temp
    },
    disabledDate(time) {
      // 禁用未来日期和超过一年前的日期
      const today = new Date()
      const oneYearAgo = new Date()
      oneYearAgo.setFullYear(today.getFullYear() - 1)
      return time.getTime() > today.getTime() || time.getTime() < oneYearAgo.getTime()
    },
    async handleDateChange(date) {
      if (!date) {
        await this.fetchCurrentRate() // 如果没有选择日期，恢复到当前汇率
        return
      }

      try {
        const [year, month, day] = date.split('-')
        const VITE_API_KEY = import.meta.env.VITE_EXCHANGE_RATE_API_KEY
        const response = await fetch(
          `https://v6.exchangerate-api.com/v6/${VITE_API_KEY}/history/${this.baseCurrency}/${year}/${month}/${day}`
        )

        if (!response.ok) {
          throw new Error('Failed to fetch historical rate')
        }

        const data = await response.json()
        const historicalRate = data.conversion_rates[this.targetCurrency]

        // 更新价格并重新计算金额
        this.price = historicalRate.toFixed(5)
        if (this.baseAmount) {
          this.handleBaseInput()
        }
      } catch (error) {
        console.error('Error fetching historical rate:', error)
        ElMessage.error('获取历史汇率失败')
      }
    },
    adjustDateRange(scale) {
      const endDate = new Date()
      const startDate = new Date()
      if (scale === '1d') {
        startDate.setDate(endDate.getDate() - 30)
      } else if (scale === '1w') {
        startDate.setDate(endDate.getDate() - 30 * 7)
      } else if (scale === '1m') {
        startDate.setMonth(endDate.getMonth() - 30)
      }
      this.selectedDateRange = [startDate, endDate]
    },
    goBack() {
      const fromPath = '/home'
      this.$router.replace(fromPath)
    },
    toggleChat() {
      this.isChatVisible = !this.isChatVisible

      // 当聊天窗口打开时，停止呼吸效果
      if (this.isChatVisible) {
        this.isBreathing = false
        this.showChatTooltip = false

        // 只有当消息列表为空时才添加欢迎消息，避免重复添加
        if (this.messages.length === 0) {
          this.messages.push({
            type: 'received',
            content:
              '欢迎使用FX-Assistant！我可以帮您：\n\n• 提供实时汇率信息和市场分析\n• 解答外汇交易相关问题\n• 生成个性化交易策略建议\n• 分析汇率风险和趋势\n• 查找专业研究报告\n\n您可以开启深度研究，输入问题，如"美欧贸易关系紧张对美元汇率的影响"，我将为您生成专业的研究报告！',
          })
        }
      }
    },
    async handleSendMessage(message, useDeepSearch = false) {
      if (!this.isWaitingResponse) {
        this.messages.push({
          type: 'sent',
          content: message,
        })
        this.isWaitingResponse = true

        try {
          const response = await fetch('http://localhost:8000/api/chatbot/chat/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Accept: 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ message, useDeepSearch }),
          })
          const data = await response.json()

          // 处理返回的响应内容
          let processedResponse = data.response
          if (!useDeepSearch) {
            processedResponse = processedResponse.replace(/```json[\s\S]*?```/g, '')
          }
          console.log('Processed response:', processedResponse)
          this.messages.push({
            type: 'received',
            content: processedResponse,
          })
        } catch (error) {
          console.error('Chat error:', error)
          this.messages.push({
            type: 'received',
            content: '抱歉，服务出现了问题，请稍后再试。',
          })
        } finally {
          this.isWaitingResponse = false
        }
      }
    },
    saveChatMode(mode) {
      this.savedChatMode = mode
      localStorage.setItem('chatMode', mode)
    },
    dismissTooltip() {
      this.showChatTooltip = false
      this.isBreathing = true // 关闭提示框后启用呼吸效果
    },
  },
}
</script>

<style scoped>
.detail-container {
  max-width: 1250px;
  margin: 0 auto;
}

.home-container {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  width: 100%;
  height: 80px;
}

.logo {
  position: absolute;
  top: 18px;
  left: 5px;
  z-index: 10;
}

.search-container {
  position: absolute;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  width: 600px;
  z-index: 10;
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
  height: 50px;
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

.avatar-container {
  position: absolute;
  top: 20px;
  right: 10px;
  z-index: 10;
  cursor: pointer;
}

.avatar-icon {
  font-size: 18px;
  font-weight: bold;
  text-transform: uppercase;
  cursor: pointer;
}

.avatar-icon:hover {
  opacity: 0.8;
}

.back-section {
  margin: 20px 0;
  padding: 0;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  padding: 10px 20px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.back-button:hover {
  background-color: #ecf5ff;
  color: #409eff;
}

.currency-info {
  display: flex;
  gap: 20px;
  width: 100%;
}

.currency-image-container {
  width: 150px;
  height: 150px;
  background-color: transparent;
  border-radius: 8px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.flag-container {
  position: relative;
  width: 120px;
  height: 120px;
}

.country-flag {
  position: absolute;
  border-radius: 50%;
  object-fit: cover;
}

.country-flag.primary {
  width: 75px;
  height: 75px;
  bottom: 10px;
  left: 10px;
  z-index: 2;
  border: 3px solid white;
}

.country-flag.secondary {
  width: 70px;
  height: 70px;
  top: 5px;
  right: 5px;
  z-index: 1;
}

.currency-details {
  flex-grow: 1;
  padding-left: 30px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 150px;
}

.currency-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  gap: 8px;
  font-weight: 600;
}

.currency-title {
  flex-grow: 1;
}

.currency-title h2 {
  margin: 0;
  font-size: 32px;
  color: #333;
  font-weight: bold;
}

.currency-name {
  color: #666;
  font-size: 24px;
  margin-top: 5px;
}

.follow-btn {
  margin-left: 15px;
  background: transparent;
  border: 1px solid #303133;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.3s ease;
  min-width: 90px;
  height: 36px;
}

.follow-btn .el-icon {
  font-size: 16px;
}

.follow-text {
  font-size: 14px;
  font-weight: 500;
}

.follow-btn:hover {
  background-color: #409eff;
  border-color: #409eff;
  transform: scale(1.05);
}

.follow-btn:hover .el-icon,
.follow-btn:hover .follow-text {
  color: white;
}

.follow-btn.is-followed {
  background-color: #808080;
  border-color: #808080;
  color: white;
}

.follow-btn.is-followed .el-icon,
.follow-btn.is-followed .follow-text {
  color: white;
}

.follow-btn.is-followed:hover {
  background-color: #409eff;
  border-color: #409eff;
}

.price-section {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-top: 20px;
}

.current-price {
  font-size: 38px;
  font-weight: bold;
  color: #333;
}

.change-info {
  font-size: 24px;
}

.change-info.up {
  color: #d24646;
}

.change-info.down {
  color: #1e723a;
}

.chart-container {
  margin-top: 20px;
  margin-bottom: 20px;
  height: 600px;
  width: 100%;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.tradingview-widget-container {
  position: relative;
  height: 100%;
}

.blue-text {
  color: #2962ff;
  text-decoration: none;
}

.bottom-container {
  width: 100%;
  margin-top: 40px;
}

.detail-content {
  background: transparent;
  padding: 20px;
  border-radius: 8px;
}

.secondary-nav {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.secondary-nav .nav-item {
  font-size: 20px;
  font-weight: bold;
  cursor: pointer;
  padding: 10px 0;
  position: relative;
}

.tertiary-nav {
  display: flex;
  gap: 30px;
  margin-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.tertiary-nav .nav-item {
  font-size: 16px;
  cursor: pointer;
  padding: 10px 0;
  position: relative;
}

.nav-item.active {
  color: #409eff;
}

.nav-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: #409eff;
}

.content-area {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.time-scale {
  margin-bottom: 15px;
}

.line-chart {
  height: 400px;
  background: #f5f7fa;
  border-radius: 4px;
}

.summary-table {
  margin-top: 20px;
}

.history-controls {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.time-label {
  font-size: 16px;
  color: #333;
}

.time-select,
.date-picker {
  flex: 1;
}

.statistics {
  display: flex;
  justify-content: space-between;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin-top: 20px;
}

.converter-container {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  margin: 20px 0;
}

.currency-input-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.currency-flag {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
}

.currency-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  font-size: 16px;
  outline: none;
  transition: all 0.3s;
}

.currency-input:focus {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.currency-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.currency-header-right {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

.right-align {
  text-align: right;
  padding-right: 20px; /* 增加右侧 padding */
}

.swap-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
}

.swap-icon .el-icon {
  font-size: 20px;
  color: #606266;
}

.date-selector {
  display: flex;
  justify-content: center;
  margin: 20px 0;
}

.date-info {
  color: #909399;
  font-size: 12px;
  margin-left: 8px;
}

/* 修改日期选择器样式 */
:deep(.el-date-picker) {
  --el-datepicker-border-color: #dcdfe6;
  --el-datepicker-off-border-color: #dcdfe6;
}

.rate-info {
  text-align: center;
  color: #606266;
  font-size: 14px;
  margin-top: 10px;
}

.converter-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.symbol-chart-container {
  height: calc(100% - 32px);
  width: 100%;
}

.advanced-chart-container {
  height: calc(100% - 32px);
  width: 100%;
}

.tradingview-widget-copyright {
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 添加下拉菜单样式 */
:deep(.el-dropdown-menu) {
  padding: 8px 0;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

:deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  font-size: 16px;
}

:deep(.el-dropdown-menu__item .el-icon) {
  margin-right: 10px;
  font-size: 18px;
}

.logo-image {
  height: 3em; /* Match the size used in AuthView */
}

.float-chat-btn {
  position: fixed;
  right: 2%;
  bottom: 3%;
  z-index: 2147483645; /* 高层级但略低于上面两个元素 */
  transition: all 0.3s ease;
}

.float-chat-btn.chat-open {
  right: -30px;
}

.float-chat-btn :deep(.el-button) {
  width: 55px;
  height: 55px;
  font-size: 28px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.float-chat-btn :deep(.el-button:hover) {
  transform: scale(1.1);
}

/* 添加呼吸效果类 */
.float-chat-btn.breathing :deep(.el-button) {
  animation: breathing 3s ease-in-out infinite;
}

@keyframes breathing {
  0% {
    transform: scale(1);
    box-shadow: 0 2px 12px 0 rgba(64, 158, 255, 0.3);
  }
  50% {
    transform: scale(1.2);
    box-shadow: 0 8px 25px 0 rgba(64, 158, 255, 0.8);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 2px 12px 0 rgba(64, 158, 255, 0.3);
  }
}

.float-chat-btn.chat-open :deep(.el-button) {
  width: 60px;
  height: 60px;
  border-radius: 30px 0 0 30px;
}

/* 聊天提示框样式 */
.chat-tooltip {
  position: absolute;
  bottom: 90px;
  right: 0;
  width: 380px;
  background-color: #f0f9ff;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2), 0 0 0 2px rgba(64, 158, 255, 0.2);
  padding: 22px;
  z-index: 2147483646; /* 仅比聊天窗口低一级 */
  animation: pulse 2s infinite alternate;
}

.tooltip-content {
  font-size: 18px;
  line-height: 1.6;
  color: #333;
  font-weight: 500;
}

.tooltip-arrow {
  position: absolute;
  bottom: -14px;
  right: 20px;
  width: 0;
  height: 0;
  border-left: 14px solid transparent;
  border-right: 14px solid transparent;
  border-top: 14px solid #f0f9ff;
}

.tooltip-close {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 18px;
  cursor: pointer;
  color: #409eff;
  transition: color 0.2s, transform 0.2s;
}

.tooltip-close:hover {
  color: #66b1ff;
  transform: scale(1.2);
}

@keyframes pulse {
  0% {
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2), 0 0 0 2px rgba(64, 158, 255, 0.2);
    transform: translateY(0);
  }
  100% {
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.25), 0 0 0 4px rgba(64, 158, 255, 0.3);
    transform: translateY(-15px);
  }
}
</style>

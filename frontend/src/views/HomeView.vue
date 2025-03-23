<template>
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
              <el-icon>
                <User />
              </el-icon>
              <span style="margin-left: 8px">我的账号</span>
            </el-dropdown-item>
            <el-dropdown-item @click="handleLogout">
              <el-icon>
                <SwitchButton />
              </el-icon>
              <span style="margin-left: 8px">退出登录</span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- Navigation Bar -->
    <div class="forex-title">
      <h2>外汇市场</h2>
      <el-dropdown
        trigger="click"
        @visible-change="handleDropdownVisibleChange"
        @command="handleCommand"
      >
        <button class="rate-button">
          {{ currentView
          }}<el-icon>
            <component :is="dropdownVisible ? 'ArrowUpBold' : 'ArrowDownBold'" />
          </el-icon>
        </button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="汇率">
              <el-icon>
                <Histogram />
              </el-icon>
              <span>汇率</span>
            </el-dropdown-item>
            <el-dropdown-item command="交叉汇率">
              <el-icon>
                <Grid />
              </el-icon>
              <span>交叉汇率</span>
            </el-dropdown-item>
            <el-dropdown-item command="热图">
              <el-icon>
                <DataAnalysis />
              </el-icon>
              <span>热图</span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <component
        :is="currentComponent"
        v-model:stocks="stocks"
        :showEmptyMessage="showEmptyMessage"
        @stock-click="handleStockClick"
        @toggle-follow="toggleFollow"
        @change-data-source="handleDataSourceChange"
      />
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
import { useForexStore } from '@/stores/forexStore'
import {
  ArrowDownBold,
  ArrowUpBold,
  ChatDotSquare,
  Check,
  Close,
  DataAnalysis,
  DataLine,
  Grid,
  Histogram,
  Message,
  Search,
  Select as SelectIcon,
  SwitchButton,
  Timer,
  User,
  UserFilled,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { addFavorite, getFavorites, getUserInfo, removeFavorite } from '../api/user'
import BottomBar from '../components/BottomBar.vue'
import ChatWindow from '../components/ChatWindow.vue'
import CrossRates from '../components/CrossRates.vue'
import HeatMap from '../components/HeatMap.vue'
import RateList from '../components/RateList.vue'
import SettingDialog from '../components/SettingDialog.vue'

export default {
  name: 'HomeView',
  components: {
    Search,
    SwitchButton,
    Check,
    SelectIcon,
    User,
    Message,
    Timer,
    ChatDotSquare,
    Close,
    ArrowDownBold,
    ArrowUpBold,
    Histogram,
    Grid,
    DataLine,
    DataAnalysis,
    RateList,
    CrossRates,
    HeatMap,
    ChatWindow,
    BottomBar,
    SettingDialog,
  },
  setup() {
    return {
      UserFilled,
    }
  },
  data() {
    return {
      stocks: [],
      messages: [],
      newMessage: '',
      isAboutUsExpanded: false,
      isCopyrightExpanded: false,
      showEmptyMessage: false,
      accountDialogVisible: false,
      isChatVisible: false,
      isDragging: false,
      dragOffset: { x: 0, y: 0 },
      chatPosition: {
        right: '2.5%',
        bottom: '10%',
      },
      isWaitingResponse: false,
      currentView: '汇率',
      dropdownVisible: false,
      userInfo: {
        username: '',
        email: '',
      },
      avatarBgColor: this.getRandomColor(),
      savedChatMode: localStorage.getItem('chatMode') || 'floating',
      showChatTooltip: true,
      isBreathing: false,
    }
  },
  async created() {
    const forexStore = useForexStore()

    // 始终显示聊天提示框
    this.showChatTooltip = true

    try {
      // 1. 加载所有汇率数据
      await forexStore.loadAllForexData()
      const data = await forexStore.getForexData('all')

      if (!data || data.length === 0) {
        console.warn('Waiting for initial data to load...')
        await new Promise((resolve) => setTimeout(resolve, 500))
        const retryData = await forexStore.getForexData('all')
        if (!retryData || retryData.length === 0) {
          throw new Error('No forex data loaded')
        }
        this.stocks = retryData
      } else {
        this.stocks = data
      }

      try {
        // 2. 获取用户信息和关注列表
        await this.fetchUserInfo()
        const response = await getFavorites()
        const favoriteSymbols = response.map((item) => item.symbol)

        // 3. 更新股票的关注状态
        this.stocks = this.stocks.map((stock) => ({
          ...stock,
          isFollowed: favoriteSymbols.includes(stock.symbol),
        }))

        // 4. 获取关注列表的最新汇率数据
        const favoriteStocks = this.stocks.filter((stock) => stock.isFollowed)
        if (favoriteStocks.length > 0) {
          // 使用 API 更新关注的货币对数据
          await forexStore.updateFavoriteStocksData(favoriteStocks)

          // 同步更新本地数据
          const updatedData = await forexStore.getForexData('all')
          this.stocks = updatedData.map((stock) => ({
            ...stock,
            isFollowed: favoriteSymbols.includes(stock.symbol),
          }))
        }

        this.showEmptyMessage = favoriteStocks.length === 0
      } catch (error) {
        console.error('Failed to fetch user info or favorites:', error)
        ElMessage.error('获取用户信息或关注列表失败')
      }
    } catch (error) {
      console.error('Failed to load forex data:', error)
      this.stocks = []
      ElMessage.error('加载汇率数据失败')
    }
  },
  computed: {
    currentComponent() {
      switch (this.currentView) {
        case '汇率':
          return RateList
        case '交叉汇率':
          return CrossRates
        case '热图':
          return HeatMap
        default:
          return RateList
      }
    },
    favoriteStocks() {
      return this.stocks.filter((stock) => stock.isFollowed)
    },
    avatarText() {
      if (!this.userInfo.username) return ''
      const firstChar = this.userInfo.username.charAt(0)
      return firstChar
    },
  },
  methods: {
    scrollToBottom() {
      if (this.$refs.chatMessages) {
        this.$refs.chatMessages.$el.querySelector('.el-scrollbar__wrap').scrollTo({
          top: this.$refs.chatMessages.$el.querySelector('.el-scrollbar__wrap').scrollHeight,
          behavior: 'smooth',
        })
      }
    },
    async handleSendMessage(message, useDeepSearch = false) {
      if (!this.isWaitingResponse) {
        this.messages.push({
          type: 'sent',
          content: message,
        })
        this.isWaitingResponse = true
        this.$nextTick(this.scrollToBottom)

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
          this.$nextTick(this.scrollToBottom)
        }
      }
    },
    sendMessage() {
      const message = this.newMessage.trim()
      if (message) {
        this.handleSendMessage(message)
        this.newMessage = ''
      }
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
        },
      })
    },
    handleLogout() {
      localStorage.removeItem('token')
      window.location.replace('/auth')
      window.onpopstate = function () {
        window.location.replace('/auth')
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
    async toggleFollow(stock) {
      try {
        if (stock.isFollowed) {
          stock.isRemoving = true
          await new Promise((resolve) => setTimeout(resolve, 300))
          await removeFavorite(stock.symbol)
          stock.isFollowed = false
          stock.isRemoving = false
          if (this.favoriteStocks.length === 0) {
            this.showEmptyMessage = false
            setTimeout(() => {
              this.showEmptyMessage = true
            }, 550)
          }
        } else {
          await addFavorite(stock.symbol)
          stock.isFollowed = true
          this.showEmptyMessage = false
        }
      } catch (error) {
        stock.isRemoving = false
        ElMessage.error('操作失败，请重试')
        console.error('Failed to toggle favorite:', error)
      }
    },
    handleAccount() {
      this.accountDialogVisible = true
    },
    handleDropdownVisibleChange(visible) {
      this.dropdownVisible = visible
    },
    handleCommand(command) {
      this.currentView = command
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
    async handleDataSourceChange(csvPath) {
      const forexStore = useForexStore()

      try {
        const type = csvPath.split('/')[1].replace('.csv', '')
        const data = await forexStore.getForexData(type)

        if (!data || data.length === 0) {
          console.warn(`Waiting for data to load for type: ${type}`)
          await new Promise((resolve) => setTimeout(resolve, 500))
          const retryData = await forexStore.getForexData(type)
          if (!retryData || retryData.length === 0) {
            throw new Error('No forex data found for type: ' + type)
          }
          this.stocks = retryData
        } else {
          this.stocks = data
        }

        // 获取关注列表
        const response = await getFavorites()
        const favoriteSymbols = response.map((item) => item.symbol)

        // 更新当前显示的股票数据（考虑分页）
        const pageSize = 80 // 与 RateList 组件中的 pageSize 保持一致
        const displayedStocks = this.stocks.slice(0, pageSize)
        await forexStore.updateFavoriteStocksData(displayedStocks, false)

        // 获取更新后的数据
        const updatedData = await forexStore.getForexData(type)
        if (updatedData) {
          this.stocks = updatedData.map((stock) => ({
            ...stock,
            isFollowed: favoriteSymbols.includes(stock.symbol),
          }))
        }

        this.showEmptyMessage = this.favoriteStocks.length === 0
      } catch (error) {
        console.error('Failed to load forex data:', error)
        ElMessage.error('加载汇率数据失败')
        this.stocks = []
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
  async mounted() {
    // Initial update of favorite stocks
    if (this.stocks.some((stock) => stock.isFollowed)) {
      const store = useForexStore()
      await store.updateFavoriteStocksData(this.stocks.filter((stock) => stock.isFollowed))
    }

    // Set up interval to update every hour
    this.updateInterval = setInterval(async () => {
      if (this.stocks.some((stock) => stock.isFollowed)) {
        const store = useForexStore()
        await store.updateFavoriteStocksData(this.stocks.filter((stock) => stock.isFollowed))
      }
    }, 3600000) // Update every hour
  },
  beforeUnmount() {
    // Clear the interval when component is destroyed
    if (this.updateInterval) {
      clearInterval(this.updateInterval)
    }
  },
}
</script>

<style scoped>
.home-container {
  position: relative;
  padding: 20px;
  max-width: 1250px;
  margin: 0 auto;
  padding-top: 40px;
}

.logo {
  position: absolute;
  top: 18px;
  left: 5px;
  z-index: 10;
}

.avatar-container {
  position: absolute;
  top: 20px;
  right: 10px;
  z-index: 10;
  cursor: pointer;
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

.main-content {
  margin-top: 70px;
  display: flex;
  gap: 20px;
  position: relative;
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

.bottom-container {
  width: 100%;
  margin-top: 40px;
}

/* 添加账号对话框样式 */
:deep(.el-dialog) {
  border-radius: 16px !important;
  overflow: hidden;
}

:deep(.el-dialog__header) {
  margin: 0;
  padding: 20px 24px;
  border-bottom: 1px solid #eee;
}

:deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
}

:deep(.el-dialog__body) {
  padding: 24px;
}

:deep(.el-button--danger.is-plain) {
  --el-button-hover-text-color: var(--el-color-danger);
  --el-button-hover-border-color: var(--el-color-danger);
  --el-button-hover-bg-color: var(--el-color-danger-light-9);
}

/* 修改浮动聊天按钮样式 */
.float-chat-btn {
  position: fixed;
  right: 2%;
  bottom: 3%;
  z-index: 99;
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

.forex-title {
  text-align: center;
  margin: 80px 0 0px;
}

.forex-title h2 {
  font-size: 24px;
  color: #333;
  margin-bottom: 10px;
}

.rate-button {
  font-size: 48px;
  color: #000;
  font-weight: bold;
  background: none;
  border: none;
  padding: 10px 20px;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 auto;
  /* 使按钮在页面上居中 */
  transition: background-color 0.3s ease;
}

.rate-button:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.rate-button .arrow {
  font-size: 36px;
  line-height: 1;
}

.rate-button :deep(.el-icon) {
  margin-left: 5px;
  margin-top: 20px;
  font-size: 34px;
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
  height: 3em;
  /* Match the size used in AuthView */
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
  z-index: 97;
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

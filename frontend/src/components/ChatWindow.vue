<template>
  <transition name="chat-slide">
    <div
      class="chat-window"
      v-show="visible"
      :style="position"
      ref="chatWindow"
      :class="{
        'fullscreen-mode': currentMode === 'fullscreen',
      }"
    >
      <div class="chat-header" @mousedown="startDrag">
        <h3>FX-Assistant</h3>
        <div class="header-buttons">
          <div class="button-group">
            <el-button
              type="default"
              :class="{ 'active-button': currentMode === 'fullscreen' }"
              @click="setMode('fullscreen')"
              >全屏</el-button
            >
            <el-button
              type="default"
              :class="{ 'active-button': currentMode === 'floating' }"
              @click="setMode('floating')"
              >浮窗</el-button
            >
          </div>
          <el-button class="close-btn" circle @click="handleClose">
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
      </div>
      <div class="resize-handle-nw" @mousedown="startResizeNW"></div>
      <el-scrollbar class="chat-messages" ref="chatMessages" @scroll="handleScroll">
        <div
          v-for="(message, index) in messages"
          :key="index"
          class="message"
          :class="message.type"
        >
          <div v-html="message.content" class="message-content"></div>
        </div>
        <div v-if="isWaitingResponse" class="message received loading-message">
          <div class="typing-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </el-scrollbar>
      <div class="chat-input">
        <div class="input-wrapper">
          <input
            type="text"
            v-model="newMessage"
            @keyup.enter="sendMessage"
            placeholder="输入消息..."
            :disabled="isWaitingResponse"
          />
          <el-button type="primary" @click="sendMessage" :disabled="isWaitingResponse"
            >发送</el-button
          >
        </div>
        <div class="options-wrapper">
          <el-checkbox v-model="useDeepSearch" :disabled="isWaitingResponse"
            >启用深度研究</el-checkbox
          >
        </div>
      </div>
      <div class="resize-handle" @mousedown="startResize"></div>
    </div>
  </transition>
</template>

<script>
import { Close, Delete, Edit, Share } from '@element-plus/icons-vue'
import { debounce } from 'lodash'
import { marked } from 'marked'

export default {
  name: 'ChatWindow',
  components: {
    Close,
    Edit,
    Share,
    Delete,
  },
  props: {
    visible: {
      type: Boolean,
      required: true,
    },
    position: {
      type: Object,
      default: () => ({
        right: '2.5%',
        bottom: '10%',
      }),
    },
    messages: {
      type: Array,
      required: true,
    },
    isWaitingResponse: {
      type: Boolean,
      default: false,
    },
    initialMode: {
      type: String,
      default: 'floating',
      validator: (value) => ['fullscreen', 'floating'].includes(value),
    },
  },
  data() {
    return {
      newMessage: '',
      isDragging: false,
      dragOffset: { x: 0, y: 0 },
      useDeepSearch: false,
      curIndex: 0,
      newMessages: {
        type: '',
        content: '',
      },
      oldLength: 2,
      renderedContent: '',
      isResizingNW: false,
      resizeStartNW: {
        x: 0,
        y: 0,
        width: 0,
        height: 0,
        left: 0,
        top: 0,
        right: 0,
        bottom: 0,
      },
      isUserScrolled: false,
      scrollContainer: null,
      lastScrollTop: 0,
      isInitialized: false,
      currentMode: this.initialMode,
      previousPosition: null,
      previousDimensions: { width: '800px', height: '600px' },
      _dragAnimationFrame: null,
      _finalPosition: null,
      isResizing: false,
      resizeStart: {
        x: 0,
        y: 0,
        width: 0,
        height: 0,
      },
      _resizeAnimationFrame: null,
      resizeOverlayNW: null,
      _resizeNWAnimationFrame: null,
    }
  },
  methods: {
    handleClose() {
      this.$emit('save-mode', this.currentMode)
      this.$emit('update:visible', false)
    },
    sendMessage() {
      if (this.newMessage.trim() && !this.isWaitingResponse) {
        this.$emit('send', this.newMessage, this.useDeepSearch)
        this.newMessage = ''
      }
    },
    showTypingEffect(message, flag) {
      if (flag == 1) {
        this.curIndex = 0
        this.newMessages = JSON.parse(JSON.stringify(message))
        message.content = ''
        this.renderedContent = ''
      }
      if (this.curIndex == this.newMessages.content.length) return
      this.renderedContent += this.newMessages.content[this.curIndex]
      this.curIndex++
      message.content = JSON.parse(JSON.stringify(this.renderedContent))

      // 配置marked选项
      marked.setOptions({
        breaks: true, // 支持GitHub风格的换行
        gfm: true, // 启用GitHub风格的Markdown
        headerIds: false, // 不为标题添加id
        mangle: false, // 不转义内联HTML
        smartLists: true, // 使用更智能的列表行为
      })

      // 在渲染前处理内容，确保标题后有空行
      let contentToRender = message.content
        .replace(/\n(#{1,6}.*)\n(?!\n)/g, '\n$1\n\n') // 添加标题后的空行
        .replace(/(#{1,6}.*)\n(?!\n)/g, '$1\n\n') // 处理文档开头的标题

      message.content = marked(contentToRender)

      // 只在用户没有手动滚动时自动滚动
      if (!this.isUserScrolled) {
        this.$nextTick(() => {
          this.scrollToBottom()
        })
      }

      this.$forceUpdate()
    },
    startDrag(e) {
      // Don't allow dragging in fullscreen mode or if clicking on buttons
      if (
        this.currentMode === 'fullscreen' ||
        e.target.closest('.close-btn') ||
        e.target.closest('.button-group')
      )
        return

      this.isDragging = true
      const chatWindow = this.$refs.chatWindow
      const rect = chatWindow.getBoundingClientRect()

      this.dragOffset = {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
      }

      // 改为普通事件监听，避免捕获阶段的潜在冲突
      document.addEventListener('mousemove', this.onDrag)
      document.addEventListener('mouseup', this.stopDrag)

      // 阻止事件默认行为，防止文本选择
      e.preventDefault()
    },
    onDrag(e) {
      if (!this.isDragging) return

      // 防止文本选择和其他默认动作
      e.preventDefault()

      // 使用变量缓存当前鼠标位置，避免多次访问事件对象
      const mouseX = e.clientX
      const mouseY = e.clientY

      // 使用 requestAnimationFrame 优化渲染性能
      if (!this._dragAnimationFrame) {
        this._dragAnimationFrame = requestAnimationFrame(() => {
          // 避免获取当前尺寸和位置的重排操作，尽量复用数据
          // 从缓存的鼠标位置计算新位置
          let left = mouseX - this.dragOffset.x
          let top = mouseY - this.dragOffset.y

          // 确保窗口保持在屏幕内
          const windowWidth = window.innerWidth
          const windowHeight = window.innerHeight
          const chatWindow = this.$refs.chatWindow
          const chatWidth = chatWindow.offsetWidth
          // const chatHeight = chatWindow.offsetHeight

          // 限制在视口内
          top = Math.max(0, Math.min(windowHeight - 50, top))
          left = Math.max(-chatWidth + 100, Math.min(windowWidth - 100, left))

          // 使用 transform 代替修改 left/top 属性，减少回流
          chatWindow.style.transform = `translate3d(${left}px, ${top}px, 0)`
          chatWindow.style.left = '0px'
          chatWindow.style.top = '0px'
          chatWindow.style.right = 'auto'
          chatWindow.style.bottom = 'auto'

          // 缓存最终位置，以便在拖动结束时使用
          this._finalPosition = { left, top }

          // 清除动画帧引用
          this._dragAnimationFrame = null
        })
      }
    },
    stopDrag() {
      if (!this.isDragging) return

      this.isDragging = false

      // 取消任何待处理的动画帧
      if (this._dragAnimationFrame) {
        cancelAnimationFrame(this._dragAnimationFrame)
        this._dragAnimationFrame = null
      }

      // 移除事件监听器
      document.removeEventListener('mousemove', this.onDrag)
      document.removeEventListener('mouseup', this.stopDrag)

      // 在拖动结束时才设置实际的位置属性，同时移除transform
      if (this._finalPosition) {
        const chatWindow = this.$refs.chatWindow
        chatWindow.style.transform = 'none'
        chatWindow.style.left = `${this._finalPosition.left}px`
        chatWindow.style.top = `${this._finalPosition.top}px`

        // 更新position属性，保持状态同步
        this.$emit('update:position', {
          left: `${this._finalPosition.left}px`,
          top: `${this._finalPosition.top}px`,
          right: 'auto',
          bottom: 'auto',
        })

        // 清除临时存储
        this._finalPosition = null
      }
    },
    handleScroll(e) {
      // 确保滚动容器已经初始化
      if (!this.scrollContainer) {
        this.scrollContainer = this.$refs.chatMessages?.$el?.querySelector('.el-scrollbar__wrap')
        if (!this.scrollContainer) return
      }

      const container = this.scrollContainer
      const isScrolledToBottom =
        container.scrollHeight - container.scrollTop - container.clientHeight < 50

      // 如果用户向上滚动，标记为手动滚动
      if (container.scrollTop < this.lastScrollTop) {
        this.isUserScrolled = true
      }

      // 如果用户滚动到底部，重置手动滚动标记
      if (isScrolledToBottom) {
        this.isUserScrolled = false
      }

      this.lastScrollTop = container.scrollTop
    },
    scrollToBottom() {
      // 确保滚动容器已经初始化
      if (!this.scrollContainer) {
        this.scrollContainer = this.$refs.chatMessages?.$el?.querySelector('.el-scrollbar__wrap')
        if (!this.scrollContainer) return
      }

      if (!this.isUserScrolled) {
        this.scrollContainer.scrollTo({
          top: this.scrollContainer.scrollHeight,
          behavior: 'smooth',
        })
      }
    },
    startResize(e) {
      e.preventDefault()
      this.isResizing = true

      const chatWindow = this.$refs.chatWindow
      const rect = chatWindow.getBoundingClientRect()

      this.resizeStart = {
        x: e.clientX,
        y: e.clientY,
        width: rect.width,
        height: rect.height,
      }

      // 添加一个临时的透明覆盖层，确保鼠标事件的持续捕获
      const overlay = document.createElement('div')
      overlay.style.position = 'fixed'
      overlay.style.top = '0'
      overlay.style.left = '0'
      overlay.style.width = '100%'
      overlay.style.height = '100%'
      overlay.style.cursor = 'se-resize'
      overlay.style.zIndex = '9999'
      overlay.style.backgroundColor = 'transparent'
      document.body.appendChild(overlay)
      this.resizeOverlay = overlay

      document.addEventListener('mousemove', this.onResize)
      document.addEventListener('mouseup', this.stopResize)
    },
    onResize(e) {
      if (!this.isResizing) return

      // 防止默认行为和事件传播
      e.preventDefault()
      e.stopPropagation()

      // 使用requestAnimationFrame避免过于频繁的DOM更新
      if (!this._resizeAnimationFrame) {
        this._resizeAnimationFrame = requestAnimationFrame(() => {
          const dx = e.clientX - this.resizeStart.x
          const dy = e.clientY - this.resizeStart.y

          const newWidth = Math.max(300, this.resizeStart.width + dx)
          const newHeight = Math.max(400, this.resizeStart.height + dy)

          // 直接设置宽高，避免使用样式字符串拼接
          const chatWindow = this.$refs.chatWindow
          chatWindow.style.width = `${newWidth}px`
          chatWindow.style.height = `${newHeight}px`

          // 清除动画帧引用
          this._resizeAnimationFrame = null
        })
      }
    },
    stopResize() {
      this.isResizing = false

      // 移除临时覆盖层
      if (this.resizeOverlay) {
        document.body.removeChild(this.resizeOverlay)
        this.resizeOverlay = null
      }

      // 取消任何待处理的动画帧
      if (this._resizeAnimationFrame) {
        cancelAnimationFrame(this._resizeAnimationFrame)
        this._resizeAnimationFrame = null
      }

      document.removeEventListener('mousemove', this.onResize)
      document.removeEventListener('mouseup', this.stopResize)
    },
    startResizeNW(e) {
      e.preventDefault()
      this.isResizingNW = true

      const chatWindow = this.$refs.chatWindow
      const rect = chatWindow.getBoundingClientRect()

      // 确保我们记录的是精确的尺寸和位置
      this.resizeStartNW = {
        x: e.clientX,
        y: e.clientY,
        width: rect.width,
        height: rect.height,
        left: rect.left,
        top: rect.top,
        // 存储右下角坐标，确保在整个过程中保持不变
        right: rect.left + rect.width,
        bottom: rect.top + rect.height,
      }

      // 添加临时覆盖层
      const overlay = document.createElement('div')
      overlay.style.position = 'fixed'
      overlay.style.top = '0'
      overlay.style.left = '0'
      overlay.style.width = '100%'
      overlay.style.height = '100%'
      overlay.style.cursor = 'nw-resize'
      overlay.style.zIndex = '9999'
      overlay.style.backgroundColor = 'transparent'
      document.body.appendChild(overlay)
      this.resizeOverlayNW = overlay

      // 取消窗口的过渡效果，使调整大小过程中更加平滑
      chatWindow.style.transition = 'none'

      document.addEventListener('mousemove', this.onResizeNW)
      document.addEventListener('mouseup', this.stopResizeNW)
    },
    onResizeNW(e) {
      if (!this.isResizingNW) return

      // 防止默认行为和事件传播
      e.preventDefault()
      e.stopPropagation()

      // 使用requestAnimationFrame
      if (!this._resizeNWAnimationFrame) {
        this._resizeNWAnimationFrame = requestAnimationFrame(() => {
          const chatWindow = this.$refs.chatWindow

          // 计算右下角坐标（以页面坐标系为基准）
          const rightBottomX = this.resizeStartNW.left + this.resizeStartNW.width
          const rightBottomY = this.resizeStartNW.top + this.resizeStartNW.height

          // 计算新的左上角位置（由鼠标控制）
          const newLeft = Math.min(e.clientX, rightBottomX - 300)
          const newTop = Math.min(e.clientY, rightBottomY - 400)

          // 计算新尺寸（保持右下角固定）
          const newWidth = rightBottomX - newLeft
          const newHeight = rightBottomY - newTop

          // 关键改进：先设置尺寸，再设置位置，避免视觉跳跃
          // 1. 保存当前滚动位置，防止内容滚动重置
          const scrollTop = this.scrollContainer?.scrollTop || 0

          // 2. 应用新尺寸和位置，顺序很重要
          // 先设置尺寸，再设置位置，减少重排
          chatWindow.style.width = `${newWidth}px`
          chatWindow.style.height = `${newHeight}px`
          chatWindow.style.left = `${newLeft}px`
          chatWindow.style.top = `${newTop}px`

          // 3. 恢复滚动位置
          if (this.scrollContainer) {
            this.scrollContainer.scrollTop = scrollTop
          }

          // 4. 更新位置属性
          this.$emit('update:position', {
            left: `${newLeft}px`,
            top: `${newTop}px`,
            right: 'auto',
            bottom: 'auto',
          })

          // 清除动画帧引用
          this._resizeNWAnimationFrame = null
        })
      }
    },
    stopResizeNW() {
      this.isResizingNW = false

      // 移除临时覆盖层
      if (this.resizeOverlayNW) {
        document.body.removeChild(this.resizeOverlayNW)
        this.resizeOverlayNW = null
      }

      // 恢复窗口的过渡效果
      const chatWindow = this.$refs.chatWindow
      chatWindow.style.transition = ''

      // 取消任何待处理的动画帧
      if (this._resizeNWAnimationFrame) {
        cancelAnimationFrame(this._resizeNWAnimationFrame)
        this._resizeNWAnimationFrame = null
      }

      document.removeEventListener('mousemove', this.onResizeNW)
      document.removeEventListener('mouseup', this.stopResizeNW)
    },
    initializeScrollContainer() {
      // 等待下一个渲染周期，确保 el-scrollbar 已经渲染
      this.$nextTick(() => {
        this.scrollContainer = this.$refs.chatMessages?.$el?.querySelector('.el-scrollbar__wrap')
        if (this.scrollContainer) {
          this.lastScrollTop = this.scrollContainer.scrollTop
          this.isInitialized = true
          this.scrollToBottom()
        }
      })
    },
    setMode(mode) {
      // Don't do anything if the same mode is selected
      if (this.currentMode === mode) return

      const chatWindow = this.$refs.chatWindow

      // 获取当前窗口位置和尺寸，用于记录并创建平滑过渡
      const currentRect = chatWindow.getBoundingClientRect()

      switch (mode) {
        case 'fullscreen':
          // 1. 保存当前位置和尺寸，用于返回浮窗模式时恢复
          this.previousPosition = JSON.parse(JSON.stringify(this.position))
          this.previousDimensions = {
            width: `${currentRect.width}px`,
            height: `${currentRect.height}px`,
            left: `${currentRect.left}px`,
            top: `${currentRect.top}px`,
          }

          // 2. 创建更平滑的过渡动画
          chatWindow.style.transition = 'all 0.3s ease-in-out'

          // 从浮窗模式到全屏的原有逻辑
          // 3. 设置扩展效果的起点（当前位置）
          chatWindow.style.width = `${currentRect.width}px`
          chatWindow.style.height = `${currentRect.height}px`
          chatWindow.style.left = `${currentRect.left}px`
          chatWindow.style.top = `${currentRect.top}px`
          chatWindow.style.right = 'auto'
          chatWindow.style.bottom = 'auto'

          // 4. 在下一帧设置目标全屏尺寸，触发动画
          requestAnimationFrame(() => {
            // 设置为全屏的目标状态
            chatWindow.style.width = '100%'
            chatWindow.style.height = '100%'
            chatWindow.style.left = '0'
            chatWindow.style.top = '0'
            chatWindow.style.zIndex = '1001'

            // 5. 动画完成后更新position属性
            setTimeout(() => {
              this.$emit('update:position', {
                top: '0',
                left: '0',
                right: '0',
                bottom: '0',
              })
              // 重置过渡属性
              chatWindow.style.transition = ''
            }, 300) // 与过渡动画时长匹配
          })

          // 确保我们不在拖拽状态
          this.isDragging = false
          document.removeEventListener('mousemove', this.onDrag)
          document.removeEventListener('mouseup', this.stopDrag)
          break

        case 'floating':
          if (this.previousPosition && this.previousDimensions) {
            // 关键改进：从全屏模式回到浮窗状态时，直接过渡到目标位置和尺寸
            chatWindow.style.transition = 'all 0.3s ease-in-out'

            // 先重置zIndex，保证不会出现闪烁
            chatWindow.style.zIndex = '98'

            if (this.currentMode === 'fullscreen') {
              // 从全屏模式恢复：直接设置最终目标位置和尺寸，一步到位
              const finalLeft = parseFloat(this.previousDimensions.left)
              const finalTop = parseFloat(this.previousDimensions.top)
              const finalWidth = parseFloat(this.previousDimensions.width)
              const finalHeight = parseFloat(this.previousDimensions.height)

              // 立即设置动画的起点（当前处于全屏状态）
              chatWindow.style.width = '100%'
              chatWindow.style.height = '100%'
              chatWindow.style.left = '0'
              chatWindow.style.top = '0'

              // 在下一帧设置目标最终位置，触发动画
              requestAnimationFrame(() => {
                // 直接设置最终的位置和尺寸，实现四面向中心收缩的效果
                chatWindow.style.width = `${finalWidth}px`
                chatWindow.style.height = `${finalHeight}px`
                chatWindow.style.left = `${finalLeft}px`
                chatWindow.style.top = `${finalTop}px`

                // 动画完成后更新position属性
                setTimeout(() => {
                  this.$emit('update:position', {
                    left: `${finalLeft}px`,
                    top: `${finalTop}px`,
                    right: 'auto',
                    bottom: 'auto',
                  })
                  // 重置过渡属性
                  chatWindow.style.transition = ''
                }, 300)
              })
            } else {
              // 从其他模式返回浮窗状态 - 移除侧栏相关逻辑
              const finalLeft = parseFloat(this.previousDimensions.left)
              const finalTop = parseFloat(this.previousDimensions.top)
              const finalWidth = parseFloat(this.previousDimensions.width)
              const finalHeight = parseFloat(this.previousDimensions.height)

              // 设置动画起点（当前位置）
              chatWindow.style.width = `${currentRect.width}px`
              chatWindow.style.height = `${currentRect.height}px`
              chatWindow.style.left = `${currentRect.left}px`
              chatWindow.style.top = `${currentRect.top}px`

              // 下一帧设置目标位置，触发动画
              requestAnimationFrame(() => {
                chatWindow.style.width = `${finalWidth}px`
                chatWindow.style.height = `${finalHeight}px`
                chatWindow.style.left = `${finalLeft}px`
                chatWindow.style.top = `${finalTop}px`

                // 动画完成后更新position属性
                setTimeout(() => {
                  this.$emit('update:position', {
                    left: `${finalLeft}px`,
                    top: `${finalTop}px`,
                    right: 'auto',
                    bottom: 'auto',
                  })
                  // 重置过渡属性
                  chatWindow.style.transition = ''
                }, 300)
              })
            }
          } else {
            // 如果没有之前的位置记录，设置默认浮窗位置
            chatWindow.style.transition = 'all 0.3s ease-in-out'
            chatWindow.style.zIndex = '98'

            // 计算居中位置
            const windowWidth = window.innerWidth
            const windowHeight = window.innerHeight
            const targetWidth = 800
            const targetHeight = 600
            const targetLeft = (windowWidth - targetWidth) / 2
            const targetTop = (windowHeight - targetHeight) / 2

            // 设置动画起点（当前状态，可能是全屏或侧栏）
            chatWindow.style.width = `${currentRect.width}px`
            chatWindow.style.height = `${currentRect.height}px`
            chatWindow.style.left = `${currentRect.left}px`
            chatWindow.style.top = `${currentRect.top}px`

            // 下一帧设置目标位置，触发动画
            requestAnimationFrame(() => {
              chatWindow.style.width = `${targetWidth}px`
              chatWindow.style.height = `${targetHeight}px`
              chatWindow.style.left = `${targetLeft}px`
              chatWindow.style.top = `${targetTop}px`

              // 动画完成后更新position属性
              setTimeout(() => {
                this.$emit('update:position', {
                  left: `${targetLeft}px`,
                  top: `${targetTop}px`,
                  right: 'auto',
                  bottom: 'auto',
                })
                // 重置过渡属性
                chatWindow.style.transition = ''
              }, 300)
            })
          }
          break
      }

      this.currentMode = mode
      this.$emit('save-mode', mode)
    },
  },
  watch: {
    visible: {
      immediate: true,
      handler(newValue) {
        if (newValue) {
          this.initializeScrollContainer()

          // Apply the current mode settings when window becomes visible
          const chatWindow = this.$refs.chatWindow
          if (this.currentMode === 'fullscreen') {
            // Set fullscreen properties
            this.$emit('update:position', {
              top: '0',
              left: '0',
              right: '0',
              bottom: '0',
            })

            // Set dimensions for fullscreen
            chatWindow.style.width = '100%'
            chatWindow.style.height = '100%'
            chatWindow.style.zIndex = '1001'
          }
        }
      },
    },
    messages: {
      handler: debounce(function (newMessages) {
        if (!this.isInitialized) {
          this.initializeScrollContainer()
        }

        // 只在用户没有手动滚动时自动滚动
        if (!this.isUserScrolled) {
          this.$nextTick(this.scrollToBottom)
        }

        // 处理逐字显示效果
        const lastMessage = newMessages[newMessages.length - 1]
        if (lastMessage && lastMessage.type === 'received') {
          if (newMessages.length !== this.oldLength) {
            this.showTypingEffect(lastMessage, 1)
            this.oldLength = newMessages.length
          } else {
            this.showTypingEffect(lastMessage, 0)
          }
        }
      }, 30),
      deep: true,
      immediate: true,
    },
  },
  mounted() {
    if (this.visible) {
      this.initializeScrollContainer()

      // Apply the initial mode settings on mount
      const chatWindow = this.$refs.chatWindow
      if (this.currentMode === 'fullscreen') {
        // Set fullscreen properties
        this.$emit('update:position', {
          top: '0',
          left: '0',
          right: '0',
          bottom: '0',
        })

        // Set dimensions for fullscreen
        chatWindow.style.width = '100%'
        chatWindow.style.height = '100%'
        chatWindow.style.zIndex = '1001'
      }
    }
  },
  beforeUnmount() {
    // Clean up event listeners when component is destroyed
    document.removeEventListener('mousemove', this.onDrag)
    document.removeEventListener('mouseup', this.stopDrag)

    // Cancel any pending animation frames
    if (this._dragAnimationFrame) {
      cancelAnimationFrame(this._dragAnimationFrame)
    }

    // Remove overlay if it exists
    if (this.resizeOverlay) {
      document.body.removeChild(this.resizeOverlay)
      this.resizeOverlay = null
    }
  },
}
</script>

<style scoped>
.chat-window {
  position: fixed;
  width: 800px;
  height: 600px;
  background: white;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 9999;
  /* 修改过渡效果，为所有属性添加过渡 */
  transition: opacity 0.3s ease, width 0.3s ease, height 0.3s ease, left 0.3s ease, top 0.3s ease,
    right 0.3s ease, bottom 0.3s ease;
  /* 添加硬件加速，提高渲染性能 */
  will-change: transform, width, height, left, top;
  transform: translate3d(0, 0, 0);
  /* 防止在拖动过程中选中文本 */
  user-select: none;
}

/* 特殊模式下重置过渡时间为0，避免与resize冲突 */
.chat-window.animating-mode-change {
  transition: none !important;
}

.fullscreen-mode {
  border-radius: 0;
  box-shadow: none;
  width: 100% !important;
  height: 100% !important;
  z-index: 1001 !important;
}

.fullscreen-mode .resize-handle,
.fullscreen-mode .resize-handle-nw {
  display: none;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #eee;
  cursor: move;
  user-select: none;
  position: relative; /* Ensure it's positioned correctly */
  z-index: 1; /* Ensure it's above other elements */
}

.fullscreen-mode .chat-header {
  cursor: default; /* Don't show move cursor in fullscreen mode */
}

.header-buttons {
  display: flex;
  align-items: center;
  gap: 10px;
}

.button-group {
  display: flex;
  border-radius: 4px;
  overflow: hidden;
  margin-right: 10px;
}

.button-group :deep(.el-button) {
  margin: 0;
  border-radius: 0;
  padding: 8px 12px;
  font-size: 12px;
  background-color: white;
  border-color: #dcdfe6;
  color: #333;
  position: relative;
}

.button-group :deep(.active-button) {
  background-color: #f2f6fc;
  color: #409eff;
  font-weight: 500;
}

/* Remove default borders between buttons */
.button-group :deep(.el-button:not(:first-child):not(:last-child)) {
  border-right: none;
  border-left: none;
}

.button-group :deep(.el-button:first-child) {
  border-right: none;
}

.button-group :deep(.el-button:last-child) {
  border-left: none;
  border-top-right-radius: 4px;
  border-bottom-right-radius: 4px;
}

/* Add white border lines for all dividers */
.button-group :deep(.el-button:not(:last-child))::after {
  content: '';
  position: absolute;
  right: 0;
  top: 20%;
  height: 60%;
  width: 1px;
  background-color: white;
  z-index: 1;
}

.button-group :deep(.el-button:not(:first-child))::before {
  content: '';
  position: absolute;
  left: 0;
  top: 20%;
  height: 60%;
  width: 1px;
  background-color: white;
  z-index: 1;
}

.button-group :deep(.el-button:hover) {
  background-color: #f5f7fa;
  color: #409eff;
}

.close-btn {
  padding: 8px;
  font-size: 16px;
}

.chat-messages {
  flex: 1;
  height: calc(100% - 135px);
}

.chat-messages :deep(.el-scrollbar__view) {
  padding: 15px;
  display: flex;
  flex-direction: column;
  overflow-wrap: break-word; /* 防止长单词溢出 */
}

.chat-messages :deep(.el-scrollbar__bar.is-horizontal) {
  display: none;
}

.chat-messages :deep(.el-scrollbar__bar.is-vertical) {
  width: 6px;
}

.message {
  margin: 10px 0;
  padding: 12px 16px;
  border-radius: 8px;
  max-width: 80%;
  word-wrap: break-word;
  white-space: pre-wrap;
  line-height: 1.4;
}

.message :deep(h1),
.message :deep(h2),
.message :deep(h3),
.message :deep(h4),
.message :deep(h5),
.message :deep(h6) {
  margin: 8px 0 4px 0;
  line-height: 1.3;
}

.message :deep(li) {
  margin: 4px 0;
  line-height: 1.6;
  padding: 0;
  list-style-position: outside;
}

.message :deep(ul),
.message :deep(ol) {
  padding-left: 2em;
  margin: 8px 0;
}

.message :deep(li > ul),
.message :deep(li > ol) {
  margin: 4px 0;
  padding-left: 2em;
  text-indent: 0;
}

.message :deep(td > p),
.message :deep(th > p) {
  margin: 0;
  display: inline;
}

.message :deep(strong) {
  font-weight: 600;
  display: inline;
}

.message :deep(em) {
  font-style: italic;
  display: inline;
}

.message :deep(h1) {
  font-size: 1.8em;
  font-weight: 600;
  margin: 16px 0 12px 0;
}
.message :deep(h2) {
  font-size: 1.5em;
  font-weight: 600;
  margin: 14px 0 10px 0;
}
.message :deep(h3) {
  font-size: 1.3em;
  font-weight: 600;
  margin: 12px 0 8px 0;
}
.message :deep(h4) {
  font-size: 1.2em;
  font-weight: 600;
  margin: 10px 0 6px 0;
}
.message :deep(h5) {
  font-size: 1.1em;
  font-weight: 600;
  margin: 8px 0 6px 0;
}
.message :deep(h6) {
  font-size: 1em;
  font-weight: 600;
  margin: 6px 0 4px 0;
}

.message :deep(code) {
  background-color: rgba(0, 0, 0, 0.06);
  padding: 2px 4px;
  border-radius: 4px;
  font-family: monospace;
}

.message :deep(pre) {
  background-color: rgba(0, 0, 0, 0.06);
  padding: 8px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 4px 0;
}

.message :deep(pre code) {
  background-color: transparent;
  padding: 0;
}

.message :deep(blockquote) {
  margin: 8px 0;
  padding: 8px 12px;
  border-left: 4px solid #ddd;
  background-color: rgba(0, 0, 0, 0.03);
}

.message :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 8px 0;
  display: table;
}

.message :deep(table + p) {
  margin-top: 2px;
  margin-bottom: 4px;
}

.message :deep(th),
.message :deep(td) {
  border: 1px solid #ddd;
  padding: 4px 8px;
  text-align: left;
  line-height: 1.3;
}

.message :deep(th) {
  background-color: rgba(0, 0, 0, 0.06);
}

.message :deep(table ~ *) {
  margin-top: 2px;
}

.message :deep(p) {
  margin: 2px 0;
  line-height: 1.6;
}

.sent {
  background-color: #409eff;
  color: white;
  margin-left: auto;
  border-radius: 12px 12px 2px 12px;
}

.sent :deep(code),
.sent :deep(pre) {
  background-color: rgba(255, 255, 255, 0.1);
}

.received {
  background-color: #f4f4f4;
  color: #333;
  margin-right: auto;
  border-radius: 12px 12px 12px 2px;
}

.message ol,
.message ul {
  list-style-position: inside;
}

.message-content {
  width: 100%;
  line-height: 1.6;
  white-space: normal;
}

.chat-input {
  padding: 15px;
  border-top: 1px solid #eee;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.input-wrapper {
  display: flex;
  gap: 10px;
}

.input-wrapper input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  outline: none;
}

.options-wrapper {
  display: flex;
  align-items: center;
  font-size: 12px;
}

.chat-slide-enter-active,
.chat-slide-leave-active {
  transition: all 0.3s ease;
}

.chat-slide-enter-from,
.chat-slide-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

.chat-slide-enter-to,
.chat-slide-leave-from {
  transform: translateX(0);
  opacity: 1;
}
.resize-handle {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 10px;
  height: 10px;
  cursor: se-resize;
}
.typing-effect {
  overflow: hidden;
  white-space: nowrap; /* 保证每个字符逐个显示，不换行 */
  width: 100%; /* 使文本显示完整 */
  animation: typing 2s steps(20, end), blink-caret 0.75s step-end infinite;
}

@keyframes typing {
  from {
    width: 0;
  }
  to {
    width: 100%;
  }
}

@keyframes blink-caret {
  from,
  to {
    border-color: transparent;
  }
  50% {
    border-color: black;
  }
}

.resize-handle-nw {
  position: absolute;
  left: 0;
  top: 0;
  width: 10px;
  height: 10px;
  cursor: nw-resize;
  z-index: 99;
}

/* 可选：添加视觉提示 */
.resize-handle-nw:hover {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 50%;
}

@keyframes typing {
  from {
    width: 0;
  }
  to {
    width: 100%;
  }
}

@keyframes blink-caret {
  from,
  to {
    border-color: transparent;
  }
  50% {
    border-color: black;
  }
}

.message :deep(hr) {
  margin: 8px 0;
}

.loading-message {
  padding: 12px 20px;
  min-width: 60px;
  max-width: 60px;
}

.typing-dots {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 4px;
  padding: 4px 0;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  background-color: #666;
  border-radius: 50%;
  display: inline-block;
  animation: bounce 1.4s infinite ease-in-out both;
}

.typing-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

/* 确保加载消息和其他消息的样式一致 */
.message.loading-message {
  background-color: #f4f4f4;
  margin-right: auto;
  margin-left: 0;
  border-radius: 12px 12px 12px 2px;
}
</style>

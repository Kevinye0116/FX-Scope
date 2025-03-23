<template>
  <div class="bottom-bar" ref="bottom">
    <div class="logo-bottom">
      <img src="/logo1.png" alt="FX-Scope Logo" class="bottom-logo-image" />
    </div>
    <div class="about-us">
      <button class="about-btn" @click="$emit('toggleAbout')">
        {{ isAboutUsExpanded ? '收起' : '关于我们' }}
      </button>
      <button class="about-btn" @click="$emit('toggleCopyright')">
        {{ isCopyrightExpanded ? '收起' : '版权声明' }}
      </button>
    </div>
  </div>

  <el-collapse-transition>
    <div v-show="isAboutUsExpanded" class="about-us-content">
      <div class="about-us-inner">
        <h2>关于我们</h2>
        <p>FX-Scope 是一个专业的外汇市场分析工具，为用户提供实时的货币对数据和智能交易建议。</p>
        <div class="about-us-grid">
          <div class="about-us-item">
            <h3>我们的团队</h3>
            <p>指导老师：方立兵、刘嘉。</p>
            <p>商业组：庄子严、陈正伟、符番煦、林泓妤、戴慧灵、陈嘉豪。</p>
            <p>
              技术组：叶金可、郑铭芝、彭梓越、商宸溪、邹佳诚、吴雨霏、杨金樽、蒋海鑫、胡燃、张家宁。
            </p>
          </div>
          <p>感谢所有为 FX-Scope 项目付出努力的同学和老师，是你们的辛勤工作让这个项目得以实现。</p>
        </div>
      </div>
    </div>
  </el-collapse-transition>

  <el-collapse-transition>
    <div v-show="isCopyrightExpanded" class="about-us-content">
      <div class="about-us-inner">
        <h2>版权声明</h2>
        <div class="about-us-grid">
          <div class="about-us-item">
            <p>© 2024 FX-Scope. 保留所有权利。</p>
            <p>未经授权，禁止复制、修改、传播本网站的任何内容。</p>
            <p>本网站提供的所有数据仅供参考，不构成投资建议。</p>
          </div>
        </div>
      </div>
    </div>
  </el-collapse-transition>
</template>

<script>
export default {
  name: 'BottomBar',
  props: {
    isAboutUsExpanded: Boolean,
    isCopyrightExpanded: Boolean,
  },
  emits: ['toggleAbout', 'toggleCopyright'],
  methods: {
    handleToggleAbout() {
      this.$emit('toggleAbout')
    },
    handleToggleCopyright() {
      this.$emit('toggleCopyright')
    },
  },
}
</script>

<style scoped>
.bottom-bar {
  display: flex;
  align-items: center;
  height: 120px;
  margin-top: 15px;
  background-color: #f5f7f9;
}

.logo-bottom {
  margin-left: 130px;
}

.about-us {
  margin-left: 70px;
}

.about-btn {
  padding: 8px 20px;
  background-color: transparent;
  border: transparent;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 400;
  transition: all 0.3s ease;
  margin-top: 5px;
  margin-right: 15px;
}

.about-btn:hover {
  background-color: #333;
  color: white;
  font-weight: 500;
}

.about-us-content {
  background-color: white;
  width: 100%;
}

.about-us-inner {
  padding: 30px 130px;
}

.about-us-inner h2 {
  color: #333;
  margin-bottom: 20px;
}

.about-us-grid {
  display: grid;
  gap: 30px;
  margin-top: 20px;
}

.about-us-item {
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
}

.about-us-item h3 {
  color: #333;
  margin-bottom: 10px;
}

.about-us-item p {
  color: #666;
  line-height: 1.6;
}

.bottom-logo-image {
  height: 2.5em; /* Slightly smaller for the bottom bar */
}
</style>

<template>
  <div class="risk-chart-container">
    <!-- 添加加载状态显示 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-content">
        <div class="typing-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
        <div class="loading-text">正在分析风险数据...</div>
      </div>
    </div>

    <!-- 上半部分 -->
    <div class="top-section">
      <!-- 左侧雷达图 -->
      <div class="radar-chart-section">
        <div ref="radarChart" class="radar-chart"></div>
      </div>

      <!-- 右侧风险分析 -->
      <div class="risk-score-section">
        <!-- 风险指数显示 -->
        <div class="risk-score-container">
          <h2>风险指数</h2>
          <div class="risk-score" :style="{ backgroundColor: getRiskColor(totalRiskScore) }">
            {{ totalRiskScore.toFixed(2) }}
          </div>
        </div>

        <!-- 详细分析 -->
        <div class="risk-factors">
          <h3>风险分析</h3>
          <div v-for="(score, factor) in riskFactors" :key="factor" class="risk-factor-item">
            <span class="factor-name">{{ factor }}:</span>
            <span class="factor-score" :style="{ color: getRiskColor(score) }">
              {{ score.toFixed(2) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 下半部分 -->
    <div class="bottom-section">
      <!-- 结构化结论 -->
      <div class="analysis-section">
        <h3>结构化结论</h3>
        <div class="analysis-content" v-html="formattedConclusion"></div>
      </div>

      <!-- 风险分析 -->
      <div class="analysis-section">
        <h3>风险分析</h3>
        <div class="analysis-content" v-html="formattedAnalysis"></div>
      </div>

      <!-- 交易建议 -->
      <div class="analysis-section">
        <h3>交易建议</h3>
        <div class="analysis-content" v-html="formattedAdvice"></div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import { marked } from 'marked' // 需要安装: npm install marked
import { getLLM } from '../api/LLM'

export default {
  name: 'RiskChart',
  data() {
    return {
      riskFactors: {
        货币政策分化度: 0,
        地缘政治风险: 0,
        技术面动能: 0,
        市场情绪极端值: 0,
        流动性风险: 0,
      },
      weights: {
        货币政策分化度: 0,
        地缘政治风险: 0,
        技术面动能: 0,
        市场情绪极端值: 0,
        流动性风险: 0,
      },
      structuredConclusion: '',
      riskAnalysis: '',
      tradingAdvice: '',
      chart: null,
      rawContent: '',
      isLoading: true,
      error: null,
    }
  },
  computed: {
    totalRiskScore() {
      return Object.entries(this.riskFactors).reduce((total, [factor, score]) => {
        return total + score * this.weights[factor]
      }, 0)
    },
    formattedConclusion() {
      return marked(this.structuredConclusion)
    },
    formattedAnalysis() {
      return marked(this.riskAnalysis)
    },
    formattedAdvice() {
      return marked(this.tradingAdvice)
    },
  },
  mounted() {
    this.initChart()
    this.fetchRiskData()
  },
  methods: {
    initChart() {
      this.chart = echarts.init(this.$refs.radarChart)
      this.updateChart()
    },
    async fetchRiskData() {
      this.isLoading = true
      this.error = null
      try {
        const response = await getLLM(this.$route.params.symbol)
        if (!response) {
          throw new Error('获取数据失败')
        }
        const content = response
        console.log('Risk data response:', content)

        // 保存原始内容
        this.rawContent = content

        // 解析风险雷达图数据
        const riskDataMatch = content.match(/```json\n{[\s\S]*?}/)
        if (riskDataMatch) {
          try {
            const riskData = JSON.parse(riskDataMatch[0].replace('```json\n', ''))

            // 更新风险因素分数
            this.riskFactors = {
              货币政策分化度: riskData['货币政策分化度']?.[0] || 0,
              地缘政治风险: riskData['地缘政治风险']?.[0] || 0,
              技术面动能: riskData['技术面动能']?.[0] || 0,
              市场情绪极端值: riskData['市场情绪极端值']?.[0] || 0,
              流动性风险: riskData['流动性风险']?.[0] || 0,
            }

            // 更新权重
            this.weights = {
              货币政策分化度: riskData['货币政策分化度']?.[1] || 0,
              地缘政治风险: riskData['地缘政治风险']?.[1] || 0,
              技术面动能: riskData['技术面动能']?.[1] || 0,
              市场情绪极端值: riskData['市场情绪极端值']?.[1] || 0,
              流动性风险: riskData['流动性风险']?.[1] || 0,
            }
          } catch (parseError) {
            console.error('解析风险数据失败:', parseError)
            this.error = '解析风险数据失败'
          }
        }

        // 解析结构化结论
        const conclusionMatch = content.match(/1\. 结构化结论([\s\S]*?)2\./)
        if (conclusionMatch) {
          this.structuredConclusion = conclusionMatch[1].trim()
        }

        // 解析风险分析
        const analysisMatch = content.match(
          /2\. 风险分析(?:（包含推理过程）)?([\s\S]*?)(?:```json[\s\S]*?```)?3\./
        )
        if (analysisMatch) {
          this.riskAnalysis = analysisMatch[1].replace(/```json[\s\S]*?```/g, '').trim()
        }

        // 解析交易建议
        const adviceMatch = content.match(/3\. 交易建议([\s\S]*?)$/)
        if (adviceMatch) {
          this.tradingAdvice = adviceMatch[1].replace(/```json[\s\S]*?```/g, '').trim()
        }

        // 确保在数据更新后再更新图表
        this.$nextTick(() => {
          this.updateChart()
        })
      } catch (error) {
        console.error('获取风险数据失败:', error)
        this.error = '获取风险数据失败'
      } finally {
        this.isLoading = false
      }
    },
    updateChart() {
      const option = {
        radar: {
          indicator: Object.keys(this.riskFactors).map((name) => ({
            name,
            max: 5,
          })),
          shape: 'polygon',
          splitNumber: 5,
          axisName: {
            color: '#333',
            fontSize: 12,
          },
          splitArea: {
            areaStyle: {
              color: ['#f5f5f5', '#e9e9e9', '#d9d9d9', '#c9c9c9', '#b9b9b9'],
            },
          },
        },
        series: [
          {
            type: 'radar',
            data: [
              {
                value: Object.values(this.riskFactors),
                name: '风险指标',
                itemStyle: {
                  color: '#ff4b2b',
                },
                areaStyle: {
                  color: 'rgba(255, 75, 43, 0.3)',
                },
              },
            ],
          },
        ],
      }

      this.chart?.setOption(option)
    },
    getRiskColor(score) {
      // 根据分数返回对应的颜色（绿色到红色的渐变）
      const red = Math.round((score / 5) * 255)
      const green = Math.round((1 - score / 5) * 255)
      return `rgb(${red}, ${green}, 0)`
    },
  },
  beforeDestroy() {
    this.chart?.dispose()
  },
}
</script>

<style scoped>
.risk-chart-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  height: 100%;
  min-height: 800px;
  position: relative;
}

.top-section {
  display: flex;
  gap: 20px;
  height: 450px;
  min-height: 400px;
}

.radar-chart-section {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.radar-chart {
  width: 100%;
  height: 100%;
}

.risk-score-section {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.bottom-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.risk-score-container {
  text-align: center;
}

.risk-score {
  display: inline-block;
  padding: 15px 30px;
  border-radius: 8px;
  font-size: 36px;
  font-weight: bold;
  color: white;
  margin-top: 10px;
}

.risk-factors {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.risk-factor-item {
  display: flex;
  justify-content: space-between;
  padding: 8px;
  background: #f5f5f5;
  border-radius: 4px;
}

.factor-name {
  font-weight: 500;
}

.factor-score {
  font-weight: bold;
}

.analysis-section,
.risk-warning-section {
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
  margin-top: 10px;
}

h2 {
  font-size: 24px;
  color: #333;
  margin: 0;
}

h3 {
  font-size: 18px;
  color: #333;
  margin: 0 0 15px 0;
}

.analysis-content :deep(h4),
.warning-content :deep(h4) {
  font-size: 16px;
  margin: 15px 0 10px;
  color: #333;
}

.analysis-content :deep(p),
.warning-content :deep(p) {
  margin: 8px 0;
  line-height: 1.6;
}

.analysis-content :deep(ol),
.warning-content :deep(ol),
.analysis-content :deep(ul),
.warning-content :deep(ul) {
  padding-left: 0;
  list-style-position: inside;
  margin: 10px 0;
}

.analysis-content :deep(li),
.warning-content :deep(li) {
  margin: 8px 0;
  padding-left: 20px;
  text-indent: -20px;
}

.analysis-content :deep(li ol),
.analysis-content :deep(li ul),
.warning-content :deep(li ol),
.warning-content :deep(li ul) {
  margin: 8px 0 8px 20px;
}

.analysis-content :deep(li p),
.warning-content :deep(li p) {
  display: inline;
  margin: 0;
}

.analysis-content :deep(strong),
.warning-content :deep(strong) {
  color: #333;
}

.analysis-content :deep(table) {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0 8px;
  margin: 15px 0;
}

.analysis-content :deep(th),
.analysis-content :deep(td) {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.analysis-content :deep(th) {
  background-color: #f5f5f5;
  font-weight: 600;
}

.analysis-content :deep(tr:last-child td) {
  border-bottom: none;
}

/* 修改加载状态样式 */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 99;
  border-radius: 8px;
}

.loading-content {
  text-align: center;
}

.loading-text {
  margin-top: 10px;
  color: #666;
  font-size: 14px;
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
</style>

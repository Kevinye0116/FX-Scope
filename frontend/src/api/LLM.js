export async function getLLM(symbol) {
   // return request({
   //     url: '/llm/',
   //     method: 'get',
   //     data: { symbol }
   // })
   const useDeepSearch = false
   const message = symbol
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

   return data.response
}

// 返回示例：
/*
1. 结构化结论

   - 方向预测：震荡（置信度60%）
   
   - 关键触发事件时间轴：

   | 日期       | 事件                 | 预期影响方向 |
   |------------|----------------------|--------------|
   | 2023-11-01 | 澳大利亚央行利率决议 | 看跌         |
   | 2023-11-05 | 阿联酋非石油出口数据 | 看涨         |
   | 2023-11-15 | 澳大利亚失业率数据   | 看涨/看跌    |
   | 2023-11-20 | 阿联酋旅游消费数据   | 看涨         |

2. 风险分析
// 也可能为：2. 风险分析（包含推理过程）

AED/AUD货币对受到多种因素的影响，包括澳大利亚的货币政策、经济数据以及阿联酋的经济活动等。目前来看，澳大利亚央行的利率决议可能对AUD产生较大影响，若加息则AUD走强，AED/AUD将看跌；反之，若维持利率不变或降息，则AUD可能走弱，AED/AUD将看涨。

阿联酋方面，由于其经济对外依赖度较高，尤其是石油和旅游业，因此非石油出口数据及旅游消费数据对其货币价值有较大影响。如果数据显示非石油出口增加或者旅游消费旺盛，则AED可能走强，AED/AUD将看涨。

风险指标分析如下：

```json
{
    "货币政策分化度": [3, 0.4],
    "地缘政治风险": [2, 0.2],
    "技术面动能": [4, 0.3],
    "市场情绪极端值": [3, 0.1],
    "流动性风险": [2, 0.1]
}
```

3. 交易建议

鉴于AED/AUD货币对当前处于震荡状态，且影响因素较多，建议采取区间交易策略。在关键事件前后应特别注意风险管理，可设置较窄的止损区间以应对突发情况。此外，密切关注澳大利亚和阿联酋的相关经济数据发布，以便及时调整交易策略。

请注意，以上分析仅供参考，实际交易中还需结合个人的风险承受能力和市场最新动态做出决策。
*/
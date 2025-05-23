# FX-Scope 技术文档

**版本：**1.0

**最后更新：** 2025/03/21

[TOC]

---

## 一、 项目概述

### 1. 项目背景

**全球外汇市场概况**

全球外汇市场是世界上交易量最大的金融市场，具有极高的流动性和广泛的参与群体。汇率瞬息万变，价格波动频繁。影响汇率变动的因素多种多样，包括国家经济政策的变化、地缘政治局势的转化、相关资产的价格波动和市场的风险情绪起伏等等。无论是发达国家还是新兴市场，汇率的变化都对国内经济和国际贸易有着深远的影响。

**企业与金融机构面临的挑战**

对企业而言，外汇风险直接关联到公司的盈利能力、成本控制效果和未来发展规划等；同样，金融机构也必须不断应对汇率波动带来的市场风险。有效管理外汇风险已成为促进实体经济稳定发展的关键环节。

**市场痛点**

在市场信息庞杂的背景下，准确识别风险信号、把握风险管理的最佳时机，一直是市场参与者面临的难题。金融市场部门的销售与交易团队虽然凭借多年经验可以识别市场驱动力量，但仍需要更先进的工具支持。

### 2. 目标用户

1. **跨国贸易企业**：他们需要管理外汇敞口，具有多货币对的风险信号、相关性分析与定制回撤等需求。
2. **金融机构**：金融机构需要进行高频的交易和投资，对实时的风险信号有高度的依赖，需要高精度的但货币对信号的详细分析。
3. **政府监管机构**：政府需要对外汇波动进行实时的监管以掌握其对宏观经济的影响，对他们来说，他们需要整合后的宏观数据以提供可解释性的报告。
4. **其他群体**：个人或中小企业，需要依照偏好为其提供专业风控资源和简易的风险信号预测工具。

### 3. 主要功能

**外汇数据**

项目最终成果以网页的形式呈现，网站提供了全球外汇市场的1500余种外汇货币对的实时外汇数据，并提供外汇市场主要货币对以及全球各地区主要货币对的交叉汇率以及货币对热图。

**风险信号**

项目基于外汇市场实时信息以及各种非结构化数据，利用大模型等先进技术进行实时分析，生成外汇货币对总体的风险信号并提供详细的分析内容。

**可解释性支持**

项目虽基于大模型等具有“黑盒性”的技术，但本项目为用户提供了风险信号数据分析结果来源于哪些数据和文件，用户也可以手动向系统提问，获取更加详细的信息。

### 4. 项目目标

我们期望通过整合前沿的统计与人工智能工具，分析历史趋势，构建多维度数据模型，以精准捕捉汇率风险信号。我们的目标是为企业和金融机构提供更具前瞻性、更加科学的风险预警系统，帮助客户有效应对外汇风险敞口，实现稳健经营。

## 二、 系统架构

### 1. 总体架构

FX-Scope采用前后端分离的总体架构，并采用模块化的开发方式，以提高系统的可扩展性和可维护性。

![系统架构](./系统架构.png)

### 2. 核心组件

| 组件名称         | 功能描述                                                     |
| ---------------- | ------------------------------------------------------------ |
| AuthView         | 用户的注册登录认证                                           |
| HomeView         | 主页容器，用于显示各详细模块                                 |
| DetailView       | 详情界面容器，用于显示货币对各详细信息                       |
| rateList         | 展示全球外汇市场主要货币对的外汇信息列表                     |
| crossRate        | 展示主要外汇市场的主要货币的交叉汇率                         |
| heatMap          | 展示主要外汇市场的主要货币的实时热图                         |
| chatWindow       | 页面聊天窗口，用户与大模型交流，获取更加详细且个性化的外汇信息 |
| settingDialogue  | 页面以及用户的一些基本设置                                   |
| 聊天支持（后端） | 用于chatWindow的后端大模型接入                               |
| 风险评估（后端） | 通过大模型等人工智能技术，对各种外汇数据进行分析，生成风险信号 |

## 三、 技术栈

### 1. 前端技术

- **框架**：Vue3
- **组件库**：Element Plus

### 2. 后端技术

- **框架**：Django
- **大模型**：通义千问、智谱、RAG和DeepResearch技术
- **数据库**：SQLite3、ChromaDB

### 4. 开发工具与环境

- **版本控制**：Git，GitLab
- **IDE/代码编辑器**：Pycharm Professional，WebStorm，VS Code，Cursor
- **API测试**：Postman
- **文档工具**：Typora，Microsoft Office

## 四、 功能模块

### 前端模块

FX-Scope前端采用模块化设计，主要分为三大模块：认证模块、主页模块和详情模块。

#### 1. 认证模块

负责用户的登录、注册和身份验证功能，确保系统安全性和用户数据隐私保护。

- **用户注册**：新用户账号创建，包含基本信息收集和验证
- **用户登录**：已有账号的身份验证和登录会话管理
- **密码重置**：用户忘记密码时的安全重置流程
- **身份验证**：确保用户访问权限的合法性，包括令牌管理

#### 2. 主页模块

系统的核心界面，提供外汇市场概览和主要功能入口，包含多个子组件：

##### 2.1 rateList（汇率列表）

- 显示主要货币对的汇率及涨跌幅等数据
- 提供涨跌幅度的视觉指示
- 提供用户关注筛选功能
- 提供主要货币对列表切换

##### 2.2 crossRate（交叉汇率）

- 展示不同货币之间的交叉汇率矩阵
- 支持不同货币市场重要货币列表切换
- 提供实时更新的交叉汇率计算
- 多国货币汇率涨跌可视化展示

##### 2.3 heatMap（热力图）

- 通过颜色深浅直观展示市场活跃度
- 支持不同货币市场的热力图切换
- 提供市场整体趋势的可视化分析

##### 2.4 chatWindow（聊天窗口）

- 用户与后端大模型的实时交流
- 提供更加详细的金融分析
- 提供更加详细的分析数据来源
- 为用户提供deep research功能选项，提供深度联网搜索的外汇情况分析

##### 2.5 settingDialogue（设置对话框）

- 用户账号设置
- 未来可能加入的用户个性化页面设置

##### 2.6 bottomBar（底部栏）

- 团队介绍以及版权声明

#### 3. 详情模块

提供深入的市场分析和交易工具，包含多个专业分析组件：

##### 3.1 K线图

- 提供多种时间周期的K线图表
- 支持各种技术指标叠加
- 支持历史数据回溯和分析

##### 3.2 汇率转换

- 精确的货币兑换计算
- 支持多种货币之间的转换

##### 3.3 雷达图

- 提供风险信号分析的可视化展示
- 直观反映风险信号分析内容

##### 3.4 风险信号

- 展示五个风险层面的风险指数
- 根据货币对动态调整各部分权重以给出综合风险评分
- 提供详细的风险分析与交易建议

### 后端模块

后端系统提供数据处理、业务逻辑和API服务，主要包含四个核心模块：

### 1. 用户登录认证

- 用户账号管理和身份验证
- 权限控制和安全策略实施
- 会话管理和令牌验证
- 用户数据加密和保护

### 2. 关注列表存取

- 向前端提供用户的个人外汇货币对关注列表
- 前端向后端增添和删除关注货币对

### 3. 聊天支持

- 提供前端ChatWindow部分的后端支持
- 接入大模型获取回复信息

##### 3.1 RAG功能

- 通过动态RAG+搜索API实现联网搜索功能
- 固定部分静态文档实现分析方法论的稳定性
- 预留接口，在后续如果用户有导入自己资料的需求也可实现

##### 3.2 DeepResearch功能

- 仿照OpenAI等大厂家的强大的聊天新功能，利用工作流的设计实现类似功能
- 模型搜索与思考时间更长，生成详细的分析报告
- 作为tool-call进行调用，可实现与普通模式之间灵活的切换

### 4. 风险评估

- 实现Deep-Research功能
- 接受用户输入作为主题创建研究计划，定义报告章节
- 执行多轮联网搜索查询收集相关资料
- 为每个章节生成内容，包括引用资料
- 合并所有章节形成完整研究报告，并基于研究报告为用户提供分析和建议
- 基于大模型和RAG技术预测货币对汇率风险

## 五、本地运行方法
### 后端
进入 `backend/` 文件夹，安装相关必需依赖，运行后端项目
   ```cmd
   > cd backend
   > pip install requirements.txt # 若使用电脑本地全局环境，可手动安装requirements中需要的库
   > pip install -U duckduckgo_search[lxml]
   > python manage.py migrate
   > python manage.py runserver
   ```
**注：后端运行需要安装完成所有依赖，否则无法正确接入大模型**

### 前端
打开新的命令提示符，进入 `frontend/` 文件夹，运行前端项目（需要先安装 npm 环境）
   ```cmd
   > cd frontend
   > npm install # 安装依赖
   > npm run dev
   ```
> 后端项目运行在本机的 `8000` 端口，前端项目运行在 `5173` 端口，若存在端口占用，可尝试关闭浏览器或重启电脑后，重新运行。
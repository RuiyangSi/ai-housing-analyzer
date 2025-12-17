# 🏠 AI驱动的智能房价分析系统

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1.2-green.svg)
![AI](https://img.shields.io/badge/AI-DeepSeek--V3-purple.svg)

**基于227万+真实成交数据的智能房地产市场分析平台**

[项目亮点](#-核心创新点) • [快速开始](#-快速开始) • [技术架构](#-技术架构)

</div>

---

## 🏗️ 技术架构

<div align="center">

![系统架构图](reports/figures/Real%20Estate%20Intelligent%20Analysis%20System%20Architecture.png)

**房地产智能分析系统总体架构图**

</div>

### 核心设计理念：数据锚定（Data Anchoring）

```
数据采集 → 数据清洗 → JSON上下文锚定 → Prompt注入 → AI推理 → 多维分析输出
```

### 四层架构体系

1. **数据层**：227万+条CSV数据 + SQLite用户库 + JSON配置
2. **业务逻辑层**：15+种分析维度 + 投资指数计算 + 跨城市对比
3. **AI增强层**：可插拔大模型 + 三角色对话 + 智能预测 + 策略规划
4. **表现层**：Flask API + ECharts可视化 + 流式响应

### 技术栈

**后端**：Flask 3.1.2 | Pandas 2.3.3 | SQLite  
**前端**：ECharts 5.4.3 | Chart.js 4.4.0 | 现代CSS3  
**AI**：DeepSeek-V3 | 流式响应 | Prompt工程

---

## ✨ 核心创新点

### 🎯 四大突破性创新

#### 1. 📊 **海量真实数据：227万+条成交记录**
- **数据规模**：2,277,464条二手房真实成交数据
- **覆盖范围**：26个省级行政区、40余座城市
- **时间跨度**：2023年1月 - 2025年11月
- **数据质量**：国内同类研究中的领先水平

#### 2. 🔌 **可插拔式AI架构：随模型进化而成长**
- **设计理念**：通过配置即可切换AI模型（DeepSeek/GPT-4/Claude）
- **技术优势**：无需重构代码，AI能力持续进化
- **实际效果**：从DeepSeek-V2升级到V3，分析质量显著提升

#### 3. 🎭 **三角色个性化服务：千人千面的智能咨询**
- **投资顾问**：专业术语、量化风险、ROI分析
- **首次购房者**：通俗表达、生活化比喻、风险提醒
- **改善型购房者**：置换策略、税费计算、时机判断
- **技术实现**：差异化的System Prompt设计，同一数据不同解读

#### 4. 🧠 **数据锚定+AI推理：可解释的房价预测引擎**
- **核心机制**：将真实数据作为"锚点"注入AI，消除幻觉
- **预测维度**：历史趋势、季节性模式、区域分化、市场热度、价格稳定性
- **三大优势**：可解释性、个性化、可迭代性

---

## 🚀 快速开始

### 环境要求
- Python 3.9+
- DeepSeek API Key（[获取地址](https://platform.deepseek.com)）

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/RuiyangSi/ai-housing-analyzer.git
cd python_house1

# 2. 创建虚拟环境并安装依赖
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. 配置环境变量
cp env.example .env
# 编辑 .env 文件，填入 DEEPSEEK_API_KEY

# 4. 启动服务
python run.py
# 或使用启动脚本: ./scripts/start.sh
```

访问 `http://localhost:5001`，默认账号：`admin` / `admin123`

---

## 📊 核心功能

### 数据分析
- ✅ 价格趋势分析（月度/季度/年度）
- ✅ 区域深度分析（Top 15热门区域）
- ✅ 户型分析（几室几厅分布与价格）
- ✅ 投资指数计算（多维度量化评分）
- ✅ 市场活跃度与波动性分析

### AI智能助手
- 🤖 实时AI对话（流式响应，打字机效果）
- 📊 图表智能解读（一键AI洞察）
- 📈 AI价格预测（数据锚定的可解释预测）
- 💡 购房策略规划（个性化建议）

### 可视化展示
- 📈 价格趋势折线图
- 🗺️ 3D房价地图（区域热力图）
- 📊 户型分布饼图与柱状图
- 📉 价格箱线图与小提琴图
- 🔥 区域-时间热力图

---

## 📁 项目结构

```
python_house1/
├── run.py                    # 项目启动入口
├── src/                      # 源代码目录
│   ├── core/                # 核心应用（app.py, config.json）
│   ├── ai/                   # AI模块（对话、分析、预测、策略）
│   ├── analysis/            # 分析模块（房价分析、全国对比）
│   └── data/                # 数据处理（爬虫、清洗、转换）
├── data/                     # 数据目录
│   └── processed/           # 处理后的数据（data_summary.json可公开）
├── reports/                  # 报告文件
│   ├── report.tex/pdf        # 学术报告
│   └── figures/             # 报告图片
├── static/                   # 静态资源（CSS, JS）
├── templates/               # HTML模板
└── docs/                    # 详细文档
```

---

## 📚 文档

- [快速启动指南](docs/guides/快速启动.md) - 5分钟快速上手
- [完整使用指南](docs/使用指南.md) - 详细功能说明
- [API文档](docs/API_DOCUMENTATION.md) - 接口说明
- [技术架构说明](docs/项目说明.md) - 系统设计细节

---

## 🎓 学术贡献

本项目构建了一套**端到端的智能房价分析系统**，在以下方面做出贡献：

1. **数据规模**：227万+条真实成交数据，覆盖26个省级行政区
2. **架构创新**：可插拔式AI架构，数据锚定机制消除AI幻觉
3. **个性化服务**：三角色体系实现"千人千面"的智能咨询
4. **预测范式**：数据锚定+AI推理的混合预测方法

**项目代码已开源**：[GitHub仓库](https://github.com/RuiyangSi/ai-housing-analyzer)

> ⚠️ **数据说明**：原始成交数据涉及隐私和网站使用协议，未在仓库中公开，仅保留汇总统计结果（`data_summary.json`）用于复现研究结论。

---

## 📈 数据发现

基于227万+条数据的分析发现：

- **空间分异**：北京（52,173元/m²）与上海（47,642元/m²）稳居价格顶端，与西部省份形成近8倍落差
- **时间演变**：市场整体经历"调整—筑底—企稳"演变，多数城市房价于2024年触底后逐步企稳
- **区域分化**：一线城市与新一线城市间存在3倍以上的价格鸿沟

---

## 🤝 贡献

欢迎提交Issue和Pull Request！

项目任务分工详见报告[附录B：项目任务分工](reports/report.pdf#page=xx)。

---

## 📄 许可证

本项目采用 MIT 许可证

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个Star！ ⭐**

Made with ❤️ by Python Course Team

</div>

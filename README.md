<div align="center">

# 🏠 AI驱动的智能房价分析系统

**基于227万+真实成交数据的智能房地产市场分析平台**

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1.2-green.svg)
![AI](https://img.shields.io/badge/AI-DeepSeek--V3-purple.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

[📐 技术架构](#-技术架构) • [✨ 项目亮点](#-核心创新点) • [🚀 快速开始](#-快速开始) • [📊 核心功能](#-核心功能)

---

</div>

## 🏗️ 技术架构

<div align="center">

![系统架构图](reports/figures/Real%20Estate%20Intelligent%20Analysis%20System%20Architecture.png)

<sub>**房地产智能分析系统总体架构图**</sub>

</div>

### 💡 核心设计理念：数据锚定（Data Anchoring）

```
数据采集 → 数据清洗 → JSON上下文锚定 → Prompt注入 → AI推理 → 多维分析输出
```

### 🏛️ 四层架构体系

| 层级 | 组件 | 说明 |
|------|------|------|
| 📊 **数据层** | CSV数据 + SQLite + JSON配置 | 227万+条真实成交数据，用户数据存储 |
| ⚙️ **业务逻辑层** | 分析引擎 + 计算模块 | 15+种分析维度，投资指数计算，跨城市对比 |
| 🤖 **AI增强层** | 可插拔大模型 + 智能服务 | 三角色对话，智能预测，策略规划 |
| 🎨 **表现层** | Flask API + 可视化 | ECharts图表，流式响应，交互式界面 |

### 🛠️ 技术栈

<table>
<tr>
<td align="center" width="33%">
<strong>后端</strong><br>
Flask 3.1.2<br>
Pandas 2.3.3<br>
SQLite
</td>
<td align="center" width="33%">
<strong>前端</strong><br>
ECharts 5.4.3<br>
Chart.js 4.4.0<br>
现代CSS3
</td>
<td align="center" width="33%">
<strong>AI</strong><br>
DeepSeek-V3<br>
流式响应<br>
Prompt工程
</td>
</tr>
</table>

---

## ✨ 核心创新点

### 🎯 四大突破性创新

<table>
<tr>
<td width="50%">

#### 📊 海量真实数据
**227万+条成交记录**

- 🗂️ **数据规模**：2,277,464条二手房真实成交数据
- 🗺️ **覆盖范围**：26个省级行政区、40余座城市
- 📅 **时间跨度**：2023年1月 - 2025年11月
- ⭐ **数据质量**：国内同类研究中的领先水平

</td>
<td width="50%">

#### 🔌 可插拔式AI架构
**随模型进化而成长**

- ⚙️ **设计理念**：通过配置即可切换AI模型
- 🚀 **技术优势**：无需重构代码，AI能力持续进化
- 📈 **实际效果**：从DeepSeek-V2升级到V3，分析质量显著提升

</td>
</tr>
<tr>
<td width="50%">

#### 🎭 三角色个性化服务
**千人千面的智能咨询**

- 💼 **投资顾问**：专业术语、量化风险、ROI分析
- 🏡 **首次购房者**：通俗表达、生活化比喻、风险提醒
- 🔄 **改善型购房者**：置换策略、税费计算、时机判断
- 🎯 **技术实现**：差异化的System Prompt设计

</td>
<td width="50%">

#### 🧠 数据锚定+AI推理
**可解释的房价预测引擎**

- 🎯 **核心机制**：将真实数据作为"锚点"注入AI，消除幻觉
- 📊 **预测维度**：历史趋势、季节性模式、区域分化、市场热度、价格稳定性
- ✨ **三大优势**：可解释性、个性化、可迭代性

</td>
</tr>
</table>

---

## 🚀 快速开始

### 📋 环境要求

- 🐍 Python 3.9+
- 🔑 DeepSeek API Key（[获取地址](https://platform.deepseek.com)）

### ⚡ 安装步骤

<details>
<summary><b>点击展开详细安装步骤</b></summary>

```bash
# 1️⃣ 克隆项目
git clone https://github.com/RuiyangSi/ai-housing-analyzer.git
cd python_house1

# 2️⃣ 创建虚拟环境并安装依赖
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3️⃣ 配置环境变量
cp env.example .env
# 编辑 .env 文件，填入 DEEPSEEK_API_KEY

# 4️⃣ 启动服务
python run.py
# 或使用启动脚本: ./scripts/start.sh
```

</details>

### 🎯 快速启动

```bash
# 方式1：使用启动脚本（推荐）
./scripts/start.sh

# 方式2：直接运行
python run.py
```

🌐 访问 `http://localhost:5001`  
👤 默认账号：`admin` / `admin123`

---

## 📊 核心功能

<table>
<tr>
<td width="33%">

### 📈 数据分析
- ✅ 价格趋势分析（月度/季度/年度）
- ✅ 区域深度分析（Top 15热门区域）
- ✅ 户型分析（几室几厅分布与价格）
- ✅ 投资指数计算（多维度量化评分）
- ✅ 市场活跃度与波动性分析

</td>
<td width="33%">

### 🤖 AI智能助手
- 💬 实时AI对话（流式响应，打字机效果）
- 🔍 图表智能解读（一键AI洞察）
- 🔮 AI价格预测（数据锚定的可解释预测）
- 💡 购房策略规划（个性化建议）

</td>
<td width="33%">

### 🎨 可视化展示
- 📈 价格趋势折线图
- 🗺️ 3D房价地图（区域热力图）
- 📊 户型分布饼图与柱状图
- 📉 价格箱线图与小提琴图
- 🔥 区域-时间热力图

</td>
</tr>
</table>

---

## 📁 项目结构

```
python_house1/
├── 🚀 run.py                    # 项目启动入口
├── 📂 src/                      # 源代码目录
│   ├── core/                    # 核心应用（app.py, config.json）
│   ├── ai/                      # AI模块（对话、分析、预测、策略）
│   ├── analysis/               # 分析模块（房价分析、全国对比）
│   └── data/                    # 数据处理（爬虫、清洗、转换）
├── 📊 data/                     # 数据目录
│   └── processed/              # 处理后的数据（data_summary.json可公开）
├── 📄 reports/                  # 报告文件
│   ├── report.tex/pdf          # 学术报告
│   └── figures/                # 报告图片
├── 🎨 static/                   # 静态资源（CSS, JS）
├── 🖼️ templates/               # HTML模板
└── 📚 docs/                     # 详细文档
```

---

## 🎓 学术贡献

本项目构建了一套**端到端的智能房价分析系统**，在以下方面做出贡献：

| 贡献维度 | 说明 |
|---------|------|
| 📊 **数据规模** | 227万+条真实成交数据，覆盖26个省级行政区 |
| 🏗️ **架构创新** | 可插拔式AI架构，数据锚定机制消除AI幻觉 |
| 🎭 **个性化服务** | 三角色体系实现"千人千面"的智能咨询 |
| 🔮 **预测范式** | 数据锚定+AI推理的混合预测方法 |

**🔗 项目代码已开源**：[GitHub仓库](https://github.com/RuiyangSi/ai-housing-analyzer)

> ⚠️ **数据说明**：原始成交数据涉及隐私和网站使用协议，未在仓库中公开，仅保留汇总统计结果（`data_summary.json`）用于复现研究结论。

---

## 📖 引用

如果您在研究中使用了本项目，请引用：

**BibTeX格式：**
```bibtex
@software{ai_housing_analyzer,
  title = {AI驱动的智能房价分析系统：基于227万+真实成交数据的智能房地产市场分析平台},
  author = {Si, Ruiyang and Jiang, Baojin and Pan, Xiaoyu and Peng, Quanyu and Xie, Jiajun},
  year = {2025},
  url = {https://github.com/RuiyangSi/ai-housing-analyzer},
  version = {1.0.0},
  note = {Python程序设计期末项目}
}
```

**APA格式：**
```
Si, R., Jiang, B., Pan, X., Peng, Q., & Xie, J. (2025). AI驱动的智能房价分析系统：基于227万+真实成交数据的智能房地产市场分析平台 [Computer software]. GitHub. https://github.com/RuiyangSi/ai-housing-analyzer
```

---

## 📈 数据发现

基于**227万+条数据**的分析发现：

| 发现维度 | 关键洞察 |
|---------|---------|
| 🗺️ **空间分异** | 北京（52,173元/m²）与上海（47,642元/m²）稳居价格顶端，与西部省份形成**近8倍落差** |
| ⏰ **时间演变** | 市场整体经历"调整—筑底—企稳"演变，多数城市房价于2024年触底后逐步企稳 |
| 📊 **区域分化** | 一线城市与新一线城市间存在**3倍以上**的价格鸿沟 |

---

## 🤝 贡献

欢迎提交Issue和Pull Request！

📋 项目任务分工详见报告[附录B：项目任务分工](reports/report.pdf#page=xx)

---

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)

---

<div align="center">

### ⭐ 如果这个项目对你有帮助，请给个Star！ ⭐

**Made with ❤️ by Python Course Team**

[⬆ 返回顶部](#-ai驱动的智能房价分析系统)

</div>

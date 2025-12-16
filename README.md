# 🏠 AI驱动的智能房价分析系统

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1.2-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![AI](https://img.shields.io/badge/AI-DeepSeek--V3-purple.svg)

**基于2023-2025年真实成交数据的智能房地产市场分析平台**

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [文档](#-文档) • [项目结构](#-项目结构)

</div>

---

## 📖 项目简介

这是一个基于Flask和AI技术的房价分析系统，集成了数据可视化、AI对话、投资分析、价格预测等多种功能。系统覆盖全国25个省份的真实房价数据（2023-2025年），总数据量达200万+条。

### 核心亮点

- 🤖 **AI智能分析**：DeepSeek-V3驱动，提供专业的市场洞察
- 📊 **多维度可视化**：ECharts/Chart.js高级图表，3D地图展示
- 🎯 **角色定制**：支持首次购房者、改善型购房者、投资顾问三种角色
- 🏘️ **户型分析**：全国首创的户型（几室几厅）深度分析
- 🗺️ **全国对比**：横向对比多个城市的房价、投资价值
- 📈 **价格预测**：基于历史数据的AI价格预测功能

---

## ✨ 功能特性

### 1. 数据分析与可视化
- ✅ 25个省份、200万+条真实成交数据
- ✅ 价格趋势分析（月度、季度、年度）
- ✅ 区域深度分析（Top 15热门区域）
- ✅ 户型分析（几室几厅分布与价格）
- ✅ 投资指数计算（多维度评分）
- ✅ 市场活跃度与波动性分析

### 2. AI智能助手
- 🤖 实时AI对话（流式响应）
- 🎨 角色扮演（首购者/改善型/投资顾问）
- 📊 图表智能解读
- 💡 一键AI洞察（深度报告生成）

### 3. 高级可视化
- 📈 价格趋势折线图
- 📊 户型分布饼图与柱状图
- 🗺️ 3D房价地图（区域热力图）
- 📉 价格箱线图与小提琴图
- 🌊 价格变化瀑布图
- 🔥 区域-时间热力图

### 4. 投资决策工具
- 💰 购房策略规划器
- 📈 AI价格预测
- 🏆 投资价值评分
- 🌐 全国城市对比
- 📊 风险评估

### 5. 用户系统
- 👤 用户注册/登录
- 🎭 角色选择与切换
- 🔐 Session管理
- 📱 响应式设计（支持移动端）

---

## 🚀 快速开始

### 环境要求

- Python 3.9+
- pip
- （可选）虚拟环境工具

### 1. 克隆项目

```bash
git clone <repository-url>
cd python_house1
```

### 2. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

复制环境变量模板：
```bash
cp env.example .env
```

编辑 `.env` 文件，配置API密钥：
```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
SECRET_KEY=your_secret_key_here
```

> 💡 获取DeepSeek API密钥：访问 [https://platform.deepseek.com](https://platform.deepseek.com)

### 4. 运行项目

**方式1：使用启动脚本（推荐）**
```bash
chmod +x start.sh
./start.sh
```

**方式2：直接运行**
```bash
python app.py
```

### 5. 访问系统

打开浏览器访问：`http://localhost:5001`

默认账号：
- 用户名：`admin`
- 密码：`admin123`
- 角色：可自由选择

---

## 📁 项目结构

```
python_house1/
├── 📱 app.py                      # Flask主应用
├── 🤖 AI模块
│   ├── ai_assistant.py            # AI对话助手
│   ├── ai_image_generator.py     # AI图像生成
│   ├── intelligent_analyzer.py   # 智能分析器
│   └── strategy_analyzer.py      # 策略分析器
├── 📊 分析模块
│   ├── housing_analyzer.py        # 房价深度分析
│   ├── national_comparator.py    # 全国对比分析
│   └── price_predictor.py        # 价格预测
├── 🗂️ 数据处理
│   ├── process_all_data.py       # 批量数据处理
│   ├── process_csv_data.py       # CSV数据处理
│   └── chengjiao_combined_crawler.py  # 数据爬虫
├── 📂 data/                       # 数据目录
│   ├── processed/                 # 处理后的数据
│   │   ├── data_summary.json     # 数据摘要
│   │   └── data_*.csv            # 各省份数据
│   └── raw/                      # 原始数据
├── 🎨 static/                     # 静态资源
│   ├── css/                      # 样式文件
│   │   ├── modern-theme.css      # 现代主题
│   │   ├── analysis.css          # 分析页样式
│   │   └── style.css             # 通用样式
│   └── js/                       # JavaScript文件
│       ├── analysis.js           # 分析页逻辑
│       ├── chart_ai.js           # 图表AI分析
│       ├── national_comparison.js # 全国对比
│       ├── user_role.js          # 用户角色管理
│       └── ...
├── 🖼️ templates/                  # HTML模板
│   ├── base_layout.html          # 基础布局
│   ├── home.html                 # 首页
│   ├── analysis.html             # 分析页
│   ├── national_comparison.html  # 全国对比
│   ├── price_prediction.html     # 价格预测
│   └── ...
├── 📚 docs/                       # 文档目录
│   ├── README.md                 # 文档索引
│   ├── guides/                   # 使用指南
│   │   ├── 快速启动.md
│   │   ├── 使用指南.md
│   │   └── AUTH_GUIDE.md
│   ├── features/                 # 功能说明
│   │   ├── 户型分析功能说明.md
│   │   ├── 户型分析完整实现.md
│   │   └── 城市搜索筛选.md
│   └── bugfix/                   # Bug修复记录
├── 🧪 tests/                      # 测试文件
│   ├── test_api.py
│   └── test_data_manager.py
├── ⚙️ 配置文件
│   ├── config.json               # 城市配置
│   ├── requirements.txt          # Python依赖
│   ├── .gitignore               # Git忽略规则
│   ├── env.example              # 环境变量模板
│   └── start.sh                 # 启动脚本
├── 📄 README.md                  # 本文件
├── 📋 CHANGELOG.md               # 更新日志
└── 📜 CONTRIBUTION.md            # 贡献指南
```

---

## 📚 文档

详细文档请查看 `docs/` 目录：

### 使用指南
- [快速启动指南](docs/guides/快速启动.md) - 5分钟快速上手
- [完整使用指南](docs/guides/使用指南.md) - 详细功能说明
- [用户认证指南](docs/guides/AUTH_GUIDE.md) - 登录注册说明

### 功能文档
- [户型分析功能](docs/features/户型分析功能说明.md) - 几室几厅分析
- [AI助手使用](docs/AI助手使用指南.md) - AI对话功能
- [3D地图使用](docs/3D房价地图使用指南.md) - 3D可视化
- [API文档](docs/API_DOCUMENTATION.md) - 接口说明

### 技术文档
- [项目说明](docs/项目说明.md) - 技术架构
- [开发指南](CONTRIBUTION.md) - 贡献代码

---

## 🎯 核心技术栈

### 后端
- **Flask 3.1.2** - Web框架
- **Pandas 2.3.3** - 数据分析
- **NumPy** - 数值计算
- **SQLite** - 用户数据存储

### 前端
- **ECharts 5.4.3** - 高级数据可视化
- **Chart.js 4.4.0** - 图表库
- **原生JavaScript** - 交互逻辑
- **现代CSS3** - 响应式设计

### AI技术
- **DeepSeek-V3** - 大语言模型
- **流式响应** - 实时AI对话
- **Prompt工程** - 角色定制

---

## 📊 数据说明

### 数据来源
- 房天下（Fang.com）公开数据
- 时间跨度：2023年1月 - 2025年11月
- 覆盖范围：全国25个省份

### 数据规模
- 总数据量：**200万+** 条
- 城市数量：**25个** 省份/直辖市
- 数据字段：成交日期、价格、面积、户型、区域等

### 数据处理
- 数据清洗与标准化
- 异常值过滤
- 多源数据合并
- 增量更新支持

---

## 🎨 特色功能展示

### 1. 户型分析（全国首创）
- 📊 几室几厅分布统计
- 💰 不同户型价格对比
- 📈 主流户型价格趋势
- 🌐 全国户型横向对比

### 2. AI智能角色
**首次购房者**：通俗易懂的分析，关注性价比
**改善型购房者**：换房策略，资金规划
**投资顾问**：专业投资建议，ROI分析

### 3. 3D房价地图
- 区域价格立体展示
- 时间轴动态播放
- 交互式缩放旋转

---

## 🔧 开发指南

### 添加新城市数据

1. 准备CSV数据文件（包含必需字段）
2. 放入 `data/processed/` 目录
3. 编辑 `config.json` 添加城市配置
4. 重启服务器

### 扩展AI功能

参考 `ai_assistant.py` 中的实现，可以：
- 添加新的prompt模板
- 扩展角色定制逻辑
- 集成新的AI模型

### 贡献代码

请查看 [CONTRIBUTION.md](CONTRIBUTION.md) 了解代码规范和提交流程。

---

## 📝 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本更新历史。

### 最新版本 v2.0.0 (2024-12)
- ✨ 新增户型分析功能
- 🤖 优化AI分析质量
- 🎨 改进UI/UX设计
- 🐛 修复已知问题

---

## 🤝 贡献

欢迎提交Issue和Pull Request！

### 贡献者
- 课程大作业团队

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件

---

## 📮 联系方式

- 项目Issues：[GitHub Issues](issues链接)
- 邮箱：your-email@example.com

---

## 🙏 致谢

- 感谢房天下（Fang.com）提供的公开数据
- 感谢DeepSeek提供的AI服务
- 感谢所有开源社区的贡献者

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个Star！ ⭐**

Made with ❤️ by Python Course Team

</div>

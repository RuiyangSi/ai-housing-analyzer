# 📁 项目结构说明

本文档说明项目的目录结构和文件组织方式。

## 🎯 整理目标

将原本散落在根目录的文件按功能模块重新组织，提高项目的可维护性和可读性。

## 📂 新的目录结构

```
python_house1/
│
├── 📱 run.py                    # 项目启动入口（新增）
│
├── 📂 src/                      # 源代码目录（新增）
│   ├── core/                    # 核心应用模块
│   │   ├── app.py              # Flask主应用（从根目录移动）
│   │   └── config.json         # 配置文件（从根目录移动）
│   ├── ai/                      # AI模块
│   │   ├── ai_assistant.py
│   │   ├── ai_image_generator.py
│   │   ├── intelligent_analyzer.py
│   │   └── strategy_analyzer.py
│   ├── analysis/                # 分析模块
│   │   ├── housing_analyzer.py
│   │   ├── national_comparator.py
│   │   └── price_predictor.py
│   └── data/                    # 数据处理模块
│       ├── process_all_data.py
│       ├── process_csv_data.py
│       ├── process_data.py
│       └── chengjiao_combined_crawler.py
│
├── 📊 reports/                  # 报告文件目录（新增）
│   ├── report.tex               # LaTeX报告源文件
│   ├── report.pdf               # PDF报告
│   ├── prompt1.txt              # Prompt模板
│   └── figures/                 # 报告图片目录（从根目录移动）
│       ├── fig*.png             # 数据分析图表
│       └── 学习漫画*.png        # 学习漫画图片
│
├── 🛠️ scripts/                  # 脚本文件目录（新增）
│   ├── start.sh                 # 启动脚本
│   └── upload_to_github.sh      # GitHub上传脚本
│
├── 📂 data/                     # 数据目录（保持不变）
│   ├── processed/               # 处理后的数据
│   └── raw/                     # 原始数据
│
├── 🎨 static/                   # 静态资源（保持不变）
│   ├── css/
│   └── js/
│
├── 🖼️ templates/                # HTML模板（保持不变）
│
├── 📚 docs/                     # 文档目录（保持不变）
│
├── 🧪 tests/                    # 测试文件（保持不变）
│   └── test_deepseek_real.py    # 从根目录移动
│
└── ⚙️ 配置文件（根目录）
    ├── requirements.txt
    ├── .gitignore
    ├── env.example
    ├── README.md
    ├── CHANGELOG.md
    └── CONTRIBUTION.md
```

## 🔄 主要变更

### 1. 源代码组织
- **之前**：所有Python文件散落在根目录
- **现在**：按功能模块分类到 `src/` 目录下
  - `src/core/` - 核心应用代码
  - `src/ai/` - AI相关模块
  - `src/analysis/` - 数据分析模块
  - `src/data/` - 数据处理脚本

### 2. 报告文件
- **之前**：报告文件在根目录
- **现在**：统一移动到 `reports/` 目录

### 3. 脚本文件
- **之前**：脚本文件在根目录
- **现在**：统一移动到 `scripts/` 目录

### 4. 启动方式
- **新增**：`run.py` 作为项目启动入口
- **更新**：`scripts/start.sh` 使用新的启动方式

## 📝 路径更新说明

### Import路径更新
所有模块间的import语句已更新为相对导入：
- `from ai_assistant import AIAssistant` → `from src.ai.ai_assistant import AIAssistant`
- `from housing_analyzer import HousingAnalyzer` → `from src.analysis.housing_analyzer import HousingAnalyzer`

### Flask路径配置
- 模板路径：`templates/`（相对于项目根目录）
- 静态文件路径：`static/`（相对于项目根目录）
- 数据文件路径：`data/processed/`（相对于项目根目录）

### 配置文件路径
- `config.json` 现在位于 `src/core/config.json`
- 数据目录配置在 `config.json` 中：`"data_directory": "data/processed"`

## 🚀 启动方式

### 方式1：使用启动脚本（推荐）
```bash
./scripts/start.sh
```

### 方式2：直接运行Python入口
```bash
python run.py
```

## ✅ 整理完成检查清单

- [x] 创建新的目录结构
- [x] 移动Python源代码文件到src/目录
- [x] 移动报告文件到reports/目录
- [x] 移动脚本文件到scripts/目录
- [x] 更新所有import路径
- [x] 更新Flask应用配置
- [x] 更新启动脚本
- [x] 创建项目启动入口run.py
- [x] 更新.gitignore
- [x] 更新README.md

## 📌 注意事项

1. **数据文件**：原始CSV数据文件已从Git跟踪中移除，仅保留汇总统计文件（`data_summary.json`）
2. **环境变量**：确保 `.env` 文件配置正确（参考 `env.example`）
3. **虚拟环境**：建议使用虚拟环境运行项目
4. **Python路径**：`run.py` 会自动添加项目根目录到Python路径

## 🔍 文件查找指南

- **核心应用代码**：`src/core/app.py`
- **AI模块**：`src/ai/`
- **数据分析**：`src/analysis/`
- **数据处理脚本**：`src/data/`
- **配置文件**：`src/core/config.json`
- **报告文件**：`reports/`
- **启动脚本**：`scripts/start.sh` 或 `run.py`

---

**整理日期**：2025年1月
**整理目的**：提高项目可维护性和代码组织性


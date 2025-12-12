# 房价数据分析系统 (2023-2025)

一个基于 Python + Flask 的房价数据分析可视化系统，支持动态添加城市数据，可扩展性强。

## ✨ 功能特点

- 📊 **多城市数据支持**：当前支持北京、厦门、武汉三个城市
- 📈 **数据可视化**：月度价格趋势图、区域对比图
- 🔄 **动态配置**：通过配置文件轻松添加新城市数据
- 📱 **响应式设计**：支持移动端和桌面端访问
- 🚀 **高性能**：数据缓存机制，快速加载

## 🗂️ 项目结构

```
python_house1/
├── app.py                          # Flask 主应用
├── config.json                     # 城市数据配置文件
├── process_data.py                 # 数据处理脚本
├── data_beijing_2023_2025.csv     # 北京数据
├── data_xiamen_2023_2025.csv      # 厦门数据
├── data_wuhan_2023_2025.csv       # 武汉数据
├── templates/
│   └── index.html                  # 前端页面
├── static/
│   ├── css/
│   │   └── style.css              # 样式文件
│   └── js/
│       └── main.js                # JavaScript 逻辑
└── venv/                          # Python 虚拟环境
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 进入项目目录
cd /Users/ruiyangsi/Desktop/python_house1

# 激活虚拟环境
source venv/bin/activate

# 确认依赖已安装
pip list | grep -E "(pandas|flask|openpyxl)"
```

### 2. 运行应用

```bash
# 激活虚拟环境（如果还未激活）
source venv/bin/activate

# 启动 Flask 服务器
python app.py
```

服务器启动后，在浏览器中访问：`http://localhost:5000`

## 📥 添加新城市数据

### 方法一：使用现有 Excel 文件

1. **准备数据文件**
   - 将新城市的 Excel 文件放入项目目录
   - 确保 Excel 文件包含以下列：
     - 成交日期、城市、区域、商圈、小区
     - 户型、面积（m²）、挂牌价（万元）
     - 成交价（万元）、成交单价（元）

2. **修改 process_data.py**
   
   在 `process_data.py` 的 `cities` 列表中添加新城市：

```python
cities = [
    # ... 现有城市 ...
    {
        'name': '上海',  # 城市名称
        'excel_file': '上海成交数据.xlsx',  # Excel 文件名
        'output_file': 'data_shanghai_2023_2025.csv'  # 输出的 CSV 文件名
    }
]
```

3. **运行数据处理脚本**

```bash
source venv/bin/activate
python process_data.py
```

4. **更新配置文件**

   编辑 `config.json`，添加新城市配置：

```json
{
  "cities": [
    {
      "name": "上海",
      "name_en": "shanghai",
      "data_file": "data_shanghai_2023_2025.csv",
      "enabled": true
    }
  ]
}
```

5. **重启应用或点击"🔄 重新加载配置"按钮**

### 方法二：直接使用 CSV 文件

如果你已经有 CSV 格式的数据：

1. **确保 CSV 包含以下列**：
   - 成交日期、城市、区域、商圈、小区
   - 户型、面积（m²）、挂牌价（万元）
   - 成交价（万元）、成交单价（元）

2. **将 CSV 文件放入项目目录**

3. **更新 config.json**：

```json
{
  "cities": [
    {
      "name": "深圳",
      "name_en": "shenzhen",
      "data_file": "data_shenzhen_2023_2025.csv",
      "enabled": true
    }
  ]
}
```

4. **刷新网页或点击重新加载按钮**

## 🔧 配置说明

### config.json 配置项

```json
{
  "cities": [
    {
      "name": "北京",           // 显示的城市名称（中文）
      "name_en": "beijing",     // 城市英文标识（用于 API）
      "data_file": "data_beijing_2023_2025.csv",  // 数据文件路径
      "enabled": true           // 是否启用该城市
    }
  ],
  "data_directory": ".",        // 数据文件所在目录
  "year_range": {
    "start": 2023,              // 分析起始年份
    "end": 2025                 // 分析结束年份
  }
}
```

### 临时禁用某个城市

只需将该城市的 `enabled` 设置为 `false`：

```json
{
  "name": "武汉",
  "name_en": "wuhan",
  "data_file": "data_wuhan_2023_2025.csv",
  "enabled": false  // 禁用武汉数据
}
```

## 📊 数据统计内容

系统提供以下数据分析：

1. **总体统计**
   - 总成交量
   - 平均成交价
   - 平均单价
   - 平均面积

2. **年度统计**
   - 各年度成交量
   - 各年度平均价格
   - 总成交额

3. **月度趋势**
   - 月度平均成交价趋势
   - 月度平均单价趋势

4. **区域分析**
   - Top 10 区域均价排名
   - 各区域成交量

## 🛠️ 技术栈

- **后端**：Python 3.x + Flask
- **数据处理**：Pandas
- **前端**：HTML5 + CSS3 + JavaScript
- **图表库**：Chart.js
- **数据格式**：CSV (UTF-8)

## 📝 API 接口

### 获取城市列表
```
GET /api/cities
```

### 获取城市统计数据
```
GET /api/city/<city_name_en>/statistics
```

### 重新加载配置
```
GET /api/reload
```

## ⚠️ 注意事项

1. **日期格式**：确保 Excel 中的日期格式为 `YYYY.MM.DD`
2. **编码**：CSV 文件使用 UTF-8 编码（带 BOM）
3. **数据质量**：删除空值和异常值以保证分析准确性
4. **文件大小**：大文件可能需要较长加载时间，建议分年份处理

## 🔄 数据更新流程

1. 准备新的数据文件（Excel 或 CSV）
2. 运行 `process_data.py` 处理数据
3. 更新 `config.json` 配置
4. 点击网页上的 "重新加载配置" 按钮或重启服务器

## 📞 常见问题

**Q: 如何更改分析的年份范围？**

A: 修改 `config.json` 中的 `year_range`，然后重新运行 `process_data.py`。

**Q: 数据加载失败怎么办？**

A: 检查以下几点：
- CSV 文件是否存在
- 文件路径是否正确
- CSV 格式是否符合要求
- 查看浏览器控制台的错误信息

**Q: 如何自定义样式？**

A: 编辑 `static/css/style.css` 文件，修改 CSS 变量或样式类。

## 📄 许可证

本项目仅供学习和研究使用。

---

**开发时间**：2025年11月


#!/bin/bash

# 房价数据分析系统启动脚本

echo "========================================"
echo "  房价数据分析系统"
echo "========================================"

# 进入项目目录
cd "$(dirname "$0")"

# 激活虚拟环境
if [ -d "venv" ]; then
    echo "✓ 激活虚拟环境..."
    source venv/bin/activate
else
    echo "❌ 错误：虚拟环境不存在"
    echo "请先运行: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# 检查数据文件是否存在
if [ ! -f "data/processed/data_beijing_2023_2025.csv" ] || [ ! -f "data/processed/data_xiamen_2023_2025.csv" ] || [ ! -f "data/processed/data_wuhan_2023_2025.csv" ]; then
    echo "⚠️  警告：数据文件不完整"
    echo "正在处理数据..."
    python process_data.py
    if [ $? -ne 0 ]; then
        echo "❌ 数据处理失败"
        exit 1
    fi
fi

echo ""
echo "✓ 启动 Flask 服务器..."
echo ""
echo "访问地址: http://localhost:5001"
echo "按 Ctrl+C 停止服务器"
echo ""

# 启动应用
python app.py


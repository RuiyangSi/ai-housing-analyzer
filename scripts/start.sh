#!/bin/bash

# AI 房价分析系统启动脚本

echo "========================================"
echo "  AI 房价分析系统 v2.0"
echo "========================================"

# 进入项目根目录（脚本在scripts/目录下，需要回到项目根目录）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# 加载环境变量（如果存在 .env 文件）
if [ -f ".env" ]; then
    echo "✓ 加载环境变量..."
    export $(cat .env | grep -v '#' | xargs)
fi

# 设置默认 API Key（如果未配置）
if [ -z "$DEEPSEEK_API_KEY" ]; then
    export DEEPSEEK_API_KEY="sk-lmybvxylhwtivvlnwieusqugkflvppcctolnqchbhnekhtnp"
    echo "✓ 使用默认 API Key"
fi

# 激活虚拟环境
if [ -d "venv" ]; then
    echo "✓ 激活虚拟环境..."
    source venv/bin/activate
else
    echo "❌ 错误：虚拟环境不存在"
    echo "请先运行: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi


# 关闭之前占用 5001 端口的进程
echo "✓ 检查端口 5001..."
PID=$(lsof -ti:5001 2>/dev/null)
if [ ! -z "$PID" ]; then
    echo "  关闭之前的进程 (PID: $PID)..."
    kill -9 $PID 2>/dev/null
    sleep 1
fi

echo ""
echo "✓ 启动 Flask 服务器..."
echo ""
echo "🌐 访问地址: http://localhost:5001"
echo "📝 首次使用请注册账号"
echo "⏹  按 Ctrl+C 停止服务器"
echo ""

# 启动应用
python run.py

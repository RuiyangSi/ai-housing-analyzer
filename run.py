#!/usr/bin/env python3
"""
项目启动入口文件
运行此文件启动Flask应用
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入并运行Flask应用
from src.core.app import app

if __name__ == '__main__':
    print("=" * 60)
    print("🏠 AI驱动的智能房价分析系统")
    print("=" * 60)
    print(f"📁 项目根目录: {project_root}")
    print(f"🌐 启动地址: http://localhost:5001")
    print("=" * 60)
    print("按 Ctrl+C 停止服务器")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5001, debug=True)


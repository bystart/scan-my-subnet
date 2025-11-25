#!/bin/bash

echo "======================================"
echo "  IP网络监控系统 - 启动脚本"
echo "======================================"
echo ""

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3，请先安装 Python 3.11+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "检测到 Python 版本: $PYTHON_VERSION"

# 创建数据目录
if [ ! -d "data" ]; then
    echo "创建数据目录..."
    mkdir -p data
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

echo ""
echo "======================================"
echo "  启动服务..."
echo "======================================"
echo ""
echo "访问地址: http://localhost:8000"
echo "按 Ctrl+C 停止服务"
echo ""

# 启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

#!/bin/bash

echo "======================================"
echo "  Docker部署脚本"
echo "======================================"
echo ""

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "错误: 未找到 Docker，请先安装 Docker"
    exit 1
fi

# 检查Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "错误: 未找到 Docker Compose，请先安装 Docker Compose"
    exit 1
fi

echo "检测到 Docker 和 Docker Compose"
echo ""

# 创建数据目录
if [ ! -d "data" ]; then
    echo "创建数据目录..."
    mkdir -p data
fi

# 构建并启动
echo "构建Docker镜像并启动容器..."
docker-compose up -d --build

echo ""
echo "======================================"
echo "  部署完成！"
echo "======================================"
echo ""
echo "访问地址: http://localhost:8000"
echo ""
echo "常用命令:"
echo "  查看日志: docker-compose logs -f"
echo "  停止服务: docker-compose down"
echo "  重启服务: docker-compose restart"
echo ""

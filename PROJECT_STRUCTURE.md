# 项目结构说明

## 目录树
```
ip-network-monitor/
├── app/                      # 后端应用目录
│   ├── __init__.py          # Python包初始化文件
│   ├── main.py              # FastAPI主应用 (API路由、业务逻辑)
│   ├── models.py            # 数据模型定义 (Pydantic)
│   ├── services.py          # 核心服务 (IP扫描、Ping功能)
│   └── storage.py           # JSON存储管理
│
├── static/                   # 前端静态文件
│   └── index.html           # 单页面应用 (Vue 3 + Tailwind CSS)
│
├── data/                     # 数据存储目录 (自动创建)
│   ├── networks.json        # 网段配置数据
│   └── ip_status.json       # IP状态数据
│
├── requirements.txt          # Python依赖包列表
├── Dockerfile               # Docker镜像构建文件
├── docker-compose.yml       # Docker Compose配置
├── .gitignore              # Git忽略文件配置
│
├── start.sh                 # 本地启动脚本
├── deploy.sh                # Docker部署脚本
├── test_system.py           # 系统功能测试脚本
│
├── README.md                # 项目说明文档
├── QUICKSTART.md            # 快速开始指南
├── USAGE.md                 # 详细使用文档
└── PROJECT_STRUCTURE.md     # 本文件
```

## 文件说明

### 核心代码文件

#### app/main.py
- FastAPI应用主文件
- 定义所有API端点
- 路由配置
- 静态文件服务

主要API端点:
- GET `/` - 前端页面
- GET `/api/networks` - 获取所有网段
- POST `/api/networks` - 创建网段
- DELETE `/api/networks/{id}` - 删除网段
- GET `/api/networks/{id}` - 获取网段详情
- POST `/api/networks/{id}/scan` - 扫描网段
- GET `/api/stats` - 获取统计信息

#### app/models.py
定义数据模型:
- `NetworkSegment` - 网段模型
- `IPStatus` - IP状态模型
- `NetworkSegmentWithIPs` - 带IP列表的网段模型
- `ScanRequest` - 扫描请求模型

#### app/services.py
核心业务逻辑:
- `ping_ip()` - 异步Ping单个IP
- `scan_network_segment()` - 扫描整个网段
- `quick_check_ips()` - 快速检查IP列表

#### app/storage.py
JSON数据持久化:
- `JSONStorage` - 存储管理类
- `load_networks()` - 加载网段数据
- `save_networks()` - 保存网段数据
- `load_ip_status()` - 加载IP状态
- `save_ip_status()` - 保存IP状态

### 前端文件

#### static/index.html
- 单页面应用
- 使用Vue 3框架
- Tailwind CSS样式
- Font Awesome图标
- 响应式设计

主要功能:
- 网段列表展示
- 添加/删除网段
- 扫描网段
- IP详情展示
- 状态筛选
- 实时统计

### 配置文件

#### requirements.txt
Python依赖包:
- fastapi - Web框架
- uvicorn - ASGI服务器
- pydantic - 数据验证
- aiofiles - 异步文件操作

#### Dockerfile
- 基于 python:3.11-slim
- 安装ping命令
- 配置工作目录
- 暴露8000端口

#### docker-compose.yml
- 服务配置
- 端口映射
- 数据卷挂载
- host网络模式

### 脚本文件

#### start.sh
本地启动脚本:
1. 检查Python版本
2. 创建虚拟环境
3. 安装依赖
4. 启动服务

#### deploy.sh
Docker部署脚本:
1. 检查Docker环境
2. 创建数据目录
3. 构建并启动容器

#### test_system.py
功能测试脚本:
- 测试数据模型
- 测试JSON存储
- 测试Ping功能
- 测试API导入

### 文档文件

#### README.md
项目主文档:
- 项目介绍
- 功能特性
- 技术栈
- 部署方法
- API文档
- 配置说明

#### QUICKSTART.md
快速开始指南:
- 三种部署方式
- 第一次使用步骤
- CIDR示例

#### USAGE.md
详细使用文档:
- 完整使用流程
- API使用示例
- 性能优化
- 故障排除
- 安全建议

## 数据流程

```
用户操作 → 前端(Vue) → API请求 → FastAPI路由 
    ↓
业务逻辑(services) → 数据存储(storage) → JSON文件
    ↓
响应返回 → 前端更新 → 用户界面
```

## 扫描流程

```
用户点击扫描 → POST /api/networks/{id}/scan
    ↓
后台任务启动 → scan_network_segment()
    ↓
并发Ping所有IP → ping_ip() × N
    ↓
收集结果 → 保存到JSON → 更新状态
    ↓
前端轮询 → 显示结果
```

## 数据存储格式

### networks.json
```json
[
  {
    "id": "uuid-string",
    "name": "网段名称",
    "cidr": "192.168.1.0/24",
    "description": "描述信息",
    "created_at": "2024-01-01T00:00:00"
  }
]
```

### ip_status.json
```json
{
  "network-id": [
    {
      "ip": "192.168.1.1",
      "is_active": true,
      "last_checked": "2024-01-01T00:00:00",
      "hostname": null
    }
  ]
}
```

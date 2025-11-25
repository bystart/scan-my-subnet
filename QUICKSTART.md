# 快速开始指南

## 方式一: Docker部署（最简单，推荐）

### 1. 确保已安装Docker
```bash
docker --version
docker-compose --version
```

### 2. 一键部署
```bash
./deploy.sh
```

### 3. 访问系统
打开浏览器访问: http://localhost:8000

**默认登录**: 用户名和密码均为 `admin`

---

## 方式二: 本地Python运行

### 1. 检查Python版本
```bash
python3 --version  # 需要 Python 3.11+
```

### 2. 一键启动
```bash
./start.sh
```

### 3. 访问系统
打开浏览器访问: http://localhost:8000

**默认登录**: 用户名和密码均为 `admin`

---

## 方式三: 手动部署

### 1. 安装依赖
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖包
pip install -r requirements.txt
```

### 2. 启动服务
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. 访问系统
打开浏览器访问: http://localhost:8000

---

## 第一次使用

### 0. 登录系统
- 打开浏览器访问 http://localhost:8000
- 输入默认用户名: `admin`
- 输入默认密码: `admin`
- 点击登录按钮

**重要**: 登录后立即修改密码！
- 点击右上角"修改密码"按钮
- 输入旧密码: `admin`
- 输入并确认新密码
- 点击"确认修改"

### 1. 添加网段
- 点击右上角"添加网段"按钮
- 输入网段信息:
  - 名称: `办公区网络`
  - CIDR: `192.168.1.0/24`
  - 描述: `一楼办公区`

### 2. 扫描网段
- 找到添加的网段
- 点击"扫描"按钮
- 等待扫描完成

### 3. 查看结果
- 点击展开按钮查看IP详情
- 绿色=在线，红色=离线
- 使用筛选按钮过滤显示

---

## 常见网段CIDR示例

| CIDR | IP范围 | 可用IP数 | 适用场景 |
|------|--------|---------|---------|
| 192.168.1.0/24 | 192.168.1.1-254 | 254 | 小型办公室 |
| 192.168.0.0/24 | 192.168.0.1-254 | 254 | 家庭网络 |
| 10.0.1.0/24 | 10.0.1.1-254 | 254 | 部门网络 |
| 172.16.0.0/16 | 172.16.0.1-255.254 | 65,534 | 企业网络 |

---

## 需要帮助?

- 查看详细文档: [README.md](README.md)
- 使用示例: [USAGE.md](USAGE.md)
- 运行测试: `python3 test_system.py`

---

## 停止服务

### Docker部署
```bash
docker-compose down
```

### 本地运行
按 `Ctrl+C` 停止服务

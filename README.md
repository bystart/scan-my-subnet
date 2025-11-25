# IP网络资源使用情况监控系统

一个基于Python 3.11和FastAPI开发的Web服务，用于监控和展示内网IP使用情况。支持多网段管理，实时扫描IP在线状态。

欢迎关注我的公众号：青檬小栈

![青檬小栈](https://mp.bystart.cn/qrcode_for_gh_72f4e30f4553_258.jpg)

## 功能特性

- 🔐 **用户认证** - JWT令牌认证，密码bcrypt加密，安全可靠
- 📊 **多网段管理** - 支持添加、删除多个内网网段
- 🔍 **IP扫描** - 自动扫描网段内所有IP的在线状态
- 📈 **实时统计** - 实时显示网段、IP总数及在线/离线统计
- 🎨 **精美界面** - 使用Vue 3 + Tailwind CSS打造现代化UI
- 💾 **JSON存储** - 无需数据库，使用JSON文件持久化数据
- 🐳 **Docker支持** - 一键Docker部署
- ⚡ **高性能** - 异步并发扫描，支持大规模网段

## 技术栈

- **后端**: FastAPI + Python 3.11
- **前端**: Vue 3 + Tailwind CSS
- **存储**: JSON文件
- **部署**: Docker + Docker Compose

## 快速开始

### 方式一: Docker部署（推荐）

1. 确保已安装Docker和Docker Compose

2. 克隆项目并启动:
```bash
docker-compose up -d
```

3. 访问 http://localhost:8000

**首次登录**: 使用默认用户名密码 `admin/admin`，登录后请立即修改密码！

### 方式二: 本地运行

1. 安装Python 3.11

2. 安装依赖:
```bash
pip install -r requirements.txt
```

3. 启动服务:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

4. 访问 http://localhost:8000

**首次登录**: 使用默认用户名密码 `admin/admin`，登录后请立即修改密码！

## 登录认证

系统已集成JWT认证，所有功能需登录后使用。

**默认账号**:
- 用户名: `admin`
- 密码: `admin`

**重要**: 首次登录后请点击右上角"修改密码"按钮修改默认密码！


## 使用说明

### 添加网段

1. 点击右上角"添加网段"按钮
2. 填写网段信息:
   - **网段名称**: 如"办公区网络"
   - **CIDR**: 如"192.168.1.0/24"
   - **描述**: 可选的备注信息
3. 点击"添加"

### 扫描IP

1. 在网段卡片中点击"扫描"按钮
2. 系统将自动扫描该网段内所有IP
3. 扫描完成后显示在线/离线统计

### 查看IP详情

1. 点击网段卡片右侧的展开按钮
2. 查看该网段所有IP的详细状态
3. 可以筛选显示: 全部/在线/离线

## 项目结构

```
ip-network-monitor/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI主应用
│   ├── models.py        # 数据模型
│   ├── services.py      # IP扫描服务
│   └── storage.py       # JSON存储
├── static/
│   └── index.html       # 前端页面
├── data/
│   ├── networks.json    # 网段数据
│   └── ip_status.json   # IP状态数据
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## API接口

### 网段管理

- `GET /api/networks` - 获取所有网段
- `POST /api/networks` - 创建网段
- `GET /api/networks/{id}` - 获取网段详情
- `DELETE /api/networks/{id}` - 删除网段

### 扫描功能

- `POST /api/networks/{id}/scan` - 启动扫描
- `GET /api/networks/{id}/scan-status` - 获取扫描状态

### 统计信息

- `GET /api/stats` - 获取全局统计

## 配置说明

### Docker部署配置

编辑 `docker-compose.yml`:

```yaml
services:
  ip-monitor:
    ports:
      - "8000:8000"  # 修改端口映射
    volumes:
      - ./data:/app/data  # 数据持久化
    network_mode: "host"  # 使用host模式扫描内网
```

### 扫描并发数

编辑 `app/services.py` 中的 `max_concurrent` 参数:

```python
async def scan_network_segment(segment: NetworkSegment, max_concurrent: int = 50):
    # max_concurrent: 最大并发扫描数，可根据性能调整
```

## 注意事项

1. **网络模式**: Docker部署时使用`host`网络模式以便扫描内网IP
2. **扫描权限**: 需要ICMP权限才能ping，某些环境可能需要root权限
3. **扫描时间**: 大网段（如/16）扫描时间较长，请耐心等待
4. **数据备份**: 建议定期备份`data`目录下的JSON文件

## 常见问题

### Q: 扫描无法检测到在线IP?
A: 检查Docker是否使用了`host`网络模式，或者目标主机防火墙是否允许ICMP

### Q: 扫描速度慢?
A: 可以调整`max_concurrent`参数增加并发数，但注意不要设置过大

### Q: 数据丢失?
A: 确保`data`目录已通过Docker volume挂载到宿主机

## 开发

### 安装开发依赖
```bash
pip install -r requirements.txt
```

### 运行测试
```bash
pytest
```

### 代码格式化
```bash
black app/
```

## 贡献

欢迎提交Issue和Pull Request!

## 作者

科长 关注我的公众号[青檬小栈](https://mp.bystart.cn/)

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Optional
import uuid
from app.models import NetworkSegment, NetworkSegmentWithIPs, ScanRequest
from app.storage import JSONStorage
from app.services import scan_network_segment, quick_check_ips
from app.auth import (
    Token, LoginRequest, ChangePasswordRequest,
    create_access_token, decode_token
)
from app.user_storage import UserStorage

app = FastAPI(
    title="IP Network Monitor",
    description="内网IP使用情况监控系统",
    version="1.0.0"
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 初始化存储
storage = JSONStorage()
user_storage = UserStorage()

# 存储扫描任务状态
scan_tasks = {}


# JWT认证依赖
async def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    """验证JWT令牌并返回用户名"""
    if not authorization:
        raise HTTPException(status_code=401, detail="未提供认证令牌")

    try:
        # 格式: "Bearer <token>"
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="无效的认证方案")
    except ValueError:
        raise HTTPException(status_code=401, detail="无效的认证头格式")

    username = decode_token(token)
    if username is None:
        raise HTTPException(status_code=401, detail="无效或过期的令牌")

    return username


@app.get("/")
async def root():
    """返回前端页面"""
    return FileResponse("static/index.html")


@app.post("/api/login", response_model=Token)
async def login(request: LoginRequest):
    """用户登录"""
    # 验证用户名和密码
    is_valid = await user_storage.verify_user(request.username, request.password)

    if not is_valid:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 创建访问令牌
    access_token = create_access_token(data={"sub": request.username})

    return Token(access_token=access_token, token_type="bearer")


@app.post("/api/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: str = Depends(get_current_user)
):
    """修改密码"""
    # 验证旧密码
    is_valid = await user_storage.verify_user(current_user, request.old_password)

    if not is_valid:
        raise HTTPException(status_code=400, detail="旧密码错误")

    # 更新密码
    success = await user_storage.update_password(current_user, request.new_password)

    if not success:
        raise HTTPException(status_code=500, detail="密码更新失败")

    return {"message": "密码修改成功"}


@app.get("/api/networks", response_model=List[NetworkSegment])
async def get_networks(current_user: str = Depends(get_current_user)):
    """获取所有网段"""
    return await storage.load_networks()


@app.post("/api/networks", response_model=NetworkSegment)
async def create_network(
    network: NetworkSegment,
    current_user: str = Depends(get_current_user)
):
    """创建新网段"""
    # 生成唯一ID
    if not network.id:
        network.id = str(uuid.uuid4())

    networks = await storage.load_networks()

    # 检查CIDR是否已存在
    if any(n.cidr == network.cidr for n in networks):
        raise HTTPException(status_code=400, detail="该网段已存在")

    networks.append(network)
    await storage.save_networks(networks)

    return network


@app.delete("/api/networks/{network_id}")
async def delete_network(
    network_id: str,
    current_user: str = Depends(get_current_user)
):
    """删除网段"""
    networks = await storage.load_networks()
    networks = [n for n in networks if n.id != network_id]
    await storage.save_networks(networks)

    # 同时删除该网段的IP状态数据
    all_status = await storage.load_ip_status()
    if network_id in all_status:
        del all_status[network_id]
        await storage.save_ip_status(all_status)

    return {"message": "删除成功"}


@app.get("/api/networks/{network_id}", response_model=NetworkSegmentWithIPs)
async def get_network_detail(
    network_id: str,
    current_user: str = Depends(get_current_user)
):
    """获取网段详情及IP列表"""
    networks = await storage.load_networks()
    network = next((n for n in networks if n.id == network_id), None)

    if not network:
        raise HTTPException(status_code=404, detail="网段不存在")

    ips = await storage.get_segment_ips(network_id)

    active_count = sum(1 for ip in ips if ip.is_active)
    inactive_count = len(ips) - active_count

    return NetworkSegmentWithIPs(
        segment=network,
        ips=ips,
        total_ips=len(ips),
        active_ips=active_count,
        inactive_ips=inactive_count
    )


async def perform_scan(network_id: str):
    """执行扫描任务"""
    try:
        scan_tasks[network_id] = {"status": "scanning", "progress": 0}

        networks = await storage.load_networks()
        network = next((n for n in networks if n.id == network_id), None)

        if not network:
            scan_tasks[network_id] = {"status": "error", "message": "网段不存在"}
            return

        # 执行扫描
        ips = await scan_network_segment(network)

        # 保存结果
        await storage.update_segment_ips(network_id, ips)

        scan_tasks[network_id] = {
            "status": "completed",
            "total": len(ips),
            "active": sum(1 for ip in ips if ip.is_active)
        }

    except Exception as e:
        scan_tasks[network_id] = {"status": "error", "message": str(e)}


@app.post("/api/networks/{network_id}/scan")
async def scan_network(
    network_id: str,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user)
):
    """扫描网段"""
    networks = await storage.load_networks()
    if not any(n.id == network_id for n in networks):
        raise HTTPException(status_code=404, detail="网段不存在")

    # 添加后台任务
    background_tasks.add_task(perform_scan, network_id)

    return {"message": "扫描任务已启动", "task_id": network_id}


@app.get("/api/networks/{network_id}/scan-status")
async def get_scan_status(
    network_id: str,
    current_user: str = Depends(get_current_user)
):
    """获取扫描状态"""
    if network_id not in scan_tasks:
        return {"status": "not_started"}
    return scan_tasks[network_id]


@app.get("/api/stats")
async def get_stats(current_user: str = Depends(get_current_user)):
    """获取统计信息"""
    networks = await storage.load_networks()
    all_status = await storage.load_ip_status()

    total_networks = len(networks)
    total_ips = 0
    total_active = 0

    for network_id in all_status:
        ips = all_status[network_id]
        total_ips += len(ips)
        total_active += sum(1 for ip in ips if ip.get('is_active', False))

    return {
        "total_networks": total_networks,
        "total_ips": total_ips,
        "active_ips": total_active,
        "inactive_ips": total_ips - total_active
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

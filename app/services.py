import asyncio
import ipaddress
import platform
from datetime import datetime
from typing import List
from app.models import IPStatus, NetworkSegment


async def ping_ip(ip: str, timeout: int = 1) -> bool:
    """
    异步ping IP地址

    Args:
        ip: IP地址
        timeout: 超时时间（秒）

    Returns:
        bool: IP是否在线
    """
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    timeout_param = '-w' if platform.system().lower() == 'windows' else '-W'

    command = ['ping', param, '1', timeout_param, str(timeout), ip]

    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await asyncio.wait_for(process.communicate(), timeout=timeout + 1)
        return process.returncode == 0
    except (asyncio.TimeoutError, Exception):
        return False


async def scan_network_segment(segment: NetworkSegment, max_concurrent: int = 50) -> List[IPStatus]:
    """
    扫描网段内所有IP

    Args:
        segment: 网段信息
        max_concurrent: 最大并发数

    Returns:
        List[IPStatus]: IP状态列表
    """
    network = ipaddress.ip_network(segment.cidr, strict=False)

    # 获取所有可用IP（排除网络地址和广播地址）
    all_ips = list(network.hosts()) if network.num_addresses > 2 else [network.network_address]

    results = []
    semaphore = asyncio.Semaphore(max_concurrent)

    async def scan_single_ip(ip):
        async with semaphore:
            ip_str = str(ip)
            is_active = await ping_ip(ip_str)
            return IPStatus(
                ip=ip_str,
                is_active=is_active,
                last_checked=datetime.now().isoformat(),
                hostname=None
            )

    # 并发扫描所有IP
    tasks = [scan_single_ip(ip) for ip in all_ips]
    results = await asyncio.gather(*tasks)

    return results


async def quick_check_ips(ips: List[str], timeout: int = 1) -> List[IPStatus]:
    """
    快速检查指定IP列表的状态

    Args:
        ips: IP地址列表
        timeout: 超时时间

    Returns:
        List[IPStatus]: IP状态列表
    """
    async def check_single(ip):
        is_active = await ping_ip(ip, timeout)
        return IPStatus(
            ip=ip,
            is_active=is_active,
            last_checked=datetime.now().isoformat(),
            hostname=None
        )

    tasks = [check_single(ip) for ip in ips]
    return await asyncio.gather(*tasks)

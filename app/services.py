import asyncio
import ipaddress
import subprocess
import platform
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict
from app.models import IPStatus, NetworkSegment


# 检查nmap是否可用
def check_nmap_available() -> bool:
    """检查系统是否安装了nmap"""
    try:
        result = subprocess.run(['nmap', '--version'],
                              capture_output=True,
                              timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


NMAP_AVAILABLE = check_nmap_available()


async def check_ip_alive(ip: str, timeout: int = 1) -> bool:
    """
    使用ping命令检测IP是否在线

    Args:
        ip: IP地址
        timeout: 超时时间（秒）

    Returns:
        bool: IP是否在线
    """
    # 根据操作系统设置ping命令参数
    system = platform.system().lower()

    if system == 'windows':
        # Windows: ping -n 1 -w timeout_ms IP
        param = '-n'
        timeout_param = '-w'
        timeout_value = str(timeout * 1000)  # Windows使用毫秒
    else:
        # Linux/Mac: ping -c 1 -W timeout_sec IP
        param = '-c'
        timeout_param = '-W'
        timeout_value = str(timeout)

    command = ['ping', param, '1', timeout_param, timeout_value, ip]

    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # 等待ping命令完成，额外增加1秒防止超时
        await asyncio.wait_for(process.communicate(), timeout=timeout + 1)

        # 返回码0表示ping成功
        return process.returncode == 0
    except (asyncio.TimeoutError, Exception):
        return False


async def scan_network_segment(segment: NetworkSegment) -> List[IPStatus]:
    """
    使用ping方式快速扫描网段

    Args:
        segment: 网段信息

    Returns:
        List[IPStatus]: IP状态列表
    """
    network = ipaddress.ip_network(segment.cidr, strict=False)

    # 获取所有可用IP（排除网络地址和广播地址）
    all_ips = list(network.hosts()) if network.num_addresses > 2 else [network.network_address]

    # 并发扫描所有IP（使用信号量控制并发数）
    max_concurrent = 50  # 最大并发50个ping（平衡速度和系统资源）
    semaphore = asyncio.Semaphore(max_concurrent)

    async def scan_single_ip(ip):
        async with semaphore:
            ip_str = str(ip)
            is_active = await check_ip_alive(ip_str)
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


async def scan_network_with_nmap(cidr: str) -> List[IPStatus]:
    """
    使用TCP方式快速扫描整个网段（已弃用，保留用于兼容）
    现在统一使用 scan_network_segment 进行扫描

    Args:
        cidr: 网段CIDR

    Returns:
        List[IPStatus]: IP状态列表
    """
    # 创建临时的NetworkSegment对象
    from app.models import NetworkSegment
    temp_segment = NetworkSegment(
        id="temp",
        name="temp",
        cidr=cidr,
        description=""
    )
    return await scan_network_segment(temp_segment)


async def scan_host_info(ip: str, start_port: int = 1, end_port: int = 1024) -> Dict:
    """
    扫描主机完整信息（使用nmap）

    Args:
        ip: IP地址
        start_port: 起始端口
        end_port: 结束端口

    Returns:
        Dict: 包含主机信息的字典
    """
    if not NMAP_AVAILABLE:
        raise RuntimeError("nmap未安装，无法执行主机扫描。请安装nmap后重试。")

    # 使用nmap扫描（更准确）
    return await scan_host_with_nmap(ip, start_port, end_port)


async def scan_host_with_nmap(ip: str, start_port: int, end_port: int) -> Dict:
    """
    使用nmap快速扫描主机信息

    Args:
        ip: IP地址
        start_port: 起始端口
        end_port: 结束端口

    Returns:
        Dict: 包含主机信息的字典
    """
    try:
        # 首先尝试完整扫描（包含OS检测，需要root权限）
        # -sV: 服务版本检测
        # -O: OS检测（需要root权限）
        # -T5: 最快的扫描速度
        # --min-rate: 最小发包速率
        # --max-retries: 最多重试1次
        cmd_full = [
            'nmap',
            '-sV',                  # 服务版本检测
            '-O',                   # OS检测
            '-T4',                  # 最快速度
            '--min-rate', '300',    # 最小发包速率
            '--max-retries', '1',   # 最多重试1次
            '--host-timeout', '180s', # 主机超时3分钟
            '-p', f'{start_port}-{end_port}',
            '-oX', '-',             # 输出XML到stdout
            ip
        ]

        # 异步执行nmap完整扫描
        process = await asyncio.create_subprocess_exec(
            *cmd_full,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        # 如果完整扫描成功，返回结果
        if process.returncode == 0:
            return parse_nmap_xml(stdout.decode('utf-8', errors='ignore'))

        # 如果完整扫描失败（通常是权限问题），降级到基础扫描
        print(f"完整nmap扫描失败（可能需要root权限），降级到基础扫描: {stderr.decode('utf-8', errors='ignore')}")

        # 基础扫描（不需要root权限，速度更快）
        cmd_basic = [
            'nmap',
            '-sV',                  # 服务版本检测
            '-T4',                  # 最快速度
            '--min-rate', '300',    # 最小发包速率
            '--max-retries', '1',   # 最多重试1次
            '--host-timeout', '180s', # 主机超时3分钟
            '-p', f'{start_port}-{end_port}',
            '-oX', '-',             # 输出XML到stdout
            ip
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd_basic,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode('utf-8', errors='ignore')
            raise RuntimeError(f"nmap基础扫描也失败，返回码: {process.returncode}, 错误: {error_msg}")

        # 解析XML输出
        result = parse_nmap_xml(stdout.decode('utf-8', errors='ignore'))

        # 标记这是基础扫描，OS信息不可用
        if not result.get('os_type'):
            result['os_type'] = 'Unknown (需要root权限进行OS检测)'

        return result

    except Exception as e:
        raise RuntimeError(f"Nmap扫描失败: {e}")


def parse_nmap_xml(xml_output: str) -> Dict:
    """
    解析nmap的XML输出

    Args:
        xml_output: nmap的XML输出

    Returns:
        Dict: 解析后的主机信息
    """
    try:
        root = ET.fromstring(xml_output)

        result = {
            'ip': '',
            'hostname': None,
            'mac_address': None,
            'os_type': None,
            'open_ports': [],
            'total_ports': 0,
            'scan_time': datetime.now().isoformat(),
            'services': {}  # 端口对应的服务信息
        }

        # 查找host节点
        host = root.find('host')
        if host is None:
            return result

        # 获取IP地址
        addr = host.find("address[@addrtype='ipv4']")
        if addr is not None:
            result['ip'] = addr.get('addr', '')

        # 获取MAC地址
        mac = host.find("address[@addrtype='mac']")
        if mac is not None:
            result['mac_address'] = mac.get('addr', '').upper()
            vendor = mac.get('vendor')
            if vendor:
                result['mac_vendor'] = vendor

        # 获取主机名
        hostnames = host.find('hostnames')
        if hostnames is not None:
            hostname = hostnames.find('hostname')
            if hostname is not None:
                result['hostname'] = hostname.get('name')

        # 获取OS信息
        os_elem = host.find('os')
        if os_elem is not None:
            osmatch = os_elem.find('osmatch')
            if osmatch is not None:
                os_name = osmatch.get('name')
                os_accuracy = osmatch.get('accuracy', '0')
                result['os_type'] = f"{os_name} ({os_accuracy}% 准确度)"
                result['os_accuracy'] = int(os_accuracy)

        # 获取端口信息
        ports = host.find('ports')
        if ports is not None:
            for port in ports.findall('port'):
                state = port.find('state')
                if state is not None and state.get('state') == 'open':
                    port_id = int(port.get('portid'))
                    result['open_ports'].append(port_id)

                    # 获取服务信息
                    service = port.find('service')
                    if service is not None:
                        service_name = service.get('name', 'unknown')
                        service_version = service.get('version', '')
                        service_product = service.get('product', '')

                        service_info = service_name
                        if service_product:
                            service_info = service_product
                            if service_version:
                                service_info += f' {service_version}'

                        result['services'][port_id] = service_info

        result['open_ports'].sort()
        result['total_ports'] = len(result['open_ports'])

        return result

    except Exception as e:
        print(f"解析nmap XML失败: {e}")
        return {
            'ip': '',
            'hostname': None,
            'mac_address': None,
            'os_type': None,
            'open_ports': [],
            'total_ports': 0,
            'scan_time': datetime.now().isoformat()
        }


async def ping_ip_with_nmap(ip: str) -> bool:
    """
    使用ping命令快速检测主机存活

    Args:
        ip: IP地址

    Returns:
        bool: 主机是否在线
    """
    # 直接使用ping检测
    return await check_ip_alive(ip, timeout=1)


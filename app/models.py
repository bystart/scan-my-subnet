from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
import ipaddress


class NetworkSegment(BaseModel):
    """网段模型"""
    id: str
    name: str
    cidr: str  # 例如: 192.168.1.0/24
    description: Optional[str] = ""
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    @validator('cidr')
    def validate_cidr(cls, v):
        # 去除前后空格
        v = v.strip()

        try:
            # 验证 CIDR 格式
            ipaddress.ip_network(v, strict=False)
        except ValueError as e:
            raise ValueError(f'无效的CIDR格式: {v}。请使用类似 192.168.1.0/24 的格式')

        return v


class IPStatus(BaseModel):
    """IP状态模型"""
    ip: str
    is_active: bool
    last_checked: str
    hostname: Optional[str] = None
    open_ports: Optional[List[int]] = []  # 开放的端口列表
    ports_scanned: bool = False  # 是否已扫描端口


class NetworkSegmentWithIPs(BaseModel):
    """带IP列表的网段模型"""
    segment: NetworkSegment
    ips: List[IPStatus]
    total_ips: int
    active_ips: int
    inactive_ips: int


class ScanRequest(BaseModel):
    """扫描请求模型"""
    segment_id: str


class PortScanRequest(BaseModel):
    """端口扫描请求模型"""
    start_port: int = Field(ge=1, le=65535, description="起始端口")
    end_port: int = Field(ge=1, le=65535, description="结束端口")

    @validator('end_port')
    def validate_port_range(cls, v, values):
        if 'start_port' in values and v < values['start_port']:
            raise ValueError('结束端口必须大于等于起始端口')
        return v

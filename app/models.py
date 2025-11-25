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
        try:
            ipaddress.ip_network(v, strict=False)
        except ValueError:
            raise ValueError(f'Invalid CIDR notation: {v}')
        return v


class IPStatus(BaseModel):
    """IP状态模型"""
    ip: str
    is_active: bool
    last_checked: str
    hostname: Optional[str] = None


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

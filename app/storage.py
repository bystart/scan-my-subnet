import json
import os
from typing import List, Dict, Optional
from pathlib import Path
import aiofiles
from app.models import NetworkSegment, IPStatus


class JSONStorage:
    """JSON文件存储管理"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.networks_file = self.data_dir / "networks.json"
        self.ip_status_file = self.data_dir / "ip_status.json"
        self._ensure_files()

    def _ensure_files(self):
        """确保数据文件存在"""
        if not self.networks_file.exists():
            self.networks_file.write_text(json.dumps([], indent=2, ensure_ascii=False))
        if not self.ip_status_file.exists():
            self.ip_status_file.write_text(json.dumps({}, indent=2, ensure_ascii=False))

    async def load_networks(self) -> List[NetworkSegment]:
        """加载所有网段"""
        async with aiofiles.open(self.networks_file, 'r', encoding='utf-8') as f:
            content = await f.read()
            data = json.loads(content)
            return [NetworkSegment(**item) for item in data]

    async def save_networks(self, networks: List[NetworkSegment]):
        """保存网段列表"""
        data = [network.model_dump() for network in networks]
        async with aiofiles.open(self.networks_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data, indent=2, ensure_ascii=False))

    async def load_ip_status(self) -> Dict[str, List[Dict]]:
        """加载IP状态数据"""
        async with aiofiles.open(self.ip_status_file, 'r', encoding='utf-8') as f:
            content = await f.read()
            return json.loads(content)

    async def save_ip_status(self, ip_status: Dict[str, List[Dict]]):
        """保存IP状态数据"""
        async with aiofiles.open(self.ip_status_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(ip_status, indent=2, ensure_ascii=False))

    async def get_segment_ips(self, segment_id: str) -> List[IPStatus]:
        """获取指定网段的IP状态"""
        all_status = await self.load_ip_status()
        if segment_id not in all_status:
            return []
        return [IPStatus(**ip) for ip in all_status[segment_id]]

    async def update_segment_ips(self, segment_id: str, ips: List[IPStatus]):
        """更新指定网段的IP状态"""
        all_status = await self.load_ip_status()
        all_status[segment_id] = [ip.model_dump() for ip in ips]
        await self.save_ip_status(all_status)

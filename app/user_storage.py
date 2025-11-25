import json
from pathlib import Path
import aiofiles
from typing import Optional
from app.auth import User, get_password_hash, verify_password


class UserStorage:
    """用户数据存储"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.users_file = self.data_dir / "users.json"
        self._ensure_default_user()

    def _ensure_default_user(self):
        """确保默认用户存在"""
        if not self.users_file.exists():
            # 创建默认admin用户
            default_user = {
                "username": "admin",
                "hashed_password": get_password_hash("admin")
            }
            self.users_file.write_text(
                json.dumps([default_user], indent=2, ensure_ascii=False)
            )

    async def get_user(self, username: str) -> Optional[User]:
        """获取用户"""
        async with aiofiles.open(self.users_file, 'r', encoding='utf-8') as f:
            content = await f.read()
            users = json.loads(content)
            for user_data in users:
                if user_data['username'] == username:
                    return User(**user_data)
        return None

    async def update_password(self, username: str, new_password: str) -> bool:
        """更新用户密码"""
        async with aiofiles.open(self.users_file, 'r', encoding='utf-8') as f:
            content = await f.read()
            users = json.loads(content)

        updated = False
        for user in users:
            if user['username'] == username:
                user['hashed_password'] = get_password_hash(new_password)
                updated = True
                break

        if updated:
            async with aiofiles.open(self.users_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(users, indent=2, ensure_ascii=False))

        return updated

    async def verify_user(self, username: str, password: str) -> bool:
        """验证用户密码"""
        user = await self.get_user(username)
        if not user:
            return False
        return verify_password(password, user.hashed_password)

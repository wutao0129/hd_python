from functools import wraps
from typing import List
from fastapi import HTTPException, Header
from sqlalchemy.orm import Session


def check_permission(required_roles: List[str] = None):
    """
    权限鉴权装饰器

    Args:
        required_roles: 允许访问的角色列表，如 ["admin", "hr"]
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从请求头获取用户信息（简化实现）
            user_role = kwargs.get("x_user_role", "employee")

            if required_roles and user_role not in required_roles:
                raise HTTPException(status_code=403, detail="无权限访问")

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def get_current_user(x_user_id: str = Header(None), x_user_role: str = Header(None)):
    """
    获取当前用户信息（从请求头）

    Returns:
        dict: 用户信息 {"id": int, "role": str}
    """
    return {
        "id": int(x_user_id) if x_user_id else None,
        "role": x_user_role or "employee"
    }

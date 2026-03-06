"""
菜单 API 路由
Updated: 2026-03-04
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Dict, Any
from database import get_db
from models import Menu, MenuI18n, MenuPermission
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["menus"])


# Pydantic 模型
class MenuCreate(BaseModel):
    menu_name: str
    parent_id: int | None = None
    menu_type: str = "menu"
    route_path: str | None = None
    icon: str | None = None
    is_enabled: bool = True


class MenuUpdate(BaseModel):
    menu_name: str | None = None
    parent_id: int | None = None
    menu_type: str | None = None
    route_path: str | None = None
    icon: str | None = None
    is_enabled: bool | None = None


class MenuI18nUpdate(BaseModel):
    translations: Dict[str, str]


class MenuPermissionSave(BaseModel):
    role_id: int
    menu_ids: List[int]


# 辅助函数
def build_menu_tree(menus: List[Menu], parent_id: int | None = None, lang: str = "zh-CN") -> List[Dict]:
    """构建菜单树"""
    result = []
    for menu in menus:
        if menu.parent_id == parent_id:
            # 获取多语言名称
            menu_name = menu.menu_name

            menu_dict = {
                "id": menu.id,
                "parent_id": menu.parent_id,
                "menu_type": menu.menu_type,
                "menu_name": menu_name,
                "icon": menu.icon,
                "route_path": menu.route_path,
                "sort_order": menu.sort_order,
                "is_enabled": menu.is_enabled,
                "children": build_menu_tree(menus, menu.id, lang)
            }
            result.append(menu_dict)

    return sorted(result, key=lambda x: x["sort_order"])


# API 端点
@router.get("/menus")
def get_user_menus(
    lang: str = Query(default="zh-CN"),
    db: Session = Depends(get_db)
):
    """获取用户菜单（简化版，返回所有启用的菜单）"""
    menus = db.query(Menu).filter(Menu.is_enabled == True).all()
    menu_tree = build_menu_tree(menus, None, lang)

    # 转换为前端期望的格式（完全按照静态菜单格式）
    def transform_menu(menu_dict):
        transformed = {
            "title": menu_dict["menu_name"],
        }

        # 添加图标
        if menu_dict["icon"]:
            transformed["icon"] = {"icon": menu_dict["icon"]}

        # 递归处理子菜单
        children = menu_dict.get("children")
        if children and len(children) > 0:
            # 有子菜单时，只添加 children，不添加 to
            transformed["children"] = [transform_menu(child) for child in children]
        else:
            # 只有在没有子菜单时才添加路由
            route_path = menu_dict.get("route_path")
            if route_path:
                # 特殊处理：/pages/misc/not-found 需要 error 参数
                if route_path == "/pages/misc/not-found":
                    transformed["to"] = "/pages/misc/not-found/404"
                # 特殊处理：/pages/misc/not-authorized 需要 error 参数
                elif route_path == "/pages/misc/not-authorized":
                    transformed["to"] = "/pages/misc/not-authorized/401"
                # 如果是以 / 开头的其他路径(外部链接或绝对路径),直接使用
                elif route_path.startswith("/"):
                    transformed["to"] = route_path
                # 如果路由名以 -id 结尾，转换为对象格式并提供默认参数
                elif route_path.endswith("-id"):
                    transformed["to"] = {
                        "name": route_path,
                        "params": {"id": "1"}
                    }
                # 如果路由名以 -tab 结尾，转换为对象格式并提供默认参数
                elif route_path.endswith("-tab"):
                    transformed["to"] = {
                        "name": route_path,
                        "params": {"tab": "profile"}
                    }
                else:
                    transformed["to"] = route_path

        return transformed

    # 过滤掉 heading 类型的菜单
    filtered_menus = [menu for menu in menu_tree if menu["menu_type"] != "heading"]
    transformed_menus = [transform_menu(menu) for menu in filtered_menus]

    return {
        "code": 0,
        "data": transformed_menus,
        "message": "success"
    }


@router.get("/admin/menus")
def get_all_menus(db: Session = Depends(get_db)):
    """获取所有菜单（管理员）"""
    menus = db.query(Menu).all()
    return {"code": 200, "data": build_menu_tree(menus)}


@router.post("/admin/menus")
def create_menu(menu_data: MenuCreate, db: Session = Depends(get_db)):
    """创建菜单"""
    # 计算排序顺序
    max_sort = db.query(Menu).filter(Menu.parent_id == menu_data.parent_id).count()

    menu = Menu(
        menu_name=menu_data.menu_name,
        parent_id=menu_data.parent_id,
        menu_type=menu_data.menu_type,
        route_path=menu_data.route_path,
        icon=menu_data.icon,
        is_enabled=menu_data.is_enabled,
        sort_order=max_sort
    )
    db.add(menu)
    db.commit()
    db.refresh(menu)

    return {
        "code": 0,
        "data": {
            "id": menu.id,
            "menu_name": menu.menu_name,
            "parent_id": menu.parent_id,
            "menu_type": menu.menu_type,
            "route_path": menu.route_path,
            "icon": menu.icon,
            "is_enabled": menu.is_enabled,
            "sort_order": menu.sort_order
        }
    }


@router.put("/admin/menus/{menu_id}")
def update_menu(menu_id: int, menu_data: MenuUpdate, db: Session = Depends(get_db)):
    """更新菜单"""
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="菜单不存在")

    if menu_data.menu_name is not None:
        menu.menu_name = menu_data.menu_name
    if menu_data.parent_id is not None:
        menu.parent_id = menu_data.parent_id
    if menu_data.menu_type is not None:
        menu.menu_type = menu_data.menu_type
    if menu_data.route_path is not None:
        menu.route_path = menu_data.route_path
    if menu_data.icon is not None:
        menu.icon = menu_data.icon
    if menu_data.is_enabled is not None:
        menu.is_enabled = menu_data.is_enabled

    db.commit()
    db.refresh(menu)

    return {"code": 0, "message": "更新成功"}


@router.delete("/admin/menus/{menu_id}")
def delete_menu(menu_id: int, db: Session = Depends(get_db)):
    """删除菜单"""
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="菜单不存在")

    # 检查是否有子菜单
    children_count = db.query(Menu).filter(Menu.parent_id == menu_id).count()
    if children_count > 0:
        raise HTTPException(status_code=400, detail="该菜单下有子菜单，无法删除")

    db.delete(menu)
    db.commit()

    return {"code": 0, "message": "删除成功"}


@router.get("/admin/menu-i18n/{menu_id}")
def get_menu_i18n(menu_id: int, db: Session = Depends(get_db)):
    """获取菜单多语言配置"""
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="菜单不存在")

    i18n_records = db.query(MenuI18n).filter(MenuI18n.menu_id == menu_id).all()
    translations = {record.language_code: record.menu_name for record in i18n_records}

    return {
        "code": 0,
        "data": {
            "menu_id": menu_id,
            "translations": translations
        }
    }


@router.put("/admin/menu-i18n/{menu_id}")
def update_menu_i18n(menu_id: int, data: MenuI18nUpdate, db: Session = Depends(get_db)):
    """更新菜单多语言配置"""
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="菜单不存在")

    # 删除现有的多语言记录
    db.query(MenuI18n).filter(MenuI18n.menu_id == menu_id).delete()

    # 添加新的多语言记录
    for lang_code, menu_name in data.translations.items():
        i18n = MenuI18n(
            menu_id=menu_id,
            language_code=lang_code,
            menu_name=menu_name
        )
        db.add(i18n)

    db.commit()

    return {"code": 0, "message": "更新成功"}


@router.get("/admin/menu-permissions/{role_id}")
def get_role_menu_permissions(role_id: int, db: Session = Depends(get_db)):
    """获取角色的菜单权限"""
    permissions = db.query(MenuPermission).filter(MenuPermission.role_id == role_id).all()
    menu_ids = [p.menu_id for p in permissions]

    return {
        "code": 200,
        "data": {"menu_ids": menu_ids}
    }


@router.post("/admin/menu-permissions")
def save_role_menu_permissions(data: MenuPermissionSave, db: Session = Depends(get_db)):
    """保存角色的菜单权限"""
    # 删除该角色的所有现有权限
    db.query(MenuPermission).filter(MenuPermission.role_id == data.role_id).delete()

    # 添加新的权限
    for menu_id in data.menu_ids:
        permission = MenuPermission(role_id=data.role_id, menu_id=menu_id)
        db.add(permission)

    db.commit()

    return {"code": 200, "message": "保存成功"}

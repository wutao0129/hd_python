"""
测试菜单 API
"""
from database import SessionLocal
from models import Menu

db = SessionLocal()

try:
    # 查询所有菜单
    menus = db.query(Menu).all()
    print(f"找到 {len(menus)} 个菜单")

    for menu in menus:
        print(f"- {menu.id}: {menu.menu_name}")

except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

finally:
    db.close()

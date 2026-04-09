import os
import sys
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import engine

def update():
    with engine.connect() as conn:
        print("Creating standalone '工作台' root menu...")
        
        # 1. 创建一个新的单独的顶级"工作台"菜单
        cursor = conn.execute(text("SELECT MAX(id) FROM menus"))
        max_id = cursor.scalar() or 100
        new_workspace_id = max_id + 1
        
        conn.execute(
            text(f"""
            INSERT INTO menus (id, parent_id, menu_type, menu_name, icon, route_path, sort_order, is_enabled)
            VALUES ({new_workspace_id}, NULL, 'menu', '工作台', 'tabler-device-desktop-analytics', NULL, 1, TRUE)
            """)
        )
        print(f"Created new standalone '工作台' root menu with ID {new_workspace_id}")
        
        # 2. 获取刚才我们加进去的仪表盘子菜单并将它们的 parent_id 指向新创建的"工作台"
        cursor = conn.execute(text("SELECT id, menu_name FROM menus WHERE route_path LIKE 'dashboards-%'"))
        dashboards = cursor.fetchall()
        
        for dashboard in dashboards:
            dash_id = dashboard[0]
            dash_name = dashboard[1]
            print(f"Moving '{dash_name}' (ID: {dash_id}) to new '工作台'")
            
            conn.execute(
                text(f"UPDATE menus SET parent_id = {new_workspace_id} WHERE id = {dash_id}")
            )
            
        conn.commit()
        print("Done!")

if __name__ == "__main__":
    update()

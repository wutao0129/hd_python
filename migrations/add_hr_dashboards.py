import os
import sys
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import engine

def add_dashboards():
    with engine.connect() as conn:
        dashboard_root_id = 10847
        print(f"Using '工作台' root menu with ID {dashboard_root_id}")
        
        # 获取现有的最大ID
        cursor = conn.execute(text("SELECT MAX(id) FROM menus"))
        max_id = cursor.scalar() or 100
        
        # 定义新的菜单 - 所有都放在"工作台"下面
        new_menus = [
            {"name": "员工自助 (ESS)", "route": "dashboards-hr-ess", "icon": "tabler-user", "sort": 3},
            {"name": "主管自助 (MSS)", "route": "dashboards-hr-mss", "icon": "tabler-users-group", "sort": 4},
            {"name": "HRBP 工作台", "route": "dashboards-hr-bu-bp", "icon": "tabler-briefcase", "sort": 5},
            {"name": "出勤雷达", "route": "dashboards-wfm-attendance-radar", "icon": "tabler-clock", "sort": 6},
            {"name": "薪酬看板", "route": "dashboards-compensation", "icon": "tabler-currency-dollar", "sort": 7},
        ]
        
        for i, menu in enumerate(new_menus):
            # 检查菜单是否已存在
            cursor = conn.execute(text(f"SELECT id FROM menus WHERE route_path = '{menu['route']}'"))
            existing_id = cursor.scalar()
            
            if existing_id:
                print(f"Menu '{menu['name']}' already exists with ID {existing_id}, updating parent.")
                conn.execute(text(f"UPDATE menus SET parent_id = {dashboard_root_id} WHERE id = {existing_id}"))
                continue
                
            menu_id = max_id + i + 1
            
            # 插入菜单记录
            conn.execute(
                text(f"""
                INSERT INTO menus (id, parent_id, menu_type, menu_name, icon, route_path, sort_order, is_enabled)
                VALUES ({menu_id}, {dashboard_root_id}, 'page', '{menu["name"]}', '{menu["icon"]}', '{menu["route"]}', {menu["sort"]}, TRUE)
                """)
            )
            
            print(f"Added menu: {menu['name']}")
            
        conn.commit()
        print("Successfully added new HR dashboards menus to database.")

if __name__ == "__main__":
    add_dashboards()

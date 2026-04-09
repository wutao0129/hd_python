import os
import sys
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import engine

def update():
    with engine.connect() as conn:
        # 获取我们刚才创建的'系统配置'顶级菜单的ID
        cursor = conn.execute(text("SELECT id FROM menus WHERE menu_name = '系统配置'"))
        sys_config_id = cursor.scalar()
        
        if not sys_config_id:
            print("Creating '系统配置' root menu...")
            cursor = conn.execute(text("SELECT MAX(id) FROM menus"))
            max_id = cursor.scalar() or 100
            sys_config_id = max_id + 1
            
            conn.execute(
                text(f"""
                INSERT INTO menus (id, parent_id, menu_type, menu_name, icon, route_path, sort_order, is_enabled)
                VALUES ({sys_config_id}, NULL, 'menu', '系统配置', 'tabler-settings', NULL, 99, TRUE)
                """)
            )
            print(f"Created '系统配置' with ID {sys_config_id}")
        else:
            print(f"Found '系统配置' with ID {sys_config_id}")
        
        # 查找已存在的菜单管理配置 (10806)
        cursor = conn.execute(text("SELECT id, parent_id FROM menus WHERE route_path = 'apps-menu-config' LIMIT 1"))
        menu_config = cursor.fetchone()
        
        if menu_config:
            menu_config_id = menu_config[0]
            old_parent_id = menu_config[1]
            
            print(f"Moving '菜单管理' (ID: {menu_config_id}) from parent {old_parent_id} to {sys_config_id}")
            
            conn.execute(
                text(f"""
                UPDATE menus 
                SET parent_id = {sys_config_id}, is_enabled = TRUE, sort_order = 1, icon = 'tabler-list-details', menu_name = '菜单配置'
                WHERE id = {menu_config_id}
                """)
            )
            print("Successfully updated menu config route.")
        else:
            print("Creating '菜单配置' under '系统配置'")
            cursor = conn.execute(text("SELECT MAX(id) FROM menus"))
            max_id = cursor.scalar() or 100
            menu_config_id = max_id + 1
            
            conn.execute(
                text(f"""
                INSERT INTO menus (id, parent_id, menu_type, menu_name, icon, route_path, sort_order, is_enabled)
                VALUES ({menu_config_id}, {sys_config_id}, 'page', '菜单配置', 'tabler-list-details', 'apps-menu-config', 1, TRUE)
                """)
            )
            print("Successfully created menu config route.")
            
        conn.commit()
        print("Done!")

if __name__ == "__main__":
    update()

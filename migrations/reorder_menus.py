import os
import sys
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import engine

def update():
    with engine.connect() as conn:
        print("Finding menus...")
        
        # 查找刚才创建的'系统配置'
        cursor = conn.execute(text("SELECT id, sort_order FROM menus WHERE menu_name = '系统配置' AND (menu_type = 'menu' OR parent_id IS NULL) LIMIT 1"))
        sys_config = cursor.fetchone()
        
        if sys_config:
            sys_config_id = sys_config[0]
            sys_config_sort = sys_config[1]
            print(f"Found '系统配置' ID: {sys_config_id}, sort_order: {sys_config_sort}")
            
            # 将'系统配置'下的菜单管理移出来，放到工作台下
            cursor = conn.execute(text(f"SELECT id FROM menus WHERE parent_id = {sys_config_id} AND route_path = 'apps-menu-config'"))
            menu_config_id = cursor.scalar()
            
            if menu_config_id:
                print(f"Moving '菜单配置' (ID: {menu_config_id}) out of '系统配置'")
            
            # 找到我们刚才创建的'工作台'顶级菜单
            cursor = conn.execute(text("SELECT id FROM menus WHERE menu_name = '工作台' AND (menu_type = 'menu' OR parent_id IS NULL) AND id > 10847 LIMIT 1"))
            workspace_id = cursor.scalar()
            
            if workspace_id:
                # 把工作台的排序设为原来'系统配置'的排序
                conn.execute(text(f"UPDATE menus SET sort_order = 99 WHERE id = {workspace_id}"))
                print(f"Updated '工作台' (ID: {workspace_id}) sort order to 99")
                
                # 把菜单配置放到工作台下
                if menu_config_id:
                    conn.execute(text(f"UPDATE menus SET parent_id = {workspace_id}, sort_order = 99 WHERE id = {menu_config_id}"))
                    print(f"Moved '菜单配置' to '工作台'")
            else:
                print("Could not find the standalone '工作台' menu!")
            
            # 删除'系统配置'
            conn.execute(text(f"DELETE FROM menus WHERE id = {sys_config_id}"))
            print(f"Deleted '系统配置'")
                
        else:
            print("Could not find '系统配置' menu!")
            
        conn.commit()
        print("Done!")

if __name__ == "__main__":
    update()

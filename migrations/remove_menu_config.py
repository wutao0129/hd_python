"""
删除菜单配置菜单项
"""
import pymysql

DB_CONFIG = {
    'host': '192.168.110.162',
    'port': 9896,
    'user': 'root',
    'password': 'myDHR2023.COM',
    'database': 'mydhr',
    'charset': 'utf8mb4'
}

connection = pymysql.connect(**DB_CONFIG)

try:
    with connection.cursor() as cursor:
        # 查找菜单配置菜单项
        cursor.execute("SELECT id, menu_name FROM menus WHERE menu_name = '菜单配置' OR route_path = 'apps-menu-config'")
        result = cursor.fetchone()

        if result:
            menu_id = result[0]
            print(f"找到菜单: ID={menu_id}, 名称={result[1]}")

            # 删除菜单（会级联删除相关的 i18n 和 permissions）
            cursor.execute("DELETE FROM menus WHERE id = %s", (menu_id,))
            connection.commit()
            print(f"✓ 已删除菜单配置菜单项")
        else:
            print("未找到菜单配置菜单项")

except Exception as e:
    connection.rollback()
    print(f"错误: {e}")

finally:
    connection.close()

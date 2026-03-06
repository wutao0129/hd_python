#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
菜单数据修复脚本
功能：修复现有菜单数据，确保非末级菜单没有路由信息
作者：Claude
创建时间：2026-03-04
"""

import pymysql
from typing import Dict, Any

# ============================================
# 数据库配置
# ============================================
DB_CONFIG = {
    'host': '192.168.110.162',
    'port': 9896,
    'user': 'root',
    'password': 'myDHR2023.COM',
    'database': 'mydhr',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}


def connect_db(config: Dict[str, Any]):
    """连接数据库"""
    try:
        connection = pymysql.connect(**config)
        print("[OK] 数据库连接成功")
        return connection
    except Exception as e:
        print(f"[ERROR] 数据库连接失败: {e}")
        raise


def fix_parent_menu_routes(connection):
    """
    修复父级菜单的路由信息和类型
    规则：
    1. 如果菜单有子菜单，则清空 route_path，设置 menu_type='menu'
    2. 如果菜单没有子菜单，设置 menu_type='page'
    """
    cursor = connection.cursor()

    try:
        print("\n[INFO] 开始修复菜单数据...")

        # 1. 修复父级菜单（有子菜单的）
        print("\n[INFO] 修复父级菜单...")
        sql_find_parents = """
            SELECT DISTINCT parent_id
            FROM menus
            WHERE parent_id IS NOT NULL
        """
        cursor.execute(sql_find_parents)
        parent_ids = [row['parent_id'] for row in cursor.fetchall()]

        if parent_ids:
            print(f"[INFO] 找到 {len(parent_ids)} 个父级菜单")

            # 更新父级菜单：清空路由，设置类型为 'menu'
            sql_update_parents = """
                UPDATE menus
                SET route_path = NULL,
                    menu_type = 'menu'
                WHERE id IN ({})
            """.format(','.join(['%s'] * len(parent_ids)))

            cursor.execute(sql_update_parents, parent_ids)
            parent_affected = cursor.rowcount
            print(f"[OK] 已修复 {parent_affected} 个父级菜单（类型=menu，路由=NULL）")
        else:
            print("[OK] 没有需要修复的父级菜单")
            parent_affected = 0

        # 2. 修复末级菜单（没有子菜单的）
        print("\n[INFO] 修复末级菜单...")

        # 先查询出所有末级菜单的ID
        sql_find_leaves = """
            SELECT m1.id
            FROM menus m1
            LEFT JOIN menus m2 ON m1.id = m2.parent_id
            WHERE m2.id IS NULL
            AND m1.menu_type != 'page'
        """
        cursor.execute(sql_find_leaves)
        leaf_ids = [row['id'] for row in cursor.fetchall()]

        if leaf_ids:
            # 更新末级菜单类型
            sql_update_leaves = """
                UPDATE menus
                SET menu_type = 'page'
                WHERE id IN ({})
            """.format(','.join(['%s'] * len(leaf_ids)))

            cursor.execute(sql_update_leaves, leaf_ids)
            leaf_affected = cursor.rowcount
            print(f"[OK] 已修复 {leaf_affected} 个末级菜单（类型=page）")
        else:
            print("[OK] 没有需要修复的末级菜单")
            leaf_affected = 0

        connection.commit()
        print(f"\n[OK] 总共修复 {parent_affected + leaf_affected} 个菜单")

        return parent_affected + leaf_affected

    except Exception as e:
        connection.rollback()
        print(f"[ERROR] 修复失败: {e}")
        raise
    finally:
        cursor.close()


def verify_menu_structure(connection):
    """验证菜单结构"""
    cursor = connection.cursor()

    try:
        print("\n" + "="*50)
        print("[INFO] 菜单结构验证")
        print("="*50)

        # 统计总数
        cursor.execute("SELECT COUNT(*) as count FROM menus")
        total = cursor.fetchone()['count']
        print(f"菜单总数: {total}")

        # 统计父级菜单（有子菜单的）
        cursor.execute("""
            SELECT COUNT(DISTINCT parent_id) as count
            FROM menus
            WHERE parent_id IS NOT NULL
        """)
        parent_count = cursor.fetchone()['count']
        print(f"父级菜单数: {parent_count}")

        # 检查父级菜单中还有路由的
        cursor.execute("""
            SELECT m1.id, m1.menu_name, m1.route_path
            FROM menus m1
            WHERE m1.id IN (
                SELECT DISTINCT parent_id
                FROM menus
                WHERE parent_id IS NOT NULL
            )
            AND m1.route_path IS NOT NULL
        """)
        invalid_parents = cursor.fetchall()

        if invalid_parents:
            print(f"\n[WARN] 发现 {len(invalid_parents)} 个父级菜单仍有路由:")
            for menu in invalid_parents:
                print(f"  - [{menu['id']}] {menu['menu_name']}: {menu['route_path']}")
        else:
            print("\n[OK] 所有父级菜单都没有路由信息")

        # 显示菜单树结构（前20条）
        print("\n菜单树结构（前20条）:")
        cursor.execute("""
            SELECT id, parent_id, menu_type, menu_name, route_path, sort_order
            FROM menus
            ORDER BY COALESCE(parent_id, 0), sort_order
            LIMIT 20
        """)

        for row in cursor.fetchall():
            indent = "  " if row['parent_id'] else ""
            parent = f"(父:{row['parent_id']})" if row['parent_id'] else "(顶级)"
            route = row['route_path'] if row['route_path'] else "(无路由)"
            print(f"{indent}[{row['id']}] {row['menu_name']} {parent} - {route}")

        print("="*50 + "\n")

    finally:
        cursor.close()


def main():
    """主执行流程"""
    print("="*50)
    print("菜单数据修复脚本")
    print("="*50)

    connection = None

    try:
        # 连接数据库
        connection = connect_db(DB_CONFIG)

        # 修复父级菜单路由
        fix_parent_menu_routes(connection)

        # 验证修复结果
        verify_menu_structure(connection)

        print("[OK] 菜单数据修复完成！\n")

    except Exception as e:
        print(f"[ERROR] 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if connection:
            connection.close()
            print("[OK] 数据库连接已关闭")


if __name__ == "__main__":
    main()

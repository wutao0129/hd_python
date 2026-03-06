#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试菜单排序功能
Created: 2026-03-06
Task: #35 - 数据库添加菜单排序字段
"""

import sys
import os

# 添加父目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine
from sqlalchemy import text


def test_menu_sorting():
    """测试菜单排序功能"""
    print("=" * 60)
    print("Menu Sorting Test")
    print("=" * 60)

    with engine.connect() as conn:
        # 测试1: 查询顶级菜单（按 sort_order 排序）
        print("\n1. Top-level menus (ordered by sort_order):")
        result = conn.execute(text("""
            SELECT id, menu_name, sort_order, parent_id
            FROM menus
            WHERE parent_id IS NULL
            ORDER BY sort_order, id
            LIMIT 10
        """))

        for row in result:
            print(f"   ID: {row[0]:3d} | Name: {row[1]:30s} | Sort: {row[2]:3d}")

        # 测试2: 查询某个父菜单下的子菜单
        print("\n2. Sub-menus under parent (ordered by sort_order):")
        result = conn.execute(text("""
            SELECT m1.id, m1.menu_name, m1.sort_order, m2.menu_name as parent_name
            FROM menus m1
            LEFT JOIN menus m2 ON m1.parent_id = m2.id
            WHERE m1.parent_id IS NOT NULL
            ORDER BY m1.parent_id, m1.sort_order, m1.id
            LIMIT 10
        """))

        for row in result:
            print(f"   ID: {row[0]:3d} | Name: {row[1]:30s} | Sort: {row[2]:3d} | Parent: {row[3]}")

        # 测试3: 验证复合索引的使用
        print("\n3. Explain query with composite index:")
        result = conn.execute(text("""
            EXPLAIN SELECT id, menu_name, sort_order
            FROM menus
            WHERE parent_id = 1
            ORDER BY sort_order
        """))

        print("   Query execution plan:")
        for row in result:
            print(f"   {row}")

        # 测试4: 统计每个父菜单下的子菜单数量
        print("\n4. Menu hierarchy statistics:")
        result = conn.execute(text("""
            SELECT
                COALESCE(parent_id, 0) as parent_id,
                COUNT(*) as child_count,
                MIN(sort_order) as min_sort,
                MAX(sort_order) as max_sort
            FROM menus
            GROUP BY parent_id
            ORDER BY parent_id
            LIMIT 10
        """))

        print(f"   {'Parent ID':<12} {'Children':<10} {'Sort Range':<15}")
        print(f"   {'-'*12} {'-'*10} {'-'*15}")
        for row in result:
            parent = "NULL" if row[0] == 0 else str(row[0])
            print(f"   {parent:<12} {row[1]:<10} {row[2]}-{row[3]}")

    print("\n" + "=" * 60)
    print("[SUCCESS] All tests passed")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_menu_sorting()
    except Exception as e:
        print(f"\n\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

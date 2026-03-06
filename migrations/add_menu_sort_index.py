#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加菜单排序复合索引
Created: 2026-03-06
Task: #35 - 数据库添加菜单排序字段
"""

import sys
import os

# 添加父目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine
from sqlalchemy import text, inspect


def check_index_exists(index_name: str) -> bool:
    """检查索引是否存在"""
    inspector = inspect(engine)
    indexes = inspector.get_indexes('menus')
    return any(idx['name'] == index_name for idx in indexes)


def add_composite_index():
    """添加复合索引"""
    print("=" * 60)
    print("Menu Sort Composite Index Migration")
    print("=" * 60)

    # 检查 sort_order 字段是否存在
    print("\n1. Checking sort_order field...")
    inspector = inspect(engine)
    columns = inspector.get_columns('menus')
    column_names = [col['name'] for col in columns]

    if 'sort_order' not in column_names:
        print("[ERROR] sort_order field does not exist")
        sys.exit(1)

    print("[OK] sort_order field exists")

    # 显示当前字段信息
    for col in columns:
        if col['name'] == 'sort_order':
            print(f"   Type: {col['type']}, Nullable: {col['nullable']}")

    # 检查现有索引
    print("\n2. Checking existing indexes...")
    indexes = inspector.get_indexes('menus')
    print(f"   Current indexes: {len(indexes)}")
    for idx in indexes:
        print(f"   - {idx['name']}: {idx['column_names']}")

    # 检查复合索引是否已存在
    if check_index_exists('idx_parent_sort'):
        print("\n[OK] Composite index idx_parent_sort already exists")
        return

    # 创建复合索引
    print("\n3. Creating composite index idx_parent_sort...")
    try:
        with engine.connect() as conn:
            conn.execute(text(
                "CREATE INDEX idx_parent_sort ON menus(parent_id, sort_order)"
            ))
            conn.commit()
        print("[OK] Composite index created successfully")
    except Exception as e:
        print(f"[ERROR] Failed to create index: {e}")
        sys.exit(1)

    # 验证索引创建
    print("\n4. Verifying index...")
    inspector = inspect(engine)
    indexes = inspector.get_indexes('menus')

    if check_index_exists('idx_parent_sort'):
        print("[OK] Index verification successful")
        print("\nFinal index list:")
        for idx in indexes:
            print(f"   - {idx['name']}: {idx['column_names']}")
    else:
        print("[ERROR] Index verification failed")
        sys.exit(1)

    # 统计菜单数据
    print("\n5. Menu data statistics...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) as count FROM menus"))
        count = result.fetchone()[0]
        print(f"   Total menus: {count}")

        if count > 0:
            result = conn.execute(text(
                "SELECT MIN(sort_order) as min, MAX(sort_order) as max, AVG(sort_order) as avg FROM menus"
            ))
            stats = result.fetchone()
            print(f"   sort_order range: {stats[0]} - {stats[1]}")
            print(f"   sort_order average: {stats[2]:.2f}")

    print("\n" + "=" * 60)
    print("[SUCCESS] Migration completed")
    print("=" * 60)


if __name__ == "__main__":
    try:
        add_composite_index()
    except KeyboardInterrupt:
        print("\n\n[WARNING] Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

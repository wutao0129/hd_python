#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标签库性能测试脚本
测试查询、筛选、搜索的性能
"""

import pymysql
import time

# 数据库连接配置
DB_CONFIG = {
    'host': '139.196.207.85',
    'port': 9896,
    'user': 'root',
    'password': 'myDHR2023.COM',
    'database': 'mydhr',
    'charset': 'utf8mb4'
}


def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)


def test_full_query(cursor):
    """测试全量查询性能"""
    print("\n1. 全量查询测试")
    print("-" * 50)

    start = time.time()
    cursor.execute("SELECT * FROM tags")
    results = cursor.fetchall()
    elapsed = (time.time() - start) * 1000

    print(f"  查询记录数: {len(results)}")
    print(f"  耗时: {elapsed:.2f}ms")

    if elapsed < 100:
        print(f"  ✅ 性能达标 (< 100ms)")
    else:
        print(f"  ⚠️  性能未达标 (期望 < 100ms)")

    return elapsed < 100


def test_category_filter(cursor):
    """测试按分类筛选性能"""
    print("\n2. 按分类筛选测试")
    print("-" * 50)

    categories = ["基础信息", "职业履历", "能力", "素质", "复合标签", "行业"]
    all_passed = True

    for category in categories:
        start = time.time()
        cursor.execute("SELECT * FROM tags WHERE category = %s", (category,))
        results = cursor.fetchall()
        elapsed = (time.time() - start) * 1000

        status = "✅" if elapsed < 50 else "⚠️"
        print(f"  {category}: {len(results)} 条, {elapsed:.2f}ms {status}")

        if elapsed >= 50:
            all_passed = False

    if all_passed:
        print(f"\n  ✅ 所有分类查询性能达标 (< 50ms)")
    else:
        print(f"\n  ⚠️  部分分类查询性能未达标")

    return all_passed


def test_keyword_search(cursor):
    """测试关键词搜索性能"""
    print("\n3. 关键词搜索测试")
    print("-" * 50)

    keywords = ["能力", "经验", "人才", "行业", "技术"]
    all_passed = True

    for keyword in keywords:
        start = time.time()
        cursor.execute(
            "SELECT * FROM tags WHERE name LIKE %s OR description LIKE %s",
            (f"%{keyword}%", f"%{keyword}%")
        )
        results = cursor.fetchall()
        elapsed = (time.time() - start) * 1000

        status = "✅" if elapsed < 100 else "⚠️"
        print(f"  '{keyword}': {len(results)} 条, {elapsed:.2f}ms {status}")

        if elapsed >= 100:
            all_passed = False

    if all_passed:
        print(f"\n  ✅ 所有关键词搜索性能达标 (< 100ms)")
    else:
        print(f"\n  ⚠️  部分关键词搜索性能未达标")

    return all_passed


def test_parent_child_query(cursor):
    """测试父子关系查询性能"""
    print("\n4. 父子关系查询测试")
    print("-" * 50)

    # 查询所有父标签
    start = time.time()
    cursor.execute("SELECT * FROM tags WHERE parent_id IS NULL")
    parents = cursor.fetchall()
    elapsed1 = (time.time() - start) * 1000

    print(f"  父标签查询: {len(parents)} 条, {elapsed1:.2f}ms")

    # 查询所有子标签
    start = time.time()
    cursor.execute("SELECT * FROM tags WHERE parent_id IS NOT NULL")
    children = cursor.fetchall()
    elapsed2 = (time.time() - start) * 1000

    print(f"  子标签查询: {len(children)} 条, {elapsed2:.2f}ms")

    # 查询特定父标签的子标签
    start = time.time()
    cursor.execute("SELECT * FROM tags WHERE parent_id = %s", (35,))  # 互联网的子标签
    children = cursor.fetchall()
    elapsed3 = (time.time() - start) * 1000

    print(f"  指定父标签的子标签: {len(children)} 条, {elapsed3:.2f}ms")

    all_passed = elapsed1 < 50 and elapsed2 < 50 and elapsed3 < 50

    if all_passed:
        print(f"\n  ✅ 父子关系查询性能达标 (< 50ms)")
    else:
        print(f"\n  ⚠️  父子关系查询性能未达标")

    return all_passed


def test_complex_query(cursor):
    """测试复合条件查询性能"""
    print("\n5. 复合条件查询测试")
    print("-" * 50)

    # 测试多条件查询
    start = time.time()
    cursor.execute("""
        SELECT * FROM tags
        WHERE category = %s AND type = %s AND status = %s
    """, ("能力", "内置", "启用"))
    results = cursor.fetchall()
    elapsed = (time.time() - start) * 1000

    print(f"  多条件查询: {len(results)} 条, {elapsed:.2f}ms")

    passed = elapsed < 100

    if passed:
        print(f"  ✅ 复合条件查询性能达标 (< 100ms)")
    else:
        print(f"  ⚠️  复合条件查询性能未达标")

    return passed


def test_index_usage(cursor):
    """测试索引使用情况"""
    print("\n6. 索引使用情况")
    print("-" * 50)

    # 检查索引
    cursor.execute("SHOW INDEX FROM tags")
    indexes = cursor.fetchall()

    print(f"  索引总数: {len(indexes)}")
    print("\n  索引列表:")
    for idx in indexes:
        print(f"    - {idx[2]}: {idx[4]} ({idx[10]})")

    # 使用 EXPLAIN 分析查询
    print("\n  查询计划分析:")

    # 分析分类查询
    cursor.execute("EXPLAIN SELECT * FROM tags WHERE category = '能力'")
    explain = cursor.fetchone()
    print(f"    分类查询: type={explain[3]}, key={explain[5]}, rows={explain[8]}")

    # 分析状态查询
    cursor.execute("EXPLAIN SELECT * FROM tags WHERE status = '启用'")
    explain = cursor.fetchone()
    print(f"    状态查询: type={explain[3]}, key={explain[5]}, rows={explain[8]}")

    return True


def main():
    """主函数"""
    print("=" * 60)
    print("标签库性能测试")
    print("=" * 60)

    connection = None
    cursor = None

    try:
        # 连接数据库
        print("\n正在连接数据库...")
        connection = get_db_connection()
        cursor = connection.cursor()
        print("✅ 数据库连接成功")

        # 执行测试
        results = []
        results.append(("全量查询", test_full_query(cursor)))
        results.append(("分类筛选", test_category_filter(cursor)))
        results.append(("关键词搜索", test_keyword_search(cursor)))
        results.append(("父子关系查询", test_parent_child_query(cursor)))
        results.append(("复合条件查询", test_complex_query(cursor)))
        results.append(("索引使用", test_index_usage(cursor)))

        # 汇总结果
        print("\n" + "=" * 60)
        print("测试结果汇总")
        print("=" * 60)

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for name, result in results:
            status = "✅ 通过" if result else "⚠️  未通过"
            print(f"  {name}: {status}")

        print(f"\n  总计: {passed}/{total} 项通过")

        if passed == total:
            print("\n✅ 所有性能测试通过！")
        else:
            print(f"\n⚠️  {total - passed} 项测试未通过，建议优化")

        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        raise

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            print("\n数据库连接已关闭")


if __name__ == "__main__":
    main()

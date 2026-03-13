#!/usr/bin/env python3
"""执行数据库迁移脚本"""
import pymysql
import sys

# 数据库连接配置
DB_CONFIG = {
    'host': '139.196.207.85',
    'port': 9896,
    'user': 'root',
    'password': 'myDHR2023.COM',
    'database': 'mydhr',
    'charset': 'utf8mb4'
}

# 执行迁移
try:
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 直接执行 SQL（不分割）
    sql = """
    ALTER TABLE tags
    ADD COLUMN similar_tags TEXT NULL COMMENT '相似标签（逗号分隔的标签名称）',
    ADD COLUMN exclusive_tags TEXT NULL COMMENT '互斥标签（逗号分隔的标签名称）'
    """

    print(f"执行迁移...")
    cursor.execute(sql)
    conn.commit()
    print("✓ 迁移成功")

except Exception as e:
    print(f"✗ 迁移失败: {e}")
    sys.exit(1)
finally:
    if 'conn' in locals():
        conn.close()

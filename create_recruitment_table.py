#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""执行招聘需求审批表创建脚本"""

import sys
from pathlib import Path
from sqlalchemy import text

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from database import engine

def execute_sql_file(filepath: str):
    """执行 SQL 文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        sql = f.read()

    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
        print(f"Success: {filepath}")

if __name__ == "__main__":
    sql_file = Path(__file__).parent / "migrations" / "create_recruitment_approvals.sql"

    try:
        print("Starting to execute SQL script...")
        execute_sql_file(str(sql_file))
        print("Table recruitment_approvals created successfully!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

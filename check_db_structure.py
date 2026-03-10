#!/usr/bin/env python3
"""检查招聘模块数据库表结构"""

from sqlalchemy import inspect
from database import engine

def check_table_structure():
    inspector = inspect(engine)

    tables = [
        'recruitment_resumes',
        'recruitment_positions',
        'recruitment_channels',
        'recruitment_interviews',
        'recruitment_offers',
        'recruitment_question_bank',
        'recruitment_job_profiles',
        'recruitment_approvals'
    ]

    for table_name in tables:
        print(f"\n{'='*80}")
        print(f"表名: {table_name}")
        print('='*80)

        try:
            columns = inspector.get_columns(table_name)
            for col in columns:
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                default = f" DEFAULT {col['default']}" if col.get('default') else ""
                print(f"  {col['name']:30} {str(col['type']):20} {nullable:10}{default}")
        except Exception as e:
            print(f"  错误: {e}")

if __name__ == "__main__":
    check_table_structure()

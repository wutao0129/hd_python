"""
执行 tag_records 表迁移
Issue #83: 数据库设计与迁移
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, Base
from models import TagRecord

def run_migration():
    """创建 tag_records 表"""
    print("开始创建 tag_records 表...")
    TagRecord.__table__.create(engine, checkfirst=True)
    print("✅ tag_records 表创建成功")

    # 验证表结构
    from sqlalchemy import inspect
    inspector = inspect(engine)

    columns = inspector.get_columns('tag_records')
    print(f"\n表字段数: {len(columns)}")
    for col in columns:
        print(f"  - {col['name']}: {col['type']}")

    indexes = inspector.get_indexes('tag_records')
    print(f"\n索引数: {len(indexes)}")
    for idx in indexes:
        print(f"  - {idx['name']}: {idx['column_names']}")

    fks = inspector.get_foreign_keys('tag_records')
    print(f"\n外键数: {len(fks)}")
    for fk in fks:
        print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")

    print("\n✅ 迁移验证完成")

if __name__ == "__main__":
    run_migration()

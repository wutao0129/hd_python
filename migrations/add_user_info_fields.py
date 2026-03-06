"""
数据库迁移脚本：添加用户信息字段到问卷答案表

执行方式：
cd hd_python目录
python migrations/add_user_info_fields.py
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from database import engine

def upgrade():
    """添加用户信息字段"""
    with engine.connect() as conn:
        fields = [
            ("user_name", "VARCHAR(100)"),
            ("user_company", "VARCHAR(200)"),
            ("user_position", "VARCHAR(100)"),
            ("user_phone", "VARCHAR(20)"),
            ("user_email", "VARCHAR(100)"),
        ]

        for field_name, field_type in fields:
            try:
                conn.execute(text(f"ALTER TABLE questionnaire_answer ADD COLUMN {field_name} {field_type}"))
                print(f"[OK] Added column: {field_name}")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print(f"[SKIP] Column already exists: {field_name}")
                else:
                    raise

        conn.commit()
        print("\n[SUCCESS] Database migration completed!")

def downgrade():
    """回滚用户信息字段"""
    with engine.connect() as conn:
        try:
            conn.execute(text("""
                ALTER TABLE questionnaire_answer
                DROP COLUMN user_name,
                DROP COLUMN user_company,
                DROP COLUMN user_position,
                DROP COLUMN user_phone,
                DROP COLUMN user_email
            """))
            conn.commit()
            print("[SUCCESS] Database rollback completed!")
        except Exception as e:
            print(f"[ERROR] Rollback failed: {e}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()

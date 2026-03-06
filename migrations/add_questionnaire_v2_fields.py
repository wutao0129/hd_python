"""
数据库迁移脚本：添加问卷V2增强字段

执行方式：
cd hd_python目录
python migrations/add_questionnaire_v2_fields.py
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from database import engine

def upgrade():
    """添加V2增强字段"""
    with engine.connect() as conn:
        try:
            # 添加Banner图配置字段
            conn.execute(text("ALTER TABLE questionnaire ADD COLUMN banner_url VARCHAR(500)"))
            print("[OK] Added column: banner_url")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("[SKIP] Column already exists: banner_url")
            else:
                raise

        try:
            conn.execute(text("ALTER TABLE questionnaire ADD COLUMN brand_text VARCHAR(100)"))
            print("[OK] Added column: brand_text")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("[SKIP] Column already exists: brand_text")
            else:
                raise

        try:
            # 添加隐私声明配置字段
            conn.execute(text("ALTER TABLE questionnaire ADD COLUMN privacy_enabled INTEGER DEFAULT 0"))
            print("[OK] Added column: privacy_enabled")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("[SKIP] Column already exists: privacy_enabled")
            else:
                raise

        try:
            conn.execute(text("ALTER TABLE questionnaire ADD COLUMN privacy_title VARCHAR(100)"))
            print("[OK] Added column: privacy_title")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("[SKIP] Column already exists: privacy_title")
            else:
                raise

        try:
            conn.execute(text("ALTER TABLE questionnaire ADD COLUMN privacy_items JSON"))
            print("[OK] Added column: privacy_items")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("[SKIP] Column already exists: privacy_items")
            else:
                raise

        conn.commit()
        print("\n[SUCCESS] Database migration completed!")

def downgrade():
    """回滚V2增强字段"""
    with engine.connect() as conn:
        try:
            conn.execute(text("""
                ALTER TABLE questionnaire
                DROP COLUMN banner_url,
                DROP COLUMN brand_text,
                DROP COLUMN privacy_enabled,
                DROP COLUMN privacy_title,
                DROP COLUMN privacy_items
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

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text
from database import engine

sql = """
INSERT INTO sys_role (ROLE_ID, ROLE_CODE, ROLE_NAME, ROLE_DESC, ROLE_TYPE, ROLE_STATUS, DELETE_MARK)
VALUES (1, 'AI_ADMIN', 'AI项目管理员', 'AI项目管理员角色', 'SYSTEM', 'ACTIVE', '0')
ON DUPLICATE KEY UPDATE
  ROLE_NAME = 'AI项目管理员',
  ROLE_DESC = 'AI项目管理员角色'
"""

with engine.connect() as conn:
    conn.execute(text(sql))
    conn.commit()
    print("Default role inserted successfully")

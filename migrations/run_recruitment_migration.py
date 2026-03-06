import pymysql
from pathlib import Path

# 数据库配置
config = {
    'host': '192.168.110.162',
    'port': 9896,
    'user': 'root',
    'password': 'myDHR2023.COM',
    'database': 'mydhr',
    'charset': 'utf8mb4'
}

# 读取 SQL 文件
sql_file = Path(__file__).parent / 'create_recruitment_approval_table.sql'
with open(sql_file, 'r', encoding='utf-8') as f:
    sql = f.read()

# 执行迁移
try:
    conn = pymysql.connect(**config)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    print("SUCCESS: recruitment_approvals table created")
except Exception as e:
    print(f"ERROR: {e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()

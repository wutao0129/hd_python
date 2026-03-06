"""
执行菜单表创建脚本
"""
import pymysql
from pathlib import Path

# 数据库连接配置
DB_CONFIG = {
    'host': '192.168.110.162',
    'port': 9896,
    'user': 'root',
    'password': 'myDHR2023.COM',
    'database': 'mydhr',
    'charset': 'utf8mb4'
}

def execute_sql_file(sql_file):
    """执行 SQL 文件"""
    # 读取 SQL 文件
    sql_content = Path(sql_file).read_text(encoding='utf-8')

    # 连接数据库
    connection = pymysql.connect(**DB_CONFIG)

    try:
        with connection.cursor() as cursor:
            # 分割并执行每个 SQL 语句
            statements = sql_content.split(';')
            for statement in statements:
                statement = statement.strip()
                if statement:
                    print(f"执行: {statement[:50]}...")
                    cursor.execute(statement)

            connection.commit()
            print("✅ 菜单表创建成功！")

    except Exception as e:
        connection.rollback()
        print(f"❌ 错误: {e}")
        raise

    finally:
        connection.close()

if __name__ == "__main__":
    execute_sql_file("migrations/create_menu_tables.sql")

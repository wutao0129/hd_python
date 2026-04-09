import os
import sys
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import engine

def check():
    with engine.connect() as conn:
        print("--- Check if apps-menu-config exists ---")
        result = conn.execute(text("SELECT id, menu_name, is_enabled FROM menus WHERE route_path='apps-menu-config'"))
        for row in result:
            print(f"Found existing: ID={row[0]}, Name={row[1]}, Enabled={row[2]}")
            
        print("\n--- Potential Parent Menus ---")
        result = conn.execute(text("SELECT id, menu_name FROM menus WHERE menu_name LIKE '%配置%' OR menu_name LIKE '%管理%' LIMIT 10"))
        for row in result:
            print(f"ID: {row[0]}, Name: {row[1]}")
            
if __name__ == "__main__":
    check()

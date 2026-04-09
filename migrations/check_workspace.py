import os
import sys
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import engine

def check():
    with engine.connect() as conn:
        print("--- All Menus with name '工作台' ---")
        result = conn.execute(text("SELECT id, parent_id, menu_name, is_enabled, menu_type FROM menus WHERE menu_name LIKE '%工作台%'"))
        for row in result:
            print(f"ID: {row[0]}, Parent: {row[1]}, Name: {row[2]}, Enabled: {row[3]}, Type: {row[4]}")
            
        print("\n--- Dashboards we added ---")
        result = conn.execute(text("SELECT id, parent_id, menu_name, route_path FROM menus WHERE route_path LIKE 'dashboards-%'"))
        for row in result:
            print(f"ID: {row[0]}, Parent: {row[1]}, Name: {row[2]}, Route: {row[3]}")

if __name__ == "__main__":
    check()

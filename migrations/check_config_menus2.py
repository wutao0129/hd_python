import os
import sys
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import engine

def check():
    with engine.connect() as conn:
        print("--- Menu Details ---")
        result = conn.execute(text("SELECT id, parent_id, menu_name, is_enabled FROM menus WHERE route_path='apps-menu-config'"))
        for row in result:
            print(f"ID: {row[0]}, Parent: {row[1]}, Name: {row[2]}, Enabled: {row[3]}")
            if row[1]:
                print("\n--- Parent Details ---")
                parent_result = conn.execute(text(f"SELECT id, menu_name, is_enabled FROM menus WHERE id={row[1]}"))
                for p_row in parent_result:
                    print(f"Parent - ID: {p_row[0]}, Name: {p_row[1]}, Enabled: {p_row[2]}")

if __name__ == "__main__":
    check()

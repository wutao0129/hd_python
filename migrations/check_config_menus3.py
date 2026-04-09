import os
import sys
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import engine

def check():
    with engine.connect() as conn:
        print("--- Root path of menu 10803 ---")
        parent_id = 10803
        path = []
        
        while parent_id:
            result = conn.execute(text(f"SELECT id, parent_id, menu_name, is_enabled FROM menus WHERE id={parent_id}"))
            for row in result:
                path.insert(0, f"ID={row[0]} Name={row[2]} Enabled={row[3]}")
                parent_id = row[1]
                
        for p in path:
            print(f" -> {p}")

if __name__ == "__main__":
    check()

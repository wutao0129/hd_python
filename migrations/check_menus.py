import os
import sys
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import engine

def check():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, menu_name FROM menus WHERE menu_type='menu' OR parent_id IS NULL"))
        print("Root menus:")
        for row in result:
            print(f"ID: {row[0]}, Name: {row[1]}")
            
if __name__ == "__main__":
    check()

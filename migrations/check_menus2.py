import os
import sys
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import engine

def check():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, menu_name FROM menus WHERE id=10847"))
        for row in result:
            print(f"ID 10847 is: {row[1]}")
            
if __name__ == "__main__":
    check()

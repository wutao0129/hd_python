"""
数据库初始化脚本
创建所有表并插入初始菜单数据
"""
from database import engine, Base
from models import Menu
from sqlalchemy.orm import Session

def init_database():
    """初始化数据库"""
    print("创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建成功")

    # 插入初始菜单数据
    print("插入初始菜单数据...")
    with Session(engine) as session:
        # 检查是否已有数据
        existing = session.query(Menu).first()
        if existing:
            print("⚠️  菜单数据已存在，跳过初始化")
            return

        # 创建示例菜单
        menus = [
            Menu(id=1, menu_name="Dashboard", menu_type="menu", icon="tabler-smart-home", route_path="/", sort_order=0, is_enabled=True),
            Menu(id=2, menu_name="Apps", menu_type="menu", icon="tabler-layout-grid-add", sort_order=1, is_enabled=True),
            Menu(id=3, menu_name="Email", parent_id=2, menu_type="menu", icon="tabler-mail", route_path="/apps/email", sort_order=0, is_enabled=True),
            Menu(id=4, menu_name="Chat", parent_id=2, menu_type="menu", icon="tabler-message-circle-2", route_path="/apps/chat", sort_order=1, is_enabled=True),
        ]

        session.add_all(menus)
        session.commit()
        print("✅ 初始菜单数据插入成功")

if __name__ == "__main__":
    init_database()

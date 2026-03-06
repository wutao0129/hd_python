#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
菜单数据迁移脚本
功能：解析 TypeScript 菜单文件，将硬编码菜单数据导入数据库
作者：Stream B Agent
创建时间：2026-03-03
"""

import re
import json
import pymysql
from typing import List, Dict, Optional, Any
from datetime import datetime


# ============================================
# 数据库配置
# ============================================
DB_CONFIG = {
    'host': '192.168.110.162',
    'port': 9896,
    'user': 'root',
    'password': 'myDHR2023.COM',
    'database': 'mydhr',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# 管理员角色 ID（请根据实际情况修改）
ADMIN_ROLE_ID = 1


# ============================================
# 中英文翻译映射表
# ============================================
TRANSLATION_MAP = {
    # Apps & Pages
    'Apps & Pages': '应用与页面',
    'Ecommerce': '电子商务',
    'Dashboard': '仪表板',
    'Product': '产品',
    'List': '列表',
    'Add': '添加',
    'Category': '分类',
    'Order': '订单',
    'Details': '详情',
    'Customer': '客户',
    'Manage Review': '评价管理',
    'Referrals': '推荐',
    'Settings': '设置',
    'Academy': '学院',
    'My Course': '我的课程',
    'Course Details': '课程详情',
    'Logistics': '物流',
    'Fleet': '车队',
    'Email': '邮件',
    'Chat': '聊天',
    'Calendar': '日历',
    'Evaluation': '评估',
    'Video Hub': '视频中心',
    '问卷管理': '问卷管理',
    'Info Collect Survey': '信息收集调查',
    'Talent Inventory': '人才盘点',
    '盘点准备': '盘点准备',
    '盘点周期管理': '盘点周期管理',
    '盘点组织管理': '盘点组织管理',
    '盘点方案管理': '盘点方案管理',
    '盘点项目管理': '盘点项目管理',
    '盘点执行': '盘点执行',
    '盘点对象管理': '盘点对象管理',
    '校准会议': '校准会议',
    '盘点进度': '盘点进度',
    '人才分析': '人才分析',
    '人才分析方案': '人才分析方案',
    '分析报告': '分析报告',
    'SAP Digital Survey': 'SAP 数字化调查',
    'SAP 谁来引领组织变革': 'SAP 谁来引领组织变革',
    'SAP TrustRadius 报告': 'SAP TrustRadius 报告',
    'SAP 超级员工时代': 'SAP 超级员工时代',
    'Recruitment': '招聘',
    'Approval': '审批',
    'Position Management': '职位管理',
    'Channel': '渠道',
    'Resume Management': '简历管理',
    'Interview': '面试',
    'Offer': 'Offer',
    'Employee Onboarding': '员工入职',
    'Onboarding Hub': '入职中心',
    'Onboarding Command Center': '入职指挥中心',
    'Onboarding Archive': '入职归档',
    'Medical Exam Center': '体检中心',
    'Invoice': '发票',
    'Preview': '预览',
    'Edit': '编辑',
    'Core HR': '核心人力',
    'Resignation': '离职',
    'Resignation List': '离职列表',
    'Form Template Config': '表单模板配置',
    'Handover Template Config': '交接模板配置',
    'Approval Flow Config': '审批流程配置',
    'User': '用户',
    'View': '查看',
    'Roles & Permissions': '角色与权限',
    'Roles': '角色',
    'Permissions': '权限',
    'Pages': '页面',
    'User Profile': '用户资料',
    'Account Settings': '账户设置',
    'Pricing': '定价',
    'FAQ': '常见问题',
    'Miscellaneous': '其他',
    'Coming Soon': '即将推出',
    'Under Maintenance': '维护中',
    'Page Not Found - 404': '页面未找到 - 404',
    'Not Authorized - 401': '未授权 - 401',
    'Authentication': '认证',
    'Login': '登录',
    'Login v1': '登录 v1',
    'Login v2': '登录 v2',
    'Register': '注册',
    'Register v1': '注册 v1',
    'Register v2': '注册 v2',
    'Register Multi-Steps': '多步注册',
    'Verify Email': '验证邮箱',
    'Verify Email v1': '验证邮箱 v1',
    'Verify Email v2': '验证邮箱 v2',
    'Forgot Password': '忘记密码',
    'Forgot Password v1': '忘记密码 v1',
    'Forgot Password v2': '忘记密码 v2',
    'Reset Password': '重置密码',
    'Reset Password v1': '重置密码 v1',
    'Reset Password v2': '重置密码 v2',
    'Two Steps': '两步验证',
    'Two Steps v1': '两步验证 v1',
    'Two Steps v2': '两步验证 v2',
    'Wizard Examples': '向导示例',
    'Checkout': '结账',
    'Property Listing': '房产列表',
    'Create Deal': '创建交易',
    'Dialog Examples': '对话框示例',
}


def translate_to_chinese(english_text: str) -> str:
    """
    将英文菜单名称翻译为中文
    如果翻译映射表中没有，则返回原文
    """
    return TRANSLATION_MAP.get(english_text, english_text)


# ============================================
# 菜单解析器
# ============================================
class MenuParser:
    """TypeScript 菜单文件解析器"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.menus = []

    def parse(self) -> List[Dict[str, Any]]:
        """
        解析 TypeScript 菜单文件
        返回菜单列表
        """
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 移除注释
        content = re.sub(r'//.*?\n', '\n', content)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

        # 提取 export default 数组内容
        match = re.search(r'export\s+default\s+\[(.*)\]', content, re.DOTALL)
        if not match:
            raise ValueError("无法找到 export default 数组")

        array_content = match.group(1)

        # 解析顶级菜单项
        self.menus = self._parse_menu_items(array_content, parent_id=None, start_order=0)

        return self.menus

    def _parse_menu_items(self, content: str, parent_id: Optional[int], start_order: int) -> List[Dict[str, Any]]:
        """
        递归解析菜单项
        """
        menus = []
        order = start_order

        # 使用栈来匹配大括号
        items = self._split_menu_items(content)

        for item_str in items:
            item_str = item_str.strip()
            if not item_str:
                continue

            menu_item = self._parse_single_item(item_str, parent_id, order)
            if menu_item:
                menus.append(menu_item)
                order += 1

        return menus

    def _split_menu_items(self, content: str) -> List[str]:
        """
        分割菜单项（处理嵌套的大括号）
        """
        items = []
        current_item = []
        brace_count = 0
        in_string = False
        escape_next = False

        for char in content:
            if escape_next:
                current_item.append(char)
                escape_next = False
                continue

            if char == '\\':
                escape_next = True
                current_item.append(char)
                continue

            if char in ('"', "'", '`'):
                in_string = not in_string
                current_item.append(char)
                continue

            if in_string:
                current_item.append(char)
                continue

            if char == '{':
                brace_count += 1
                current_item.append(char)
            elif char == '}':
                brace_count -= 1
                current_item.append(char)
                if brace_count == 0:
                    # 完整的菜单项
                    items.append(''.join(current_item))
                    current_item = []
            elif char == ',' and brace_count == 0:
                # 顶级逗号，分隔菜单项
                if current_item:
                    items.append(''.join(current_item))
                    current_item = []
            else:
                current_item.append(char)

        if current_item:
            items.append(''.join(current_item))

        return items

    def _parse_single_item(self, item_str: str, parent_id: Optional[int], order: int) -> Optional[Dict[str, Any]]:
        """
        解析单个菜单项
        """
        # 检查是否是 heading 类型
        heading_match = re.search(r"heading:\s*['\"](.+?)['\"]", item_str)
        if heading_match:
            return {
                'parent_id': parent_id,
                'menu_type': 'heading',
                'menu_name': heading_match.group(1),
                'icon': None,
                'route_path': None,
                'sort_order': order,
                'children': []
            }

        # 解析普通菜单项
        title_match = re.search(r"title:\s*['\"](.+?)['\"]", item_str)
        if not title_match:
            return None

        title = title_match.group(1)

        # 提取图标
        icon = None
        icon_match = re.search(r"icon:\s*\{\s*icon:\s*['\"](.+?)['\"]", item_str)
        if icon_match:
            icon = icon_match.group(1)

        # 提取路由
        route = None
        # 简单字符串路由
        to_match = re.search(r"to:\s*['\"](.+?)['\"]", item_str)
        if to_match:
            route = to_match.group(1)
        else:
            # 对象路由（提取 name）
            to_obj_match = re.search(r"to:\s*\{\s*name:\s*['\"](.+?)['\"]", item_str)
            if to_obj_match:
                route = to_obj_match.group(1)
            else:
                # path 路由
                to_path_match = re.search(r"to:\s*\{\s*path:\s*['\"](.+?)['\"]", item_str)
                if to_path_match:
                    route = to_path_match.group(1)

        # 检查是否有 children
        children_match = re.search(r"children:\s*\[(.*)\]", item_str, re.DOTALL)
        children = []
        if children_match:
            children_content = children_match.group(1)
            # 递归解析子菜单（暂时不设置 parent_id，稍后处理）
            children = self._parse_menu_items(children_content, parent_id=None, start_order=0)

        return {
            'parent_id': parent_id,
            'menu_type': 'page',
            'menu_name': title,
            'icon': icon,
            'route_path': route,
            'sort_order': order,
            'children': children
        }


# ============================================
# 数据库操作
# ============================================
class MenuImporter:
    """菜单数据导入器"""

    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self.connection = None
        self.cursor = None

    def connect(self):
        """连接数据库"""
        try:
            self.connection = pymysql.connect(**self.db_config)
            self.cursor = self.connection.cursor()
            print("✅ 数据库连接成功")
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            raise

    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("✅ 数据库连接已关闭")

    def clear_tables(self):
        """清空菜单相关表（支持重复执行）"""
        try:
            print("🔄 清空现有菜单数据...")
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            self.cursor.execute("TRUNCATE TABLE menu_permissions")
            self.cursor.execute("TRUNCATE TABLE menu_i18n")
            self.cursor.execute("TRUNCATE TABLE menus")
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            self.connection.commit()
            print("✅ 现有数据已清空")
        except Exception as e:
            print(f"❌ 清空数据失败: {e}")
            raise

    def import_menus(self, menus: List[Dict[str, Any]]):
        """
        导入菜单数据
        递归处理嵌套菜单，建立父子关系
        """
        try:
            print("🔄 开始导入菜单数据...")
            total_count = self._import_menu_recursive(menus, parent_id=None)
            self.connection.commit()
            print(f"✅ 菜单数据导入成功，共导入 {total_count} 条记录")
            return total_count
        except Exception as e:
            self.connection.rollback()
            print(f"❌ 菜单数据导入失败: {e}")
            raise

    def _import_menu_recursive(self, menus: List[Dict[str, Any]], parent_id: Optional[int]) -> int:
        """
        递归导入菜单
        返回导入的菜单数量
        """
        count = 0

        for menu in menus:
            # 插入菜单主表
            sql = """
                INSERT INTO menus (parent_id, menu_type, menu_name, icon, route_path, sort_order, is_enabled)
                VALUES (%s, %s, %s, %s, %s, %s, 1)
            """
            self.cursor.execute(sql, (
                parent_id,
                menu['menu_type'],
                menu['menu_name'],
                menu['icon'],
                menu['route_path'],
                menu['sort_order']
            ))

            # 获取插入的菜单 ID
            menu_id = self.cursor.lastrowid
            count += 1

            # 插入多语言数据
            self._insert_i18n(menu_id, menu['menu_name'])

            # 递归处理子菜单
            if menu.get('children'):
                child_count = self._import_menu_recursive(menu['children'], parent_id=menu_id)
                count += child_count

        return count

    def _insert_i18n(self, menu_id: int, menu_name: str):
        """
        插入多语言数据
        """
        # 英文
        sql_en = """
            INSERT INTO menu_i18n (menu_id, language_code, menu_name)
            VALUES (%s, 'en', %s)
        """
        self.cursor.execute(sql_en, (menu_id, menu_name))

        # 中文
        chinese_name = translate_to_chinese(menu_name)
        sql_zh = """
            INSERT INTO menu_i18n (menu_id, language_code, menu_name)
            VALUES (%s, 'zh', %s)
        """
        self.cursor.execute(sql_zh, (menu_id, chinese_name))

    def assign_permissions(self, role_id: int):
        """
        为指定角色分配所有菜单权限
        """
        try:
            print(f"🔄 为角色 {role_id} 分配菜单权限...")

            # 查询所有菜单 ID
            self.cursor.execute("SELECT id FROM menus")
            menu_ids = [row['id'] for row in self.cursor.fetchall()]

            # 批量插入权限
            sql = """
                INSERT INTO menu_permissions (role_id, menu_id)
                VALUES (%s, %s)
            """
            for menu_id in menu_ids:
                self.cursor.execute(sql, (role_id, menu_id))

            self.connection.commit()
            print(f"✅ 权限分配成功，共分配 {len(menu_ids)} 个菜单权限")
        except Exception as e:
            self.connection.rollback()
            print(f"❌ 权限分配失败: {e}")
            raise

    def verify_data(self):
        """
        验证数据完整性
        """
        print("\n" + "="*50)
        print("📊 数据完整性验证")
        print("="*50)

        # 统计菜单数量
        self.cursor.execute("SELECT COUNT(*) as count FROM menus")
        menu_count = self.cursor.fetchone()['count']
        print(f"菜单总数: {menu_count}")

        # 统计各类型菜单
        self.cursor.execute("""
            SELECT menu_type, COUNT(*) as count
            FROM menus
            GROUP BY menu_type
        """)
        for row in self.cursor.fetchall():
            print(f"  - {row['menu_type']}: {row['count']}")

        # 统计层级
        self.cursor.execute("""
            SELECT
                CASE
                    WHEN parent_id IS NULL THEN '顶级菜单'
                    ELSE '子菜单'
                END as level,
                COUNT(*) as count
            FROM menus
            GROUP BY level
        """)
        for row in self.cursor.fetchall():
            print(f"  - {row['level']}: {row['count']}")

        # 统计多语言数据
        self.cursor.execute("SELECT COUNT(*) as count FROM menu_i18n")
        i18n_count = self.cursor.fetchone()['count']
        print(f"多语言记录数: {i18n_count}")

        # 统计权限数据
        self.cursor.execute("SELECT COUNT(*) as count FROM menu_permissions")
        perm_count = self.cursor.fetchone()['count']
        print(f"权限记录数: {perm_count}")

        # 检查数据一致性
        print("\n数据一致性检查:")
        if i18n_count == menu_count * 2:
            print("  ✅ 多语言数据完整（每个菜单有中英文两条记录）")
        else:
            print(f"  ⚠️ 多语言数据不完整（预期 {menu_count * 2}，实际 {i18n_count}）")

        if perm_count == menu_count:
            print("  ✅ 权限数据完整（管理员拥有所有菜单权限）")
        else:
            print(f"  ⚠️ 权限数据不完整（预期 {menu_count}，实际 {perm_count}）")

        # 显示部分菜单数据
        print("\n前 10 条菜单数据:")
        self.cursor.execute("""
            SELECT id, parent_id, menu_type, menu_name, route_path, sort_order
            FROM menus
            ORDER BY id
            LIMIT 10
        """)
        for row in self.cursor.fetchall():
            parent = row['parent_id'] if row['parent_id'] else 'NULL'
            print(f"  [{row['id']}] {row['menu_name']} (类型: {row['menu_type']}, 父ID: {parent}, 路由: {row['route_path']})")

        print("="*50 + "\n")


# ============================================
# 主函数
# ============================================
def main():
    """
    主执行流程
    """
    print("="*50)
    print("菜单数据迁移脚本")
    print("="*50 + "\n")

    # 菜单文件路径
    menu_file = "D:/workspace/AI-WEB/ccpm_project/aicreate_ccpm/src/navigation/vertical/apps-and-pages.ts"

    try:
        # 1. 解析菜单文件
        print("🔄 解析菜单文件...")
        parser = MenuParser(menu_file)
        menus = parser.parse()
        print(f"✅ 菜单文件解析成功，共解析 {len(menus)} 个顶级菜单\n")

        # 2. 连接数据库
        importer = MenuImporter(DB_CONFIG)
        importer.connect()

        # 3. 清空现有数据
        importer.clear_tables()

        # 4. 导入菜单数据
        total_count = importer.import_menus(menus)

        # 5. 分配权限
        importer.assign_permissions(ADMIN_ROLE_ID)

        # 6. 验证数据
        importer.verify_data()

        # 7. 关闭连接
        importer.close()

        print("✅ 菜单数据迁移完成！\n")

    except FileNotFoundError:
        print(f"❌ 错误：找不到菜单文件 {menu_file}")
        print("请确保脚本在正确的目录下执行")
    except Exception as e:
        print(f"❌ 错误：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

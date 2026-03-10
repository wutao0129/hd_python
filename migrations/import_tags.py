#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标签库数据迁移脚本
从预定义的标签数据导入到 MySQL 数据库
"""

import sys
import os
import json
from datetime import datetime
import pymysql

# 数据库连接配置
DB_CONFIG = {
    'host': '139.196.207.85',
    'port': 9896,
    'user': 'root',
    'password': 'myDHR2023.COM',
    'database': 'mydhr',
    'charset': 'utf8mb4'
}


def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)

# 40条标签数据（6大分类：基础信息、职业履历、能力、素质、复合标签、行业）
TAGS_DATA = [
    # 基础信息类标签 (7条)
    {"name": "年龄", "code": "age", "category": "基础信息", "type": "内置", "scene": ["招聘", "盘点"], "rule_type": "数值范围", "rule_detail": "18-65岁", "description": "员工年龄信息", "status": "启用", "graph_type": "节点"},
    {"name": "性别", "code": "gender", "category": "基础信息", "type": "内置", "scene": ["招聘", "统计"], "rule_type": "枚举", "rule_detail": "男/女", "description": "员工性别", "status": "启用", "graph_type": "节点"},
    {"name": "学历", "code": "education", "category": "基础信息", "type": "内置", "scene": ["招聘", "盘点"], "rule_type": "枚举", "rule_detail": "博士/硕士/本科/专科/高中及以下", "description": "最高学历", "status": "启用", "graph_type": "节点"},
    {"name": "工作年限", "code": "work_years", "category": "基础信息", "type": "内置", "scene": ["招聘", "盘点"], "rule_type": "数值范围", "rule_detail": "0-50年", "description": "工作经验年限", "status": "启用", "graph_type": "节点"},
    {"name": "职级", "code": "job_level", "category": "基础信息", "type": "内置", "scene": ["盘点", "晋升"], "rule_type": "枚举", "rule_detail": "P1-P10", "description": "员工职级", "status": "启用", "graph_type": "节点"},
    {"name": "部门", "code": "department", "category": "基础信息", "type": "内置", "scene": ["组织", "统计"], "rule_type": "树形", "rule_detail": "组织架构树", "description": "所属部门", "status": "启用", "graph_type": "节点"},
    {"name": "岗位", "code": "position", "category": "基础信息", "type": "内置", "scene": ["招聘", "盘点"], "rule_type": "文本", "rule_detail": "岗位名称", "description": "当前岗位", "status": "启用", "graph_type": "节点"},

    # 职业履历类标签 (8条)
    {"name": "项目经验", "code": "project_exp", "category": "职业履历", "type": "内置", "scene": ["招聘", "盘点"], "rule_type": "列表", "rule_detail": "项目名称、角色、时间", "description": "参与过的项目", "status": "启用", "graph_type": "关系", "relation_name": "参与项目"},
    {"name": "管理经验", "code": "management_exp", "category": "职业履历", "type": "内置", "scene": ["招聘", "晋升"], "rule_type": "布尔+数值", "rule_detail": "是否有管理经验及年限", "description": "团队管理经验", "status": "启用", "graph_type": "节点"},
    {"name": "行业经验", "code": "industry_exp", "category": "职业履历", "type": "内置", "scene": ["招聘"], "rule_type": "列表", "rule_detail": "行业名称及年限", "description": "从业行业背景", "status": "启用", "graph_type": "关系", "relation_name": "从事行业"},
    {"name": "跳槽频率", "code": "job_change_freq", "category": "职业履历", "type": "内置", "scene": ["招聘", "风险"], "rule_type": "数值", "rule_detail": "平均任职月数", "description": "职业稳定性指标", "status": "启用", "graph_type": "节点"},
    {"name": "晋升记录", "code": "promotion_history", "category": "职业履历", "type": "内置", "scene": ["盘点", "晋升"], "rule_type": "列表", "rule_detail": "晋升时间、职级变化", "description": "历史晋升情况", "status": "启用", "graph_type": "关系", "relation_name": "晋升至"},
    {"name": "培训经历", "code": "training_history", "category": "职业履历", "type": "内置", "scene": ["发展"], "rule_type": "列表", "rule_detail": "培训课程、时间、证书", "description": "参加过的培训", "status": "启用", "graph_type": "关系", "relation_name": "参加培训"},
    {"name": "获奖记录", "code": "awards", "category": "职业履历", "type": "内置", "scene": ["盘点", "激励"], "rule_type": "列表", "rule_detail": "奖项名称、时间、级别", "description": "获得的荣誉奖项", "status": "启用", "graph_type": "节点"},
    {"name": "离职风险", "code": "turnover_risk", "category": "职业履历", "type": "自定义", "scene": ["风险", "保留"], "rule_type": "评分", "rule_detail": "1-10分", "description": "离职倾向评估", "status": "启用", "graph_type": "节点"},

    # 能力类标签 (8条)
    {"name": "技术能力", "code": "technical_skill", "category": "能力", "type": "内置", "scene": ["招聘", "盘点"], "rule_type": "评分+列表", "rule_detail": "技能名称及熟练度", "description": "专业技术能力", "status": "启用", "graph_type": "关系", "relation_name": "掌握技能"},
    {"name": "沟通能力", "code": "communication", "category": "能力", "type": "内置", "scene": ["盘点", "晋升"], "rule_type": "评分", "rule_detail": "1-5分", "description": "表达和沟通能力", "status": "启用", "graph_type": "节点"},
    {"name": "领导力", "code": "leadership", "category": "能力", "type": "内置", "scene": ["盘点", "晋升"], "rule_type": "评分", "rule_detail": "1-5分", "description": "团队领导能力", "status": "启用", "graph_type": "节点"},
    {"name": "学习能力", "code": "learning_ability", "category": "能力", "type": "内置", "scene": ["招聘", "发展"], "rule_type": "评分", "rule_detail": "1-5分", "description": "快速学习新知识的能力", "status": "启用", "graph_type": "节点"},
    {"name": "问题解决", "code": "problem_solving", "category": "能力", "type": "内置", "scene": ["招聘", "盘点"], "rule_type": "评分", "rule_detail": "1-5分", "description": "分析和解决问题的能力", "status": "启用", "graph_type": "节点"},
    {"name": "创新能力", "code": "innovation", "category": "能力", "type": "内置", "scene": ["盘点", "激励"], "rule_type": "评分", "rule_detail": "1-5分", "description": "创新思维和实践能力", "status": "启用", "graph_type": "节点"},
    {"name": "执行力", "code": "execution", "category": "能力", "type": "内置", "scene": ["盘点"], "rule_type": "评分", "rule_detail": "1-5分", "description": "任务执行和落地能力", "status": "启用", "graph_type": "节点"},
    {"name": "抗压能力", "code": "stress_resistance", "category": "能力", "type": "内置", "scene": ["招聘", "盘点"], "rule_type": "评分", "rule_detail": "1-5分", "description": "压力承受能力", "status": "启用", "graph_type": "节点"},

    # 素质类标签 (7条)
    {"name": "责任心", "code": "responsibility", "category": "素质", "type": "内置", "scene": ["招聘", "盘点"], "rule_type": "评分", "rule_detail": "1-5分", "description": "工作责任感", "status": "启用", "graph_type": "节点"},
    {"name": "团队协作", "code": "teamwork", "category": "素质", "type": "内置", "scene": ["招聘", "盘点"], "rule_type": "评分", "rule_detail": "1-5分", "description": "团队合作精神", "status": "启用", "graph_type": "节点"},
    {"name": "主动性", "code": "initiative", "category": "素质", "type": "内置", "scene": ["盘点", "晋升"], "rule_type": "评分", "rule_detail": "1-5分", "description": "工作主动性", "status": "启用", "graph_type": "节点"},
    {"name": "诚信度", "code": "integrity", "category": "素质", "type": "内置", "scene": ["招聘", "风险"], "rule_type": "评分", "rule_detail": "1-5分", "description": "诚实守信程度", "status": "启用", "graph_type": "节点"},
    {"name": "敬业度", "code": "dedication", "category": "素质", "type": "内置", "scene": ["盘点", "保留"], "rule_type": "评分", "rule_detail": "1-5分", "description": "工作投入程度", "status": "启用", "graph_type": "节点"},
    {"name": "适应性", "code": "adaptability", "category": "素质", "type": "内置", "scene": ["招聘", "变革"], "rule_type": "评分", "rule_detail": "1-5分", "description": "环境适应能力", "status": "启用", "graph_type": "节点"},
    {"name": "价值观匹配", "code": "value_fit", "category": "素质", "type": "内置", "scene": ["招聘", "文化"], "rule_type": "评分", "rule_detail": "1-5分", "description": "与企业文化的契合度", "status": "启用", "graph_type": "节点"},

    # 复合标签 (4条)
    {"name": "高潜人才", "code": "high_potential", "category": "复合标签", "type": "自定义", "scene": ["盘点", "继任"], "rule_type": "复合规则", "rule_detail": "绩效A+潜力高+学习能力强", "description": "具有高发展潜力的人才", "status": "启用", "graph_type": "节点"},
    {"name": "关键人才", "code": "key_talent", "category": "复合标签", "type": "自定义", "scene": ["保留", "激励"], "rule_type": "复合规则", "rule_detail": "关键岗位+高绩效+难替代", "description": "对组织至关重要的人才", "status": "启用", "graph_type": "节点"},
    {"name": "技术专家", "code": "technical_expert", "category": "复合标签", "type": "自定义", "scene": ["盘点", "发展"], "rule_type": "复合规则", "rule_detail": "技术能力5分+工作年限5年+", "description": "技术领域的专家", "status": "启用", "graph_type": "节点"},
    {"name": "管理储备", "code": "management_reserve", "category": "复合标签", "type": "自定义", "scene": ["继任", "发展"], "rule_type": "复合规则", "rule_detail": "领导力4分+潜力高+意愿强", "description": "管理岗位后备人才", "status": "启用", "graph_type": "节点"},

    # 行业类标签 (6条，包含层级结构)
    {"name": "互联网", "code": "industry_internet", "category": "行业", "type": "内置", "scene": ["招聘", "统计"], "rule_type": "枚举", "rule_detail": "一级行业", "description": "互联网行业", "status": "启用", "graph_type": "节点", "parent_id": None},
    {"name": "电商", "code": "industry_ecommerce", "category": "行业", "type": "内置", "scene": ["招聘"], "rule_type": "枚举", "rule_detail": "二级行业", "description": "电子商务", "status": "启用", "graph_type": "节点", "parent_id": "industry_internet"},
    {"name": "金融", "code": "industry_finance", "category": "行业", "type": "内置", "scene": ["招聘", "统计"], "rule_type": "枚举", "rule_detail": "一级行业", "description": "金融行业", "status": "启用", "graph_type": "节点", "parent_id": None},
    {"name": "银行", "code": "industry_bank", "category": "行业", "type": "内置", "scene": ["招聘"], "rule_type": "枚举", "rule_detail": "二级行业", "description": "银行业", "status": "启用", "graph_type": "节点", "parent_id": "industry_finance"},
    {"name": "制造业", "code": "industry_manufacturing", "category": "行业", "type": "内置", "scene": ["招聘", "统计"], "rule_type": "枚举", "rule_detail": "一级行业", "description": "制造业", "status": "启用", "graph_type": "节点", "parent_id": None},
    {"name": "汽车制造", "code": "industry_auto", "category": "行业", "type": "内置", "scene": ["招聘"], "rule_type": "枚举", "rule_detail": "二级行业", "description": "汽车制造业", "status": "启用", "graph_type": "节点", "parent_id": "industry_manufacturing"},
]


def create_tags_table(cursor):
    """创建标签表"""
    print("正在创建 tags 表...")

    # 读取 SQL 文件
    sql_file = os.path.join(os.path.dirname(__file__), 'create_tags_table.sql')
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql = f.read()

    # 执行 SQL
    cursor.execute(sql)
    print("✅ tags 表创建成功")


def import_tags(cursor, connection):
    """导入标签数据"""
    print(f"\n正在导入 {len(TAGS_DATA)} 条标签数据...")

    # 第一轮：插入所有没有 parent_id 依赖的标签
    parent_code_to_id = {}
    tags_with_parent = []

    insert_sql = """
    INSERT INTO tags (name, code, category, type, scene, rule_type, rule_detail,
                     description, status, parent_id, graph_type, relation_name)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    for tag in TAGS_DATA:
        scene_json = json.dumps(tag.get("scene", []), ensure_ascii=False) if tag.get("scene") else None

        if tag.get("parent_id") is None or not isinstance(tag.get("parent_id"), str):
            # 没有父标签依赖，直接插入
            cursor.execute(insert_sql, (
                tag["name"],
                tag["code"],
                tag["category"],
                tag["type"],
                scene_json,
                tag.get("rule_type"),
                tag.get("rule_detail"),
                tag.get("description"),
                tag["status"],
                None,  # parent_id
                tag.get("graph_type"),
                tag.get("relation_name")
            ))
            # 记录 code 到 id 的映射
            parent_code_to_id[tag["code"]] = cursor.lastrowid
            print(f"  ✓ 插入标签: {tag['name']} (ID: {cursor.lastrowid})")
        else:
            # 有父标签依赖，暂存
            tags_with_parent.append(tag)

    connection.commit()

    # 第二轮：插入有 parent_id 依赖的标签
    if tags_with_parent:
        print(f"\n正在插入 {len(tags_with_parent)} 条子标签...")
        for tag in tags_with_parent:
            parent_code = tag["parent_id"]
            parent_id = parent_code_to_id.get(parent_code)

            if parent_id is None:
                print(f"  ⚠️  警告: 找不到父标签 {parent_code}，跳过 {tag['name']}")
                continue

            scene_json = json.dumps(tag.get("scene", []), ensure_ascii=False) if tag.get("scene") else None

            cursor.execute(insert_sql, (
                tag["name"],
                tag["code"],
                tag["category"],
                tag["type"],
                scene_json,
                tag.get("rule_type"),
                tag.get("rule_detail"),
                tag.get("description"),
                tag["status"],
                parent_id,
                tag.get("graph_type"),
                tag.get("relation_name")
            ))
            print(f"  ✓ 插入子标签: {tag['name']} (父ID: {parent_id})")

        connection.commit()

    print(f"\n✅ 标签数据导入完成")


def verify_data(cursor):
    """验证数据完整性"""
    print("\n正在验证数据...")

    # 检查总数
    cursor.execute("SELECT COUNT(*) FROM tags")
    total = cursor.fetchone()[0]
    print(f"  总记录数: {total}")

    # 按分类统计
    cursor.execute("""
        SELECT category, COUNT(*) as cnt
        FROM tags
        GROUP BY category
        ORDER BY category
    """)
    print("\n  分类统计:")
    for row in cursor.fetchall():
        print(f"    {row[0]}: {row[1]} 条")

    # 检查父子关系
    cursor.execute("SELECT COUNT(*) FROM tags WHERE parent_id IS NOT NULL")
    child_count = cursor.fetchone()[0]
    print(f"\n  子标签数量: {child_count}")

    # 检查索引
    cursor.execute("SHOW INDEX FROM tags")
    indexes = cursor.fetchall()
    print(f"\n  索引数量: {len(indexes)}")

    if total == len(TAGS_DATA):
        print(f"\n✅ 数据验证通过: {total}/{len(TAGS_DATA)} 条记录")
        return True
    else:
        print(f"\n❌ 数据验证失败: 期望 {len(TAGS_DATA)} 条，实际 {total} 条")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("标签库数据迁移脚本")
    print("=" * 60)

    connection = None
    cursor = None

    try:
        # 连接数据库
        print("\n正在连接数据库...")
        connection = get_db_connection()
        cursor = connection.cursor()
        print("✅ 数据库连接成功")

        # 创建表
        create_tags_table(cursor)
        connection.commit()

        # 导入数据
        import_tags(cursor, connection)

        # 验证数据
        success = verify_data(cursor)

        print("\n" + "=" * 60)
        if success:
            print("✅ 迁移完成！")
        else:
            print("⚠️  迁移完成，但数据验证未通过，请检查")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        if connection:
            connection.rollback()
        raise

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            print("\n数据库连接已关闭")


if __name__ == "__main__":
    main()

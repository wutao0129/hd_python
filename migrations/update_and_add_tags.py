#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标签库数据更新与扩充脚本
1. 更新现有标签的 rule_type、scene、usage_count、activity_rate
2. 新增更多标签条目
"""

import json
import random
from datetime import datetime
import pymysql

DB_CONFIG = {
    'host': '139.196.207.85',
    'port': 9896,
    'user': 'root',
    'password': 'myDHR2023.COM',
    'database': 'mydhr',
    'charset': 'utf8mb4'
}

# ==================== 第一部分：更新现有标签 ====================
# code -> { rule_type: [...], scene: [...], usage_count, activity_rate }
EXISTING_TAG_UPDATES = {
    # 基础信息类
    "age": {"rule_type": ["自动", "计算"], "scene": ["人才盘点", "招聘评估", "薪酬调整"], "usage_count": 856, "activity_rate": 92},
    "gender": {"rule_type": ["自动"], "scene": ["招聘评估", "人才盘点"], "usage_count": 720, "activity_rate": 85},
    "education": {"rule_type": ["自动", "导入"], "scene": ["招聘评估", "人才盘点", "岗位匹配"], "usage_count": 934, "activity_rate": 95},
    "work_years": {"rule_type": ["自动", "计算"], "scene": ["招聘评估", "人才盘点", "薪酬调整"], "usage_count": 812, "activity_rate": 88},
    "job_level": {"rule_type": ["自动"], "scene": ["人才盘点", "晋升评估", "薪酬调整"], "usage_count": 967, "activity_rate": 96},
    "department": {"rule_type": ["自动"], "scene": ["人才盘点", "人才池筛选"], "usage_count": 1024, "activity_rate": 98},
    "position": {"rule_type": ["自动"], "scene": ["招聘评估", "人才盘点", "岗位匹配"], "usage_count": 890, "activity_rate": 91},

    # 职业履历类
    "project_exp": {"rule_type": ["手动", "导入"], "scene": ["招聘评估", "人才盘点", "岗位匹配"], "usage_count": 456, "activity_rate": 72},
    "management_exp": {"rule_type": ["手动", "计算"], "scene": ["招聘评估", "晋升评估", "继任规划"], "usage_count": 389, "activity_rate": 68},
    "industry_exp": {"rule_type": ["手动", "导入"], "scene": ["招聘评估", "人才池筛选"], "usage_count": 312, "activity_rate": 61},
    "job_change_freq": {"rule_type": ["计算", "AI"], "scene": ["招聘评估", "离职预警"], "usage_count": 278, "activity_rate": 55},
    "promotion_history": {"rule_type": ["自动", "计算"], "scene": ["人才盘点", "晋升评估", "继任规划"], "usage_count": 534, "activity_rate": 76},
    "training_history": {"rule_type": ["自动", "导入"], "scene": ["培训发展", "人才盘点"], "usage_count": 423, "activity_rate": 65},
    "awards": {"rule_type": ["手动", "导入"], "scene": ["人才盘点", "绩效管理"], "usage_count": 267, "activity_rate": 52},
    "turnover_risk": {"rule_type": ["AI", "计算"], "scene": ["离职预警", "人才盘点", "薪酬调整"], "usage_count": 645, "activity_rate": 82},

    # 能力类
    "technical_skill": {"rule_type": ["手动", "AI"], "scene": ["招聘评估", "人才盘点", "岗位匹配"], "usage_count": 723, "activity_rate": 87},
    "communication": {"rule_type": ["手动", "AI"], "scene": ["人才盘点", "晋升评估"], "usage_count": 567, "activity_rate": 78},
    "leadership": {"rule_type": ["手动", "AI"], "scene": ["人才盘点", "晋升评估", "继任规划"], "usage_count": 612, "activity_rate": 81},
    "learning_ability": {"rule_type": ["手动", "AI"], "scene": ["招聘评估", "培训发展", "人才盘点"], "usage_count": 489, "activity_rate": 73},
    "problem_solving": {"rule_type": ["手动", "AI"], "scene": ["招聘评估", "人才盘点"], "usage_count": 445, "activity_rate": 70},
    "innovation": {"rule_type": ["手动", "AI"], "scene": ["人才盘点", "绩效管理"], "usage_count": 356, "activity_rate": 63},
    "execution": {"rule_type": ["手动", "计算"], "scene": ["人才盘点", "绩效管理"], "usage_count": 478, "activity_rate": 71},
    "stress_resistance": {"rule_type": ["手动", "AI"], "scene": ["招聘评估", "人才盘点"], "usage_count": 334, "activity_rate": 58},

    # 素质类
    "responsibility": {"rule_type": ["手动", "AI"], "scene": ["招聘评估", "人才盘点", "绩效管理"], "usage_count": 512, "activity_rate": 75},
    "teamwork": {"rule_type": ["手动", "AI"], "scene": ["招聘评估", "人才盘点"], "usage_count": 489, "activity_rate": 74},
    "initiative": {"rule_type": ["手动", "AI"], "scene": ["人才盘点", "晋升评估"], "usage_count": 423, "activity_rate": 67},
    "integrity": {"rule_type": ["手动"], "scene": ["招聘评估", "离职预警"], "usage_count": 234, "activity_rate": 48},
    "dedication": {"rule_type": ["手动", "AI"], "scene": ["人才盘点", "绩效管理"], "usage_count": 378, "activity_rate": 64},
    "adaptability": {"rule_type": ["手动", "AI"], "scene": ["招聘评估", "人才盘点"], "usage_count": 312, "activity_rate": 59},
    "value_fit": {"rule_type": ["手动", "AI"], "scene": ["招聘评估", "人才盘点"], "usage_count": 289, "activity_rate": 56},

    # 复合标签
    "high_potential": {"rule_type": ["计算", "AI"], "scene": ["人才盘点", "继任规划", "培训发展"], "usage_count": 756, "activity_rate": 89},
    "key_talent": {"rule_type": ["计算", "AI"], "scene": ["人才盘点", "人才池筛选", "薪酬调整"], "usage_count": 678, "activity_rate": 84},
    "technical_expert": {"rule_type": ["计算", "AI"], "scene": ["人才盘点", "培训发展", "岗位匹配"], "usage_count": 534, "activity_rate": 77},
    "management_reserve": {"rule_type": ["计算", "AI"], "scene": ["继任规划", "培训发展", "晋升评估"], "usage_count": 489, "activity_rate": 73},

    # 行业类
    "industry_internet": {"rule_type": ["手动", "导入"], "scene": ["招聘评估", "人才池筛选"], "usage_count": 345, "activity_rate": 62},
    "industry_ecommerce": {"rule_type": ["手动", "导入"], "scene": ["招聘评估"], "usage_count": 178, "activity_rate": 45},
    "industry_finance": {"rule_type": ["手动", "导入"], "scene": ["招聘评估", "人才池筛选"], "usage_count": 312, "activity_rate": 58},
    "industry_bank": {"rule_type": ["手动", "导入"], "scene": ["招聘评估"], "usage_count": 156, "activity_rate": 42},
    "industry_manufacturing": {"rule_type": ["手动", "导入"], "scene": ["招聘评估", "人才池筛选"], "usage_count": 267, "activity_rate": 53},
    "industry_auto": {"rule_type": ["手动", "导入"], "scene": ["招聘评估"], "usage_count": 134, "activity_rate": 38},
}

# ==================== 第二部分：新增标签 ====================
NEW_TAGS = [
    # 基础信息 - 补充
    {"name": "入职日期", "code": "hire_date", "category": "基础信息", "type": "内置",
     "scene": ["人才盘点", "薪酬调整"], "rule_type": ["自动"],
     "rule_detail": "从HR系统自动获取入职日期", "description": "员工入职时间",
     "status": "启用", "graph_type": "节点", "usage_count": 780, "activity_rate": 86},

    {"name": "合同类型", "code": "contract_type", "category": "基础信息", "type": "内置",
     "scene": ["招聘评估", "人才盘点"], "rule_type": ["自动"],
     "rule_detail": "固定期限/无固定期限/劳务派遣/实习", "description": "劳动合同类型",
     "status": "启用", "graph_type": "节点", "usage_count": 650, "activity_rate": 79},

    {"name": "工作地点", "code": "work_location", "category": "基础信息", "type": "内置",
     "scene": ["招聘评估", "人才池筛选"], "rule_type": ["自动"],
     "rule_detail": "城市/办公地点", "description": "员工工作所在地",
     "status": "启用", "graph_type": "节点", "usage_count": 590, "activity_rate": 75},

    {"name": "薪资等级", "code": "salary_grade", "category": "基础信息", "type": "内置",
     "scene": ["薪酬调整", "人才盘点"], "rule_type": ["自动", "计算"],
     "rule_detail": "G1-G20薪资等级", "description": "员工薪资等级",
     "status": "启用", "graph_type": "节点", "usage_count": 720, "activity_rate": 83},

    # 职业履历 - 补充
    {"name": "证书资质", "code": "certifications", "category": "职业履历", "type": "内置",
     "scene": ["招聘评估", "岗位匹配", "培训发展"], "rule_type": ["手动", "导入"],
     "rule_detail": "专业证书名称、等级、有效期", "description": "持有的专业证书和资质",
     "status": "启用", "graph_type": "关系", "relation_name": "持有证书", "usage_count": 345, "activity_rate": 60},

    {"name": "海外经历", "code": "overseas_exp", "category": "职业履历", "type": "自定义",
     "scene": ["招聘评估", "人才池筛选"], "rule_type": ["手动", "导入"],
     "rule_detail": "海外工作/留学经历", "description": "海外工作或学习经历",
     "status": "启用", "graph_type": "节点", "usage_count": 189, "activity_rate": 43},

    {"name": "内部调动", "code": "internal_transfer", "category": "职业履历", "type": "内置",
     "scene": ["人才盘点", "继任规划"], "rule_type": ["自动"],
     "rule_detail": "部门调动记录", "description": "内部岗位调动历史",
     "status": "启用", "graph_type": "关系", "relation_name": "调动至", "usage_count": 412, "activity_rate": 66},

    # 能力 - 补充
    {"name": "数据分析能力", "code": "data_analysis", "category": "能力", "type": "自定义",
     "scene": ["招聘评估", "人才盘点", "岗位匹配"], "rule_type": ["手动", "AI"],
     "rule_detail": "1-5分，含数据工具熟练度", "description": "数据分析和解读能力",
     "status": "启用", "graph_type": "节点", "usage_count": 378, "activity_rate": 64},

    {"name": "项目管理能力", "code": "project_management", "category": "能力", "type": "自定义",
     "scene": ["人才盘点", "晋升评估", "岗位匹配"], "rule_type": ["手动", "AI"],
     "rule_detail": "1-5分，含PMP等认证加分", "description": "项目规划和管理能力",
     "status": "启用", "graph_type": "节点", "usage_count": 423, "activity_rate": 69},

    {"name": "跨部门协作", "code": "cross_dept_collab", "category": "能力", "type": "自定义",
     "scene": ["人才盘点", "晋升评估"], "rule_type": ["手动", "AI"],
     "rule_detail": "1-5分", "description": "跨部门沟通协调能力",
     "status": "启用", "graph_type": "关系", "relation_name": "协作部门", "usage_count": 289, "activity_rate": 55},

    {"name": "战略思维", "code": "strategic_thinking", "category": "能力", "type": "自定义",
     "scene": ["人才盘点", "晋升评估", "继任规划"], "rule_type": ["手动", "AI"],
     "rule_detail": "1-5分", "description": "战略规划和全局思维能力",
     "status": "启用", "graph_type": "节点", "usage_count": 312, "activity_rate": 58},

    {"name": "客户导向", "code": "customer_orientation", "category": "能力", "type": "自定义",
     "scene": ["人才盘点", "绩效管理"], "rule_type": ["手动", "AI"],
     "rule_detail": "1-5分", "description": "以客户为中心的服务意识",
     "status": "启用", "graph_type": "节点", "usage_count": 267, "activity_rate": 52},

    # 素质 - 补充
    {"name": "情绪管理", "code": "emotional_management", "category": "素质", "type": "自定义",
     "scene": ["招聘评估", "人才盘点"], "rule_type": ["手动", "AI"],
     "rule_detail": "1-5分", "description": "情绪控制和管理能力",
     "status": "启用", "graph_type": "节点", "usage_count": 234, "activity_rate": 49},

    {"name": "自驱力", "code": "self_motivation", "category": "素质", "type": "自定义",
     "scene": ["人才盘点", "晋升评估"], "rule_type": ["手动", "AI"],
     "rule_detail": "1-5分", "description": "自我驱动和目标导向",
     "status": "启用", "graph_type": "节点", "usage_count": 356, "activity_rate": 62},

    {"name": "全局观", "code": "big_picture", "category": "素质", "type": "自定义",
     "scene": ["人才盘点", "晋升评估", "继任规划"], "rule_type": ["手动", "AI"],
     "rule_detail": "1-5分", "description": "全局视野和大局意识",
     "status": "启用", "graph_type": "节点", "usage_count": 278, "activity_rate": 54},

    # 复合标签 - 补充
    {"name": "业务骨干", "code": "business_backbone", "category": "复合标签", "type": "自定义",
     "scene": ["人才盘点", "人才池筛选", "绩效管理"], "rule_type": ["计算", "AI"],
     "rule_detail": "绩效B+以上+工作年限3年+专业能力强", "description": "业务领域的核心骨干",
     "status": "启用", "graph_type": "节点", "usage_count": 567, "activity_rate": 78},

    {"name": "新星员工", "code": "rising_star", "category": "复合标签", "type": "自定义",
     "scene": ["人才盘点", "培训发展", "晋升评估"], "rule_type": ["计算", "AI"],
     "rule_detail": "入职2年内+绩效A+学习能力强", "description": "快速成长的新员工",
     "status": "启用", "graph_type": "节点", "usage_count": 423, "activity_rate": 71},

    {"name": "跨界人才", "code": "cross_domain", "category": "复合标签", "type": "自定义",
     "scene": ["人才盘点", "人才池筛选", "岗位匹配"], "rule_type": ["计算", "AI"],
     "rule_detail": "多行业经验+多岗位经历+适应性强", "description": "具有跨领域经验的复合型人才",
     "status": "启用", "graph_type": "节点", "usage_count": 234, "activity_rate": 51},

    {"name": "文化大使", "code": "culture_ambassador", "category": "复合标签", "type": "自定义",
     "scene": ["人才盘点", "绩效管理"], "rule_type": ["手动", "AI"],
     "rule_detail": "价值观匹配高+团队协作强+主动性高", "description": "企业文化的积极传播者",
     "status": "启用", "graph_type": "节点", "usage_count": 189, "activity_rate": 44},

    {"name": "待发展人才", "code": "needs_development", "category": "复合标签", "type": "自定义",
     "scene": ["人才盘点", "培训发展"], "rule_type": ["计算", "AI"],
     "rule_detail": "潜力高+当前绩效中等+需要培养", "description": "有潜力但需要进一步培养的人才",
     "status": "启用", "graph_type": "节点", "usage_count": 345, "activity_rate": 61},

    # 行业 - 补充
    {"name": "医疗健康", "code": "industry_healthcare", "category": "行业", "type": "内置",
     "scene": ["招聘评估", "人才池筛选"], "rule_type": ["手动", "导入"],
     "rule_detail": "一级行业", "description": "医疗健康行业",
     "status": "启用", "graph_type": "节点", "usage_count": 234, "activity_rate": 50},

    {"name": "教育培训", "code": "industry_education", "category": "行业", "type": "内置",
     "scene": ["招聘评估", "人才池筛选"], "rule_type": ["手动", "导入"],
     "rule_detail": "一级行业", "description": "教育培训行业",
     "status": "启用", "graph_type": "节点", "usage_count": 198, "activity_rate": 46},

    {"name": "房地产", "code": "industry_realestate", "category": "行业", "type": "内置",
     "scene": ["招聘评估", "人才池筛选"], "rule_type": ["手动", "导入"],
     "rule_detail": "一级行业", "description": "房地产行业",
     "status": "启用", "graph_type": "节点", "usage_count": 167, "activity_rate": 41},

    {"name": "新能源", "code": "industry_new_energy", "category": "行业", "type": "内置",
     "scene": ["招聘评估", "人才池筛选"], "rule_type": ["手动", "导入"],
     "rule_detail": "一级行业", "description": "新能源行业",
     "status": "启用", "graph_type": "节点", "usage_count": 212, "activity_rate": 48},

    {"name": "人工智能", "code": "industry_ai", "category": "行业", "type": "内置",
     "scene": ["招聘评估", "人才池筛选"], "rule_type": ["手动", "导入"],
     "rule_detail": "二级行业（互联网子行业）", "description": "人工智能行业",
     "status": "启用", "graph_type": "节点", "usage_count": 289, "activity_rate": 57,
     "parent_code": "industry_internet"},

    {"name": "保险", "code": "industry_insurance", "category": "行业", "type": "内置",
     "scene": ["招聘评估"], "rule_type": ["手动", "导入"],
     "rule_detail": "二级行业（金融子行业）", "description": "保险行业",
     "status": "启用", "graph_type": "节点", "usage_count": 145, "activity_rate": 39,
     "parent_code": "industry_finance"},
]


def get_db_connection():
    return pymysql.connect(**DB_CONFIG)


def update_existing_tags(cursor, connection):
    """更新现有标签的 rule_type、scene、usage_count、activity_rate"""
    print(f"\n正在更新 {len(EXISTING_TAG_UPDATES)} 条现有标签...")

    update_sql = """
    UPDATE tags
    SET rule_type = %s, scene = %s, usage_count = %s, activity_rate = %s
    WHERE code = %s
    """

    updated = 0
    for code, data in EXISTING_TAG_UPDATES.items():
        rule_type_json = json.dumps(data["rule_type"], ensure_ascii=False)
        scene_json = json.dumps(data["scene"], ensure_ascii=False)

        cursor.execute(update_sql, (
            rule_type_json,
            scene_json,
            data["usage_count"],
            data["activity_rate"],
            code
        ))
        if cursor.rowcount > 0:
            updated += 1
            print(f"  ✓ 更新: {code} (rule_type={data['rule_type']}, usage={data['usage_count']})")
        else:
            print(f"  ⚠️ 未找到: {code}")

    connection.commit()
    print(f"\n✅ 更新完成: {updated}/{len(EXISTING_TAG_UPDATES)} 条")


def add_new_tags(cursor, connection):
    """新增标签"""
    print(f"\n正在新增 {len(NEW_TAGS)} 条标签...")

    # 先获取现有 code -> id 映射（用于 parent_code 解析）
    cursor.execute("SELECT id, code FROM tags")
    code_to_id = {row[1]: row[0] for row in cursor.fetchall()}

    insert_sql = """
    INSERT INTO tags (name, code, category, type, scene, rule_type, rule_detail,
                     description, status, parent_id, graph_type, relation_name,
                     usage_count, activity_rate)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    inserted = 0
    skipped = 0
    for tag in NEW_TAGS:
        # 检查是否已存在
        if tag["code"] in code_to_id:
            print(f"  ⏭️ 已存在: {tag['name']} ({tag['code']})")
            skipped += 1
            continue

        # 解析 parent_code
        parent_id = None
        if "parent_code" in tag:
            parent_id = code_to_id.get(tag["parent_code"])
            if parent_id is None:
                print(f"  ⚠️ 父标签未找到: {tag['parent_code']}，跳过 {tag['name']}")
                continue

        scene_json = json.dumps(tag["scene"], ensure_ascii=False)
        rule_type_json = json.dumps(tag["rule_type"], ensure_ascii=False)

        cursor.execute(insert_sql, (
            tag["name"],
            tag["code"],
            tag["category"],
            tag["type"],
            scene_json,
            rule_type_json,
            tag.get("rule_detail"),
            tag.get("description"),
            tag["status"],
            parent_id,
            tag.get("graph_type"),
            tag.get("relation_name"),
            tag.get("usage_count", 0),
            tag.get("activity_rate", 0),
        ))

        new_id = cursor.lastrowid
        code_to_id[tag["code"]] = new_id
        inserted += 1
        print(f"  ✓ 新增: {tag['name']} ({tag['code']}) ID={new_id}")

    connection.commit()
    print(f"\n✅ 新增完成: {inserted} 条, 跳过: {skipped} 条")


def verify_data(cursor):
    """验证数据"""
    print("\n正在验证数据...")

    cursor.execute("SELECT COUNT(*) FROM tags")
    total = cursor.fetchone()[0]
    print(f"  总记录数: {total}")

    cursor.execute("""
        SELECT category, COUNT(*) as cnt
        FROM tags GROUP BY category ORDER BY cnt DESC
    """)
    print("\n  分类统计:")
    for row in cursor.fetchall():
        print(f"    {row[0]}: {row[1]} 条")

    cursor.execute("SELECT COUNT(*) FROM tags WHERE usage_count > 0")
    with_usage = cursor.fetchone()[0]
    print(f"\n  有使用数据的标签: {with_usage}")

    cursor.execute("SELECT AVG(activity_rate) FROM tags WHERE activity_rate > 0")
    avg_rate = cursor.fetchone()[0]
    print(f"  平均活跃度: {avg_rate:.1f}%")


def main():
    print("=" * 60)
    print("标签库数据更新与扩充脚本")
    print("=" * 60)

    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        print("✅ 数据库连接成功")

        # 第一步：更新现有标签
        update_existing_tags(cursor, connection)

        # 第二步：新增标签
        add_new_tags(cursor, connection)

        # 第三步：验证
        verify_data(cursor)

        print("\n" + "=" * 60)
        print("✅ 数据更新与扩充完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        if connection:
            connection.rollback()
        raise
    finally:
        if connection:
            connection.close()
            print("\n数据库连接已关闭")


if __name__ == "__main__":
    main()

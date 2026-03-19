"""
为时间倒序前20个标签创建规则数据
"""
from database import SessionLocal
from models import SysTag, SysTagTriggerRule, SysTagTriggerCondition, SysTagTriggerAction
from sqlalchemy import desc
from datetime import datetime
import re

db = SessionLocal()

# 获取时间倒序前20个标签
tags = db.query(SysTag).filter(SysTag.del_flag == '0').order_by(desc(SysTag.update_time)).limit(20).all()

print(f'找到 {len(tags)} 个标签')
print()

created_count = 0
skipped_count = 0

for tag in tags:
    # 检查是否已有规则
    existing_rule = db.query(SysTagTriggerRule).filter(
        SysTagTriggerRule.tag_name == tag.tag_name,
        SysTagTriggerRule.del_flag == '0'
    ).first()

    if existing_rule:
        print(f'跳过 {tag.tag_name} (已有规则 rule_id={existing_rule.rule_id})')
        skipped_count += 1
        continue

    # 解析 rule_detail 获取条件信息
    rule_detail = tag.rule_detail or ''

    # 提取数据源表和字段
    # 格式: "数据源: TAL_STAFF.FIELD_NAME, 条件: FIELD_NAME = 'value'"
    table_field = None
    condition_str = None

    if '数据源:' in rule_detail and '条件:' in rule_detail:
        parts = rule_detail.split('条件:')
        if len(parts) == 2:
            # 提取表.字段
            source_part = parts[0].replace('数据源:', '').strip()
            if ',' in source_part:
                source_part = source_part.split(',')[0].strip()
            table_field = source_part

            # 提取条件
            condition_str = parts[1].strip()

    if not table_field or not condition_str:
        print(f'跳过 {tag.tag_name} (无法解析规则: {rule_detail})')
        skipped_count += 1
        continue

    # 解析条件获取操作符和值
    operator = None
    value = None
    field_name = table_field.split('.')[-1] if '.' in table_field else table_field

    # 匹配不同的操作符
    if ' LIKE ' in condition_str.upper():
        operator = 'LIKE'
        # 提取 LIKE 后面的值
        match = re.search(r"LIKE\s+['\"](.+?)['\"]", condition_str, re.IGNORECASE)
        if match:
            value = match.group(1)
    elif ' = ' in condition_str:
        operator = '='
        # 提取 = 后面的值
        match = re.search(r"=\s+['\"](.+?)['\"]", condition_str)
        if match:
            value = match.group(1)
    elif ' >= ' in condition_str and ' AND ' in condition_str.upper():
        # 范围条件，如: AGE >= 18 AND AGE <= 35
        operator = 'BETWEEN'
        # 提取两个数值
        matches = re.findall(r'(\d+)', condition_str)
        if len(matches) >= 2:
            value = f"{matches[0]},{matches[1]}"
    elif ' >= ' in condition_str:
        operator = '>='
        match = re.search(r'>=\s+(\d+)', condition_str)
        if match:
            value = match.group(1)

    if not operator or not value:
        print(f'跳过 {tag.tag_name} (无法解析条件: {condition_str})')
        skipped_count += 1
        continue

    now = datetime.now()

    # 创建触发规则
    new_rule = SysTagTriggerRule(
        model_id='default',
        tag_name=tag.tag_name,
        tag_category=tag.tag_category,
        rule_type='single_indicator',
        logic='AND',
        status='1',
        del_flag='0',
        create_time=now,
        update_time=now,
    )
    db.add(new_rule)
    db.flush()  # 获取 rule_id

    # 创建触发条件
    new_condition = SysTagTriggerCondition(
        rule_id=new_rule.rule_id,
        type='field_compare',
        target_id=table_field,
        target_name=field_name,
        operator=operator,
        value=value,
        status='1',
        del_flag='0',
        create_time=now,
        update_time=now,
    )
    db.add(new_condition)

    # 创建触发动作
    new_action = SysTagTriggerAction(
        rule_id=new_rule.rule_id,
        type='add_to_talent_tag',
        config=f'{{"tag_id": {tag.tag_id}, "tag_name": "{tag.tag_name}"}}',
        status='1',
        del_flag='0',
        create_time=now,
        update_time=now,
    )
    db.add(new_action)

    created_count += 1
    print(f'✓ 创建规则: {tag.tag_name}')
    print(f'  rule_id={new_rule.rule_id}')
    print(f'  条件: {table_field} {operator} {value}')
    print()

db.commit()
print(f'\n✅ 成功创建 {created_count} 个规则')
print(f'⏭️  跳过 {skipped_count} 个标签')

db.close()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
恢复被删除的229条标签并重新归类到6个分类中
分类映射规则：
- 教育 → 基础信息
- 特质 → 素质
- 风险 → 复合标签
- 潜力 → 复合标签
- 绩效 → 复合标签
- 经验 → 职业履历
- 行为 → 能力
- 发展 → 复合标签
- 专业 → 能力
"""

import json
import pymysql

DB_CONFIG = {
    'host': '139.196.207.85',
    'port': 9896,
    'user': 'root',
    'password': 'myDHR2023.COM',
    'database': 'mydhr',
    'charset': 'utf8mb4'
}

# 分类映射：旧分类 → 新分类
CATEGORY_MAP = {
    '教育': '基础信息',
    '特质': '素质',
    '风险': '复合标签',
    '潜力': '复合标签',
    '绩效': '复合标签',
    '经验': '职业履历',
    '行为': '能力',
    '发展': '复合标签',
    '专业': '能力',
}

# 被删除的229条标签数据 (id, name, code, old_category)
DELETED_TAGS = [
    # === 专业 → 能力 ===
    (94, '技术开发', 'major_188'),
    (95, '数据技术', 'major_194'),
    (96, '管理类', 'major_198'),
    (97, '职能类', 'major_203'),
    (98, '技术架构', 'major_208'),
    (225, 'Java开发', 'major_189'),
    (226, 'Python开发', 'major_190'),
    (227, '前端开发', 'major_191'),
    (228, '算法工程', 'major_192'),
    (229, 'AI/ML', 'major_193'),
    (230, '数据分析', 'major_195'),
    (231, '大数据', 'major_196'),
    (232, '云计算', 'major_197'),
    (233, '项目管理', 'major_199'),
    (234, '产品设计', 'major_200'),
    (235, '供应链管理', 'major_201'),
    (236, '质量管理', 'major_202'),
    (237, '财务分析', 'major_204'),
    (238, '法务合规', 'major_205'),
    (239, '市场营销', 'major_206'),
    (240, '人力资源', 'major_207'),
    (241, '架构设计', 'major_209'),
    (242, 'DevOps', 'major_210'),
    (243, '信息安全', 'major_211'),

    # === 教育 → 基础信息 ===
    (109, '院校层次', 'edu_254'),
    (110, '专业背景', 'edu_259'),
    (111, '学位类型', 'edu_263'),
    (112, '职业资格', 'edu_268'),
    (276, '985院校', 'edu_255'),
    (277, '211院校', 'edu_256'),
    (278, '海外院校', 'edu_257'),
    (279, 'QS100', 'edu_258'),
    (280, '理工科', 'edu_260'),
    (281, '商科', 'edu_261'),
    (282, '文科', 'edu_262'),
    (283, '双学位', 'edu_264'),
    (284, '在职研究生', 'edu_265'),
    (285, 'MBA', 'edu_266'),
    (286, 'EMBA', 'edu_267'),
    (287, 'CPA', 'edu_269'),
    (288, 'PMP', 'edu_270'),
    (289, 'CFA', 'edu_271'),
    (290, '律师资格', 'edu_272'),
    (291, '建造师', 'edu_273'),
    (292, '会计师', 'edu_274'),
    (293, '工程师', 'edu_275'),
    (294, '经济师', 'edu_276'),

    # === 特质 → 素质 ===
    (113, '工作态度', 'trait_277'),
    (114, '协作特质', 'trait_282'),
    (115, '个人品质', 'trait_287'),
    (116, '心理特质', 'trait_292'),
    (117, '思维特质', 'trait_295'),
    (118, '驱动力', 'trait_299'),
    (295, '高敬业度', 'trait_278'),
    (296, '高责任心', 'trait_279'),
    (297, '积极主动', 'trait_280'),
    (298, '追求卓越', 'trait_281'),
    (299, '乐于分享', 'trait_283'),
    (300, '善于合作', 'trait_284'),
    (301, '开放包容', 'trait_285'),
    (302, '同理心强', 'trait_286'),
    (303, '诚实守信', 'trait_288'),
    (304, '正直谦逊', 'trait_289'),
    (305, '自律性强', 'trait_290'),
    (306, '好奇心强', 'trait_291'),
    (307, '坚韧不拔', 'trait_293'),
    (308, '情绪稳定', 'trait_294'),
    (309, '创新思维', 'trait_296'),
    (310, '系统思维', 'trait_297'),
    (311, '批判性思维', 'trait_298'),
    (312, '自我驱动', 'trait_300'),
    (313, '结果导向', 'trait_301'),

    # === 风险 → 复合标签 ===
    (119, '绩效风险', 'risk_305'),
    (120, '合规风险', 'risk_308'),
    (121, '健康风险', 'risk_312'),
    (122, '满意度风险', 'risk_315'),
    (123, '能力风险', 'risk_321'),
    (124, '组织风险', 'risk_324'),
    (314, '绩效下滑', 'risk_306'),
    (315, '倦怠风险', 'risk_307'),
    (316, '合规风险', 'risk_309'),
    (317, '竞业限制', 'risk_310'),
    (318, '劳动纠纷', 'risk_311'),
    (319, '健康风险', 'risk_313'),
    (320, '加班过度', 'risk_314'),
    (321, '满意度低', 'risk_316'),
    (322, '薪酬竞争力低', 'risk_317'),
    (323, '晋升瓶颈', 'risk_318'),
    (324, '关系紧张', 'risk_319'),
    (325, '文化适配低', 'risk_320'),
    (326, '技能过时', 'risk_322'),
    (327, '替代性高', 'risk_323'),
    (328, '关键岗位空缺', 'risk_325'),
    (329, '团队不稳定', 'risk_326'),
    (330, '考勤异常', 'risk_327'),
    (424, '离职风险', 'risk_lzfx'),
    (426, '离职风险高', 'risk_lzfx_h'),
    (427, '离职风险中', 'risk_lzfx_m'),
    (428, '离职风险低', 'risk_lzfx_l'),

    # === 潜力 → 复合标签 ===
    (125, '综合潜力', 'potential_328'),
    (126, '管理潜力', 'potential_332'),
    (127, '技术潜力', 'potential_336'),
    (128, '发展潜力', 'potential_339'),
    (129, '成长特征', 'potential_343'),
    (130, '动机特征', 'potential_348'),
    (331, '高潜力', 'potential_329'),
    (332, '中等潜力', 'potential_330'),
    (333, '稳定贡献者', 'potential_331'),
    (334, '管理潜力高', 'potential_333'),
    (335, '领导力潜力', 'potential_334'),
    (336, '战略视野潜力', 'potential_335'),
    (337, '技术潜力高', 'potential_337'),
    (338, '创新潜力', 'potential_338'),
    (339, '国际化潜力', 'potential_340'),
    (340, '跨界潜力', 'potential_341'),
    (341, '复合型潜力', 'potential_342'),
    (342, '成长速度快', 'potential_344'),
    (343, '学习曲线陡', 'potential_345'),
    (344, '适应性强', 'potential_346'),
    (345, '可塑性强', 'potential_347'),
    (346, '高成就动机', 'potential_349'),
    (347, '目标导向强', 'potential_350'),
    (348, '自我提升', 'potential_351'),
    (349, '变革推动', 'potential_352'),
    (350, '人才培养潜力', 'potential_353'),

    # === 绩效 → 复合标签 ===
    (131, '绩效等级', 'perf_354'),
    (132, '绩效趋势', 'perf_360'),
    (133, 'KPI达成', 'perf_364'),
    (134, 'OKR完成', 'perf_367'),
    (135, '荣誉奖项', 'perf_369'),
    (136, '贡献表现', 'perf_372'),
    (351, '绩效卓越', 'perf_355'),
    (352, '绩效优秀', 'perf_356'),
    (353, '绩效良好', 'perf_357'),
    (354, '绩效合格', 'perf_358'),
    (355, '绩效待改进', 'perf_359'),
    (356, '绩效连续优秀', 'perf_361'),
    (357, '绩效进步明显', 'perf_362'),
    (358, '绩效稳定', 'perf_363'),
    (359, 'KPI超额达成', 'perf_365'),
    (360, 'KPI达标', 'perf_366'),
    (361, 'OKR完成率高', 'perf_368'),
    (362, '季度之星', 'perf_370'),
    (363, '年度优秀', 'perf_371'),
    (364, '项目贡献突出', 'perf_373'),
    (365, '客户满意度高', 'perf_374'),
    (366, '质量零缺陷', 'perf_375'),
    (367, '效率标杆', 'perf_376'),
    (368, '成本控制优秀', 'perf_377'),
    (369, '创新贡献', 'perf_378'),
    (370, '团队贡献', 'perf_379'),

    # === 经验 → 职业履历 ===
    (137, '业务经验', 'exp_386'),
    (138, '优化经验', 'exp_393'),
    (139, '培养经验', 'exp_396'),
    (140, '协作经验', 'exp_399'),
    (371, '国际业务', 'exp_387'),
    (372, '并购整合', 'exp_388'),
    (373, '新业务开拓', 'exp_389'),
    (374, '产品上市', 'exp_390'),
    (375, '融资经验', 'exp_391'),
    (376, '上市经验', 'exp_392'),
    (377, '流程优化', 'exp_394'),
    (378, '数字化转型', 'exp_395'),
    (379, '培训授课', 'exp_397'),
    (380, '导师经验', 'exp_398'),
    (381, '跨领域', 'exp_400'),
    (382, '跨文化协作', 'exp_401'),
    (383, '公关经验', 'exp_402'),
    (384, '政府关系', 'exp_403'),
    (425, '管理经验', 'exp_gljy'),
    (429, '项目管理', 'exp_xmgl'),
    (430, '团队管理', 'exp_tdgl'),
    (431, '客户管理', 'exp_khgl'),
    (432, '供应商管理', 'exp_gysgl'),
    (433, '危机管理', 'exp_wjgl'),
    (434, '变革管理', 'exp_bggl'),

    # === 行为 → 能力 ===
    (141, '协作行为', 'behavior_404'),
    (142, '沟通行为', 'behavior_407'),
    (143, '学习行为', 'behavior_411'),
    (144, '创新行为', 'behavior_414'),
    (145, '执行行为', 'behavior_417'),
    (146, '规范行为', 'behavior_421'),
    (147, '服务行为', 'behavior_425'),
    (148, '适应行为', 'behavior_427'),
    (385, '协作优秀', 'behavior_405'),
    (386, '团队建设积极', 'behavior_406'),
    (387, '沟通积极', 'behavior_408'),
    (388, '反馈及时', 'behavior_409'),
    (389, '会议积极', 'behavior_410'),
    (390, '学习持续', 'behavior_412'),
    (391, '知识分享活跃', 'behavior_413'),
    (392, '创新活跃', 'behavior_415'),
    (393, '指导乐于', 'behavior_416'),
    (394, '执行力强', 'behavior_418'),
    (395, '问题解决高效', 'behavior_419'),
    (396, '时间管理优秀', 'behavior_420'),
    (397, '合规规范', 'behavior_422'),
    (398, '安全达标', 'behavior_423'),
    (399, '出勤优秀', 'behavior_424'),
    (400, '客户服务优质', 'behavior_426'),
    (401, '变革适应快', 'behavior_428'),
    (402, '冲突处理妥当', 'behavior_429'),
    (403, '自我管理优秀', 'behavior_430'),

    # === 发展 → 复合标签 ===
    (149, '管理培养', 'develop_431'),
    (150, '技术培养', 'develop_436'),
    (151, '导师培养', 'develop_439'),
    (152, '发展计划', 'develop_443'),
    (153, '发展状态', 'develop_448'),
    (154, '发展方向', 'develop_453'),
    (404, '储备干部', 'develop_432'),
    (405, '高管继任候选', 'develop_433'),
    (406, '管理培训生', 'develop_434'),
    (407, '管理路线', 'develop_435'),
    (408, '技术带头人培养', 'develop_437'),
    (409, '专家路线', 'develop_438'),
    (410, '导师候选', 'develop_440'),
    (411, '内部讲师', 'develop_441'),
    (412, '教练候选', 'develop_442'),
    (413, '轮岗计划中', 'develop_444'),
    (414, 'IDP进行中', 'develop_445'),
    (415, '项目历练中', 'develop_446'),
    (416, '挂职锻炼', 'develop_447'),
    (417, '培训完成率高', 'develop_449'),
    (418, '认证进行中', 'develop_450'),
    (419, '晋升准备就绪', 'develop_451'),
    (420, '学历提升中', 'develop_452'),
    (421, '横向发展中', 'develop_454'),
    (422, '国际化发展', 'develop_455'),
    (423, '创新孵化候选', 'develop_456'),
]

# 旧分类前缀 → 旧分类名
PREFIX_TO_OLD_CATEGORY = {
    'major_': '专业',
    'edu_': '教育',
    'trait_': '特质',
    'risk_': '风险',
    'potential_': '潜力',
    'perf_': '绩效',
    'exp_': '经验',
    'behavior_': '行为',
    'develop_': '发展',
}


def get_old_category(code):
    for prefix, cat in PREFIX_TO_OLD_CATEGORY.items():
        if code.startswith(prefix):
            return cat
    return None


def get_new_category(code):
    old = get_old_category(code)
    if old:
        return CATEGORY_MAP.get(old, old)
    return None


def main():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 检查哪些 id 已存在（避免重复插入）
    all_ids = [t[0] for t in DELETED_TAGS]
    placeholders = ','.join(['%s'] * len(all_ids))
    cursor.execute(f'SELECT id FROM tags WHERE id IN ({placeholders})', all_ids)
    existing_ids = {row[0] for row in cursor.fetchall()}

    # 也检查 code 是否已存在
    all_codes = [t[2] for t in DELETED_TAGS]
    placeholders_c = ','.join(['%s'] * len(all_codes))
    cursor.execute(f'SELECT code FROM tags WHERE code IN ({placeholders_c})', all_codes)
    existing_codes = {row[0] for row in cursor.fetchall()}

    insert_sql = """
    INSERT INTO tags (id, name, code, category, type, status, graph_type)
    VALUES (%s, %s, %s, %s, '自定义', '启用', '节点')
    """

    inserted = 0
    skipped = 0
    for tag_id, name, code in DELETED_TAGS:
        if tag_id in existing_ids or code in existing_codes:
            skipped += 1
            continue

        new_cat = get_new_category(code)
        if not new_cat:
            print(f'  ⚠️ 无法确定分类: {name}({code})')
            continue

        cursor.execute(insert_sql, (tag_id, name, code, new_cat))
        inserted += 1

    conn.commit()
    print(f'✅ 恢复完成: 插入 {inserted} 条, 跳过 {skipped} 条(已存在)')

    # 验证
    cursor.execute('SELECT category, COUNT(*) FROM tags GROUP BY category ORDER BY COUNT(*) DESC')
    print('\n分类统计:')
    total = 0
    for row in cursor.fetchall():
        print(f'  {row[0]}: {row[1]} 条')
        total += row[1]
    print(f'  合计: {total} 条')

    conn.close()


if __name__ == '__main__':
    main()

-- 更新标签的相似标签和互斥标签数据
-- 相似标签：与该标签是近义词的标签（1-2个，没有则不填）
-- 互斥标签：不能同时出现在同一个人身上的标签（1-2个，没有则不填）
-- 执行时间: 2026-03-18

-- ==================== 第一步：清空所有标签的相似和互斥数据 ====================
UPDATE sys_tag SET similar_tags = NULL, exclusive_tags = NULL;

-- ==================== 第二步：按需更新 ====================

-- ==================== 基础信息类 ====================

-- 年龄
UPDATE sys_tag SET
  similar_tags = NULL,
  exclusive_tags = NULL
WHERE tag_code ='age';

-- 性别
UPDATE sys_tag SET
  similar_tags = NULL,
  exclusive_tags = NULL
WHERE tag_code ='gender';

-- 学历
UPDATE sys_tag SET
  similar_tags = NULL,
  exclusive_tags = NULL
WHERE tag_code ='education';

-- 工作年限
UPDATE sys_tag SET
  similar_tags = NULL,
  exclusive_tags = NULL
WHERE tag_code ='work_years';

-- 职级
UPDATE sys_tag SET
  similar_tags = '岗位',
  exclusive_tags = NULL
WHERE tag_code ='job_level';

-- 部门
UPDATE sys_tag SET
  similar_tags = NULL,
  exclusive_tags = NULL
WHERE tag_code ='department';

-- 岗位
UPDATE sys_tag SET
  similar_tags = '职级',
  exclusive_tags = NULL
WHERE tag_code ='position';

-- 入职日期
UPDATE sys_tag SET
  similar_tags = NULL,
  exclusive_tags = NULL
WHERE tag_code ='hire_date';

-- 合同类型
UPDATE sys_tag SET
  similar_tags = NULL,
  exclusive_tags = NULL
WHERE tag_code ='contract_type';

-- 工作地点
UPDATE sys_tag SET
  similar_tags = NULL,
  exclusive_tags = NULL
WHERE tag_code ='work_location';

-- 薪资等级
UPDATE sys_tag SET
  similar_tags = '职级',
  exclusive_tags = NULL
WHERE tag_code ='salary_grade';

-- ==================== 职业履历类 ====================

-- 项目经验
UPDATE sys_tag SET
  similar_tags = NULL,
  exclusive_tags = NULL
WHERE tag_code ='project_exp';

-- 管理经验
UPDATE sys_tag SET
  similar_tags = '领导力',
  exclusive_tags = NULL
WHERE tag_code ='management_exp';

-- 行业经验
UPDATE sys_tag SET
  similar_tags = NULL,
  exclusive_tags = NULL
WHERE tag_code ='industry_exp';

-- 跳槽频率
UPDATE sys_tag SET
  similar_tags = '离职风险',
  exclusive_tags = '敬业度'
WHERE tag_code ='job_change_freq';

-- 晋升记录
UPDATE sys_tag SET
  similar_tags = NULL,
  exclusive_tags = NULL
WHERE tag_code ='promotion_history';

-- 培训经历
UPDATE sys_tag SET
  similar_tags = NULL,
  exclusive_tags = NULL
WHERE tag_code ='training_history';

-- 获奖记录
UPDATE sys_tag SET
  similar_tags = '证书资质',
  exclusive_tags = NULL
WHERE tag_code ='awards';

-- 离职风险
UPDATE sys_tag SET
  similar_tags = '跳槽频率',
  exclusive_tags = '敬业度,高潜人才'
WHERE tag_code ='turnover_risk';

-- 证书资质
UPDATE sys_tag SET
  similar_tags = '获奖记录',
  exclusive_tags = NULL
WHERE tag_code ='certifications';

-- 海外经历
UPDATE sys_tag SET
  similar_tags = NULL,
  exclusive_tags = NULL
WHERE tag_code ='overseas_exp';

-- 内部调动
UPDATE sys_tag SET
  similar_tags = '晋升记录',
  exclusive_tags = NULL
WHERE tag_code ='internal_transfer';

-- ==================== 能力类 ====================

-- 技术能力
UPDATE sys_tag SET
  similar_tags = NULL,
  exclusive_tags = NULL
WHERE tag_code ='technical_skill';

-- 沟通能力
UPDATE sys_tag SET
  similar_tags = '跨部门协作',
  exclusive_tags = NULL
WHERE tag_code ='communication';

-- 领导力
UPDATE sys_tag SET
  similar_tags = '管理经验',
  exclusive_tags = NULL
WHERE tag_code ='leadership';

-- 学习能力
UPDATE sys_tag SET
  similar_tags = '适应性',
  exclusive_tags = NULL
WHERE tag_code ='learning_ability';

-- 问题解决
UPDATE sys_tag SET
  similar_tags = NULL,
  exclusive_tags = NULL
WHERE tag_code ='problem_solving';

-- 创新能力
UPDATE sys_tag SET
  similar_tags = NULL,
  exclusive_tags = NULL
WHERE tag_code ='innovation';

-- 执行力
UPDATE sys_tag SET
  similar_tags = '主动性',
  exclusive_tags = NULL
WHERE tag_code ='execution';

-- 抗压能力
UPDATE sys_tag SET
  similar_tags = '情绪管理',
  exclusive_tags = NULL
WHERE tag_code ='stress_resistance';

-- 数据分析能力
UPDATE sys_tag SET
  similar_tags = '技术能力',
  exclusive_tags = NULL
WHERE tag_code ='data_analysis';

-- 项目管理能力
UPDATE sys_tag SET
  similar_tags = '管理经验',
  exclusive_tags = NULL
WHERE tag_code ='project_management';

-- 跨部门协作
UPDATE sys_tag SET
  similar_tags = '沟通能力,团队协作',
  exclusive_tags = NULL
WHERE tag_code ='cross_dept_collab';

-- 战略思维
UPDATE sys_tag SET
  similar_tags = '全局观',
  exclusive_tags = NULL
WHERE tag_code ='strategic_thinking';

-- 客户导向
UPDATE sys_tag SET
  similar_tags = NULL,
  exclusive_tags = NULL
WHERE tag_code ='customer_orientation';

-- ==================== 素质类 ====================

-- 责任心
UPDATE sys_tag SET
  similar_tags = '敬业度',
  exclusive_tags = NULL
WHERE tag_code ='responsibility';

-- 团队协作
UPDATE sys_tag SET
  similar_tags = '跨部门协作',
  exclusive_tags = NULL
WHERE tag_code ='teamwork';

-- 主动性
UPDATE sys_tag SET
  similar_tags = '自驱力,执行力',
  exclusive_tags = '待发展人才'
WHERE tag_code ='initiative';

-- 诚信度
UPDATE sys_tag SET
  similar_tags = NULL,
  exclusive_tags = NULL
WHERE tag_code ='integrity';

-- 敬业度
UPDATE sys_tag SET
  similar_tags = '责任心',
  exclusive_tags = '离职风险'
WHERE tag_code ='dedication';

-- 适应性
UPDATE sys_tag SET
  similar_tags = '学习能力',
  exclusive_tags = NULL
WHERE tag_code ='adaptability';

-- 价值观匹配
UPDATE sys_tag SET
  similar_tags = NULL,
  exclusive_tags = '离职风险'
WHERE tag_code ='value_fit';

-- 情绪管理
UPDATE sys_tag SET
  similar_tags = '抗压能力',
  exclusive_tags = NULL
WHERE tag_code ='emotional_management';

-- 自驱力
UPDATE sys_tag SET
  similar_tags = '主动性',
  exclusive_tags = '待发展人才'
WHERE tag_code ='self_motivation';

-- 全局观
UPDATE sys_tag SET
  similar_tags = '战略思维',
  exclusive_tags = NULL
WHERE tag_code ='big_picture';

-- ==================== 复合标签 ====================

-- 高潜人才
UPDATE sys_tag SET
  similar_tags = '关键人才',
  exclusive_tags = '待发展人才'
WHERE tag_code ='high_potential';

-- 关键人才
UPDATE sys_tag SET
  similar_tags = '高潜人才,业务骨干',
  exclusive_tags = '待发展人才'
WHERE tag_code ='key_talent';

-- 技术专家
UPDATE sys_tag SET
  similar_tags = '业务骨干',
  exclusive_tags = '待发展人才'
WHERE tag_code ='technical_expert';

-- 管理储备
UPDATE sys_tag SET
  similar_tags = '高潜人才',
  exclusive_tags = '待发展人才'
WHERE tag_code ='management_reserve';

-- 业务骨干
UPDATE sys_tag SET
  similar_tags = '关键人才,技术专家',
  exclusive_tags = '待发展人才'
WHERE tag_code ='business_backbone';

-- 新星员工
UPDATE sys_tag SET
  similar_tags = '高潜人才',
  exclusive_tags = NULL
WHERE tag_code ='rising_star';

-- 跨界人才
UPDATE sys_tag SET
  similar_tags = NULL,
  exclusive_tags = NULL
WHERE tag_code ='cross_domain';

-- 文化大使
UPDATE sys_tag SET
  similar_tags = '价值观匹配',
  exclusive_tags = NULL
WHERE tag_code ='culture_ambassador';

-- 待发展人才
UPDATE sys_tag SET
  similar_tags = NULL,
  exclusive_tags = '高潜人才,关键人才'
WHERE tag_code ='needs_development';

-- ==================== 行业类 ====================
-- 行业标签：同级一级行业之间互斥（一个人的主行业标签只能有一个）

-- 互联网（一级）
UPDATE sys_tag SET
  similar_tags = NULL,
  exclusive_tags = '金融,制造业'
WHERE tag_code ='industry_internet';

-- 电商（二级，互联网子行业）
UPDATE sys_tag SET
  similar_tags = '互联网',
  exclusive_tags = NULL
WHERE tag_code ='industry_ecommerce';

-- 金融（一级）
UPDATE sys_tag SET
  similar_tags = NULL,
  exclusive_tags = '互联网,制造业'
WHERE tag_code ='industry_finance';

-- 银行（二级，金融子行业）
UPDATE sys_tag SET
  similar_tags = '金融',
  exclusive_tags = NULL
WHERE tag_code ='industry_bank';

-- 制造业（一级）
UPDATE sys_tag SET
  similar_tags = NULL,
  exclusive_tags = '互联网,金融'
WHERE tag_code ='industry_manufacturing';

-- 汽车制造（二级，制造业子行业）
UPDATE sys_tag SET
  similar_tags = '制造业',
  exclusive_tags = NULL
WHERE tag_code ='industry_auto';

-- 医疗健康（一级）
UPDATE sys_tag SET
  similar_tags = NULL,
  exclusive_tags = '互联网,金融'
WHERE tag_code ='industry_healthcare';

-- 教育培训（一级）
UPDATE sys_tag SET
  similar_tags = NULL,
  exclusive_tags = NULL
WHERE tag_code ='industry_education';

-- 房地产（一级）
UPDATE sys_tag SET
  similar_tags = NULL,
  exclusive_tags = NULL
WHERE tag_code ='industry_realestate';

-- 新能源（一级）
UPDATE sys_tag SET
  similar_tags = '制造业',
  exclusive_tags = NULL
WHERE tag_code ='industry_new_energy';

-- 人工智能（二级，互联网子行业）
UPDATE sys_tag SET
  similar_tags = '互联网',
  exclusive_tags = NULL
WHERE tag_code ='industry_ai';

-- 保险（二级，金融子行业）
UPDATE sys_tag SET
  similar_tags = '金融',
  exclusive_tags = NULL
WHERE tag_code ='industry_insurance';

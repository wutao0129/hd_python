-- 更新标签的相似标签和互斥标签数据
-- 相似标签：与该标签含义相近的近义词标签
-- 互斥标签：不能同时出现在同一个人身上的标签
-- 执行时间: 2026-03-17

-- ==================== 基础信息类 ====================

-- 年龄
UPDATE tags SET
  similar_tags = '工作年限,入职日期',
  exclusive_tags = NULL
WHERE code ='age';

-- 性别
UPDATE tags SET
  similar_tags = NULL,
  exclusive_tags = NULL
WHERE code ='gender';

-- 学历
UPDATE tags SET
  similar_tags = '证书资质,培训经历',
  exclusive_tags = NULL
WHERE code ='education';

-- 工作年限
UPDATE tags SET
  similar_tags = '年龄,入职日期,行业经验',
  exclusive_tags = NULL
WHERE code ='work_years';

-- 职级
UPDATE tags SET
  similar_tags = '薪资等级,岗位',
  exclusive_tags = NULL
WHERE code ='job_level';

-- 部门
UPDATE tags SET
  similar_tags = '工作地点',
  exclusive_tags = NULL
WHERE code ='department';

-- 岗位
UPDATE tags SET
  similar_tags = '职级,薪资等级',
  exclusive_tags = NULL
WHERE code ='position';

-- 入职日期
UPDATE tags SET
  similar_tags = '工作年限,年龄',
  exclusive_tags = NULL
WHERE code ='hire_date';

-- 合同类型
UPDATE tags SET
  similar_tags = NULL,
  exclusive_tags = NULL
WHERE code ='contract_type';

-- 工作地点
UPDATE tags SET
  similar_tags = '部门',
  exclusive_tags = NULL
WHERE code ='work_location';

-- 薪资等级
UPDATE tags SET
  similar_tags = '职级,岗位',
  exclusive_tags = NULL
WHERE code ='salary_grade';

-- ==================== 职业履历类 ====================

-- 项目经验
UPDATE tags SET
  similar_tags = '管理经验,培训经历',
  exclusive_tags = NULL
WHERE code ='project_exp';

-- 管理经验
UPDATE tags SET
  similar_tags = '领导力,项目管理能力,项目经验',
  exclusive_tags = NULL
WHERE code ='management_exp';

-- 行业经验
UPDATE tags SET
  similar_tags = '工作年限,海外经历',
  exclusive_tags = NULL
WHERE code ='industry_exp';

-- 跳槽频率
UPDATE tags SET
  similar_tags = '离职风险',
  exclusive_tags = '敬业度,忠诚度'
WHERE code ='job_change_freq';

-- 晋升记录
UPDATE tags SET
  similar_tags = '职级,内部调动',
  exclusive_tags = NULL
WHERE code ='promotion_history';

-- 培训经历
UPDATE tags SET
  similar_tags = '学历,证书资质,学习能力',
  exclusive_tags = NULL
WHERE code ='training_history';

-- 获奖记录
UPDATE tags SET
  similar_tags = '证书资质',
  exclusive_tags = NULL
WHERE code ='awards';

-- 离职风险
UPDATE tags SET
  similar_tags = '跳槽频率',
  exclusive_tags = '敬业度,高潜人才,关键人才'
WHERE code ='turnover_risk';

-- 证书资质
UPDATE tags SET
  similar_tags = '学历,培训经历,获奖记录',
  exclusive_tags = NULL
WHERE code ='certifications';

-- 海外经历
UPDATE tags SET
  similar_tags = '行业经验,跨界人才',
  exclusive_tags = NULL
WHERE code ='overseas_exp';

-- 内部调动
UPDATE tags SET
  similar_tags = '晋升记录,跨部门协作',
  exclusive_tags = NULL
WHERE code ='internal_transfer';

-- ==================== 能力类 ====================

-- 技术能力
UPDATE tags SET
  similar_tags = '数据分析能力,问题解决',
  exclusive_tags = NULL
WHERE code ='technical_skill';

-- 沟通能力
UPDATE tags SET
  similar_tags = '跨部门协作,团队协作,客户导向',
  exclusive_tags = NULL
WHERE code ='communication';

-- 领导力
UPDATE tags SET
  similar_tags = '管理经验,战略思维,项目管理能力',
  exclusive_tags = NULL
WHERE code ='leadership';

-- 学习能力
UPDATE tags SET
  similar_tags = '适应性,创新能力',
  exclusive_tags = NULL
WHERE code ='learning_ability';

-- 问题解决
UPDATE tags SET
  similar_tags = '技术能力,创新能力,数据分析能力',
  exclusive_tags = NULL
WHERE code ='problem_solving';

-- 创新能力
UPDATE tags SET
  similar_tags = '学习能力,问题解决,战略思维',
  exclusive_tags = NULL
WHERE code ='innovation';

-- 执行力
UPDATE tags SET
  similar_tags = '责任心,主动性,自驱力',
  exclusive_tags = NULL
WHERE code ='execution';

-- 抗压能力
UPDATE tags SET
  similar_tags = '情绪管理,适应性',
  exclusive_tags = NULL
WHERE code ='stress_resistance';

-- 数据分析能力
UPDATE tags SET
  similar_tags = '技术能力,问题解决',
  exclusive_tags = NULL
WHERE code ='data_analysis';

-- 项目管理能力
UPDATE tags SET
  similar_tags = '领导力,管理经验,跨部门协作',
  exclusive_tags = NULL
WHERE code ='project_management';

-- 跨部门协作
UPDATE tags SET
  similar_tags = '沟通能力,团队协作,项目管理能力',
  exclusive_tags = NULL
WHERE code ='cross_dept_collab';

-- 战略思维
UPDATE tags SET
  similar_tags = '领导力,全局观,创新能力',
  exclusive_tags = NULL
WHERE code ='strategic_thinking';

-- 客户导向
UPDATE tags SET
  similar_tags = '沟通能力,责任心',
  exclusive_tags = NULL
WHERE code ='customer_orientation';

-- ==================== 素质类 ====================

-- 责任心
UPDATE tags SET
  similar_tags = '敬业度,执行力,主动性',
  exclusive_tags = '离职风险'
WHERE code ='responsibility';

-- 团队协作
UPDATE tags SET
  similar_tags = '沟通能力,跨部门协作',
  exclusive_tags = NULL
WHERE code ='teamwork';

-- 主动性
UPDATE tags SET
  similar_tags = '自驱力,执行力,责任心',
  exclusive_tags = '待发展人才'
WHERE code ='initiative';

-- 诚信度
UPDATE tags SET
  similar_tags = '责任心,价值观匹配',
  exclusive_tags = NULL
WHERE code ='integrity';

-- 敬业度
UPDATE tags SET
  similar_tags = '责任心,自驱力,主动性',
  exclusive_tags = '离职风险,跳槽频率'
WHERE code ='dedication';

-- 适应性
UPDATE tags SET
  similar_tags = '学习能力,抗压能力,情绪管理',
  exclusive_tags = NULL
WHERE code ='adaptability';

-- 价值观匹配
UPDATE tags SET
  similar_tags = '诚信度,敬业度,文化大使',
  exclusive_tags = '离职风险'
WHERE code ='value_fit';

-- 情绪管理
UPDATE tags SET
  similar_tags = '抗压能力,适应性',
  exclusive_tags = NULL
WHERE code ='emotional_management';

-- 自驱力
UPDATE tags SET
  similar_tags = '主动性,敬业度,执行力',
  exclusive_tags = '待发展人才'
WHERE code ='self_motivation';

-- 全局观
UPDATE tags SET
  similar_tags = '战略思维,领导力',
  exclusive_tags = NULL
WHERE code ='big_picture';

-- ==================== 复合标签 ====================

-- 高潜人才
UPDATE tags SET
  similar_tags = '关键人才,新星员工,管理储备',
  exclusive_tags = '离职风险,待发展人才'
WHERE code ='high_potential';

-- 关键人才
UPDATE tags SET
  similar_tags = '高潜人才,技术专家,业务骨干',
  exclusive_tags = '离职风险,待发展人才'
WHERE code ='key_talent';

-- 技术专家
UPDATE tags SET
  similar_tags = '关键人才,业务骨干',
  exclusive_tags = '待发展人才'
WHERE code ='technical_expert';

-- 管理储备
UPDATE tags SET
  similar_tags = '高潜人才,新星员工',
  exclusive_tags = '离职风险'
WHERE code ='management_reserve';

-- 业务骨干
UPDATE tags SET
  similar_tags = '关键人才,技术专家',
  exclusive_tags = '待发展人才'
WHERE code ='business_backbone';

-- 新星员工
UPDATE tags SET
  similar_tags = '高潜人才,管理储备',
  exclusive_tags = '离职风险'
WHERE code ='rising_star';

-- 跨界人才
UPDATE tags SET
  similar_tags = '海外经历,业务骨干',
  exclusive_tags = NULL
WHERE code ='cross_domain';

-- 文化大使
UPDATE tags SET
  similar_tags = '价值观匹配,团队协作',
  exclusive_tags = '离职风险'
WHERE code ='culture_ambassador';

-- 待发展人才
UPDATE tags SET
  similar_tags = NULL,
  exclusive_tags = '高潜人才,关键人才,技术专家,业务骨干'
WHERE code ='needs_development';

-- ==================== 行业类 ====================
-- 行业标签的互斥关系：同级行业之间互斥（一个人的主行业只能是一个）

-- 互联网（一级）
UPDATE tags SET
  similar_tags = '人工智能',
  exclusive_tags = '金融,制造业,医疗健康,教育培训,房地产,新能源'
WHERE code ='industry_internet';

-- 电商（二级，互联网子行业）
UPDATE tags SET
  similar_tags = '互联网,人工智能',
  exclusive_tags = '银行,保险,汽车制造'
WHERE code ='industry_ecommerce';

-- 金融（一级）
UPDATE tags SET
  similar_tags = '银行,保险',
  exclusive_tags = '互联网,制造业,医疗健康,教育培训,房地产,新能源'
WHERE code ='industry_finance';

-- 银行（二级，金融子行业）
UPDATE tags SET
  similar_tags = '金融,保险',
  exclusive_tags = '电商,人工智能,汽车制造'
WHERE code ='industry_bank';

-- 制造业（一级）
UPDATE tags SET
  similar_tags = '汽车制造,新能源',
  exclusive_tags = '互联网,金融,医疗健康,教育培训,房地产'
WHERE code ='industry_manufacturing';

-- 汽车制造（二级，制造业子行业）
UPDATE tags SET
  similar_tags = '制造业,新能源',
  exclusive_tags = '电商,银行,人工智能,保险'
WHERE code ='industry_auto';

-- 医疗健康（一级）
UPDATE tags SET
  similar_tags = NULL,
  exclusive_tags = '互联网,金融,制造业,教育培训,房地产,新能源'
WHERE code ='industry_healthcare';

-- 教育培训（一级）
UPDATE tags SET
  similar_tags = NULL,
  exclusive_tags = '互联网,金融,制造业,医疗健康,房地产,新能源'
WHERE code ='industry_education';

-- 房地产（一级）
UPDATE tags SET
  similar_tags = NULL,
  exclusive_tags = '互联网,金融,制造业,医疗健康,教育培训,新能源'
WHERE code ='industry_realestate';

-- 新能源（一级）
UPDATE tags SET
  similar_tags = '制造业,汽车制造',
  exclusive_tags = '互联网,金融,医疗健康,教育培训,房地产'
WHERE code ='industry_new_energy';

-- 人工智能（二级，互联网子行业）
UPDATE tags SET
  similar_tags = '互联网,电商',
  exclusive_tags = '银行,保险,汽车制造'
WHERE code ='industry_ai';

-- 保险（二级，金融子行业）
UPDATE tags SET
  similar_tags = '金融,银行',
  exclusive_tags = '电商,人工智能,汽车制造'
WHERE code ='industry_insurance';

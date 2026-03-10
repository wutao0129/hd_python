-- 标签打标记录测试数据
-- Epic: tag-record-api
-- Issue: #83 数据库设计与迁移
-- 说明: 使用实际 tags 表中的标签数据（通过 tag_id 直接引用）

INSERT INTO tag_records (employee_id, employee_name, department, position, tag_id, tag_name, tag_code, tag_category, source, source_detail, tagged_at, tagged_by, status, expires_at, removed_at, removed_by, remove_reason) VALUES
-- 员工1: 张三 - 技术部（3个标签）
('EMP001', '张三', '技术部', '高级工程师', 31, '高潜人才', 'high_potential', '复合标签', 'system', 'AI评估系统自动标记', '2026-01-15 09:30:00', '系统', '生效中', NULL, NULL, NULL, NULL),
('EMP001', '张三', '技术部', '高级工程师', 33, '技术专家', 'technical_expert', '复合标签', 'manual', NULL, '2026-02-01 14:20:00', '李经理', '生效中', NULL, NULL, NULL, NULL),
('EMP001', '张三', '技术部', '高级工程师', 16, '技术能力', 'technical_skill', '能力', 'system', '技能评估系统', '2026-01-10 11:00:00', '系统', '生效中', NULL, NULL, NULL, NULL),

-- 员工2: 李四 - 产品部（2个标签）
('EMP002', '李四', '产品部', '产品经理', 31, '高潜人才', 'high_potential', '复合标签', 'manual', NULL, '2026-01-20 10:00:00', '王总监', '生效中', NULL, NULL, NULL, NULL),
('EMP002', '李四', '产品部', '产品经理', 32, '关键人才', 'key_talent', '复合标签', 'import', '年度人才盘点导入', '2025-12-01 08:00:00', '人力资源部', '生效中', NULL, NULL, NULL, NULL),

-- 员工3: 王五 - 销售部（含已过期标签）
('EMP003', '王五', '销售部', '销售总监', 18, '领导力', 'leadership', '能力', 'system', '绩效系统自动标记', '2025-06-15 09:00:00', '系统', '已过期', '2025-12-31 23:59:59', NULL, NULL, NULL),
('EMP003', '王五', '销售部', '销售总监', 32, '关键人才', 'key_talent', '复合标签', 'manual', NULL, '2026-02-10 16:30:00', '赵VP', '生效中', NULL, NULL, NULL, NULL),

-- 员工4: 赵六 - 财务部（含已移除标签）
('EMP004', '赵六', '财务部', '财务主管', 15, '离职风险', 'turnover_risk', '职业履历', 'system', 'AI预警系统标记', '2025-11-01 10:00:00', '系统', '已移除', NULL, '2026-01-15 14:00:00', '李经理', '员工已转正，风险解除'),

-- 员工5: 孙七 - 人力资源部
('EMP005', '孙七', '人力资源部', 'HRBP', 31, '高潜人才', 'high_potential', '复合标签', 'manual', NULL, '2026-03-01 09:00:00', '陈总', '生效中', NULL, NULL, NULL, NULL),

-- 员工6: 周八 - 技术部（2个标签）
('EMP006', '周八', '技术部', '架构师', 33, '技术专家', 'technical_expert', '复合标签', 'system', '技能评估系统', '2026-01-10 11:00:00', '系统', '生效中', NULL, NULL, NULL, NULL),
('EMP006', '周八', '技术部', '架构师', 34, '管理储备', 'management_reserve', '复合标签', 'manual', NULL, '2026-02-20 15:00:00', '技术VP', '生效中', NULL, NULL, NULL, NULL),

-- 员工7: 吴九 - 市场部
('EMP007', '吴九', '市场部', '市场总监', 32, '关键人才', 'key_talent', '复合标签', 'import', '继任计划导入', '2025-09-15 08:30:00', '人力资源部', '生效中', NULL, NULL, NULL, NULL);

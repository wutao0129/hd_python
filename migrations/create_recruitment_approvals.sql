-- 招聘需求审批表
CREATE TABLE IF NOT EXISTS recruitment_approvals (
    -- 主键
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',

    -- 申请人信息
    applicant_id BIGINT NOT NULL COMMENT '申请人ID（关联sys_user.USER_ID）',
    applicant_name VARCHAR(100) NOT NULL COMMENT '申请人姓名',
    department_id BIGINT NOT NULL COMMENT '申请人部门ID（关联org_department.DEPID）',
    department_name VARCHAR(200) NOT NULL COMMENT '申请人部门名称',

    -- 职位信息
    position_name VARCHAR(200) NOT NULL COMMENT '职位名称',
    position_code VARCHAR(50) COMMENT '职位编码',
    recruit_count INT NOT NULL DEFAULT 1 COMMENT '招聘人数',
    position_type VARCHAR(50) NOT NULL COMMENT '职位类型：full_time(正式工)/contract(合同工)/intern(实习生)',
    work_location VARCHAR(200) NOT NULL COMMENT '工作地点',
    position_level VARCHAR(50) COMMENT '职位级别：P5/P6/P7等',
    expected_onboard_date DATE NOT NULL COMMENT '期望到岗时间',
    recruit_reason VARCHAR(50) NOT NULL COMMENT '招聘原因：new(新增)/replacement(替换)/expansion(扩编)',

    -- 审批信息
    status VARCHAR(20) NOT NULL DEFAULT 'draft' COMMENT '审批状态：draft(草稿)/pending(待审批)/approved(已通过)/rejected(已驳回)/withdrawn(已撤回)',
    reject_reason TEXT COMMENT '驳回原因',
    approver_id BIGINT COMMENT '审批人ID（关联sys_user.USER_ID）',
    approver_name VARCHAR(100) COMMENT '审批人姓名',
    approved_at DATETIME COMMENT '审批时间',

    -- 时间戳
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间（申请时间）',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    submitted_at DATETIME COMMENT '提交审批时间',
    withdrawn_at DATETIME COMMENT '撤回时间',

    -- 软删除
    deleted_at DATETIME COMMENT '删除时间（软删除）',

    -- 索引
    INDEX idx_applicant_id (applicant_id),
    INDEX idx_department_id (department_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_expected_onboard_date (expected_onboard_date),
    INDEX idx_position_name (position_name),
    INDEX idx_deleted_at (deleted_at),
    INDEX idx_status_created (status, created_at),
    INDEX idx_applicant_status (applicant_id, status),
    INDEX idx_department_status (department_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='招聘需求审批表';

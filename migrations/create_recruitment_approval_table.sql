-- 创建招聘审批单表
CREATE TABLE IF NOT EXISTS recruitment_approvals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL COMMENT '审批单标题',
    position VARCHAR(100) NOT NULL COMMENT '招聘职位',
    department VARCHAR(100) COMMENT '部门',
    description TEXT COMMENT '职位描述',
    status VARCHAR(20) NOT NULL DEFAULT 'draft' COMMENT '状态: draft-草稿, pending-待审批, approved-已通过, rejected-已驳回',
    creator_id INT COMMENT '创建人ID',
    creator_name VARCHAR(100) COMMENT '创建人姓名',
    approver_id INT COMMENT '审批人ID',
    approver_name VARCHAR(100) COMMENT '审批人姓名',
    approval_comment TEXT COMMENT '审批意见',
    submitted_at DATETIME COMMENT '提交时间',
    approved_at DATETIME COMMENT '审批时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_status (status),
    INDEX idx_creator_id (creator_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='招聘审批单表';

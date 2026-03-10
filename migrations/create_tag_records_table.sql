-- 创建标签打标记录表
-- Epic: tag-record-api
-- Issue: #83 数据库设计与迁移
-- 创建时间: 2026-03-10

CREATE TABLE IF NOT EXISTS tag_records (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',

    -- 员工信息（冗余存储，避免频繁JOIN）
    employee_id VARCHAR(50) NOT NULL COMMENT '员工ID/工号',
    employee_name VARCHAR(100) NOT NULL COMMENT '员工姓名',
    department VARCHAR(100) DEFAULT NULL COMMENT '部门',
    position VARCHAR(100) DEFAULT NULL COMMENT '职位',

    -- 标签信息（冗余存储）
    tag_id INT NOT NULL COMMENT '标签ID',
    tag_name VARCHAR(100) NOT NULL COMMENT '标签名称',
    tag_code VARCHAR(100) NOT NULL COMMENT '标签编码',
    tag_category VARCHAR(50) NOT NULL COMMENT '标签分类',

    -- 打标信息
    source VARCHAR(50) NOT NULL DEFAULT 'manual' COMMENT '来源：manual/system/import',
    source_detail TEXT DEFAULT NULL COMMENT '来源详情',
    tagged_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '打标时间',
    tagged_by VARCHAR(100) DEFAULT NULL COMMENT '打标人',
    expires_at DATETIME DEFAULT NULL COMMENT '过期时间',

    -- 状态管理（软删除）
    status ENUM('生效中', '已过期', '已移除') NOT NULL DEFAULT '生效中' COMMENT '状态',
    removed_at DATETIME DEFAULT NULL COMMENT '移除时间',
    removed_by VARCHAR(100) DEFAULT NULL COMMENT '移除人',
    remove_reason TEXT DEFAULT NULL COMMENT '移除原因',

    -- 时间戳
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 索引
    INDEX idx_tr_employee_id (employee_id),
    INDEX idx_tr_tag_id (tag_id),
    INDEX idx_tr_status (status),
    INDEX idx_tr_source (source),
    INDEX idx_tr_tagged_at (tagged_at),
    INDEX idx_tr_composite (employee_id, tag_id, status),

    -- 外键
    CONSTRAINT fk_tr_tag_id FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='标签打标记录表';

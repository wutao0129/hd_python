-- 标签库数据表
-- 用于存储人才标签的基础信息、分类、规则和使用统计

CREATE TABLE IF NOT EXISTS tags (
  id INT PRIMARY KEY AUTO_INCREMENT COMMENT '标签ID',
  name VARCHAR(100) NOT NULL COMMENT '标签名称',
  code VARCHAR(100) NOT NULL UNIQUE COMMENT '标签编码',
  category VARCHAR(50) NOT NULL COMMENT '标签分类（基础信息、职业履历、能力、素质、复合标签、行业）',
  type ENUM('内置', '自定义') DEFAULT '自定义' COMMENT '标签类型',
  scene JSON COMMENT '标签场景（数组）',
  rule_type VARCHAR(50) COMMENT '规则类型',
  rule_detail TEXT COMMENT '规则说明',
  description TEXT COMMENT '标签描述',
  status ENUM('启用', '禁用') DEFAULT '启用' COMMENT '状态',
  parent_id INT NULL COMMENT '父标签ID（用于层级结构）',
  usage_count INT DEFAULT 0 COMMENT '使用次数',
  activity_rate INT DEFAULT 0 COMMENT '活跃度',
  graph_type ENUM('节点', '关系') NULL COMMENT '知识图谱类型',
  relation_name VARCHAR(100) NULL COMMENT '关系名称',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

  INDEX idx_category (category),
  INDEX idx_type (type),
  INDEX idx_status (status),
  INDEX idx_parent_id (parent_id),
  INDEX idx_code (code),

  FOREIGN KEY (parent_id) REFERENCES tags(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='标签库表';

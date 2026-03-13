-- 添加相似标签和互斥标签字段
-- Epic: tag-graph-relations
-- 创建时间: 2026-03-12

ALTER TABLE tags
ADD COLUMN similar_tags TEXT NULL COMMENT '相似标签（逗号分隔的标签名称）',
ADD COLUMN exclusive_tags TEXT NULL COMMENT '互斥标签（逗号分隔的标签名称）';

-- 添加菜单排序复合索引
-- 用于优化按父菜单和排序顺序查询的性能
-- Created: 2026-03-06

-- 检查并删除旧的单列索引（如果需要）
-- DROP INDEX IF EXISTS idx_parent_id ON menus;
-- DROP INDEX IF EXISTS idx_sort_order ON menus;

-- 添加复合索引（parent_id + sort_order）
-- 这个索引可以同时优化按 parent_id 和 sort_order 的查询
CREATE INDEX IF NOT EXISTS idx_parent_sort ON menus(parent_id, sort_order);

-- 验证索引创建
SHOW INDEX FROM menus WHERE Key_name = 'idx_parent_sort';

-- 菜单初始化数据
-- 规则：
-- 1. 有子菜单的父级菜单 menu_type='menu'，route_path=NULL
-- 2. 末级菜单 menu_type='page'，有具体的 route_path
-- 3. 按钮类型 menu_type='button'

-- 清空现有数据
DELETE FROM `menu_permissions`;
DELETE FROM `menu_i18n`;
DELETE FROM `menus`;

-- 重置自增ID
ALTER TABLE `menus` AUTO_INCREMENT = 1;
ALTER TABLE `menu_i18n` AUTO_INCREMENT = 1;
ALTER TABLE `menu_permissions` AUTO_INCREMENT = 1;

-- ============================================
-- 一级菜单（菜单组，无路由）
-- ============================================

-- 1. 仪表盘（顶级菜单组）
INSERT INTO `menus` (`id`, `parent_id`, `menu_type`, `menu_name`, `icon`, `route_path`, `sort_order`, `is_enabled`)
VALUES (1, NULL, 'menu', '仪表盘', 'tabler-smart-home', NULL, 1, TRUE);

-- 2. 应用管理（顶级菜单组）
INSERT INTO `menus` (`id`, `parent_id`, `menu_type`, `menu_name`, `icon`, `route_path`, `sort_order`, `is_enabled`)
VALUES (2, NULL, 'menu', '应用管理', 'tabler-apps', NULL, 2, TRUE);

-- 3. 系统设置（顶级菜单组）
INSERT INTO `menus` (`id`, `parent_id`, `menu_type`, `menu_name`, `icon`, `route_path`, `sort_order`, `is_enabled`)
VALUES (3, NULL, 'menu', '系统设置', 'tabler-settings', NULL, 3, TRUE);

-- ============================================
-- 二级菜单（具体页面，有路由）
-- ============================================

-- 仪表盘子菜单
INSERT INTO `menus` (`id`, `parent_id`, `menu_type`, `menu_name`, `icon`, `route_path`, `sort_order`, `is_enabled`)
VALUES (11, 1, 'page', '数据概览', 'tabler-chart-line', 'apps-dashboard', 1, TRUE);

INSERT INTO `menus` (`id`, `parent_id`, `menu_type`, `menu_name`, `icon`, `route_path`, `sort_order`, `is_enabled`)
VALUES (12, 1, 'page', '分析报表', 'tabler-chart-bar', 'apps-analytics', 2, TRUE);

-- 应用管理子菜单
INSERT INTO `menus` (`id`, `parent_id`, `menu_type`, `menu_name`, `icon`, `route_path`, `sort_order`, `is_enabled`)
VALUES (21, 2, 'page', '用户管理', 'tabler-users', 'apps-user-list', 1, TRUE);

INSERT INTO `menus` (`id`, `parent_id`, `menu_type`, `menu_name`, `icon`, `route_path`, `sort_order`, `is_enabled`)
VALUES (22, 2, 'page', '角色管理', 'tabler-user-check', 'apps-role-list', 2, TRUE);

INSERT INTO `menus` (`id`, `parent_id`, `menu_type`, `menu_name`, `icon`, `route_path`, `sort_order`, `is_enabled`)
VALUES (23, 2, 'page', '权限管理', 'tabler-lock', 'apps-permission-list', 3, TRUE);

-- 系统设置子菜单
INSERT INTO `menus` (`id`, `parent_id`, `menu_type`, `menu_name`, `icon`, `route_path`, `sort_order`, `is_enabled`)
VALUES (31, 3, 'page', '菜单配置', 'tabler-menu-2', 'apps-menu-config', 1, TRUE);

INSERT INTO `menus` (`id`, `parent_id`, `menu_type`, `menu_name`, `icon`, `route_path`, `sort_order`, `is_enabled`)
VALUES (32, 3, 'page', '系统参数', 'tabler-adjustments', 'apps-system-config', 2, TRUE);

INSERT INTO `menus` (`id`, `parent_id`, `menu_type`, `menu_name`, `icon`, `route_path`, `sort_order`, `is_enabled`)
VALUES (33, 3, 'page', '操作日志', 'tabler-file-text', 'apps-operation-log', 3, TRUE);

-- ============================================
-- 多语言配置
-- ============================================

-- 一级菜单多语言
INSERT INTO `menu_i18n` (`menu_id`, `language_code`, `menu_name`) VALUES
(1, 'en-US', 'Dashboard'),
(1, 'zh-CN', '仪表盘'),
(2, 'en-US', 'Applications'),
(2, 'zh-CN', '应用管理'),
(3, 'en-US', 'System'),
(3, 'zh-CN', '系统设置');

-- 二级菜单多语言
INSERT INTO `menu_i18n` (`menu_id`, `language_code`, `menu_name`) VALUES
(11, 'en-US', 'Overview'),
(11, 'zh-CN', '数据概览'),
(12, 'en-US', 'Analytics'),
(12, 'zh-CN', '分析报表'),
(21, 'en-US', 'Users'),
(21, 'zh-CN', '用户管理'),
(22, 'en-US', 'Roles'),
(22, 'zh-CN', '角色管理'),
(23, 'en-US', 'Permissions'),
(23, 'zh-CN', '权限管理'),
(31, 'en-US', 'Menu Config'),
(31, 'zh-CN', '菜单配置'),
(32, 'en-US', 'System Config'),
(32, 'zh-CN', '系统参数'),
(33, 'en-US', 'Operation Log'),
(33, 'zh-CN', '操作日志');

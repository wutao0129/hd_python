-- 菜单系统数据库表创建脚本

-- 删除旧表（如果存在）
DROP TABLE IF EXISTS `menu_permissions`;
DROP TABLE IF EXISTS `menu_i18n`;
DROP TABLE IF EXISTS `menus`;

-- 1. 菜单主表
CREATE TABLE `menus` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '菜单ID',
  `parent_id` INT NULL COMMENT '父菜单ID',
  `menu_type` VARCHAR(20) NOT NULL DEFAULT 'menu' COMMENT '菜单类型',
  `menu_name` VARCHAR(100) NOT NULL COMMENT '菜单名称',
  `icon` VARCHAR(100) NULL COMMENT '菜单图标',
  `route_path` VARCHAR(200) NULL COMMENT '路由路径',
  `sort_order` INT NOT NULL DEFAULT 0 COMMENT '排序顺序',
  `is_enabled` BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否启用',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX `idx_parent_id` (`parent_id`),
  INDEX `idx_sort_order` (`sort_order`),
  FOREIGN KEY (`parent_id`) REFERENCES `menus`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='菜单主表';

-- 2. 菜单多语言表
CREATE TABLE `menu_i18n` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '多语言记录ID',
  `menu_id` INT NOT NULL COMMENT '关联的菜单ID',
  `language_code` VARCHAR(10) NOT NULL COMMENT '语言代码',
  `menu_name` VARCHAR(100) NOT NULL COMMENT '翻译后的菜单名称',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  UNIQUE INDEX `uk_menu_lang` (`menu_id`, `language_code`),
  FOREIGN KEY (`menu_id`) REFERENCES `menus`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='菜单多语言表';

-- 3. 菜单权限表
CREATE TABLE `menu_permissions` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '权限记录ID',
  `role_id` INT NOT NULL COMMENT '角色ID',
  `menu_id` INT NOT NULL COMMENT '菜单ID',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  UNIQUE INDEX `uk_role_menu` (`role_id`, `menu_id`),
  INDEX `idx_role_id` (`role_id`),
  FOREIGN KEY (`menu_id`) REFERENCES `menus`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='菜单权限表';

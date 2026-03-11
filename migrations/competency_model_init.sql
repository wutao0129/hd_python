-- ============================================================
-- 胜任力模型系统 - 数据库初始化脚本
-- Database: MySQL 8.x / utf8mb4
-- 说明: 创建胜任力模型相关的15张表 + 预置数据
-- ============================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- 1. DROP TABLES (反向依赖顺序)
-- ============================================================

DROP TABLE IF EXISTS `indicator_library`;
DROP TABLE IF EXISTS `match_result_level`;
DROP TABLE IF EXISTS `indicator_rule_config`;
DROP TABLE IF EXISTS `dimension_weight_config`;
DROP TABLE IF EXISTS `rule_set`;
DROP TABLE IF EXISTS `tag_trigger_action`;
DROP TABLE IF EXISTS `tag_trigger_condition`;
DROP TABLE IF EXISTS `tag_trigger_rule`;
DROP TABLE IF EXISTS `behavior_anchor`;
DROP TABLE IF EXISTS `scoring_level_mapping`;
DROP TABLE IF EXISTS `scoring_scheme`;
DROP TABLE IF EXISTS `competency_item`;
DROP TABLE IF EXISTS `competency_dimension`;
DROP TABLE IF EXISTS `competency_model_condition`;
DROP TABLE IF EXISTS `competency_model`;

-- ============================================================
-- 2. CREATE TABLES (正向依赖顺序)
-- ============================================================

-- ----- 1. competency_model 胜任力模型主表 -----
CREATE TABLE `competency_model` (
  `id`            VARCHAR(36)   NOT NULL COMMENT 'UUID主键',
  `model_code`    VARCHAR(20)   NOT NULL COMMENT '模型编码 CM-YYYY-NNN',
  `position_name` VARCHAR(100)  NOT NULL COMMENT '岗位名称',
  `position_level` VARCHAR(20)  NOT NULL COMMENT '职级',
  `department`    VARCHAR(100)  NOT NULL COMMENT '部门',
  `industry`      VARCHAR(50)   NOT NULL COMMENT '行业',
  `version`       VARCHAR(10)   NOT NULL DEFAULT 'V1.0',
  `status`        VARCHAR(20)   NOT NULL DEFAULT 'draft' COMMENT 'active/draft/archived',
  `style`         VARCHAR(200)  DEFAULT NULL COMMENT '模型风格',
  `created_by`    VARCHAR(50)   NOT NULL DEFAULT '',
  `created_at`    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at`    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_model_code` (`model_code`),
  KEY `idx_cm_status` (`status`),
  KEY `idx_cm_industry` (`industry`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='胜任力模型主表';

-- ----- 2. competency_model_condition 适用条件表 -----
CREATE TABLE `competency_model_condition` (
  `id`         BIGINT       NOT NULL AUTO_INCREMENT,
  `model_id`   VARCHAR(36)  NOT NULL,
  `dimension`  VARCHAR(30)  NOT NULL COMMENT 'positionType/level/department/industry/location',
  `values`     JSON         NOT NULL,
  `logic`      VARCHAR(5)   NOT NULL DEFAULT 'AND',
  `sort_order` INT          NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `idx_cmc_model` (`model_id`),
  FOREIGN KEY (`model_id`) REFERENCES `competency_model`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='适用条件表';

-- ----- 3. competency_dimension 能力维度表 -----
CREATE TABLE `competency_dimension` (
  `id`         BIGINT       NOT NULL AUTO_INCREMENT,
  `model_id`   VARCHAR(36)  NOT NULL,
  `name`       VARCHAR(50)  NOT NULL,
  `icon`       VARCHAR(50)  DEFAULT NULL,
  `color`      VARCHAR(20)  DEFAULT NULL,
  `weight`     DECIMAL(5,2) NOT NULL DEFAULT 25.00,
  `sort_order` INT          NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `idx_cd_model` (`model_id`),
  FOREIGN KEY (`model_id`) REFERENCES `competency_model`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='能力维度表';

-- ----- 4. competency_item 能力指标项表 -----
CREATE TABLE `competency_item` (
  `id`           BIGINT       NOT NULL AUTO_INCREMENT,
  `dimension_id` BIGINT       NOT NULL,
  `model_id`     VARCHAR(36)  NOT NULL,
  `name`         VARCHAR(100) NOT NULL,
  `description`  TEXT         DEFAULT NULL,
  `level`        VARCHAR(20)  NOT NULL DEFAULT '熟练',
  `weight`       DECIMAL(5,2) NOT NULL DEFAULT 0,
  `sort_order`   INT          NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `idx_ci_dimension` (`dimension_id`),
  KEY `idx_ci_model` (`model_id`),
  FOREIGN KEY (`dimension_id`) REFERENCES `competency_dimension`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`model_id`) REFERENCES `competency_model`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='能力指标项表';

-- ----- 5. scoring_scheme 评分方案表 -----
CREATE TABLE `scoring_scheme` (
  `id`              VARCHAR(36)  NOT NULL,
  `model_id`        VARCHAR(36)  DEFAULT NULL COMMENT 'NULL=全局预置',
  `name`            VARCHAR(100) NOT NULL,
  `type`            VARCHAR(30)  NOT NULL,
  `scale`           INT          NOT NULL DEFAULT 100,
  `description`     TEXT         DEFAULT NULL,
  `level_dict_type` VARCHAR(10)  NOT NULL DEFAULT 'L1_L5',
  `peer_group_rule` VARCHAR(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_ss_model` (`model_id`),
  FOREIGN KEY (`model_id`) REFERENCES `competency_model`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='评分方案表';

-- ----- 6. scoring_level_mapping 评分等级映射表 -----
CREATE TABLE `scoring_level_mapping` (
  `id`        BIGINT       NOT NULL AUTO_INCREMENT,
  `scheme_id` VARCHAR(36)  NOT NULL,
  `level`     VARCHAR(10)  NOT NULL,
  `label`     VARCHAR(50)  NOT NULL,
  `min_score` DECIMAL(8,2) NOT NULL,
  `max_score` DECIMAL(8,2) NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`scheme_id`) REFERENCES `scoring_scheme`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='评分等级映射表';

-- ----- 7. behavior_anchor 行为锚点表 -----
CREATE TABLE `behavior_anchor` (
  `id`                   BIGINT       NOT NULL AUTO_INCREMENT,
  `item_id`              BIGINT       NOT NULL,
  `model_id`             VARCHAR(36)  NOT NULL,
  `level`                VARCHAR(10)  NOT NULL,
  `label`                VARCHAR(200) NOT NULL,
  `behavior_description` TEXT         NOT NULL,
  `example`              TEXT         DEFAULT NULL,
  `min_score`            DECIMAL(8,2) DEFAULT NULL,
  `max_score`            DECIMAL(8,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_ba_item` (`item_id`),
  KEY `idx_ba_model` (`model_id`),
  FOREIGN KEY (`item_id`) REFERENCES `competency_item`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`model_id`) REFERENCES `competency_model`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='行为锚点表';

-- ----- 8. tag_trigger_rule 标签触发规则表 -----
CREATE TABLE `tag_trigger_rule` (
  `id`           BIGINT      NOT NULL AUTO_INCREMENT,
  `model_id`     VARCHAR(36) NOT NULL,
  `tag_name`     VARCHAR(50) NOT NULL,
  `tag_color`    VARCHAR(20) NOT NULL DEFAULT '#1976D2',
  `tag_category` VARCHAR(30) NOT NULL COMMENT 'talent_pool/skill/warning/development',
  `rule_type`    VARCHAR(30) NOT NULL COMMENT 'single_indicator/multi_indicator/dimension/composite',
  `logic`        VARCHAR(5)  NOT NULL DEFAULT 'AND',
  `expire_days`  INT         DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_ttr_model` (`model_id`),
  FOREIGN KEY (`model_id`) REFERENCES `competency_model`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='标签触发规则表';

-- ----- 9. tag_trigger_condition 标签触发条件表 -----
CREATE TABLE `tag_trigger_condition` (
  `id`          BIGINT      NOT NULL AUTO_INCREMENT,
  `rule_id`     BIGINT      NOT NULL,
  `type`        VARCHAR(30) NOT NULL COMMENT 'indicator_level/dimension_score/overall_score',
  `target_id`   VARCHAR(36) DEFAULT NULL,
  `target_name` VARCHAR(100) DEFAULT NULL,
  `operator`    VARCHAR(5)  NOT NULL DEFAULT '>=',
  `value`       VARCHAR(50) NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`rule_id`) REFERENCES `tag_trigger_rule`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='标签触发条件表';

-- ----- 10. tag_trigger_action 标签触发动作表 -----
CREATE TABLE `tag_trigger_action` (
  `id`      BIGINT      NOT NULL AUTO_INCREMENT,
  `rule_id` BIGINT      NOT NULL,
  `type`    VARCHAR(30) NOT NULL COMMENT 'add_to_talent_pool/push_training/add_to_succession/send_notification',
  `config`  TEXT        DEFAULT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`rule_id`) REFERENCES `tag_trigger_rule`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='标签触发动作表';

-- ----- 11. rule_set 规则集表 -----
CREATE TABLE `rule_set` (
  `id`             VARCHAR(36)  NOT NULL,
  `name`           VARCHAR(100) NOT NULL,
  `scenarios`      JSON         NOT NULL,
  `status`         VARCHAR(20)  NOT NULL DEFAULT 'draft',
  `score_formula`  VARCHAR(30)  NOT NULL DEFAULT 'weighted_average',
  `pass_score`     INT          NOT NULL DEFAULT 60,
  `effective_type` VARCHAR(20)  DEFAULT NULL,
  `effective_date` DATE         DEFAULT NULL,
  `version`        VARCHAR(10)  NOT NULL DEFAULT 'V1.0',
  `remark`         TEXT         DEFAULT NULL,
  `created_by`     VARCHAR(50)  NOT NULL DEFAULT '',
  `created_at`     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at`     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_rs_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='规则集表';

-- ----- 12. dimension_weight_config 维度权重配置表 -----
CREATE TABLE `dimension_weight_config` (
  `id`              BIGINT       NOT NULL AUTO_INCREMENT,
  `rule_set_id`     VARCHAR(36)  NOT NULL,
  `dimension`       VARCHAR(30)  NOT NULL,
  `dimension_label` VARCHAR(50)  NOT NULL,
  `weight`          DECIMAL(5,2) NOT NULL,
  `min_pass_score`  INT          NOT NULL DEFAULT 60,
  `scoring_scheme`  VARCHAR(30)  DEFAULT NULL,
  `is_required`     TINYINT(1)   NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`rule_set_id`) REFERENCES `rule_set`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='维度权重配置表';

-- ----- 13. indicator_rule_config 指标规则配置表 -----
CREATE TABLE `indicator_rule_config` (
  `id`                BIGINT       NOT NULL AUTO_INCREMENT,
  `rule_set_id`       VARCHAR(36)  NOT NULL,
  `indicator_id`      BIGINT       DEFAULT NULL,
  `indicator_name`    VARCHAR(100) NOT NULL,
  `dimension`         VARCHAR(30)  NOT NULL,
  `weight`            DECIMAL(5,2) NOT NULL,
  `match_formula`     VARCHAR(30)  NOT NULL DEFAULT 'level_match',
  `threshold_level`   VARCHAR(5)   NOT NULL DEFAULT 'L3',
  `min_accept_level`  VARCHAR(5)   NOT NULL DEFAULT 'L1',
  `deviation_penalty` DECIMAL(5,2) NOT NULL DEFAULT 5.00,
  `is_key_indicator`  TINYINT(1)   NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`rule_set_id`) REFERENCES `rule_set`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='指标规则配置表';

-- ----- 14. match_result_level 匹配结果等级表 -----
CREATE TABLE `match_result_level` (
  `id`           BIGINT      NOT NULL AUTO_INCREMENT,
  `rule_set_id`  VARCHAR(36) NOT NULL,
  `level`        VARCHAR(5)  NOT NULL,
  `label`        VARCHAR(50) NOT NULL,
  `min_score`    INT         NOT NULL,
  `max_score`    INT         NOT NULL,
  `color`        VARCHAR(20) NOT NULL,
  `description`  TEXT        DEFAULT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`rule_set_id`) REFERENCES `rule_set`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='匹配结果等级表';

-- ----- 15. indicator_library 指标库表 -----
CREATE TABLE `indicator_library` (
  `id`          BIGINT       NOT NULL AUTO_INCREMENT,
  `name`        VARCHAR(100) NOT NULL,
  `description` TEXT         DEFAULT NULL,
  `category`    VARCHAR(50)  NOT NULL COMMENT '业务能力/专业技能/领导力/个人特质',
  `level`       VARCHAR(20)  NOT NULL DEFAULT '熟练',
  `is_preset`   TINYINT(1)   NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='指标库表';

-- ============================================================
-- 3. 预置数据
-- ============================================================

-- ----- 指标库 (16条) -----
INSERT INTO `indicator_library` (`name`, `description`, `category`, `level`, `is_preset`) VALUES
('战略思维', '从全局视角分析问题，制定长期发展策略', '业务能力', '精通', 1),
('客户导向', '以客户需求为中心，持续提升客户满意度', '业务能力', '精通', 1),
('商业敏锐度', '敏锐捕捉商业机会，理解市场竞争格局', '业务能力', '精通', 1),
('创新能力', '推动业务创新，探索新的增长模式', '业务能力', '熟练', 1),
('数据分析', '运用数据驱动决策，进行业务分析和预测', '专业技能', '熟练', 1),
('项目管理', '有效规划和执行项目，确保按时交付', '专业技能', '熟练', 1),
('沟通表达', '清晰准确地传达信息，有效影响他人', '专业技能', '精通', 1),
('谈判能力', '在复杂场景下达成双赢的谈判结果', '专业技能', '精通', 1),
('团队领导', '激励和引导团队成员，达成团队目标', '领导力', '精通', 1),
('人才培养', '识别和发展团队人才，建设人才梯队', '领导力', '熟练', 1),
('变革管理', '推动组织变革，引领团队适应新环境', '领导力', '熟练', 1),
('决策能力', '在不确定环境下做出有效决策', '领导力', '精通', 1),
('抗压韧性', '在高压环境下保持稳定表现和积极心态', '个人特质', '精通', 1),
('学习敏捷', '快速学习新知识和技能，适应变化', '个人特质', '精通', 1),
('诚信正直', '坚守职业道德，言行一致', '个人特质', '精通', 1),
('结果导向', '以目标为驱动，追求卓越成果', '个人特质', '精通', 1);

-- ----- 预置评分方案 (10个模板, model_id=NULL表示全局) -----
INSERT INTO `scoring_scheme` (`id`, `model_id`, `name`, `type`, `scale`, `description`, `level_dict_type`) VALUES
('preset-scheme-001', NULL, '标准百分制', 'absolute_score', 100, '0-100分直接映射L1-L5等级', 'L1_L5'),
('preset-scheme-002', NULL, '标准5分制', 'absolute_score', 5, '0-5分映射L1-L5等级', 'L1_L5'),
('preset-scheme-003', NULL, '自定义字典评分', 'absolute_score', 100, '基础/熟练/精通/专家四级', 'custom'),
('preset-scheme-004', NULL, '同岗位百分位', 'percentile', 100, '基于同岗位人群相对排名', 'L1_L5'),
('preset-scheme-005', NULL, '行为频次（5级）', 'frequency', 5, '从不/很少/有时/经常/总是', 'L1_L5'),
('preset-scheme-006', NULL, '星级评定（5星）', 'frequency', 5, '★到★★★★★', 'L1_L5'),
('preset-scheme-007', NULL, '行为锚定BARS', 'behavior_anchored', 5, '选择最匹配的行为描述定级', 'L1_L5'),
('preset-scheme-008', NULL, '目标达成率', 'goal_achievement', 200, '基于KPI/OKR达成率(0-200%)', 'L1_L5'),
('preset-scheme-009', NULL, '等级直选', 'direct_select', 5, '评估者直接选择L1-L5等级', 'L1_L5'),
('preset-scheme-010', NULL, '关键事件法', 'evidence', 5, '收集关键行为事件证据评审', 'L1_L5');

-- ----- 评分等级映射 -----

-- 标准百分制 L1-L5
INSERT INTO `scoring_level_mapping` (`scheme_id`, `level`, `label`, `min_score`, `max_score`) VALUES
('preset-scheme-001', 'L1', '入门级', 0, 20),
('preset-scheme-001', 'L2', '初级', 21, 40),
('preset-scheme-001', 'L3', '熟练级', 41, 60),
('preset-scheme-001', 'L4', '精通级', 61, 80),
('preset-scheme-001', 'L5', '大师级', 81, 100);

-- 标准5分制
INSERT INTO `scoring_level_mapping` (`scheme_id`, `level`, `label`, `min_score`, `max_score`) VALUES
('preset-scheme-002', 'L1', '入门级', 0, 1),
('preset-scheme-002', 'L2', '初级', 1.01, 2),
('preset-scheme-002', 'L3', '熟练级', 2.01, 3),
('preset-scheme-002', 'L4', '精通级', 3.01, 4),
('preset-scheme-002', 'L5', '大师级', 4.01, 5);

-- 自定义字典评分
INSERT INTO `scoring_level_mapping` (`scheme_id`, `level`, `label`, `min_score`, `max_score`) VALUES
('preset-scheme-003', 'C1', '基础', 0, 40),
('preset-scheme-003', 'C2', '熟练', 41, 60),
('preset-scheme-003', 'C3', '精通', 61, 80),
('preset-scheme-003', 'C4', '专家', 81, 100);

-- 同岗位百分位
INSERT INTO `scoring_level_mapping` (`scheme_id`, `level`, `label`, `min_score`, `max_score`) VALUES
('preset-scheme-004', 'L1', 'Bottom 10%', 0, 10),
('preset-scheme-004', 'L2', 'Below Average', 11, 30),
('preset-scheme-004', 'L3', 'Average', 31, 70),
('preset-scheme-004', 'L4', 'Above Average', 71, 90),
('preset-scheme-004', 'L5', 'Top 10%', 91, 100);

-- 行为频次（5级）
INSERT INTO `scoring_level_mapping` (`scheme_id`, `level`, `label`, `min_score`, `max_score`) VALUES
('preset-scheme-005', 'L1', '从不', 0, 1),
('preset-scheme-005', 'L2', '很少', 1.01, 2),
('preset-scheme-005', 'L3', '有时', 2.01, 3),
('preset-scheme-005', 'L4', '经常', 3.01, 4),
('preset-scheme-005', 'L5', '总是', 4.01, 5);

-- 星级评定（5星）
INSERT INTO `scoring_level_mapping` (`scheme_id`, `level`, `label`, `min_score`, `max_score`) VALUES
('preset-scheme-006', 'L1', '★', 0, 1),
('preset-scheme-006', 'L2', '★★', 1.01, 2),
('preset-scheme-006', 'L3', '★★★', 2.01, 3),
('preset-scheme-006', 'L4', '★★★★', 3.01, 4),
('preset-scheme-006', 'L5', '★★★★★', 4.01, 5);

-- 行为锚定BARS
INSERT INTO `scoring_level_mapping` (`scheme_id`, `level`, `label`, `min_score`, `max_score`) VALUES
('preset-scheme-007', 'L1', '入门级', 0, 1),
('preset-scheme-007', 'L2', '初级', 1.01, 2),
('preset-scheme-007', 'L3', '熟练级', 2.01, 3),
('preset-scheme-007', 'L4', '精通级', 3.01, 4),
('preset-scheme-007', 'L5', '大师级', 4.01, 5);

-- 目标达成率
INSERT INTO `scoring_level_mapping` (`scheme_id`, `level`, `label`, `min_score`, `max_score`) VALUES
('preset-scheme-008', 'L1', '未达标', 0, 60),
('preset-scheme-008', 'L2', '基本达标', 61, 80),
('preset-scheme-008', 'L3', '达标', 81, 100),
('preset-scheme-008', 'L4', '超额达标', 101, 150),
('preset-scheme-008', 'L5', '卓越', 151, 200);

-- 等级直选
INSERT INTO `scoring_level_mapping` (`scheme_id`, `level`, `label`, `min_score`, `max_score`) VALUES
('preset-scheme-009', 'L1', '入门级', 0, 1),
('preset-scheme-009', 'L2', '初级', 1.01, 2),
('preset-scheme-009', 'L3', '熟练级', 2.01, 3),
('preset-scheme-009', 'L4', '精通级', 3.01, 4),
('preset-scheme-009', 'L5', '大师级', 4.01, 5);

-- 关键事件法
INSERT INTO `scoring_level_mapping` (`scheme_id`, `level`, `label`, `min_score`, `max_score`) VALUES
('preset-scheme-010', 'L1', '入门级', 0, 1),
('preset-scheme-010', 'L2', '初级', 1.01, 2),
('preset-scheme-010', 'L3', '熟练级', 2.01, 3),
('preset-scheme-010', 'L4', '精通级', 3.01, 4),
('preset-scheme-010', 'L5', '大师级', 4.01, 5);

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- 初始化完成
-- ============================================================

-- 扩展 indicator_library 表
ALTER TABLE indicator_library
  ADD COLUMN code VARCHAR(50) UNIQUE AFTER id,
  ADD COLUMN weight INT DEFAULT 0 AFTER category,
  ADD COLUMN status TINYINT DEFAULT 1 AFTER is_preset,
  ADD COLUMN ref_count INT DEFAULT 0 AFTER status,
  ADD COLUMN created_by VARCHAR(100) AFTER ref_count,
  ADD COLUMN updated_by VARCHAR(100) AFTER created_by,
  ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP AFTER updated_by,
  ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER created_at,
  ADD COLUMN deleted_at DATETIME NULL AFTER updated_at;

-- 为现有数据生成编码
UPDATE indicator_library SET code = CONCAT('IND-', LPAD(id, 3, '0')) WHERE code IS NULL;

-- 操作日志表
CREATE TABLE IF NOT EXISTS hr_indicator_library_log (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  indicator_id BIGINT NULL,
  operation VARCHAR(20) NOT NULL,
  detail JSON,
  operator VARCHAR(100),
  operated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_indicator_id (indicator_id),
  INDEX idx_operated_at (operated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

# 招聘管理模块数据库模型修复记录

## 修复日期
2026-03-09

## 问题描述
前端访问 `/api/recruitment-resume/list` 接口时返回 500 错误，原因是 Python 模型定义与实际数据库表结构不匹配。

## 修复内容

### 1. 数据库表结构检查
创建了 `check_db_structure.py` 脚本来检查实际的数据库表结构。

### 2. 模型定义修复 (models.py)

#### RecruitmentResume (招聘简历表)
**修复前的字段：**
- position_id, phone, email, source, resume_url, education, work_experience, expected_salary, notes, created_at, updated_at

**修复后的字段（匹配数据库）：**
- name, age, school, degree, experience, status, applied_at, current_company, skills (JSON), scores (JSON), applied_position, department

#### RecruitmentPosition (招聘岗位表)
**修复前的字段：**
- employment_type, description, requirements, recruiter_id, recruiter_name, updated_at

**修复后的字段（匹配数据库）：**
- candidates, responsibilities, approval_id, published_channels (JSON)
- 移除了 employment_type, description, requirements, recruiter_id, recruiter_name, updated_at

#### RecruitmentChannel (招聘渠道表)
**修复前的字段：**
- contact_person, contact_phone, contact_email, cost, description, updated_at

**修复后的字段（匹配数据库）：**
- 移除了所有额外字段，只保留基础字段

#### RecruitmentInterview (面试记录表)
**修复前的字段：**
- round, interview_type, scheduled_time, interviewer_ids, interviewer_names, location, result, updated_at

**修复后的字段（匹配数据库）：**
- candidate_name, position_name, interviewer, interview_date, interview_method
- 移除了 round, interview_type, scheduled_time, interviewer_ids, interviewer_names, location, result, updated_at

#### RecruitmentOffer (Offer表)
**修复前的字段：**
- position_title, salary, start_date, accept_date, reject_reason, notes, updated_at

**修复后的字段（匹配数据库）：**
- position_name, offer_salary, expected_onboard_date
- 移除了 position_title, salary, start_date, accept_date, reject_reason, notes, updated_at

#### RecruitmentQuestionBank (题库表)
**修复前的字段：**
- category, question, answer, tags (String), updated_at

**修复后的字段（匹配数据库）：**
- title, content, type, tags (JSON)
- 移除了 category, question, answer, updated_at

#### RecruitmentJobProfile (岗位画像表)
- **完全删除**：数据库中不存在此表

#### RecruitmentApproval (招聘审批单表)
**字段类型修复：**
- id: Integer → BigInteger
- applicant_id: Integer → BigInteger
- department_id: Integer → BigInteger
- department_name: String(100) → String(200)
- position_code: NOT NULL → Optional
- position_level: NOT NULL → Optional
- expected_onboard_date: String(20) → DateTime
- recruit_reason: Text → String(50)
- approver_id: Integer → BigInteger
- 新增字段: deleted_at

### 3. 路由文件修复

#### recruitment_resume.py
- 修复 `_to_dict()` 函数以匹配新的模型字段
- 修复 `get_list()` 查询参数和过滤器
- 修复 `ResumeCreate` 和 `ResumeUpdate` Schema
- 修复 `create()` 和 `update()` 函数

#### recruitment_position.py
- 修复 `_to_dict()` 函数以匹配新的模型字段
- 修复 `PositionCreate` 和 `PositionUpdate` Schema
- 修复 `create()` 和 `update()` 函数
- 修复 `publish_to_channels()` 函数

### 4. main.py 修复
- 移除了对不存在的 `recruitment_job_profile` 路由的引用

## 验证结果

### 测试接口
1. `/api/recruitment-resume/list` - ✅ 返回 200，数据结构正确
2. `/api/recruitment-position/list` - ✅ 返回 200，数据结构正确

### 数据示例
简历数据包含：id, name, age, school, degree, experience, status, appliedAt, currentCompany, skills, scores, appliedPosition, department

岗位数据包含：id, title, department, salaryRange, status, candidates, responsibilities, location, headcount, createdAt, approvalId, publishedChannels

## 注意事项
1. 所有字段的 nullable 设置已根据数据库实际情况调整
2. JSON 字段类型已正确映射
3. 外键约束已移除（数据库中不存在外键）
4. 时间戳字段已根据数据库实际情况调整

## 后续建议
1. 前端代码需要相应调整以匹配新的 API 数据结构
2. 考虑添加数据迁移脚本以保持模型和数据库的一致性
3. 建议使用 Alembic 进行数据库版本管理

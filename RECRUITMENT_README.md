# 招聘管理模块后端接口

## 概述

本模块为招聘管理系统提供完整的后端 API 接口，包含 9 个子模块，共 43 个接口。

## 技术栈

- FastAPI 框架
- SQLAlchemy ORM
- MySQL 数据库
- Pydantic 数据验证

## 模块列表

### 1. 招聘审批管理 (recruitment_approval)
- 路径前缀: `/api/recruitment-approval`
- 接口数: 9 个
- 功能: 创建、查询、提交、审批、撤回审批单

### 2. 岗位管理 (recruitment_position)
- 路径前缀: `/api/recruitment-position`
- 接口数: 6 个
- 功能: 岗位的增删改查、发布到渠道

### 3. 简历管理 (recruitment_resume)
- 路径前缀: `/api/recruitment-resume`
- 接口数: 7 个
- 功能: 简历的增删改查、安排面试、淘汰候选人

### 4. 招聘渠道管理 (recruitment_channel)
- 路径前缀: `/api/recruitment-channel`
- 接口数: 5 个
- 功能: 渠道的增删改查

### 5. 面试管理 (recruitment_interview)
- 路径前缀: `/api/recruitment-interview`
- 接口数: 5 个
- 功能: 面试记录的增删改查、提交反馈

### 6. Offer 管理 (recruitment_offer)
- 路径前缀: `/api/recruitment-offer`
- 接口数: 5 个
- 功能: Offer 的增删改查、审批、发放

### 7. 仪表板统计 (recruitment_dashboard)
- 路径前缀: `/api/recruitment-dashboard`
- 接口数: 1 个
- 功能: 获取统计数据

### 8. 题库管理 (recruitment_question_bank)
- 路径前缀: `/api/recruitment-question-bank`
- 接口数: 5 个
- 功能: 题目的增删改查

### 9. 岗位画像管理 (recruitment_job_profile)
- 路径前缀: `/api/recruitment-job-profile`
- 接口数: 4 个
- 功能: 岗位画像的增删改查

## 数据库表

| 表名 | 说明 |
|------|------|
| recruitment_approvals | 招聘审批单 |
| recruitment_positions | 招聘岗位 |
| recruitment_resumes | 简历 |
| recruitment_channels | 招聘渠道 |
| recruitment_interviews | 面试记录 |
| recruitment_offers | Offer |
| recruitment_question_bank | 题库 |
| recruitment_job_profiles | 岗位画像 |

## 安装和启动

### 1. 创建数据库表

```bash
cd D:\procjet\hd_python
python create_recruitment_tables.py
```

### 2. 启动服务

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 字段命名规范

### 数据库字段 (snake_case)
- `position_id`
- `candidate_name`
- `created_at`

### API 响应字段 (camelCase)
- `positionId`
- `candidateName`
- `createdAt`

字段转换通过 Pydantic 的 `populate_by_name` 配置自动完成。

## 接口响应格式

### 成功响应
```json
{
  "code": 200,
  "message": "success",
  "data": {
    // 数据内容
  }
}
```

### 列表响应
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 100,
    "page": 1,
    "pageSize": 20,
    "items": [...]
  }
}
```

### 错误响应
```json
{
  "detail": "错误信息"
}
```

## 常见接口示例

### 获取岗位列表
```
GET /api/recruitment-position/list?status=published&page=1&page_size=20
```

### 创建简历
```
POST /api/recruitment-resume
Content-Type: application/json

{
  "positionId": 1,
  "name": "张三",
  "phone": "13800138000",
  "email": "zhangsan@example.com",
  "source": "智联招聘"
}
```

### 安排面试
```
POST /api/recruitment-resume/1/schedule-interview
Content-Type: application/json

{
  "interviewType": "技术面试",
  "scheduledTime": "2024-03-15T14:00:00Z",
  "interviewerNames": "李四,王五",
  "location": "会议室A"
}
```

### 获取统计数据
```
GET /api/recruitment-dashboard/stats
```

## 权限控制

所有接口都需要通过 `get_current_user` 中间件进行身份验证。请求时需要在 Header 中携带认证信息。

## 注意事项

1. 所有时间字段使用 ISO 8601 格式
2. 列表接口支持分页、筛选、搜索
3. 删除操作为物理删除，请谨慎操作
4. 外键关联已在模型中定义，删除时注意数据完整性

## 文件结构

```
hd_python/
├── models.py                           # 数据库模型定义
├── database.py                         # 数据库配置
├── main.py                            # 主应用入口
├── middleware.py                      # 中间件（认证等）
├── create_recruitment_tables.py       # 数据库表创建脚本
└── routers/
    ├── recruitment_approval.py        # 招聘审批
    ├── recruitment_position.py        # 岗位管理
    ├── recruitment_resume.py          # 简历管理
    ├── recruitment_channel.py         # 渠道管理
    ├── recruitment_interview.py       # 面试管理
    ├── recruitment_offer.py           # Offer管理
    ├── recruitment_dashboard.py       # 仪表板统计
    ├── recruitment_question_bank.py   # 题库管理
    └── recruitment_job_profile.py     # 岗位画像管理
```

## 开发者

生成时间: 2024-03-09

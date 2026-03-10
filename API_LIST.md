# 招聘管理模块接口清单

## 1. 招聘审批管理 (9个接口)

### 基础路径: `/api/recruitment-approval`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/list` | 获取审批单列表 |
| GET | `/{approval_id}` | 获取审批单详情 |
| POST | `` | 创建审批单 |
| PUT | `/{approval_id}` | 更新审批单 |
| DELETE | `/{approval_id}` | 删除审批单 |
| POST | `/{approval_id}/submit` | 提交审批 |
| POST | `/{approval_id}/withdraw` | 撤回审批 |
| POST | `/{approval_id}/approve` | 审批通过 |
| POST | `/{approval_id}/reject` | 审批驳回 |

## 2. 岗位管理 (6个接口)

### 基础路径: `/api/recruitment-position`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/list` | 获取岗位列表 |
| GET | `/{position_id}` | 获取岗位详情 |
| POST | `` | 创建岗位 |
| PUT | `/{position_id}` | 更新岗位 |
| DELETE | `/{position_id}` | 删除岗位 |
| POST | `/{position_id}/publish` | 发布到渠道 |

## 3. 简历管理 (7个接口)

### 基础路径: `/api/recruitment-resume`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/list` | 获取简历列表 |
| GET | `/{resume_id}` | 获取简历详情 |
| POST | `` | 创建简历 |
| PUT | `/{resume_id}` | 更新简历 |
| DELETE | `/{resume_id}` | 删除简历 |
| POST | `/{resume_id}/schedule-interview` | 安排面试 |
| POST | `/{resume_id}/reject` | 淘汰候选人 |

## 4. 招聘渠道管理 (5个接口)

### 基础路径: `/api/recruitment-channel`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/list` | 获取渠道列表 |
| GET | `/{channel_id}` | 获取渠道详情 |
| POST | `` | 创建渠道 |
| PUT | `/{channel_id}` | 更新渠道 |
| DELETE | `/{channel_id}` | 删除渠道 |

## 5. 面试管理 (5个接口)

### 基础路径: `/api/recruitment-interview`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/list` | 获取面试列表 |
| GET | `/{interview_id}` | 获取面试详情 |
| POST | `` | 创建面试记录 |
| POST | `/{interview_id}/feedback` | 提交面试反馈 |
| DELETE | `/{interview_id}` | 删除面试记录 |

## 6. Offer管理 (5个接口)

### 基础路径: `/api/recruitment-offer`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/list` | 获取Offer列表 |
| GET | `/{offer_id}` | 获取Offer详情 |
| POST | `` | 创建Offer |
| POST | `/{offer_id}/approve` | 审批Offer |
| POST | `/{offer_id}/send` | 发放Offer |

## 7. 仪表板统计 (1个接口)

### 基础路径: `/api/recruitment-dashboard`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/stats` | 获取统计数据 |

## 8. 题库管理 (5个接口)

### 基础路径: `/api/recruitment-question-bank`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/list` | 获取题目列表 |
| GET | `/{question_id}` | 获取题目详情 |
| POST | `` | 创建题目 |
| PUT | `/{question_id}` | 更新题目 |
| DELETE | `/{question_id}` | 删除题目 |

## 9. 岗位画像管理 (4个接口)

### 基础路径: `/api/recruitment-job-profile`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/list` | 获取岗位画像列表 |
| GET | `/{profile_id}` | 获取岗位画像详情 |
| POST | `` | 创建岗位画像 |
| PUT | `/{profile_id}` | 更新岗位画像 |

---

**总计: 47 个接口**

## 通用参数说明

### 列表查询参数
- `page`: 页码，默认 1
- `page_size`: 每页数量，默认 20
- `keyword`: 关键词搜索
- `status`: 状态筛选

### 响应格式
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

## 认证说明

所有接口都需要通过 `get_current_user` 中间件进行身份验证。

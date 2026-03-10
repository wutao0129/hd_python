# 快速启动指南

## 1. 创建数据库表

```bash
cd D:\procjet\hd_python
python create_recruitment_tables.py
```

预期输出：
```
开始创建招聘管理模块数据库表...
✅ 数据库表创建完成！

已创建的表：
  - recruitment_approvals (招聘审批单)
  - recruitment_positions (招聘岗位)
  - recruitment_resumes (简历)
  - recruitment_channels (招聘渠道)
  - recruitment_interviews (面试记录)
  - recruitment_offers (Offer)
  - recruitment_question_bank (题库)
  - recruitment_job_profiles (岗位画像)
```

## 2. 验证路由注册

```bash
python test_routes.py
```

预期输出：
```
[OK] All routes registered successfully!
总计: 23 个路由
已注册: 23 个
缺失: 0 个
```

## 3. 启动服务

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 4. 访问 API 文档

浏览器打开：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 5. 测试接口

### 测试岗位列表接口
```bash
curl http://localhost:8000/api/recruitment-position/list
```

### 测试统计接口
```bash
curl http://localhost:8000/api/recruitment-dashboard/stats
```

## 常见问题

### Q: 数据库连接失败
A: 检查 database.py 中的数据库配置是否正确

### Q: 认证失败
A: 确保请求头中包含正确的认证信息，或检查 middleware.py

### Q: 路由未找到
A: 运行 test_routes.py 验证路由是否正确注册

## 文档参考

- 完整文档: RECRUITMENT_README.md
- 接口清单: API_LIST.md
- 生成总结: SUMMARY.md

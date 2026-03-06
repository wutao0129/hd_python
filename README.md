# 后端 API 项目文档

## 项目概述

基于 FastAPI 的后端 API 服务，为前端 Vue 3 项目提供数据接口。

## 技术栈

- **FastAPI** - 现代化的 Python Web 框架
- **SQLAlchemy** - ORM 数据库操作
- **PyMySQL** - MySQL 数据库驱动
- **Uvicorn** - ASGI 服务器
- **Pydantic** - 数据验证

## 项目结构

```
hd_python/
├── main.py              # FastAPI 应用入口
├── database.py          # 数据库连接配置
├── models.py            # SQLAlchemy 数据模型
├── requirements.txt     # Python 依赖包
├── routers/             # API 路由模块
│   ├── questionnaire.py # 问卷管理
│   ├── survey.py        # 问卷填写
│   ├── export.py        # 数据导出
│   ├── upload.py        # 文件上传
│   └── menu.py          # 菜单管理
├── migrations/          # 数据库迁移文件
└── uploads/             # 上传文件存储
```

## 数据库配置

### 连接信息（database.py）

```python
DATABASE_URL = "mysql+pymysql://root:myDHR2023.COM@192.168.110.162:9896/mydhr?charset=utf8mb4"
```

**配置说明：**
- 数据库类型：MySQL
- 主机：192.168.110.162
- 端口：9896
- 数据库名：mydhr
- 字符集：utf8mb4

**重要提示：**
- 数据库连接已配置 `pool_pre_ping=True`，自动检测连接有效性
- 使用 `SessionLocal` 创建数据库会话
- 使用 `get_db()` 依赖注入获取数据库连接

### 数据模型

主要模型定义在 `models.py` 中：

- **Questionnaire** - 问卷表
- **Menu** - 菜单表（包含多语言支持）
- 其他业务模型...

## 启动方式

### 开发环境启动

```bash
# 进入项目目录
cd D:\workspace\AI-WEB\ccpm_project\hd_python

# 安装依赖（首次运行）
pip install -r requirements.txt

# 启动服务（开发模式，自动重载）
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 或使用 Python 模块方式
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 生产环境启动

```bash
# 后台运行
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &

# 或使用多进程
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 停止服务

```bash
# Windows
taskkill //F //IM uvicorn.exe

# Linux/Mac
pkill -f "uvicorn.*main:app"
```

## API 路由

### 健康检查

```
GET /health
返回：{"status": "ok"}
```

### 菜单管理（menu.py）

```
GET  /api/menus              # 获取用户菜单（前端使用）
GET  /api/admin/menus        # 获取所有菜单（管理端）
POST /api/admin/menus        # 创建菜单
PUT  /api/admin/menus/{id}   # 更新菜单
DELETE /api/admin/menus/{id} # 删除菜单
```

### 问卷管理（questionnaire.py）

```
GET  /api/questionnaires     # 获取问卷列表
POST /api/questionnaires     # 创建问卷
GET  /api/questionnaires/{id} # 获取问卷详情
PUT  /api/questionnaires/{id} # 更新问卷
DELETE /api/questionnaires/{id} # 删除问卷
```

### 其他路由

- **survey.py** - 问卷填写相关接口
- **export.py** - 数据导出接口
- **upload.py** - 文件上传接口

## 开发规范

### 添加新路由

1. 在 `routers/` 目录创建新的路由文件
2. 定义 APIRouter 实例
3. 在 `main.py` 中导入并注册路由

示例：

```python
# routers/new_feature.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter(prefix="/api/new-feature", tags=["新功能"])

@router.get("/")
def get_items(db: Session = Depends(get_db)):
    return {"items": []}
```

```python
# main.py
from routers import new_feature
app.include_router(new_feature.router)
```

### 数据库操作

**使用依赖注入获取数据库会话：**

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db

@router.get("/items")
def get_items(db: Session = Depends(get_db)):
    items = db.query(Model).all()
    return items
```

**不要手动创建 SessionLocal：**

```python
# ❌ 错误方式
from database import SessionLocal
db = SessionLocal()

# ✅ 正确方式
def get_items(db: Session = Depends(get_db)):
    # 使用 db
```

### 添加新数据模型

1. 在 `models.py` 中定义模型类
2. 继承 `Base` 类
3. 使用 SQLAlchemy 2.0 风格的类型注解

示例：

```python
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class NewModel(Base):
    __tablename__ = "new_table"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
```

### CORS 配置

已配置允许所有来源的跨域请求：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

生产环境建议限制 `allow_origins` 为具体域名。

### 静态文件

上传文件存储在 `uploads/` 目录，通过 `/uploads/` 路径访问。

## 常见问题

### 数据库连接失败

**问题：** `Access denied for user 'root'@'xxx'`

**原因：** IP 地址变化导致数据库权限不匹配

**解决：** 联系数据库管理员添加新 IP 的访问权限

### 端口被占用

**问题：** `Address already in use`

**解决：**
```bash
# 查找占用端口的进程
netstat -ano | findstr :8000

# 停止进程
taskkill //F //PID <进程ID>
```

### 代码修改不生效

**原因：** Python 缓存或多个进程运行

**解决：**
```bash
# 1. 停止所有 uvicorn 进程
taskkill //F //IM uvicorn.exe

# 2. 清除 Python 缓存
find . -type d -name __pycache__ -exec rm -rf {} +
find . -name "*.pyc" -delete

# 3. 重新启动
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API 文档

启动服务后访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 注意事项

1. **不要在 epic worktree 中创建后端项目** - 后端项目独立于前端分支
2. **数据库连接已配置** - 直接使用 `get_db()` 依赖注入
3. **使用 SQLAlchemy 2.0 语法** - 类型注解 + `Mapped`
4. **路由前缀统一** - 所有 API 使用 `/api/` 前缀
5. **停止服务后再修改代码** - 避免多进程冲突

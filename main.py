from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import questionnaire, survey, export, upload, menu, role, recruitment_approval, tags, tag_records
from pathlib import Path

app = FastAPI(title="问卷接口服务", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
upload_dir = Path("uploads")
upload_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(questionnaire.router)
app.include_router(survey.router)
app.include_router(export.router)
app.include_router(upload.router)
app.include_router(menu.router)
app.include_router(role.router)
app.include_router(recruitment_approval.router)
app.include_router(tags.router)
app.include_router(tag_records.router)


@app.get("/health")
def health():
    return {"status": "ok"}

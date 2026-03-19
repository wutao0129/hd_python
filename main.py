from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import (
    questionnaire,
    survey,
    export,
    upload,
    menu,
    role,
    recruitment_approval,
    recruitment_position,
    recruitment_resume,
    recruitment_channel,
    recruitment_interview,
    recruitment_offer,
    recruitment_dashboard,
    recruitment_question_bank,
    competency_model,
    indicator_library,
    matching,
    rule_set
)
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
app.include_router(recruitment_position.router)
app.include_router(recruitment_resume.router)
app.include_router(recruitment_channel.router)
app.include_router(recruitment_interview.router)
app.include_router(recruitment_offer.router)
app.include_router(recruitment_dashboard.router)
app.include_router(recruitment_question_bank.router)
app.include_router(competency_model.router)
app.include_router(competency_model.scoring_router)
app.include_router(indicator_library.router)
app.include_router(matching.router)
app.include_router(rule_set.router)


@app.get("/health")
def health():
    return {"status": "ok"}

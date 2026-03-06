from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import SysRole

router = APIRouter(prefix="/api", tags=["roles"])

@router.get("/roles")
def get_roles(db: Session = Depends(get_db)):
    """获取角色列表"""
    roles = db.query(SysRole).filter(
        (SysRole.DELETE_MARK == None) | (SysRole.DELETE_MARK != '1')
    ).all()
    return {
        "code": 200,
        "data": [{"id": r.ROLE_ID, "name": r.ROLE_NAME, "description": r.ROLE_DESC} for r in roles]
    }

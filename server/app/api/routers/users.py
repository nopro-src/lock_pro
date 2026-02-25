from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.deps import get_db, get_current_account
from app.api.schemas.users import AccountOut
from app.db.models import Account

router = APIRouter()


@router.get("", response_model=list[AccountOut])
def list_users(db: Session = Depends(get_db), acc=Depends(get_current_account)):
    # simple admin list for web demo; production nên hạn chế theo lock
    rows = db.execute(select(Account).order_by(Account.id.desc()).limit(200)).scalars().all()
    return [AccountOut(id=u.id, email=u.email, full_name=u.full_name, is_active=u.is_active) for u in rows]
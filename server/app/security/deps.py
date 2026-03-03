from __future__ import annotations

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.exceptions import http_401
from app.security.jwt import decode_token
from app.repos.account_repo import AccountRepo
from app.models.account import Account

from fastapi import Depends
from app.exceptions import http_403
from app.models.account import GlobalRole


def get_current_account(
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None),
) -> Account:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise http_401("Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_token(token)
        account_id = int(payload.sub)
    except Exception:
        raise http_401("Invalid token")

    acct = AccountRepo(db).get_by_id(account_id)
    if not acct or not acct.is_active:
        raise http_401("Account disabled or not found")
    return acct

def require_global_role(*roles: GlobalRole):
    def _dep(acct=Depends(get_current_account)):
        if acct.global_role not in roles:
            raise http_403("Forbidden: insufficient global role")
        return acct
    return _dep
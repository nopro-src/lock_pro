import secrets
from sqlalchemy.orm import Session
from app.db.repositories import locks_repo, accounts_repo
from app.core.exceptions import not_found, forbidden, bad_request


ROLE_OWNER = "OWNER"
ROLE_USER = "USER"


def create_lock_as_owner(db: Session, owner_account_id: int, name: str):
    # generate pairing code (later ESP32 can use it)
    code = secrets.token_hex(8)
    lk = locks_repo.create_lock(db, name=name, code=code)
    locks_repo.add_member(db, lock_id=lk.id, account_id=owner_account_id, role=ROLE_OWNER)
    return lk


def require_owner(db: Session, lock_id: int, account_id: int):
    mem = locks_repo.get_membership(db, lock_id, account_id)
    if not mem:
        raise forbidden("Not a member of this lock")
    if mem.role != ROLE_OWNER:
        raise forbidden("Owner role required")
    return mem


def add_user_to_lock(db: Session, lock_id: int, owner_account_id: int, email: str, role: str):
    require_owner(db, lock_id, owner_account_id)
    if role not in (ROLE_OWNER, ROLE_USER):
        raise bad_request("Invalid role")

    acc = accounts_repo.get_by_email(db, email)
    if not acc:
        raise not_found("Account not found")

    existing = locks_repo.get_membership(db, lock_id, acc.id)
    if existing:
        return existing

    return locks_repo.add_member(db, lock_id, acc.id, role=role)
from sqlalchemy.orm import Session
from app.db.repositories import accounts_repo
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import bad_request, unauthorized


def register(db: Session, email: str, password: str, full_name: str = ""):
    if accounts_repo.get_by_email(db, email):
        raise bad_request("Email already exists")
    acc = accounts_repo.create(db, email=email, password_hash=hash_password(password), full_name=full_name)
    token = create_access_token(subject=str(acc.id))
    return acc, token


def login(db: Session, email: str, password: str):
    acc = accounts_repo.get_by_email(db, email)
    if not acc:
        raise unauthorized("Invalid credentials")
    if not verify_password(password, acc.password_hash):
        raise unauthorized("Invalid credentials")
    if not acc.is_active:
        raise unauthorized("Account inactive")
    token = create_access_token(subject=str(acc.id))
    return acc, token
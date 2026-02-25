from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.repositories.accounts_repo import get_by_email, create
from app.core.security import hash_password

DEFAULT_OWNER_EMAIL = "owner@example.com"
DEFAULT_OWNER_PASSWORD = "12345678"
DEFAULT_OWNER_NAME = "Owner"

def seed_default_owner():
    db: Session = SessionLocal()
    try:
        acc = get_by_email(db, DEFAULT_OWNER_EMAIL)
        if not acc:
            create(
                db,
                email=DEFAULT_OWNER_EMAIL,
                password_hash=hash_password(DEFAULT_OWNER_PASSWORD),
                full_name=DEFAULT_OWNER_NAME,
            )
            print(f"[seed] created owner: {DEFAULT_OWNER_EMAIL} / {DEFAULT_OWNER_PASSWORD}")
        else:
            print(f"[seed] owner already exists: {DEFAULT_OWNER_EMAIL}")
    finally:
        db.close()
from __future__ import annotations

from app.models.lock_member import LockRole


def role_rank(role: LockRole) -> int:
    return {
        LockRole.OWNER: 3,
        LockRole.ADMIN: 2,
        LockRole.USER: 1,
    }[role]


def has_at_least(member_role: LockRole, required: LockRole) -> bool:
    return role_rank(member_role) >= role_rank(required)
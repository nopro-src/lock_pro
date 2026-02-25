from __future__ import annotations

from fastapi import HTTPException, status


class AppError(Exception):
    """Base app exception (non-HTTP)"""


class NotFoundError(AppError):
    pass


class ForbiddenError(AppError):
    pass


class ConflictError(AppError):
    pass


class ValidationAppError(AppError):
    pass


def http_401(detail: str = "Unauthorized") -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


def http_403(detail: str = "Forbidden") -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def http_404(detail: str = "Not found") -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def http_409(detail: str = "Conflict") -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)


def http_422(detail: str = "Unprocessable entity") -> HTTPException:
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)
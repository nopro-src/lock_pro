from fastapi import HTTPException


def bad_request(msg: str) -> HTTPException:
    return HTTPException(status_code=400, detail=msg)


def forbidden(msg: str = "Forbidden") -> HTTPException:
    return HTTPException(status_code=403, detail=msg)


def unauthorized(msg: str = "Unauthorized") -> HTTPException:
    return HTTPException(status_code=401, detail=msg)


def not_found(msg: str = "Not found") -> HTTPException:
    return HTTPException(status_code=404, detail=msg)
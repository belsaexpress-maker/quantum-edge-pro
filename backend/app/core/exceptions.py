from fastapi import HTTPException


def not_found(message: str = "Kayıt bulunamadı"):
    raise HTTPException(
        status_code=404,
        detail=message
    )


def bad_request(message: str = "Geçersiz istek"):
    raise HTTPException(
        status_code=400,
        detail=message
    )


def unauthorized(message: str = "Yetkisiz işlem"):
    raise HTTPException(
        status_code=401,
        detail=message
    )


def forbidden(message: str = "Bu işlem için yetkiniz yok"):
    raise HTTPException(
        status_code=403,
        detail=message
    )
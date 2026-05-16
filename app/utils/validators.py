import re
from fastapi import HTTPException

def validate_phone(phone: str) -> str:
    pattern = r'^\+?[1-9]\d{1,14}$'
    if not re.match(pattern, phone):
        raise HTTPException(
            status_code=400,
            detail="Invalid phone number format"
        )
    return phone

def validate_url(url: str) -> str:
    pattern = r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
    if not re.match(pattern, url):
        raise HTTPException(
            status_code=400,
            detail="Invalid URL format"
        )
    return url

def validate_rating(rating: int) -> int:
    if rating < 1 or rating > 5:
        raise HTTPException(
            status_code=400,
            detail="Rating must be between 1 and 5"
        )
    return rating

def validate_file_size(file_size: int, max_size_mb: int = 5) -> bool:
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File size must not exceed {max_size_mb}MB"
        )
    return True

def validate_file_extension(filename: str, allowed: list) -> str:
    ext = filename.split(".")[-1].lower()
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed)}"
        )
    return ext
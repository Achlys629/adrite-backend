from fastapi import Query
from typing import Optional

class PaginationParams:
    def __init__(
        self,
        page: int = Query(default=1, ge=1),
        limit: int = Query(default=10, ge=1, le=100),
        search: Optional[str] = Query(default=None)
    ):
        self.page = page
        self.limit = limit
        self.search = search
        self.offset = (page - 1) * limit

def paginate_query(query, pagination: PaginationParams):
    total = query.count()
    items = query.offset(pagination.offset).limit(pagination.limit).all()
    return {
        "items": items,
        "total": total,
        "page": pagination.page,
        "limit": pagination.limit,
        "pages": (total + pagination.limit - 1) // pagination.limit
    }
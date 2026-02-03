from app.api.v1 import members, books, borrow
from fastapi import FastAPI

app = FastAPI(title="Library Management API")

app.include_router(books.router, prefix="/api/v1/books", tags=["Books"])
app.include_router(members.router, prefix="/api/v1/members", tags=["Members"])
app.include_router(borrow.router, prefix="/api/v1/borrow", tags=["Borrows"])

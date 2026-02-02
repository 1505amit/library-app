from app.api.v1 import members
from fastapi import FastAPI
from app.api.v1 import books

app = FastAPI(title="Library Management API")

app.include_router(books.router, prefix="/api/v1/books", tags=["Books"])
app.include_router(members.router, prefix="/api/v1/members", tags=["Members"])

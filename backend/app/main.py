from app.api.v1 import members, books, borrow
from app.common.settings import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Library Management API")

# Get allowed origins from settings
ALLOWED_ORIGINS = settings.allowed_origins.split(",")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(books.router, prefix="/api/v1/books", tags=["Books"])
app.include_router(members.router, prefix="/api/v1/members", tags=["Members"])
app.include_router(borrow.router, prefix="/api/v1/borrow", tags=["Borrows"])

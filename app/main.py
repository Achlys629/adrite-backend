from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import models
from fastapi.exception_handlers import http_exception_handler,RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.utils.exceptions import validation_exception_handler, http_exception_handler as custom_http_handler
from slowapi.errors import RateLimitExceeded
from app.middleware.rate_limit import limiter, rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded 
from app.api.v1.endpoints import auth, users, projects, invoices, tickets, blogs, chat, payments, admin, webhooks
from app.utils.logger import logger
from starlette.middleware.base import BaseHTTPMiddleware
from app.middleware.logging import logging_middleware
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("ADRITE AGENCY API started successfully")
    yield
    # Shutdown
    logger.info("ADRITE AGENCY API shutting down")

app = FastAPI(
    title="ADRITE AGENCY API",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True},
     lifespan=lifespan
    
)
# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

@app.middleware("http")
async def add_ngrok_header(request, call_next):
    response = await call_next(request)
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",
                   "https://devotedly-subtotal-evident.ngrok-free.dev"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(invoices.router, prefix="/api/v1/invoices", tags=["Invoices"])
app.include_router(tickets.router, prefix="/api/v1/tickets", tags=["Tickets"])
app.include_router(blogs.router, prefix="/api/v1/blogs", tags=["Blogs"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["Webhooks"])

app.add_middleware(BaseHTTPMiddleware, dispatch=logging_middleware)

@app.get("/")
def root():
    return {"message": "ADRITE AGENCY API is running"}





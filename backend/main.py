from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from routes import admin, auth
from config.settings import settings

# Configure HTTPBearer security for Swagger UI
security = HTTPBearer()

app = FastAPI(
    title=settings.APP_NAME,
    description="Role-based access control system for college hackathon management",
    version=settings.API_VERSION,
    debug=settings.DEBUG,
    swagger_ui_parameters={
        "persistAuthorization": True  # Keep authorization after page refresh
    }
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.API_VERSION,
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
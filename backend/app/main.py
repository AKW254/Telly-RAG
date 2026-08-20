from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

#Configs
from app.config.settings import settings

#Database 
from app.database.database import init_db

#Middlewares
from app.middlewares.brokerAvailabilityMiddleware import BrokerAvailabilityMiddleware
from app.middlewares.logger_middleware import LoggingMiddleware
from app.middlewares.ratelimit_middleware import RateLimitMiddleware
#from app.middlewares.securityheader_middleware import SecurityHeadersMiddleware

#Routes
from app.api.routes.auth import router as auth
from app.api.routes.documents import router as documents
from app.api.routes.chats import router as chats

#Logger 
from app.utils.logger import logger


# --------------------------------------------------
# App Initialization
# --------------------------------------------------

def create_app()-> FastAPI:
    app = FastAPI(
        title="Telly Agentic RAG Chat Bot",
        version="1.0.0",
        description="LangChain-powered Retrival augmented Genation Conversation Bot",
    )
# --------------------------------------------------
# Middlewares Initialization
# --------------------------------------------------
    #Fastapi 
    app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.get_cors_origins(),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            )
    #User Defined
    app.add_middleware(BrokerAvailabilityMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)
    #app.add_middleware(SecurityHeadersMiddleware)
    
  
# --------------------------------------------------
# Routes
# --------------------------------------------------  
    app.include_router(auth,prefix="/api/auth", tags=["auth"])
    app.include_router(documents, prefix="/api/documents", tags=["documents"])
    app.include_router(chats,prefix="/api/chats", tags=["chats"])
    
# --------------------------------------------------
# Startup Event
# --------------------------------------------------
    @app.on_event("startup")
    async def startup_event():
        logger.info("Starting Telly RAG Chatbot API...")
        init_db()

# --------------------------------------------------
# Shutdown Event
# --------------------------------------------------
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Shutting down API...")

# --------------------------------------------------
# Root Route
# --------------------------------------------------
    @app.get("/", tags=["Root"])
    def root():
        return {
        "status": "ok",
        "message": "Telly RAG Chatbot API running"
        }


# --------------------------------------------------
# Health Check
# --------------------------------------------------
    @app.get("/health", tags=["Health"])
    def health_check():
        return {"status": "healthy"}

    return app  


# --------------------------------------------------
# App Instance
# --------------------------------------------------  

app=create_app()

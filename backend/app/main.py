from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.core import config
from dotenv import load_dotenv
load_dotenv()
app = FastAPI(title=config.PROJECT_NAME)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=config.API_V1_STR)

@app.get("/")
async def root():
    """Root endpoint for healthcheck"""
    return {"message": "Document Research & Theme Identification Chatbot API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
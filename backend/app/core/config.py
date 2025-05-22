# backend/app/core/config.py
import os

# Application settings
PROJECT_NAME = "Document Research & Theme Identification Chatbot"
API_V1_STR = "/api/v1"

# Database settings
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./docresearch.db")

# Document storage
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./data/uploads")
EMBEDDING_DIR = os.getenv("EMBEDDING_DIR", "./data/embeddings")

# Google Generative AI settings
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# OCR and text extraction settings
OCR_DPI = 300

# Vector DB settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_RESULTS = 5

# Model settings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "gemini-1.5-flash"
LLM_TEMPERATURE = 0.3

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EMBEDDING_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DATABASE_URL.replace("sqlite:///", "")), exist_ok=True)
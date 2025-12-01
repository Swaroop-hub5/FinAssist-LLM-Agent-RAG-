import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # Using "gemini-flash-latest" - ensure Generative Language API is enabled in Google Cloud Console
    LLM_MODEL = "gemini-flash-latest" 
    
    VECTOR_STORE_PATH = "faiss_index"

settings = Settings()

if not settings.GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file")
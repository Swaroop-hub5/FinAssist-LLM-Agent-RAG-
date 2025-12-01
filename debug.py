import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load your API Key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ Error: GOOGLE_API_KEY not found in .env")
    exit()

print(f"🔑 Testing API Key: {api_key[:5]}...{api_key[-5:]}")

try:
    genai.configure(api_key=api_key)
    print("📡 Connecting to Google API...")
    
    print("\n✅ AVAILABLE MODELS FOR THIS KEY:")
    print("-" * 30)
    found_any = False
    for m in genai.list_models():
        # We only care about models that can generate text (content)
        if 'generateContent' in m.supported_generation_methods:
            print(f"• {m.name}")
            found_any = True
            
    if not found_any:
        print("❌ No text generation models found. This usually means the 'Generative Language API' is disabled for this project.")
    print("-" * 30)

except Exception as e:
    print(f"\n❌ CRITICAL ERROR: {str(e)}")
    print("This often means the API Key is invalid or from the wrong provider (Vertex AI vs AI Studio).")
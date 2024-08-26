from openai import OpenAI
from app.config import OPENAI_API_KEY

print(f"API Key: {OPENAI_API_KEY[:8]}...")

try:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    models = openai_client.models.list()
    print("OpenAI client initialized successfully")
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    raise

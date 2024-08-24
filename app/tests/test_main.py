import os
from openai import OpenAI
from app.config import OPENAI_API_KEY

# Print the API key (first few characters) for debugging
print(f"API Key: {OPENAI_API_KEY[:8]}...")

# Initialize OpenAI client
try:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    # Test the client with a simple API call
    models = openai_client.models.list()
    print("OpenAI client initialized successfully")
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    raise

# Rest of your code...
import os
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENVIRONMENT = 'aped-4627-b74a'
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PINECONE_HOST = 'https://owngpt-a9vgyyl.svc.aped-4627-b74a.pinecone.io'
# REDIS_URL = os.getenv("REDIS_URL")
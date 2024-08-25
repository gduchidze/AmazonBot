import os
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

load_dotenv()

PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
PINECONE_ENVIRONMENT = 'aped-4627-b74a'
PINECONE_INDEX_NAME = os.environ.get('PINECONE_INDEX_NAME')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
PINECONE_HOST = 'https://owngpt-a9vgyyl.svc.aped-4627-b74a.pinecone.io'
# REDIS_URL = os.getenv("REDIS_URL")

openai_client = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME, host=PINECONE_HOST)
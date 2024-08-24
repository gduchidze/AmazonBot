from app.config import PINECONE_INDEX_NAME, PINECONE_HOST, OPENAI_API_KEY, PINECONE_API_KEY
from openai import OpenAI
from pinecone import Pinecone
import pandas as pd
from tqdm import tqdm

openai_client = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME, host=PINECONE_HOST)

df = pd.read_csv('data/products.csv')

def create_product_text(row):
    values = [str(val) if not pd.isna(val) else '' for val in [
        row['Product Name'], row['Brand Name'], row['Category'],
        row['About Product'], row['Product Description']
    ]]
    return ' '.join(values).strip()

def get_embeddings(texts):
    response = openai_client.embeddings.create(
        input=texts,
        model="text-embedding-3-small"
    )
    return [emb.embedding for emb in response.data]

def clean_metadata(row):
    return {
        'product_name': str(row['Product Name']) if not pd.isna(row['Product Name']) else '',
        'brand_name': str(row['Brand Name']) if not pd.isna(row['Brand Name']) else '',
        'category': str(row['Category']) if not pd.isna(row['Category']) else '',
        'selling_price': str(row['Selling Price']) if not pd.isna(row['Selling Price']) else '',
        'about_product': str(row['About Product']) if not pd.isna(row['About Product']) else '',
        'product_url': str(row['Product Url']) if not pd.isna(row['Product Url']) else ''
    }


batch_size = 100
vectors = []

for i in tqdm(range(0, len(df), batch_size)):
    batch = df.iloc[i:i + batch_size]
    texts = [create_product_text(row) for _, row in batch.iterrows()]
    embeddings = get_embeddings(texts)

    for (_, row), emb in zip(batch.iterrows(), embeddings):
        if pd.isna(row['Uniq Id']):
            continue
        vector = {
            'id': str(row['Uniq Id']),
            'values': emb,
            'metadata': clean_metadata(row)
        }
        vectors.append(vector)

    if vectors:
        try:
            index.upsert(vectors)
        except Exception as e:
            print(f"Error upserting batch: {e}")
            print("Problematic vectors:")
            for v in vectors:
                print(v['id'], v['metadata'])
    vectors = []

if vectors:
    try:
        index.upsert(vectors)
    except Exception as e:
        print(f"Error upserting final batch: {e}")
        print("Problematic vectors:")
        for v in vectors:
            print(v['id'], v['metadata'])

print("Upload complete!")
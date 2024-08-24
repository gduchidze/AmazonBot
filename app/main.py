import os
from openai import OpenAI
from pinecone import Pinecone
from app.config import PINECONE_INDEX_NAME, PINECONE_HOST, OPENAI_API_KEY, PINECONE_API_KEY

# Initialize OpenAI and Pinecone clients
openai_client = OpenAI(
    api_key=OPENAI_API_KEY
)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME, host=PINECONE_HOST)


def get_embedding(text):
    """Get embedding for a given text."""
    response = openai_client.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    return response.data[0].embedding


def search_products(query, top_k=10):
    """Search for products based on the query."""
    query_embedding = get_embedding(query)
    results = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
    return results.matches


def format_product(product):
    """Format product information for display."""
    return f"""
Product: {product.metadata['product_name']}
Brand: {product.metadata['brand_name']}
Category: {product.metadata['category']}
Price: {product.metadata['selling_price']}
About: {product.metadata['about_product'][:100]}...
URL: {product.metadata['product_url']}
"""


def generate_response(conversation_history, user_input, products):
    """Generate a response using the OpenAI API."""
    formatted_products = "\n".join([format_product(p) for p in products[:5]])

    messages = conversation_history + [
        {"role": "user", "content": user_input},
        {"role": "system",
         "content": f"Here are the top 5 product recommendations based on the user's query:\n\n{formatted_products}\n\nPlease provide a helpful response to the user based on these product recommendations. Suggest products that best match their query, and offer to provide more information or refine the search if needed."}
    ]

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.1,
    )

    return response.choices[0].message.content


def product_recommendation_bot(user_input):
    conversation_history = [
        {"role": "system",
         "content": "You are a E-commerce site Duchi's product recommendation assistant. Your goal is to help users find products they're looking for based on their queries."}
    ]

    results = search_products(user_input)

    if not results:
        return generate_response(conversation_history, user_input, [])
    else:
        return generate_response(conversation_history, user_input, results)


if __name__ == "__main__":
    user_query = "I'm looking for a new smartphone with a good camera"
    response = product_recommendation_bot(user_query)
    print(response)
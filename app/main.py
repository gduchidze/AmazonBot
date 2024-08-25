import os
from openai import OpenAI
from pinecone import Pinecone
from app.config import PINECONE_INDEX_NAME, PINECONE_HOST, OPENAI_API_KEY, PINECONE_API_KEY
from app.functions import function_registry, should_call_function, execute_function, format_product
from app.prompt import SYSTEM_PROMPT

openai_client = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME, host=PINECONE_HOST)


def get_embedding(text):
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


def run_conversation():
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    print("Duchi's Product Recommendation Bot: Hello! How can I help you find products today?")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("Duchi's Product Recommendation Bot: Thank you for using our service. Goodbye!")
            break

        messages.append({"role": "user", "content": user_input})

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        assistant_response = response.choices[0].message.content

        function_name, args = should_call_function(assistant_response)
        if function_name:
            try:
                if function_name == "search_products":
                    function_result = search_products(**args)
                    formatted_products = [format_product(product) for product in function_result]
                    function_response = "\n".join(formatted_products)
                else:
                    function_result = execute_function(function_name, args)
                    function_response = function_result

                messages.append({"role": "function", "name": function_name, "content": function_response})

                second_response = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages
                )
                assistant_response = second_response.choices[0].message.content
            except ValueError as e:
                assistant_response += f"\n(Error: {str(e)})"

        print(f"Duchi's Bot: {assistant_response}")
        messages.append({"role": "assistant", "content": assistant_response})

if __name__ == "__main__":
    run_conversation()
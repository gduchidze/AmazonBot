from flask import Flask, request, jsonify
from config import PINECONE_INDEX_NAME, PINECONE_HOST, OPENAI_API_KEY, PINECONE_API_KEY, openai_client, pc, index
from functions import function_registry, should_call_function, execute_function, format_product
from prompt import SYSTEM_PROMPT

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Amazon Chat."

def get_embedding(text):
    """Get the text embedding for a given text."""
    response = openai_client.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    return response.data[0].embedding


def search_products(query, top_k=10):
    """Search for products based on a query."""
    query_embedding = get_embedding(query)
    results = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
    return results.matches


@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message']
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input}
    ]

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

    return jsonify({"response": assistant_response})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
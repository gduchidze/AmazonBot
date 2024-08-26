import json
from typing import Callable, Dict, Any
import re

# ფუნქციების რეესტრი, სადაც ვინახავთ ყველა რეგისტრირებულ ფუნქციას
function_registry: Dict[str, Dict[str, Any]] = {}

def register_function(name: str, description: str, parameters: Dict[str, Any]):
    """
    დეკორატორი ფუნქციების რეგისტრაციისთვის.
    name: ფუნქციის სახელი
    description: ფუნქციის აღწერა
    parameters: ფუნქციის პარამეტრების აღწერა
    """
    def decorator(func: Callable):
        function_registry[name] = {
            "function": func,
            "description": description,
            "parameters": parameters
        }
        return func
    return decorator

@register_function(
    name="search_products",
    description="Search for products based on a query",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The search query for products"},
            "top_k": {"type": "integer", "description": "Number of top results to return", "default": 5}
        },
        "required": ["query"]
    }
)
# აქ უნდა იყოს search_products ფუნქციის იმპლემენტაცია

@register_function(
    name="format_product",
    description="Format a product's information",
    parameters={
        "type": "object",
        "properties": {
            "product": {"type": "object", "description": "The product object to format"}
        },
        "required": ["product"]
    }
)
def format_product(product: Dict[str, Any]):
    """
    აფორმატებს პროდუქტის ინფორმაციას სტრიქონად.
    product: პროდუქტის ობიექტი
    return: დაფორმატებული სტრიქონი პროდუქტის ინფორმაციით
    """
    return f"""
Product: {product['name']}
Price: ${product['price']}
Category: {product['category']}
"""

def process_function_call(function_call: Dict[str, Any]) -> Dict[str, Any]:
    """
    ამუშავებს ფუნქციის გამოძახებას.
    :param function_call: ფუნქციის გამოძახების ინფორმაცია
    :return: ფუნქციის შედეგი
    """
    function_name = function_call.get("name")
    if function_name not in function_registry:
        raise ValueError(f"Unknown function: {function_name}")

    function_info = function_registry[function_name]
    function_args = json.loads(function_call.get("arguments", "{}"))

    result = function_info["function"](**function_args)
    return {
        "role": "function",
        "name": function_name,
        "content": json.dumps(result, default=lambda x: x.__dict__)
    }

def should_call_function(message: str) -> tuple[str | None, dict | None]:
    """
    ამოწმებს, უნდა თუ არა ფუნქციის გამოძახება მოცემული შეტყობინების საფუძველზე.
    :param message: შესამოწმებელი შეტყობინება
    :return: ფუნქციის სახელი და არგუმენტები, თუ ნაპოვნია
    """
    function_call_pattern = r'(search_products|format_product)\((.*?)\)'
    match = re.search(function_call_pattern, message)
    if match:
        function_name = match.group(1)
        args_str = match.group(2)
        args = {}
        if args_str:
            arg_pattern = r'(\w+)\s*=\s*([^,]+)'
            arg_matches = re.findall(arg_pattern, args_str)
            for key, value in arg_matches:
                args[key.strip()] = value.strip().strip('"\'')
        return function_name, args
    return None, None

def execute_function(function_name: str, args: Dict[str, Any]) -> Any:
    """
    ასრულებს მითითებულ ფუნქციას მოცემული არგუმენტებით.
    :param function_name: გამოსაძახებელი ფუნქციის სახელი
    :param args: ფუნქციის არგუმენტები
    :return: ფუნქციის შედეგი
    """
    if function_name in function_registry:
        return function_registry[function_name]['function'](**args)
    else:
        raise ValueError(f"Function {function_name} not found in registry")
'''El agente debe:

Recibir un prompt del cliente (Ej. necesito “100 cajas de tornillos y 50 martillos”).
Extraer los items y cantidades.
Consultar una base de precios en memoria.
Calcular el total
Responder una cotización formateada (ej. Tabla de productos, cantidad, precio unitario y total.'''

from typing import TypedDict
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

# Productos
products = [
    {"name": "Screw", "price": 0.25},
    {"name": "Hammer", "price": 15.99},
    {"name": "Wrench Set", "price": 45.50},
    {"name": "Drill Bit", "price": 3.75},
    {"name": "Nail", "price": 0.10},
    {"name": "Screwdriver", "price": 8.99},
    {"name": "Pliers", "price": 12.25},
    {"name": "Tape Measure", "price": 6.50},
    {"name": "Level", "price": 18.75},
    {"name": "Bolt", "price": 0.45}
]

load_dotenv()
llm = ChatOpenAI(model='gpt-4o', temperature=0)

# Modelos
class Product(BaseModel):
    quantity: int
    name: str
    price: float

class ProductNeededItem(BaseModel):
    name: str
    quantity: int

class ProductNeeded(BaseModel):
    products: list[ProductNeededItem]

class State(TypedDict):
    input_client: str
    total: float
    products: list[Product]
    structure_output: list[str]

# Funciones de nodo
def get_products_quantity(state: State) -> State:

    assistant = '''You are a distributor for a company that sells products.
    A client needs these products: {input}.
    Identify the product name (in singular) and quantity'''

    
    prompt = assistant.format(input=state['input_client'])
    response = llm.with_structured_output(ProductNeeded).invoke(prompt)
    print(response)
    products_list = []
    for item in response.products:
        product_info = next((p for p in products if p['name'].lower() == item.name.lower()), None)
        if product_info:
            products_list.append(Product(
                name=item.name,
                quantity=item.quantity,
                price=product_info['price']
            ))

    state['products'] = products_list
    return state

def calculate_total_price(state: State) -> State:
    """Calcular el total general de la cotización y actualizar el state"""
    total = 0
    for product in state['products']:
        total += product.price * product.quantity
    state['total'] = total
    return state

def format_output(state: State) -> State:
    """Generar la cotización final en un string simple"""
    lines = ["Product Quotation:\n"]
    for p in state['products']:
        lines.append(f"- {p.name}: {p.quantity} x ${p.price:.2f}")
    lines.append(f"\nTotal to pay: ${state['total']:.2f}")

    state['structure_output'] = ["\n".join(lines)]
    return state

# Construcción del grafo
builder = StateGraph(State)
builder.add_node('get_products_quantity', get_products_quantity)
builder.add_node('calculate_total_price', calculate_total_price)
builder.add_node('format_output', format_output)

builder.add_edge(START, 'get_products_quantity')
builder.add_edge('get_products_quantity', 'calculate_total_price')
builder.add_edge('calculate_total_price', 'format_output')
builder.add_edge('format_output', END)

graph = builder.compile()

user_request = input("What do you want to quote today? ")

initial_state = {
    "input_client": user_request
}
response = graph.invoke(initial_state)
print(response)

from openai import OpenAI
from .models import User, Producto, Categoria, Proveedor, Cliente, Venta, DetalleVenta
from datetime import date

client = OpenAI(
    api_key="",
    base_url="https://api.groq.com/openai/v1"
)


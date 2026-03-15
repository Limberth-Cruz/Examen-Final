from openai import OpenAI
from .models import User, Producto, Categoria, Proveedor, Cliente, Venta, DetalleVenta
from datetime import date

client = OpenAI(
    api_key="",
    base_url="https://api.groq.com/openai/v1"
)

analisis_ia.html

{% extends 'admin/master.html' %}

{% block body %}

<h2> Análisis Inteligente</h2>

<div style="white-space: pre-line; border:1px solid #ccc; padding:15px;">
    {{ analisis }}
</div>

{% endblock %}

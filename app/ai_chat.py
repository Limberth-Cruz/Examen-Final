from openai import OpenAI
from .models import User, Producto, Categoria, Proveedor, Cliente, Venta, DetalleVenta
from datetime import date

client = OpenAI(
    api_key="TU_API_KEY_AQUI",
    base_url="https://api.groq.com/openai/v1"
)

def preguntar_chatbot(pregunta):

    # 🔥 SI PREGUNTA POR HOY → CONSULTA DIRECTA A BD
    if "hoy" in pregunta.lower():

        ventas_hoy = Venta.query.filter(
            Venta.fecha == date.today()
        ).all()

        if not ventas_hoy:
            return "Hoy no se realizaron ventas."

        # calcular productos vendidos
        productos_vendidos = {}
        total_hoy = 0

        for venta in ventas_hoy:
            for detalle in venta.detalles:
                nombre = detalle.producto.nombre_producto
                productos_vendidos[nombre] = productos_vendidos.get(nombre, 0) + detalle.cantidad
                total_hoy += float(detalle.subtotal)

        resultado = "📊 Productos vendidos hoy:\n"

        for nombre, cantidad in productos_vendidos.items():
            resultado += f"- {nombre}: {cantidad}\n"

        resultado += f"\n💰 Total vendido hoy: Bs. {total_hoy:.2f}"

        return resultado

        # ==========================
    # SI NO ES "HOY" → USA IA
    # ==========================

    usuarios = User.query.all()
    productos = Producto.query.all()
    categorias = Categoria.query.all()
    proveedores = Proveedor.query.all()
    clientes = Cliente.query.all()
    ventas = Venta.query.all()
    detalles = DetalleVenta.query.all()

    lista_usuarios = ""
    for u in usuarios:
        lista_usuarios += f"{u.username} rol:{u.role}\n"

    lista_productos = ""
    for p in productos:
        lista_productos += f"{p.nombre_producto} stock:{p.stock} precio:{p.precio_venta}\n"

    lista_categorias = ""
    for c in categorias:
        lista_categorias += f"{c.nombre_categoria}\n"

    lista_proveedores = ""
    for pr in proveedores:
        lista_proveedores += f"{pr.nombre}\n"

    lista_clientes = ""
    for c in clientes:
        lista_clientes += f"{c.nombre}\n"

    lista_ventas = ""
    for v in ventas:
        lista_ventas += f"venta {v.id_venta} total:{v.total}\n"

    lista_detalles = ""
    for d in detalles:
        lista_detalles += f"venta:{d.id_venta} producto:{d.id_producto} cantidad:{d.cantidad}\n"

    contexto = f"""
Eres un asistente inteligente de una papelería conectado a la base de datos.

USUARIOS:
{lista_usuarios}

PRODUCTOS:
{lista_productos}

CATEGORÍAS:
{lista_categorias}

PROVEEDORES:
{lista_proveedores}

CLIENTES:
{lista_clientes}

VENTAS:
{lista_ventas}

DETALLE DE VENTAS:
{lista_detalles}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": contexto},
            {"role": "user", "content": pregunta}
        ]
    )

    return response.choices[0].message.content
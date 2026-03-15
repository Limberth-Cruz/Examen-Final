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

    
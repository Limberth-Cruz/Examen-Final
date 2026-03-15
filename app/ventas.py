from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import date
from .extensions import db
from .models import Producto, Cliente, Venta, DetalleVenta
from flask_login import current_user, login_required

ventas_bp = Blueprint("ventas", __name__, url_prefix="/ventas")

# Inicializar carrito en sesión
def init_carrito():
    if "carrito" not in session:
        session["carrito"] = []

@ventas_bp.route("/", methods=["GET", "POST"])
@login_required
def vender():
    init_carrito()
    productos = Producto.query.all()
    clientes = Cliente.query.all()

    if request.method == "POST":
        # Agregar producto al carrito
        producto_id = int(request.form.get("producto_id"))
        cantidad = int(request.form.get("cantidad"))
        producto = Producto.query.get(producto_id)
        if producto and cantidad > 0 and cantidad <= producto.stock:
            carrito = session["carrito"]
            # Verificar si producto ya está en carrito
            for item in carrito:
                if item["id"] == producto.id_producto:
                    item["cantidad"] += cantidad
                    item["subtotal"] = float(item["cantidad"]) * float(producto.precio_venta)
                    break
            else:
                carrito.append({
                    "id": producto.id_producto,
                    "nombre": producto.nombre_producto,
                    "precio": float(producto.precio_venta),
                    "cantidad": cantidad,
                    "subtotal": float(producto.precio_venta) * cantidad
                })
            session["carrito"] = carrito
            flash(f"{producto.nombre_producto} agregado al carrito", "success")
        else:
            flash("Cantidad inválida o stock insuficiente", "danger")
        return redirect(url_for("ventas.vender"))

    # Calcular total
    total = sum(item["subtotal"] for item in session["carrito"])
    return render_template("vender.html", productos=productos, clientes=clientes, carrito=session["carrito"], total=total)

@ventas_bp.route("/finalizar", methods=["POST"])
@login_required
def finalizar():
    cliente_id = int(request.form.get("cliente_id"))
    carrito = session.get("carrito", [])

    if not carrito:
        flash("Carrito vacío", "warning")
        return redirect(url_for("ventas.vender"))

    total = sum(item["subtotal"] for item in carrito)

    # Crear la venta usando el usuario logueado
    venta = Venta(
        fecha=date.today(),
        id_cliente=cliente_id,
        id=current_user.id,  # <-- FK correcta al usuario logueado
        total=total
    )
    db.session.add(venta)
    db.session.flush()  # obtener id_venta antes de los detalles

    # Agregar detalles y descontar stock
    for item in carrito:
        producto = Producto.query.get(item["id"])
        detalle = DetalleVenta(
            id_venta=venta.id_venta,
            id_producto=producto.id_producto,
            cantidad=item["cantidad"],
            precio_unitario=producto.precio_venta,
            subtotal=item["subtotal"]
        )
        producto.stock -= item["cantidad"]
        db.session.add(detalle)

    db.session.commit()
    session["carrito"] = []
    flash("Venta registrada con éxito", "success")
    return redirect(url_for("ventas.vender"))